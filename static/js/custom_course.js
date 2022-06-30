import Vue from "vue";
import store from "./store.js";
import "./base.js";
import "../css/custom_course.css";
const axios = require("axios");

document.addEventListener("DOMContentLoaded", function() {
  new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    data: function() {
      return {
        navBtn: false,
        content: [],
        courseForm: {
          name: "",
          url: ""
        }
      };
    },
    methods: {
      addCustomCourse: function(e) {
        let evt = {
          name: this.courseForm.name,
          url: this.courseForm.url
        };
        this.computing = true;
        axios({
          method: "POST",
          url: Flask.url_for("calendar.add_custom_course"),
          data: evt,
          header: { "Content-Type": "application/json" }
        })
          .then(resp => {
            console.log(resp);
          })
          .catch(err => {
            store.error(err.response.data);
          })
          .then(() => {
            this.computing = false;
          });
      }
    },
    mounted() {
      axios({
        method: "GET",
        url: `/static/text/contribute/contribute-${document
          .getElementById("current-locale")
          .textContent.trim()
          .toLowerCase()}.json`
      })
        .then(resp => {
          this.content = resp.data;
        })
        .catch(err => {
          store.error(err.response.data);
        })
        .then(() => {}); // TODO
    }
  });
});
