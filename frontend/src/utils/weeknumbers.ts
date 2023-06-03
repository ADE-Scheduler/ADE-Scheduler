import { h } from "vue";
import i18n from "@/i18n";

interface fcContentInjectionArg {
  num: number;
  text: string;
  date: Date;
}

function getWeekNumber(date: Date) {
  const d = new Date(
    Date.UTC(date.getFullYear(), date.getMonth(), date.getDate())
  );
  const dayNo = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNo);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
}

function addDays(date: Date, days: number) {
  const d = new Date(date.valueOf());
  d.setDate(d.getDate() + days);
  return d;
}

// Manual week numbering
const uclWeeksNo = {
  "2019": [
    0, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3, -3,
  ],
  "2020": [
    -3, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3, -3,
  ],
  "2021": [
    0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
    12, 13, 14, -3, -3, 0,
  ],
  "2022": [
    0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -1, 10, 11, 12, 13, -3, -3, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3,
  ],
  "2023": [
    -3, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, -1, -1, 9, 10, 11, 12, 13, -3, -3,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3, -3,
  ],
  "2024": [
    -3, 0, 0, 0, -2, 1, 2, 3, 4, 5, 6, 7, 8, -1, -1, 9, 10, 11, 12, 13, -3, -3,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, -3, -3,
  ],
};

export function getWeekText(arg: fcContentInjectionArg) {
  // Get week number & year
  // From: https://stackoverflow.com/a/6117889
  // Since FC set first day to be Sunday in some places, we shift the current day by one to be at least Monday, otherwise we get previous week number.
  const week: number = getWeekNumber(addDays(arg.date, 1));
  const year: string = arg.date.getUTCFullYear().toString();
  const wtype =
    year in uclWeeksNo ? (uclWeeksNo as any)[year][week - 1] : undefined;

  // Get week text
  if (wtype > 0) return `S${wtype}`;
  else {
    switch (wtype) {
      case -1:
        return i18n.global.t("easter");
      case -2:
        return i18n.global.t("break");
      case -3:
        return i18n.global.t("blocus");
      default:
        return "-";
    }
  }
}
