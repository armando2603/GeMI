
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/Index.vue') }
    ]
  },
  {
    path: '/survey',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/survey.vue') }
    ]
  },
  {
    path: '/about',
    component: () => import('pages/about.vue')
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
