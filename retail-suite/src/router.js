import {
  IconDeviceDesktopAnalytics,
  IconCreditCard,
  IconScan,
  IconBarcode,
} from '@tabler/icons-vue'

import { createRouter, createWebHistory } from "vue-router";
import { session, checkSession } from '@/services/auth'
import { config } from '@/config/frappe'
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
  if (to.path === "/") {
    if (isAuth) {
      return next("/pos");
    }

    const loginUrl = `/login?redirect-to=${encodeURIComponent(
      window.location.href
    )}`;

    window.location.href = loginUrl;

    return next(false);
  }

  if (to.path === '/login' && isAuth) {
    return next('/pos')
  }

  if (to.meta.requiresAuth && !isAuth) {
    window.location.href = `/login?redirect-to=${encodeURIComponent(window.location.href)}`;
    return next(false);
  }

  if (to.meta.roles && to.meta.roles.length > 0) {
    const userRoles = session.roles || []
    const hasAccess = to.meta.roles.some(role => userRoles.includes(role))
    if (!hasAccess) return next({ name: 'Forbidden' })
  }

  if (session.user === null && !to.meta.requiresAuth && !isAuth) {
    return window.location.replace(
      `/login?redirect-to=${encodeURIComponent(window.location.href)}`
    );
  }
  next()
})
export default router;
