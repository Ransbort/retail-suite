import {
  IconDeviceDesktopAnalytics,
  IconCreditCard,
  IconScan,
  IconBarcode,
} from '@tabler/icons-vue'

import { createRouter, createWebHistory } from "vue-router";
import { session, checkSession } from '@/services/auth'
import POS from "@/pages/POS.vue";
import Pay from "@/pages/Pay.vue";
import NonPage from "@/pages/NonPage.vue";
import MobileScan from "@/pages/MobileScan.vue";
import Invoice from "@/components/modals/invoiceTemplate.vue";
const routes = [
  {
    path: "/pos",
    name: "POS",
    component: POS,
    meta: {
      title: "POS",
      requiresAuth: false,
      layout: 'none',
      icon: IconDeviceDesktopAnalytics,
      keywords: ['pos', 'cashier', 'sale', 'point of sale', 'checkout'],
      section: "POS"
    }
  },
  {
    path: "/payment",
    name: "Payment",
    component: Pay,
    meta: {
      title: "Payment",
       layout: 'none',
      requiresAuth: true,
      icon: IconCreditCard,
      keywords: ['payment', 'pay', 'cash', 'reconcile', 'settle'],
      section: 'Payment'
    }
  },
  {
    path: "/mobile-scan",
    name: "MobileScan",
    component: MobileScan,
    meta: {
      title: "Mobile Scan",
      requiresAuth: false,
      layout: 'none',
      icon: IconScan,
      keywords: ['scan', 'barcode', 'camera', 'mobile', 'qr'],
      section: "Inventory Dashboard"
    }
  },
  {
    path: '/invoices/:name',
    name: 'Invoice',
    component: Invoice,
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: NonPage,
    meta: { requiresAuth: false }
  }

]

const router = createRouter({
  history: createWebHistory(),
  routes,
});

let sessionChecked = false;
router.beforeEach(async (to, from, next) => {
  if (!sessionChecked) {
    await checkSession()
    sessionChecked = true
  }

  const isAuth = !!session.user

  if (to.path === '/') {
    if (isAuth) return next('/pos')
    window.location.href = import.meta.env.MODE === 'development'
      ? `${import.meta.env.VITE_FRAPPE_URL}/login?redirect-to=${encodeURIComponent(window.location.href)}`
      : `/login?redirect-to=${encodeURIComponent(window.location.href)}`
    return next(false)
  }

  if (to.meta.requiresAuth && !isAuth) {
    window.location.href = import.meta.env.MODE === 'development'
      ? `${import.meta.env.VITE_FRAPPE_URL}/login?redirect-to=${encodeURIComponent(window.location.href)}`
      : `/login?redirect-to=${encodeURIComponent(window.location.href)}`
    return next(false)
  }

  if (to.meta.roles?.length > 0) {
    const hasAccess = to.meta.roles.some(role => (session.roles || []).includes(role))
    if (!hasAccess) return next({ name: 'Forbidden' })
  }

  next()
})
export default router;
