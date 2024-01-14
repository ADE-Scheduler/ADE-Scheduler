import { ref } from "vue";
import { defineStore } from "pinia";

interface Code {
  id: number;
  code: string;
}

interface Schedule {
  id: number;
  name: string;
}

export const useScheduleStore = defineStore("schedule", () => {
  // Current code list
  const codes = ref<Code[]>([
    { id: 1, code: "LMECA1901" },
    { id: 2, code: "LMECA2660" },
    { id: 3, code: "LEPL1103" },
  ]);

  function addCode(code: string) {
    const id = Date.now();
    codes.value.push({ id, code });
  }

  function hasCode(code: string) {
    return codes.value.some((e) => e.code === code);
  }

  function deleteCode(code: string) {
    codes.value = codes.value.filter((e) => e.code !== code);
  }

  // Schedule list
  const currentSchedule = ref<Schedule>({ id: 1, name: "Schedule 1" });
  const schedules = ref<Schedule[]>([
    currentSchedule.value,
    { id: 2, name: "Schedule 2" },
    { id: 3, name: "Schedule 3" },
    { id: 4, name: "Schedule 4 - a very long schedule !" },
  ]);

  function newSchedule() {
    const id = Date.now();
    const schedule = { id, name: "New Schedule" };
    schedules.value.push(schedule);
    currentSchedule.value = schedule;
  }

  function deleteSchedule(id: number) {
    schedules.value = schedules.value.filter((schedule) => schedule.id !== id);
    // If the current schedule is deleted, set the first schedule as current
    if (currentSchedule.value.id === id) {
      // If the schedule list is empty, create a new schedule
      if (schedules.value.length === 0) {
        newSchedule();
      }
      currentSchedule.value = schedules.value[0];
    }
  }

  function getScheduleName(id: number) {
    const schedule = schedules.value.find((schedule) => schedule.id === id);
    if (schedule === undefined) {
      throw new Error(`Schedule ${id} not found`);
    }
    return schedule.name;
  }

  function setCurrentSchedule(id: number) {
    const schedule = schedules.value.find((schedule) => schedule.id === id);
    if (schedule === undefined) {
      throw new Error(`Schedule ${id} not found`);
    }
    currentSchedule.value = schedule;
  }

  return {
    codes,
    addCode,
    hasCode,
    deleteCode,
    schedules,
    currentSchedule,
    setCurrentSchedule,
    newSchedule,
    deleteSchedule,
    getScheduleName,
  };
});
