/* global Flask */

import Vue from 'vue';
import { Carousel } from 'bootstrap'; // eslint-disable-line no-unused-vars
import store from './store.js';
import Spinner from '../../components/Spinner.vue';

import './base.js';
import '../css/admin.css';

const Plotly = require('plotly.js-dist');
const axios = require('axios');

document.addEventListener('DOMContentLoaded', () => {
  new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    components: { spinner: Spinner },
    data() {
      return {
        computing: false,
        plots: [],
      };
    },
    created() {
      this.fetchData();
    },
    methods: {
      fetchData() {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('admin.get_data'),
        })
          .then((resp) => {
            this.plots = resp.data;
            this.$nextTick(() => {
              this.plots.forEach((plot) => {
                const obj = JSON.parse(plot.data);
                obj.layout.width =
                  document.getElementById('carouselPlots').offsetWidth - 320;
                obj.layout.height = obj.layout.width * 0.7;
                Plotly.newPlot(plot.id, obj);
              });
            });
          })
          .catch((err) => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      },
    },
  });
});
