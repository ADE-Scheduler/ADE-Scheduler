import { createI18n } from "vue-i18n";

// English locales import
import api_en from "@/i18n/en/api.json";
import calendar_en from "@/i18n/en/calendar.json";

// French locales import
import api_fr from "@/i18n/fr/api.json";
import calendar_fr from "@/i18n/fr/calendar.json";

export default createI18n({
  globalInjection: true,
  legacy: false,
  locale: "fr",
  messages: {
    en: {
      api: api_en,
      calendar: calendar_en,
    },
    fr: {
      api: api_fr,
      calendar: calendar_fr,
    },
  },
});
