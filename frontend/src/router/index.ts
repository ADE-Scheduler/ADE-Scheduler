import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/calendar",
  },
  {
    path: "/calendar",
    component: () => import("@/views/CalendarView.vue"),
    children: [
      {
        path: "",
        name: "Calendar",
        component: () => import("@/components/MainCalendar.vue"),
      },
      {
        path: "/codes/:code",
        name: "Code",
        component: () => import("@/views/CodeView.vue"),
      },
      {
        path: "/schedules/:schedule",
        name: "Schedule",
        component: () => import("@/views/ScheduleView.vue"),
      },
    ],
  },
  {
    path: "/classroom",
    name: "Classroom",
    component: () => import("@/views/ClassroomView.vue"),
  },
  {
    // We use history mode instead of hash mode.
    // The production servers must be configured as a "catch-all", as described here:
    // https://router.vuejs.org/guide/essentials/history-mode.html#example-server-configurations
    path: "/:pathMatch(.*)",
    component: () => import("@/views/errors/NotFound.vue"),
    name: "NotFound",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
