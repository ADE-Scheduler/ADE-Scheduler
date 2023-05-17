import { createApp } from "vue";
import { createPinia } from "pinia";
import { createI18n } from "vue-i18n";

import App from "@/App.vue";
import router from "@/router";

import "bootstrap";
import "@/assets/bootstrap.scss";

const i18n = createI18n({
  globalInjection: false,
  legacy: false,
  locale: "fr",
});

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(i18n);

app.mount("#app");
