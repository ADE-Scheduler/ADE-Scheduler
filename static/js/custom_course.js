import Vue from "vue";
import store from "./store.js";
import "./base.js";
import "../css/custom_course.css";
import AlertToast from "../../components/AlertToast.vue";
const axios = require("axios");

document.addEventListener("DOMContentLoaded", function() {
  new Vue({
    el: "#app",
    delimiters: ["[[", "]]"],
    components: { alerttoast: AlertToast },
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
          url: Flask.url_for("custom_course.index"),
          data: evt,
          header: { "Content-Type": "application/json" }
        })
          .then(resp => {
            // window.location.href = Flask.url_for("calendar.index"); // redirecting
            store.success("Your course has been created.");
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
