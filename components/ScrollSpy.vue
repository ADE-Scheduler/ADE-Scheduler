<template>
  <div>
    <div class="row">
      <!-- Menu bar -->
      <nav class="col-md-3 col-lg-2 d-md-block bg-light navigator collapse" id="navigator">
        <nav class="nav nav-pills navigator-sticky d-flex flex-column p-3">
          <div v-for="item in content">
            <a class="nav-link main-link mb-0 active"
               v-bind:href="'#' + item.id"
               v-on:click.prevent="scroll(item.id, true)"
            >
              {{ item.title }}
            </a>
            <nav class="nav sub-nav flex-column">
              <a class="nav-link ms-4"
                 v-for="subitem in item.subtitles"
                 v-bind:href="'#' + subitem.id"
                 v-on:click="scroll(subitem.id, false)"
              >
                {{ subitem.title }}
              </a>
            </nav>
          </div>
        </nav>
      </nav>

      <!-- Content -->
      <div class="col-md-9 ms-sm-auto col-lg-10 p-3">
        <div class="container-lg">
          <div v-for="item in content">
            <h3 class="my-5" v-bind:id="item.id">
              <i v-bind:class="item.icon"></i>
              {{ item.title }}
            </h3>
            <p v-html="item.content"></p>
            <div v-for="subitem in item.subtitles">
              <h4 v-bind:id="subitem.id">
                <i v-bind:class="subitem.icon"></i>
                {{ subitem.title }}
              </h4>
              <hr class="mb-3">
              <p v-html="subitem.content"></p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toggle button  -->
    <button class="btn btn-dark btn-nav">
      <svg width="25px" height="25px" viewBox="0 0 16 16" class="bi bi-chevron-bar-contract" fill="currentColor" xmlns="http://www.w3.org/2000/svg"
           v-on:click="toggleNav(false)"
           v-if="navBtn"
      >
          <path fill-rule="evenodd" d="M7.646 4.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1-.708.708L8 5.707l-5.646 5.647a.5.5 0 0 1-.708-.708l6-6z"/>
      </svg>
      <svg width="25px" height="25px" viewBox="0 0 16 16" class="bi bi-chevron-bar-expand" fill="currentColor" xmlns="http://www.w3.org/2000/svg"
           v-on:click="toggleNav(true)"
           v-else
      >
        <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>
      </svg>
    </button>
  </div>
</template>


<script>
  import { Collapse, ScrollSpy } from 'bootstrap';
  const axios = require('axios');

  export default {
    props: ['path'],
    data() {
      return {
        nav: {},
        navBtn: false,
        content: {},
      }
    },
    methods: {
      scroll(id, flag) {
        document.getElementById(id).scrollIntoView();
        if (window.innerWidth < 767.98 && !flag) {
          this.toggleNav(false);
        }
      },
      toggleNav(show) {
        this.navBtn = show;
        if (show)   { this.nav.show(); }
        else        { this.nav.hide(); }
      },
    },
    mounted() {
      axios({
        method: 'GET',
        url: `/static/text/${this.path}/${this.path}-${document.getElementById('current-locale').textContent.trim().toLowerCase()}.json`
      })
        .then(resp => {
          this.content = resp.data;
          this.$nextTick(() => {
            new ScrollSpy(document.body, {
              target: '#navigator',
              offset: 70,
            });
            this.nav = new Collapse(document.getElementById('navigator'), {
              toggle: false,
            });
          });
        })
        .catch(() => {})
        .then(() => {});  // TODO
    }
  }
</script>


<style lang="scss" scoped>
  @import '../static/css/bootstrap.scss';
  @import 'bootstrap-icons/font/bootstrap-icons.css';

  .navigator {
      position: fixed;
      top: 0;
      bottom: 0;
      left: 0;
      z-index: 3;
      padding: 56px 0 0;
      box-shadow: inset -1px 0 0 rgba(0, 0, 0, .1);
  }

  .btn-nav {
      position: fixed;
      z-index: 4;
      bottom: 40px;
      right: 20px;
      width: 60px;
      height: 60px;
      border-radius: 30px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
  }
  @media (min-width: 767.98px) {
      .btn-nav {
          display: none;
      }
  }

  .main-link {
      color: var(--bs-dark);
  }
  .main-link.active {
      color: var(--bs-light) !important;
      background-color: var(--bs-dark) !important;
  }
  .main-link + .nav {
      display: none;
  }
  .main-link.active + .nav {
      display: block;
  }

  .sub-nav > .nav-link {
      color: var(--bs-gray);
  }
  .sub-nav > .nav-link:hover {
      color: var(--bs-dark);
  }
  .sub-nav > .nav-link.active {
      color: var(--bs-success);
      background-color: transparent;
  }
</style>
