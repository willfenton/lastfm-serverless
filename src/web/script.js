const urlParams = new URLSearchParams(window.location.search)
let lastfmUsername = urlParams.get("lastfm_username")
if (lastfmUsername == null) {
    lastfmUsername = "willfenton14"
}

const DateTime = luxon.DateTime;

// VueJS
const vm = new Vue({
    el: "#vue-app",
    data: function () {
        return {
            dataUrl: 'https://lastfm-serverless-athena-output.s3.amazonaws.com/willfenton14/get_all/b1535d1d-84be-4a2f-bacd-c08a7a2287d7.csv',
            albums: [],
            modalAlbum: {}
        }
    },
    created() {
        Papa.parse(this.dataUrl, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                let scrobbles = results.data

                let albums = {}

                console.log(scrobbles)

                scrobbles.forEach(({artist_name, album_name, track_name, unix_timestamp, album_art_url}) => {
                    unix_timestamp = Number.parseInt(unix_timestamp)

                    const key = `${artist_name}:${album_name}`
                    if (key in albums) {
                        const album = albums[key]
                        album.timestamps.push(unix_timestamp)
                        album.scrobbles += 1
                        if (track_name in album.tracks) {
                            const track = album.tracks[track_name]
                            track.scrobbles += 1
                            track.timestamps.push(unix_timestamp)
                        } else {
                            album.tracks[track_name] = {
                                trackName: track_name,
                                timestamps: [unix_timestamp],
                                scrobbles: 1
                            }
                        }
                    } else {
                        const album = {
                            albumName: album_name,
                            artistName: artist_name,
                            albumArtUrl: album_art_url,
                            timestamps: [unix_timestamp],
                            tracks: {},
                            scrobbles: 1
                        }
                        album.tracks[track_name] = {
                            trackName: track_name,
                            timestamps: [unix_timestamp],
                            scrobbles: 1
                        }
                        albums[key] = album
                    }
                })

                this.albums = Object.values(albums)

                this.albums.forEach((album) => {
                    album.timestamps.sort()
                    album.tracks = Object
                        .values(album.tracks)
                        .sort((a, b) => b.scrobbles - a.scrobbles)
                    album.tracks.forEach((track) => track.timestamps.sort())
                    album.topTrack = album.tracks[0].trackName
                    album.firstTimestamp = album.timestamps[0]
                    album.lastTimestamp = album.timestamps[album.timestamps.length - 1]
                })

                this.albums = this.albums
                    .filter((album) => album.scrobbles >= 50 && album.tracks.length > 1)
                    .sort((a, b) => b.scrobbles - a.scrobbles)

                console.log(this.albums)

                if (!window.mobilecheck()) {
                    $(function () {
                        $('[data-toggle="tooltip"]').tooltip({boundary: 'window'})
                    })
                }
            }
        })
    },
    methods: {
        setModalData: function (album) {
            this.modalAlbum = album

            chart.data.datasets = []

            const now = DateTime.now()
            let luxonDates = this.modalAlbum.timestamps.map((timestamp) => DateTime.fromSeconds(timestamp))
            let days = groupBy(luxonDates, (timestamp) => {
                if (timestamp.year === now.year && timestamp.month === now.month) {
                    return now.toMillis()
                } else {
                    return timestamp.set({
                        day: timestamp.daysInMonth,
                        hour: 23,
                        minute: 59,
                        second: 59,
                        millisecond: 0
                    }).toMillis()
                }
            })
            console.log(days)

            let total = 0
            const data = []

            data.push({
                x: DateTime.fromSeconds(this.modalAlbum.timestamps[0]),
                y: total
            })
            Object.entries(days).forEach(([timestamp, dates], index) => {
                    if (index > 1) {
                        const prev = data[data.length - 1].x
                        const monthEarlier = DateTime.fromMillis(Number.parseInt(timestamp)).minus({months: 1})
                        if (prev < monthEarlier) {
                            data.push({
                                x: monthEarlier,
                                y: total
                            })
                        }
                    }
                    total += dates.length
                    data.push({
                        x: DateTime.fromMillis(Number.parseInt(timestamp)),
                        y: total
                    })
                }
            )
            const last = data[data.length - 1].x
            if (!(last.year === now.year && last.month === now.month)) {
                data.push({
                    x: now,
                    y: total
                })
            }

            // const data = Object.entries(days).map(([timestamp, dates]) => {
            //     return {
            //         x: DateTime.fromMillis(Number.parseInt(timestamp)),
            //         y: dates.length
            //     }
            // })

            // this.modalAlbum.timestamps.forEach((timestamp, index) => {
            //     data.push({
            //         x: DateTime.fromSeconds(timestamp),
            //         y: index + 1
            //     })
            // })

            console.log(data)

            chart.data.datasets.push({
                label: "Scrobbles",
                data: data,
                backgroundColor: "#9c9c9c"
            })

            chart.update()
        },
        parseTimestamp: function (timestamp) {
            let date = new Date(timestamp * 1000)
            return date.toLocaleString()
        }
    }
})

const chart = new Chart(document.getElementById('canvas').getContext('2d'), {
    type: 'line',
    datasets: [],
    options: {
        plugins: {
            title: {
                text: 'Scrobbles over time',
                display: true
            }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'month',
                    // Luxon format string
                    tooltipFormat: 'LLLL y'
                },
                title: {
                    display: true,
                    text: 'Date'
                },
                ticks: {
                    align: 'start'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Scrobbles'
                }
            }
        },
    }
})

window.mobilecheck = function () {
    var check = false;
    (function (a) {
        if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    return check;
};
