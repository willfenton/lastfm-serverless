import Vue from 'vue'
import * as Papa from 'papaparse'
import {DateTime} from 'luxon'
// @ts-ignore
import * as bootstrap from 'bootstrap'
import {Chart, ChartDataset, registerables} from 'chart.js';
import 'chartjs-adapter-luxon';
import {Album, CsvScrobble, MusicData} from './music'

import 'bootstrap/dist/css/bootstrap.css'
import './style.css'

Chart.register(...registerables);


// so obscenely large that Vue struggles hard with it, so keep it outside of the Vue app
let musicData = new MusicData()

const vm = new Vue({
    el: '#vue-app',
    data: {
        dataUrl: 'https://lastfm-serverless-athena-output.s3.amazonaws.com/willfenton14/get_all/b1535d1d-84be-4a2f-bacd-c08a7a2287d7.csv',
        modalAlbum: {},
        modalTopTrack: {},
        modalAlbumFirstTimestamp: {},
        modalAlbumLastTimestamp: {}
    },
    created: function () {
        Papa.parse(this.dataUrl, {
            download: true,
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                const scrobbles = results.data as Array<CsvScrobble>
                console.log('Parsed CSV', scrobbles)

                musicData.addScrobbles(scrobbles)
                console.log('Processed scrobbles', musicData)

                // Music data is outside of Vue's data so it can't auto-update
                this.$forceUpdate()

                // for whatever reason this needs to load a little later
                setTimeout(loadTooltips, 100)
            }
        })
    },
    methods: {
        getTopAlbums(numAlbums: number): Array<Album> {
            return musicData.albumArray
                .filter((album) => album.tracks.length >= 2)
                .slice(0, numAlbums)
        },
        setModalData(album: Album): void {
            this.modalAlbum = album
            this.modalTopTrack = album.tracks[0]

            const timestamps = album.getAllTimestampsSorted()
                .map((timestamp) => timestamp.toLocaleString(DateTime.DATETIME_FULL))

            this.modalAlbumFirstTimestamp = timestamps[0]
            this.modalAlbumLastTimestamp = timestamps[timestamps.length - 1]

            modalChart.data.datasets = []
            const dataset: ChartDataset = {
                label: 'Scrobbles',
                data: album.getScrobblesPerMonthChartData(),
                backgroundColor: '#9c9c9c',
                barPercentage: 1.0,
                categoryPercentage: 0.9
            }
            // @ts-ignore
            modalChart.data.datasets.push(dataset)
            modalChart.update()
        }
    }
})

const canvas = document.getElementById('canvas') as HTMLCanvasElement
const modalChart = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: {
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                text: 'Scrobbles per month',
                display: true
            }
        },
        scales: {
            x: {
                type: 'time',
                max: DateTime.now().toMillis(),
                time: {
                    unit: 'month',
                    // Luxon format string
                    tooltipFormat: 'LLLL y'
                },
                title: {
                    display: true,
                    text: 'Month'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Scrobbles'
                }
            }
        }
    },
    plugins: []
})

const loadTooltips = () => {
    // TODO: what even is this...
    []
        .slice
        .call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        .map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl)
        })
}