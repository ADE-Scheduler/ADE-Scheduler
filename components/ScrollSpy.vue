<template>
  <div>
    <div class="row">
      <!-- Menu bar -->
      <nav class="col-md-3 col-lg-2 d-md-block bg-light navigator collapse" id="navigator">
        <nav class="nav nav-pills navigator-sticky d-flex flex-column p-3">
          <div v-for="item in content" v-bind:key="item.id">
            <a class="nav-link main-link mb-0 active"
               v-bind:href="'#' + item.id"
               v-on:click.prevent="scroll(item.id, true)"
               v-html="item.title"
            >
            </a>
            <nav class="nav sub-nav flex-column">
              <a class="nav-link ms-4"
                 v-for="subitem in item.subtitles"
                 v-bind:key="subitem.id"
                 v-bind:href="'#' + subitem.id"
                 v-on:click="scroll(subitem.id, false)"
                 v-html="subitem.title"
              >
              </a>
            </nav>
          </div>
        </nav>
      </nav>

      <!-- Content -->
      <div class="col-md-9 ms-sm-auto col-lg-10 p-3">
        <div class="container-lg">
          <img class="mx-auto d-block mt-5" v-bind:src="logo" v-if="logo" width="10%"/>
          <div v-for="item in content" v-bind:key="item.id">
            <div class="d-flex flex-row my-5">
              <h3 class="align-item-center me-2" v-bind:class="item.icon" v-show="item.icon"></h3>
              <h3 v-bind:id="item.id" v-html="item.title"></h3>
            </div>
            <p v-html="item.content"></p>
            <div v-for="subitem in item.subtitles" v-bind:key="subitem.id">
              <div class="d-flex flex-row">
                <h4 class="align-item-center me-2" v-bind:class="subitem.icon" v-show="subitem.icon"></h4>
                <h4 v-bind:id="subitem.id" v-html="subitem.title"></h4>
              </div>
              <hr class="mb-3">
              <p v-html="subitem.content"></p>
              <div class="embed-responsive embed-responsive-16by9 my-3 d-flex justify-content-center"
                   v-if="subitem.video"
              >
                <iframe width="560" height="315" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen
                        v-bind:src="subitem.video"
                ></iframe>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toggle button  -->
    <button class="btn btn-dark btn-nav" v-on:click="toggleNav">
      <i style="font-size: 32px" class="bi bi-chevron-up" v-if="navBtn"/>
      <i style="font-size: 32px" class="bi bi-chevron-down" v-else/>
    </button>
  </div>
</template>


<script>
  import { Collapse, ScrollSpy } from 'bootstrap';

  export default {
  props: ['content', 'logo'],
    data() {
      return {
        nav: {},
        navBtn: false,
      }
    },
    methods: {
      scroll(id, flag) {
        document.getElementById(id).scrollIntoView();
        if (window.innerWidth < 767.98 && !flag) {
          this.toggleNav();
        }
      },
      toggleNav() {
        this.navBtn = !this.navBtn;
        if (this.navBtn)  { this.nav.show(); }
        else              { this.nav.hide(); }
      },
    },
    mounted() {
      this.nav = new Collapse(document.getElementById('navigator'), {
        toggle: false,
      });
      new ScrollSpy(document.body, {
        target: '#navigator',
        offset: 70,
      });
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
