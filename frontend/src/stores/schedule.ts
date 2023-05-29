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
    { id: 1, code: "code 1" },
    { id: 2, code: "code 2" },
    { id: 3, code: "code 3" },
    { id: 4, code: "code 4 - a very long code !" },
  ]);

  function addCode(code: string) {
    const id = Date.now();
    codes.value.push({ id, code });
  }

  function deleteCode(id: number) {
    codes.value = codes.value.filter((code) => code.id !== id);
  }

  // Schedule list
  const currentSchedule = ref<Schedule>({ id: 1, name: "Schedule 1" });
  const schedules = ref<Schedule[]>([
    { id: 1, name: "Schedule 1" },
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
    deleteCode,
    schedules,
    currentSchedule,
    setCurrentSchedule,
    newSchedule,
    deleteSchedule,
    getScheduleName,
  };
});
