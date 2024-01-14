<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { useAlertStore } from "@/stores";
import { useScheduleStore } from "@/stores";
import { useRoute, useRouter } from "vue-router";

// i18n stuff
const { t } = useI18n({
  inheritLocale: true,
  useScope: "local",
});

// stores
const alertStore = useAlertStore();
const scheduleStore = useScheduleStore();

// router
const route = useRoute();
const router = useRouter();

// sanitize the code
if (Array.isArray(route.params.code)) {
  alertStore.append("danger", t("error-code-array"));
  throw new Error("Route code is an array of strings");
}
const code = ref<string>(route.params.code);

// Add/remove code
function deleteCode(code: string) {
  scheduleStore.deleteCode(code);
  router.push({ name: "Calendar" });
}

function addCode(code: string) {
  scheduleStore.addCode(code);
  router.push({ name: "Calendar" });
}
</script>

<template>
  <div class="container-fluid py-3">
    <RouterLink
      :to="{ name: 'Calendar' }"
      class="link-secondary link-underline-opacity-0"
    >
      <i class="bi bi-arrow-left me-2" />
      <span>{{ t("nav-back") }}</span>
    </RouterLink>
    <div class="container mt-3">
      <div class="d-flex">
        <h1 class="display-6">{{ code }}</h1>
        <button
          role="button"
          class="btn btn-link link-danger ms-auto"
          @click.stop="deleteCode(code)"
          v-if="scheduleStore.hasCode(code)"
        >
          <i class="bi bi-trash3"></i>
        </button>
        <button
          role="button"
          class="btn btn-link link-success ms-auto"
          @click.stop="addCode(code)"
          v-else
        >
          <i class="bi bi-plus-lg"></i>
        </button>
      </div>
      <!-- TODO: fill the content with the code info & event selector -->
      <p class="bg-dark-subtle rounded p-3">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed consectetur
        ornare nisi sit amet condimentum. Suspendisse non mattis mi. Donec
        aliquam metus felis, rhoncus condimentum dolor mattis vel. Cras non sem
        interdum sapien pulvinar vulputate. Mauris sed massa libero. Vivamus
        risus leo, cursus non aliquet accumsan, tristique a lorem. Orci varius
        natoque penatibus et magnis dis parturient montes, nascetur ridiculus
        mus. Class aptent taciti sociosqu ad litora torquent per conubia nostra,
        per inceptos himenaeos. Nunc sit amet scelerisque lectus. Pellentesque
        ornare bibendum molestie. Maecenas non sem ac tellus hendrerit laoreet.
        Duis at lorem justo. Aenean nec massa id dolor ullamcorper pellentesque.
        Quisque ac nulla sem. Maecenas at diam placerat, accumsan elit
        hendrerit, feugiat tortor. Aenean ut leo in magna pharetra congue eget
        ac ex. Suspendisse vel mollis nunc. Morbi lobortis lacinia egestas.
        Phasellus mollis volutpat congue. Duis feugiat enim a lectus condimentum
        suscipit. Sed at tincidunt ante. Pellentesque non vestibulum lacus.
        Maecenas porttitor aliquet tortor, at iaculis justo convallis eget.
        Morbi non consectetur tortor. Etiam eleifend ex diam, sed mollis risus
        tincidunt ac. Nam ut orci molestie, porttitor risus ut, sagittis erat.
        Curabitur mattis sapien a rhoncus pulvinar. Duis ultrices dolor nec ante
        fringilla condimentum et ac odio. Maecenas posuere et dolor vitae
        maximus. Mauris non vulputate libero, vel feugiat mauris. In vitae
        ornare massa. Integer interdum ante at mauris mattis lacinia eget eget
        nunc. Aliquam fermentum volutpat nibh, nec finibus sapien tristique
        lacinia. Aliquam velit ante, dictum quis fringilla ac, dictum et augue.
        Fusce lobortis condimentum arcu, sed vulputate urna venenatis id. Nunc
        lobortis lectus sed varius condimentum. Vestibulum tristique varius
        urna, consequat mollis nisi scelerisque ac. Mauris faucibus nisl at
        lacus iaculis feugiat. Sed ac mi id arcu consectetur iaculis. Fusce orci
        tellus, aliquam venenatis orci a, mattis rhoncus tellus. Suspendisse
        sagittis, lacus a pretium rhoncus, sem turpis blandit sem, vulputate
        ultrices felis nisl ut libero. Quisque ultricies ultricies turpis, id
        gravida justo pulvinar quis. Aenean faucibus, metus non consequat
        eleifend, nibh enim blandit lectus, nec porta odio augue vitae massa.
        Mauris imperdiet nunc sit amet dui dictum tempor. Vestibulum ante ipsum
        primis in faucibus orci luctus et ultrices posuere cubilia curae;
        Vivamus malesuada luctus mauris, et auctor tortor cursus nec. In euismod
        semper quam, vitae gravida elit tempor in. Nunc suscipit vestibulum
        neque, sit amet condimentum dolor iaculis sodales. Sed maximus ipsum vel
        velit sodales, ultricies consectetur magna porttitor. Sed dictum elit in
        erat mattis, at posuere elit cursus. Morbi accumsan dui velit, sed
        elementum felis ultricies quis. Curabitur ut rutrum lectus, a varius
        ante. Praesent at semper ligula, nec vehicula orci. Aenean vehicula,
        augue at lobortis fringilla, lorem magna ultricies erat, suscipit ornare
        dui libero ut velit. Vestibulum auctor lacus at nunc auctor dapibus.
        Fusce tincidunt nibh lectus, vel scelerisque justo semper sed. Donec
        bibendum hendrerit auctor. In hac habitasse platea dictumst. Etiam in
        semper lectus. Ut sagittis convallis mi mollis semper. Orci varius
        natoque penatibus et magnis dis parturient montes, nascetur ridiculus
        mus. Donec dignissim lacinia augue gravida ultricies. Aenean leo est,
        pretium vel consequat ut, pharetra auctor nisi.
      </p>
      <div class="d-flex">
        <button
          role="button"
          class="btn btn-outline-secondary ms-auto"
          @click="deleteCode(code)"
          v-if="scheduleStore.hasCode(code)"
        >
          {{ t("delete-code") }}
        </button>
        <button
          role="button"
          class="btn btn-outline-secondary ms-auto"
          @click="addCode(code)"
          v-else
        >
          {{ t("add-code") }}
        </button>
      </div>
    </div>
  </div>
</template>

<i18n lang="yaml">
en:
  nav-back: "Back to calendar"
  add-code: "Add course"
  delete-code: "Delete course"
  error-code-array: "URL code argument is an array of strings"
fr:
  nav-back: "Retour au calendrier"
  add-code: "Ajouter cours"
  delete-code: "Supprimer cours"
  error-code-array: "L'argument code de l'URL est un tableau de strings"
</i18n>
