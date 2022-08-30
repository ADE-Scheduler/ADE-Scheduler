<template>
  <div class="row">
    <!-- Menu bar -->
    <sidebar-menu ref="navigator">
      <div v-for="item in content" :key="item.id">
        <a
          class="nav-link main-link rounded mb-0 active"
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
    </sidebar-menu>

    <!-- Content -->
    <div class="col-md-9 ms-sm-auto col-lg-10 p-3">
      <div class="container-lg">
        <img v-if="logo" class="mx-auto d-block mt-5" :src="logo" width="10%" />
        <div v-for="item in content" :key="item.id">
          <div class="d-flex flex-row my-5">
            <h3
              v-show="item.icon"
              class="align-item-center me-2"
              :class="item.icon"
            />
            <h3 :id="item.id" v-html="item.title" />
          </div>
          <p v-html="item.content" />
          <div v-for="subitem in item.subtitles" :key="subitem.id">
            <div class="d-flex flex-row">
              <h4
                v-show="subitem.icon"
                class="align-item-center me-2"
                :class="subitem.icon"
              />
              <h4 :id="subitem.id" v-html="subitem.title" />
            </div>
            <hr class="mb-3" />
            <p v-html="subitem.content" />
            <div
              v-if="subitem.video"
              class="embed-responsive embed-responsive-16by9 my-3 d-flex justify-content-center"
            >
              <iframe
                width="560"
                height="315"
                frameborder="0"
                allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
                :src="subitem.video"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ScrollSpy } from 'bootstrap';
import SidebarMenu from './SidebarMenu.vue';

export default {
  components: { 'sidebar-menu': SidebarMenu },
  props: ['content', 'logo'],
  data() {
    return {
      scrollspy: {},
    };
  },
  watch: {
    content() {
      this.$nextTick(() => {
        [].slice
          .call(document.querySelectorAll('[data-bs-spy="scroll"]'))
          .forEach(function (dataSpyEl) {
            this.scrollspy.getInstance(dataSpyEl).refresh();
          });
      });
    },
  },
  mounted() {
    this.scrollspy = new ScrollSpy(document.body, {
      target: this.$refs.navigator.$el,
      offset: 70,
    });
  },
  methods: {
    scroll(id, flag) {
      document.getElementById(id).scrollIntoView();
      if (window.innerWidth < 767.98 && !flag) {
        this.$refs.navigator.close();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
@import '../static/css/bootstrap.scss';
@import 'bootstrap-icons/font/bootstrap-icons.css';

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
