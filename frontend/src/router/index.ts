import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    redirect: '/calendar',
  },
  {
    path: '/calendar',
    name: 'Calendar',
    component: () => import('@/views/CalendarView.vue'),
  },
  {
    // We use history mode instead of hash mode.
    // The production servers must be configured as a "catch-all", as described here:
    // https://router.vuejs.org/guide/essentials/history-mode.html#example-server-configurations
    path: '/:pathMatch(.*)',
    component: () => import('@/views/errors/NotFound.vue'),
    name: 'NotFound',
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
