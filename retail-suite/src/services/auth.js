// auth.js
import { reactive, computed } from 'vue'
import { createResource, frappeRequest,call } from 'frappe-ui'
import router from '../router'

// ==========================================
// Session User from Cookie
// ==========================================
function sessionUser() {
  const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
  const user = cookies.get("user_id")
  return user === "Guest" ? null : user
}

// ==========================================
// Session State
// ==========================================
export const session = reactive({
  user: null,
  isAuthenticated: computed(() => !!session.user),
  full_name: null,
  email: null,

  login: createResource({
    url: 'login',
    makeParams({ username, password }) {
      return { usr: username, pwd: password }
    },
    async onSuccess(data) {
      session.user = sessionUser()
      session.full_name = data?.full_name || null
      session.email = data?.email || null
      session.login.reset()
      console.log('👤user session:', session)
      router.push({ name: 'POS' })
    },
    onError(err) {
      console.error("❌ Login error:", err)
    }
  }),

  logout: createResource({
    url: 'logout',
    onSuccess() {
      session.user = null
      session.full_name = null
      session.email = null
      router.push({ name: 'Login' })
    },
    onError() {
      session.user = null
      router.push({ name: 'Login' })
    }
  }),
})

// ==========================================
// Check Existing Session (API-based)
// ==========================================
// export async function checkSession() {
//   try {
//     const data = await frappeRequest({
//       url: '/api/method/frappe.auth.get_logged_user',
//     })
//     console.log("👤 Logged in user:", data)
//     const user = data
//     if (!user || user === 'Guest') {
//       session.user = null
//       return false
//     }

//     session.user = user
//     return true

//   } catch (err) {
//     // 403 or network error = not logged in
//     session.user = null
//     return false
//   }
// }
export async function checkSession() {
  const user = sessionUser()
  if (user) {
    session.user = user
    return true
  }
  session.user = null
  return false
}
// ==========================================
// API Methods
// ==========================================
export const api = {
  get: (url, { params } = {}) => frappeRequest({ url, params }),
  post: (url, data) => frappeRequest({ url, method: 'POST', body: data }),
  put: (url, data) => frappeRequest({ url, method: 'PUT', body: data }),
  delete: (url) => frappeRequest({ url, method: 'DELETE' }),
  patch: (url, data) => frappeRequest({ url, method: 'PATCH', body: data }),
}
