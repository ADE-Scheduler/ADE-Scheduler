/* global Flask */

import Vue from 'vue';
import Spinner from '../../components/Spinner.vue';
import { Carousel } from 'bootstrap';   // eslint-disable-line no-unused-vars

import './base.js';
import '../css/admin.css';

const Plotly = require('plotly.js-dist');
const axios = require('axios');


document.addEventListener('DOMContentLoaded', function() {
  new Vue({
    el: '#app',
    delimiters: ['[[',']]'],
    components: {'spinner': Spinner},
    data: function() {
      return {
        error: false,
        computing: false,
        plots: [],
      };
    },
    created:  function () {
      this.fetchData();
    },
    methods: {
      fetchData: function() {
        this.computing = true;
        axios({
          method: 'GET',
          url: Flask.url_for('admin.get_data'),
        })
          .then(resp => {
            this.plots = resp.data;
            this.$nextTick(() => {
              this.plots.forEach(plot => {
                let obj = JSON.parse(plot.data);
                obj.layout.width = document.getElementById('carouselPlots').offsetWidth-320;
                obj.layout.height = obj.layout.width * 0.7;
                Plotly.newPlot(plot.id, obj);
              });
            });
          })
          .catch(() => {
            this.error = true;
          })
          .then(() => {
            this.computing = false;
          });
      },
    },
  });
});
