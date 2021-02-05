<template>
  <div>
    <div class="row">
      <!-- Menu bar -->
      <nav
        id="navigator"
        class="col-md-3 col-lg-2 d-md-block bg-light navigator collapse"
      >
        <nav class="nav nav-pills navigator-sticky d-flex flex-column p-3">
          <div
            v-for="item in content"
            :key="item.id"
          >
            <a
              class="nav-link main-link mb-0 active"
              :href="'#' + item.id"
              @click.prevent="scroll(item.id, true)"
              v-html="item.title"
            />
            <nav class="nav sub-nav flex-column">
              <a
                v-for="subitem in item.subtitles"
                :key="subitem.id"
                class="nav-link ms-4"
                :href="'#' + subitem.id"
                @click="scroll(subitem.id, false)"
                v-html="subitem.title"
              />
            </nav>
          </div>
        </nav>
      </nav>

      <!-- Content -->
      <div class="col-md-9 ms-sm-auto col-lg-10 p-3">
        <div class="container-lg">
          <div
            v-for="item in content"
            :key="item.id"
          >
            <div class="d-flex flex-row my-5">
              <h3
                v-show="item.icon"
                class="align-item-center me-2"
                :class="item.icon"
              />
              <h3
                :id="item.id"
                v-html="item.title"
              />
            </div>
            <p v-html="item.content" />
            <div
              v-for="subitem in item.subtitles"
              :key="subitem.id"
            >
              <div class="d-flex flex-row">
                <h4
                  v-show="subitem.icon"
                  class="align-item-center me-2"
                  :class="subitem.icon"
                />
                <h4
                  :id="subitem.id"
                  v-html="subitem.title"
                />
              </div>
              <hr class="mb-3">
              <p v-html="subitem.content" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toggle button  -->
    <button
      class="btn btn-dark btn-nav"
      @click="toggleNav"
    >
      <i
        v-if="navBtn"
        style="font-size: 32px"
        class="bi bi-chevron-up"
      />
      <i
        v-else
        style="font-size: 32px"
        class="bi bi-chevron-down"
      />
    </button>
  </div>
</template>


<script>
import { Collapse, ScrollSpy } from 'bootstrap';

export default {
  props: ['content'],
  data() {
    return {
      nav: {},
      navBtn: false,
    };
  },
  mounted() {
    console.log(document.getElementById('navigator').classList);
    this.nav = new Collapse(document.getElementById('navigator'), {
      toggle: false,
    });
    new ScrollSpy(document.body, {
      target: '#navigator',
      offset: 70,
    });
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
  }
};
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
