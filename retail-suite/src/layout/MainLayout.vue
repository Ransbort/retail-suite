<!-- MainLayouts.vue -->
<template>
  <div :class="isDark ? 'theme-dark' : 'theme-light'" class="flex h-screen">
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top Navigation Bar -->
      <nav style="background: var(--nav-bg); border-bottom: 1px solid var(--divider);" class="shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div class="flex items-center justify-between px-4 sm:px-6 py-3">
          <!-- Left Section -->
          <div class="flex items-center gap-4">
            <!-- Mobile Menu Button -->
            <button
              @click="toggleSidebar"
              class="md:hidden text-gray-900 dark:text-gray-100 hover:text-gray-900 dark:hover:text-white focus:outline-none"
              title="Toggle Sidebar"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <!-- Breadcrumb Navigation -->
            <div class="hidden sm:flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
               <template v-if="currentPage.section && currentPage.section !== currentPage.title">
                 <span class="hover:text-gray-900 dark:hover:text-white cursor-pointer transition">{{ __(currentPage.section) }}</span>
                 <svg class="w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                 </svg>
               </template>
              <span class="text-gray-900 dark:text-gray-50">{{ __(currentPage.title) }}</span>
            </div>
          </div>

          <!-- Right Section -->
          <div class="flex items-center gap-3 sm:gap-4">
            <!-- Search Bar (Desktop) -->
            <div class="hidden lg:block relative w-64">
              <input
                v-model="searchQuery"
                @input="handleSearch"
                @keydown.enter="navigateToResult"
                @focus="showSearchResults = true"
                type="text"
                placeholder="Search pages..."
                class="
                  w-full px-4 py-2 pl-10
                  border border-gray-300
                  rounded-lg
                  focus:outline-none focus:ring-2 focus:ring-blue-500
                  focus:bg-gray-100
                  transition
                  text-gray-900
                "

              />
              <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>

              <!-- Search Results Dropdown -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="showSearchResults && searchQuery.length > 0"
                  class="absolute top-full left-0 right-0 mt-2 rounded-lg shadow-xl z-50 border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto"
                >
                  <div v-if="filteredPages.length === 0" class="p-4 text-center text-gray-500 dark:text-gray-400">
                    No results found
                  </div>
                  <div v-else>
                    <div
                      v-for="(page, index) in filteredPages"
                      :key="index"
                      @click="navigateToPage(page.path)"
                      :class="[
                        'p-4 border-b border-gray-100 dark:border-gray-900 cursor-pointer transition hover:bg-blue-50 dark:hover:bg-gray-700',
                        index === selectedResultIndex ? 'bg-blue-50' : ''
                      ]"
                    >
                      <div class="flex items-center gap-3 sm:gap-4">
                        <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
                          <component :is="page.icon" class="w-5 h-5" :style="{ color: primaryColor }" :stroke-width="2" />
                        </div>
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ page.name }}</p>
                          <p class="text-xs text-gray-500 dark:text-gray-400">{{ page.description }}</p>
                        </div>
                        <svg class="w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Notifications -->
            <div class="relative">
              <button
                @click="showNotifications = !showNotifications"
                class="relative p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                :title="__('Notifications')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span v-if="notificationCount > 0" class="absolute top-1 right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                  {{ notificationCount }}
                </span>
              </button>

              <!-- Notifications Dropdown -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="showNotifications"
                  class="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-900 rounded-lg shadow-xl z-50 border border-gray-200 dark:border-gray-700"
                >
                  <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <h3 class="text-sm font-semibold text-gray-900 dark:text-white">Notifications</h3>
                    <button
                      v-if="notificationCount > 0"
                      @click="markAllAsRead"
                      class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                    >
                      Mark all as read
                    </button>
                  </div>
                  <div class="max-h-96 overflow-y-auto">
                    <div v-if="notifications.length === 0" class="p-4 text-center text-gray-500 dark:text-gray-400">
                      No notifications
                    </div>
                    <div
                      v-for="notification in notifications"
                      :key="notification.id"
                      @click="markAsRead(notification.id)"
                      :class="[
                        'p-4 border-b border-gray-100 dark:border-gray-700 cursor-pointer transition',
                        notification.read ? 'bg-white dark:bg-gray-900 hover:bg-gray-50 dark:hover:bg-gray-700' : 'bg-blue-50  hover:bg-blue-100 dark:hover:bg-gray-600'
                      ]"
                    >
                      <div class="flex gap-3">
                        <div :class="getNotificationIconBg(notification.type)">
                          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                          </svg>
                        </div>
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ notification.title }}</p>
                          <p class="text-sm text-gray-500 dark:text-gray-400">{{ notification.message }}</p>
                          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ notification.time }}</p>
                        </div>
                        <div v-if="!notification.read" class="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-1"></div>
                      </div>
                    </div>
                  </div>
                  <div class="p-4 border-t border-gray-200 dark:border-gray-700 text-center">
                    <button
                       @click="$router.push('/notification-center')"
                      class="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                      {{ __('View All Notifications') }}
                    </button>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Messages -->
            <div class="relative">
              <button
                @click="showMessages = !showMessages"
                class="relative p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                :title="__('Messages')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span v-if="messageCount > 0" class="absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-blue-600 rounded-full">
                  {{ messageCount }}
                </span>
              </button>

              <!-- Messages Dropdown -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="showMessages"
                  class="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-900 rounded-lg shadow-xl z-50 border border-gray-200 dark:border-gray-700"
                >
                  <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 class="text-sm font-semibold text-gray-900 dark:text-white">Messages</h3>
                  </div>
                  <div class="max-h-96 overflow-y-auto">
                    <div v-if="messages.length === 0" class="p-4 text-center text-gray-500 dark:text-gray-400">
                      No messages
                    </div>
                    <div
                      v-for="message in messages"
                      :key="message.id"
                      class="p-4 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition"
                    >
                      <div class="flex gap-3">
                        <div class="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <span class="text-white font-semibold text-sm">{{ message.sender.charAt(0) }}</span>
                        </div>
                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium text-gray-900 dark:text-white">{{ message.sender }}</p>
                          <p class="text-sm text-gray-500 dark:text-gray-400 truncate">{{ message.subject }}</p>
                          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ message.time }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="p-4 border-t border-gray-200 dark:border-gray-700 text-center">
                    <button

                    class="text-sm text-blue-600 dark:text-blue-400
                           hover:text-blue-700 dark:hover:text-blue-300 font-medium">
                      __{{ __('View All Messages') }}
                    </button>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Settings -->
            <button
              @click="$router.push('/settings')"
              class="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              title="Settings"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>

            <!-- Profile Dropdown -->
            <div class="relative">
              <button
                @click="showProfileDropdown = !showProfileDropdown"
                class="flex items-center gap-2 p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                title="Profile"
              >
                <img
                  :src="userAvatar"
                  :alt="userName"
                  class="w-8 h-8 rounded-full object-cover"
                />
                <span class="hidden sm:inline text-sm font-medium text-gray-700 dark:text-gray-300">{{ userName }}</span>
                <svg class="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              </button>

              <!-- Profile Dropdown Menu -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="showProfileDropdown"
                  class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-900 rounded-lg shadow-xl z-50 border border-gray-200 dark:border-gray-700"
                >
                  <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ userName }}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">{{ userEmail }}</p>
                  </div>
                  <nav class="p-2 space-y-1">
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
                    >
                      {{ __('Profile') }}
                    </a>
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
                    >
                      __{{ __('Settings') }}
                    </a>
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition"
                    >
                      __{{ __('Help & Support') }}
                    </a>
                  </nav>
                  <div class="p-2 border-t border-gray-200 dark:border-gray-700">
                    <button
                      @click="logout"
                      class="w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition text-left"
                    >
                      __{{ __('Logout') }}
                    </button>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Theme Toggle -->
            <button
              @click="toggleTheme"
              class="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              :title="__('Toggle Theme')"
            >
              <svg v-if="isDark" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
              </svg>
            </button>
          </div>
        </div>
      </nav>

      <!-- Main Content with Sidebar -->
      <div class="flex flex-1 overflow-hidden">
        <!-- Sidebar Component -->
        <Sidebar :is-collapsed="isSidebarCollapsed" @toggle="toggleSidebar" :style="{ background: 'var(--app-bg)' }" />

        <!-- Page Content -->
        <div class="flex-1 overflow-auto" :style="{ background: 'var(--app-bg)' }">
          <main class="p-6">
            <slot />
          </main>
        </div>
      </div>
    </div>

    <!-- Mobile Overlay -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isSidebarCollapsed"
        @click="toggleSidebar"
        class="fixed inset-0 bg-gray-900 bg-opacity-50 z-30 md:hidden"
      ></div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  getNotifications,
  getMessages,
  markNotificationAsRead,
  markAllNotificationsAsRead
} from '@/services/api.js'
import config from '@/config/frappe'
import { useSettingsStore } from '@/stores/settings.js'
import {useShiftStore} from '@/stores/shift'

import Sidebar from './Sidebar.vue'
import { session } from '@/services/auth';
// Settings Store
const settingsStore = useSettingsStore()
const shiftStore = useShiftStore()

const route = useRoute()
const router = useRouter()

// State
const showNotifications = ref(false)
const showMessages = ref(false)
const showProfileDropdown = ref(false)
const isSidebarCollapsed = ref(false)

// Dark Mode from Settings Store
const isDark = computed(() => settingsStore.settings.appearance.theme === 'dark')
const primaryColor = computed(() => settingsStore.settings.appearance.primaryColor || '#06b6d4')
const currentPage = computed(() => {
  const currentRoute = route.meta

  return {
    section: currentRoute.section || '',
    title: currentRoute.title || 'Dashboard'
  }
})

// Search State
const searchQuery = ref('')
const showSearchResults = ref(false)
const selectedResultIndex = ref(0)

const availablePages = computed(() => {
  return router.options.routes.map(route => ({
    name: route.name,
    path: route.path,
    description: route.meta?.description || '',
    icon: route.meta?.icon || '',
    keywords: route.meta?.keywords || []
  }))
})
// User Data
const userName = ref('Ahmed Reda')
const userEmail = ref('ahmed@example.com')
const userAvatar = ref('https://ui-avatars.com/api/?name=Ahmed+Reda&background=0D8ABC&color=fff')

// Notifications
const notifications = ref([])

// Messages
const messages = ref([])

// Computed Properties
const notificationCount = computed(() => notifications.value.filter(n => !n.read).length)
const messageCount = computed(() => messages.value.length)

// Search Computed
const filteredPages = computed(() => {
  if (!searchQuery.value) return []

  const query = searchQuery.value.toLowerCase().trim()

  return availablePages.value.filter(page => {
    const nameMatch = page.name.toLowerCase().includes(query)
    const descMatch = page.description.toLowerCase().includes(query)
    const keywordMatch = page.keywords.some(keyword => keyword.includes(query))

    return nameMatch || descMatch || keywordMatch
  })
})

// Methods
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleTheme = () => {
  const newTheme = settingsStore.settings.appearance.theme === 'dark' ? 'light' : 'dark'
  settingsStore.settings.appearance.theme = newTheme
  applyTheme(newTheme)
}

const applyTheme = (theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const logout = () => {
  session.logout.submit()
}
const markAsRead = async (notificationId) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    const success = await markNotificationAsRead(notificationId)
    if (success) {
      notification.read = true
    }
  }
}

const markAllAsRead = async () => {
  const unreadIds = notifications.value
    .filter(n => !n.read)
    .map(n => n.id)

  if (unreadIds.length > 0) {
    const success = await markAllNotificationsAsRead(unreadIds)
    if (success) {
      notifications.value.forEach(n => {
        n.read = true
      })
    }
  }
}

const getNotificationIcon = (type) => {
  const icons = {
    alert: 'AlertIcon',
    purchase: 'ShoppingCartIcon',
    success: 'CheckIcon',
    default: 'BellIcon'
  }
  return icons[type] || icons.default
}

const getNotificationIconBg = (type) => {
  const colors = {
    alert: 'bg-red-500',
    purchase: 'bg-blue-500',
    success: 'bg-green-500',
    default: 'bg-gray-500'
  }
  return `w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${colors[type] || colors.default}`
}

// Search Methods
const handleSearch = () => {
  showSearchResults.value = true
  selectedResultIndex.value = 0
}

const navigateToPage = (path) => {
  searchQuery.value = ''
  showSearchResults.value = false
  window.location.href = path
}

const navigateToResult = () => {
  if (filteredPages.value.length > 0) {
    const selectedPage = filteredPages.value[selectedResultIndex.value]
    navigateToPage(selectedPage.path)
  }
}

// Close search results when clicking outside
const handleClickOutside = (event) => {
  const searchContainer = event.target.closest('.relative.w-64')
  if (!searchContainer) {
    showSearchResults.value = false
  }
}

// Lifecycle Hooks
onMounted(async () => {

  document.addEventListener('click', handleClickOutside)
  applyTheme(settingsStore.settings.appearance.theme)

  // Load user info from Frappe
  const userInfo = await shiftStore.getCurrentUserInfo()
  if (userInfo) {
    userName.value = userInfo.full_name || userInfo.user
    userEmail.value = userInfo.email
    userAvatar.value = userInfo.user_image
      ? `${window.location.origin}${userInfo.user_image}`
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(userInfo.full_name)}&background=0D8ABC&color=fff`
  }

  // Load notifications
  const notificationsData = await getNotifications(userName.value)
  console.log("notificationsData",notificationsData)
  if (notificationsData.length > 0) {
    notifications.value = notificationsData.map((n, index) => ({
      id: n.name,
      title: n.subject || 'Notification',
      message: n.email_content || '',
      time: formatTime(n.creation),
      type: getNotificationType(n.type),
      read: n.read || false
    }))
  }

  // Load messages
  const messagesData = await getMessages()
  if (messagesData.length > 0) {
    messages.value = messagesData.map(m => ({
      id: m.name,
      sender: m.sender || 'System',
      subject: m.subject || 'Message',
      time: formatTime(m.creation)
    }))
  }

  // Setup Socket.io for realtime notifications
  setupRealtimeNotifications()
})

// Helper Functions
const formatTime = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (days < 7) return `${days} day${days > 1 ? 's' : ''} ago`
  return date.toLocaleDateString()
}

const getNotificationType = (type) => {
  const typeMap = {
    'Alert': 'alert',
    'Purchase': 'purchase',
    'Success': 'success',
    'Info': 'info'
  }
  return typeMap[type] || 'alert'
}

const setupRealtimeNotifications = () => {
  // Check if frappe.realtime is available
  if (typeof frappe !== 'undefined' && frappe.realtime) {
    frappe.realtime.on('notification', (data) => {
      const newNotification = {
        id: Date.now(),
        title: data.subject || 'New Notification',
        message: data.message || '',
        time: 'Just now',
        type: data.type || 'alert',
        read: false
      }
      notifications.value.unshift(newNotification)
    })

    frappe.realtime.on('new_message', (data) => {
      const newMessage = {
        id: Date.now(),
        sender: data.sender || 'System',
        subject: data.subject || 'New Message',
        time: 'Just now'
      }
      messages.value.unshift(newMessage)
    })
  }
}

</script>

<style scoped>
/* Smooth transitions */
.transition {
  transition: all 0.2s ease;
}

/* Scrollbar styling - Dark Mode Support */
main::-webkit-scrollbar {
  width: 8px;
}

main::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

main::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded;
}

main::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400 dark:bg-gray-500;
}
</style>
