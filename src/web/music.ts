import {DateTime} from 'luxon'
import {ScatterDataPoint} from 'chart.js';
import 'chartjs-adapter-luxon';
import {groupBy} from 'lodash';


export interface CsvScrobble {
    track_name: string
    album_name: string
    artist_name: string
    album_art_url: string
    unix_timestamp: string
}

export class MusicData {
    // sorted arrays for fast iteration, maps for fast lookup
    // probably better to use a binary search tree but ¯\_(ツ)_/¯

    artistArray: Array<Artist>
    albumArray: Array<Album>
    trackArray: Array<Track>

    artistMap: Map<string, Artist>
    albumMap: Map<string, Album>
    trackMap: Map<string, Track>

    constructor() {
        this.artistArray = new Array<Artist>()
        this.albumArray = new Array<Album>()
        this.trackArray = new Array<Track>()

        this.artistMap = new Map<string, Artist>()
        this.albumMap = new Map<string, Album>()
        this.trackMap = new Map<string, Track>()
    }

    addScrobbles(scrobbles: Array<CsvScrobble>): void {
        scrobbles.forEach((scrobble) => this.addScrobble(scrobble))

        // sort artists, albums, and tracks by scrobbles in descending order
        this.artistArray.sort((a, b) => b.scrobbles - a.scrobbles)
        this.albumArray.sort((a, b) => b.scrobbles - a.scrobbles)
        this.trackArray.sort((a, b) => b.scrobbles - a.scrobbles)
        this.artistArray.forEach((artist) => {
            artist.albums.sort((a, b) => b.scrobbles - a.scrobbles)
            artist.tracks.sort((a, b) => b.scrobbles - a.scrobbles)
        })
        this.albumArray.forEach((album) => {
            album.tracks.sort((a, b) => b.scrobbles - a.scrobbles)
        })

        // sort timestamps in ascending order
        this.trackArray.forEach((track) => {
            track.timestamps.sort((a, b) => a.toMillis() - b.toMillis())
        })
    }

    private addScrobble(scrobble: CsvScrobble): void {
        const artistKey = scrobble.artist_name
        const albumKey = `${scrobble.artist_name}:${scrobble.album_name}`
        const trackKey = `${scrobble.artist_name}:${scrobble.album_name}:${scrobble.track_name}`

        let artist: Artist
        if (this.artistMap.has(artistKey)) {
            artist = this.artistMap.get(artistKey) as Artist
        } else {
            artist = new Artist(scrobble.artist_name)

            this.artistMap.set(artistKey, artist)
            this.artistArray.push(artist)
        }

        let album: Album
        if (this.albumMap.has(albumKey)) {
            album = this.albumMap.get(albumKey) as Album
        } else {
            album = new Album(scrobble.album_name, artist, scrobble.album_art_url)

            this.albumMap.set(albumKey, album)
            this.albumArray.push(album)
            artist.albums.push(album)
        }

        let track: Track
        if (this.trackMap.has(trackKey)) {
            track = this.trackMap.get(trackKey) as Track
        } else {
            track = new Track(scrobble.track_name, album, artist)

            this.trackMap.set(trackKey, track)
            this.trackArray.push(track)
            artist.tracks.push(track)
            album.tracks.push(track)
        }

        artist.scrobbles += 1
        album.scrobbles += 1
        track.scrobbles += 1

        const timestamp = DateTime.fromSeconds(Number.parseInt(scrobble.unix_timestamp))
        track.timestamps.push(timestamp)
    }
}

export class Artist {
    artistName: string
    albums: Array<Album>
    tracks: Array<Track>
    scrobbles: number = 0

    constructor(artistName: string) {
        this.artistName = artistName
        this.albums = new Array<Album>()
        this.tracks = new Array<Track>()
        this.scrobbles = 0
    }
}

export class Album {
    albumName: string
    artistName: string
    tracks: Array<Track>
    albumArtUrl: string
    scrobbles: number = 0

    constructor(albumName: string, artist: Artist, albumArtUrl: string) {
        this.albumName = albumName
        this.artistName = artist.artistName
        this.tracks = new Array<Track>()
        this.albumArtUrl = albumArtUrl
        this.scrobbles = 0
    }

    getAllTimestamps(): Array<DateTime> {
        // combine timestamp arrays from all tracks
        return this.tracks
            .map((track) => track.timestamps)
            .reduce((prev, current) => prev.concat(current))
    }

    getAllTimestampsSorted(): Array<DateTime> {
        return this.getAllTimestamps()
            .sort((a, b) => a.toMillis() - b.toMillis())
    }

    getScrobblesPerMonthChartData(): Array<ScatterDataPoint> {
        const timestamps = this.getAllTimestampsSorted()
        const timestampsByMonth = groupBy(timestamps, (timestamp) => {
            return `${timestamp.year}:${timestamp.month}`
        })

        return Object.values(timestampsByMonth).map((timestamps) => {
            const dt = timestamps[0].set({day: 1, hour: 0, minute: 0, second: 0, millisecond: 0})
            return {
                x: dt.toMillis(),
                y: timestamps.length
            }
        })
    }
}

export class Track {
    trackName: string
    albumName: string
    artistName: string
    albumArtUrl: string
    timestamps: Array<DateTime>
    scrobbles: number = 0

    constructor(trackName: string, album: Album, artist: Artist) {
        this.trackName = trackName
        this.albumName = album.albumName
        this.artistName = artist.artistName
        this.albumArtUrl = album.albumArtUrl
        this.timestamps = new Array<DateTime>()
    }
}