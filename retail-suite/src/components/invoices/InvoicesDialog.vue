<template>
  <!-- ════════════════ OVERLAY ════════════════ -->
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200 ease-out"
      leave-active-class="transition-opacity duration-200 ease-out"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="show"
        class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/55 backdrop-blur-sm"
        @click.self="close"
        aria-modal="true"
        role="dialog"
        aria-label="Invoices"
      >
        <!-- ════════════════ DIALOG ════════════════ -->
        <Transition
          enter-active-class="transition-all duration-[220ms] ease-out"
          leave-active-class="transition-all duration-[220ms] ease-out"
          enter-from-class="opacity-0 scale-[0.97] translate-y-2"
          leave-to-class="opacity-0 scale-[0.97] translate-y-2"
        >
          <div v-if="show" class="w-[95vw] h-[92vh] max-w-[1500px] flex flex-col rounded-xl overflow-hidden bg-[var(--card-bg)] border border-[var(--card-border)] shadow-[0_24px_64px_rgba(0,0,0,0.35),0_0_0_1px_rgba(255,255,255,0.04)] max-[540px]:max-h-[95vh] max-[540px]:rounded-[10px]">

            <!-- ── TOP BAR ── -->
            <div class="flex items-center justify-between px-4 py-2.5 border-b border-[var(--card-border)] bg-[var(--item-bg)] flex-shrink-0">
              <div class="flex items-center gap-2">
                <span
                  class="flex items-center justify-center w-7 h-7 rounded-md text-white"
                  :style="{ background: primaryColor }"
                >
                  <FileText class="w-4 h-4" />
                </span>
                <span class="text-[13px] font-bold text-[var(--text-main)] tracking-wide">{{ __('Invoices') }}</span>
                <span class="text-[9px] font-bold px-1.5 py-0.5 rounded tracking-[0.08em] bg-[var(--info-bg)]" :style="{ color: primaryColor }">POS</span>
              </div>
              <button class="flex items-center justify-center w-7 h-7 rounded-md border-none cursor-pointer bg-transparent text-[var(--text-muted)] transition-colors hover:bg-[var(--nav-item-hover-bg)] hover:text-[var(--text-main)]" @click="close" aria-label="Close">
                <X class="w-3.5 h-3.5" />
              </button>
            </div>

            <!-- ── BODY ── -->
            <div class="flex flex-1 min-h-0 overflow-hidden max-[540px]:flex-col">

              <!-- LEFT NAV -->
              <nav class="w-[180px] flex-shrink-0 flex flex-col gap-0.5 p-2 border-r border-[var(--card-border)] bg-[var(--item-bg)] overflow-y-auto max-[540px]:w-full max-[540px]:flex-row max-[540px]:p-2 max-[540px]:gap-1 max-[540px]:overflow-x-auto max-[540px]:border-r-0 max-[540px]:border-b max-[540px]:[scrollbar-width:none] max-[540px]:[&::-webkit-scrollbar]:hidden">
                <button
                    v-for="mode in modes"
                    :key="mode.key"
                    class="group flex items-center gap-2 py-2 px-2.5 rounded-[7px] border-none cursor-pointer text-left bg-transparent text-[var(--text-muted)] transition-colors text-xs font-medium relative hover:bg-[var(--nav-item-hover-bg)] hover:text-[var(--text-sub)] max-[540px]:flex-col max-[540px]:gap-[3px] max-[540px]:py-1.5 max-[540px]:px-2.5 max-[540px]:text-[10px] max-[540px]:min-w-fit max-[540px]:whitespace-nowrap max-[540px]:items-center"
                    :class="{ 'font-semibold': activeMode === mode.key }"
                    :style="activeMode === mode.key
                      ? {
                          background: `${primaryColorSoft} !important`,
                          color: `${primaryColor} !important`
                        }
                      : {}"
                    @click="switchMode(mode.key)"
                  >
                  <span class="flex items-center flex-shrink-0">
                    <component :is="mode.icon" class="w-4 h-4" />
                  </span>
                  <span class="flex-1 leading-tight">{{ mode.label }}</span>
                  <span
                    v-if="mode.badge !== null"
                    class="text-[10px] font-bold px-1.5 py-px rounded-full bg-[var(--card-border)] text-[var(--text-muted)]"
                    :style="activeMode === mode.key ? { background: primaryColor, color: '#fff' } : {}"
                  >{{ mode.badge }}</span>
                  <span
                    class="flex items-center opacity-0 transition-opacity group-hover:opacity-100 max-[540px]:hidden"
                    :class="{ 'opacity-100': activeMode === mode.key }"
                  >
                    <ChevronRight class="w-2.5 h-2.5" />
                  </span>
                </button>

                <!-- Quick stats in nav -->
                <div class="mt-auto pt-3 flex items-center justify-center gap-2.5 max-[540px]:hidden">
                  <div class="flex flex-col items-center gap-px">
                    <span class="text-sm font-bold text-[var(--text-main)] leading-none">{{ draftInvoices.length }}</span>
                    <span class="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">{{ __('Drafts') }}</span>
                  </div>
                  <div class="w-px h-6 bg-[var(--card-border)]" />
                  <div class="flex flex-col items-center gap-px">
                    <span class="text-sm font-bold text-[var(--text-main)] leading-none">{{ returnInvoices.length }}</span>
                    <span class="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">{{ __('Returns') }}</span>
                  </div>
                </div>
              </nav>

              <!-- RIGHT WORKSPACE -->
              <div class="flex-1 min-w-0 overflow-y-auto [scrollbar-width:thin] max-[540px]:max-h-[calc(95vh-140px)]">
                <Transition
                  mode="out-in"
                  enter-active-class="transition-all duration-[180ms] ease-out"
                  leave-active-class="transition-opacity duration-[120ms] ease-out"
                  enter-from-class="opacity-0 translate-x-2"
                  leave-to-class="opacity-0"
                >

                  <!-- ─────── A: DRAFT INVOICES ─────── -->
                  <div v-if="activeMode === 'draft'" key="draft" class="flex flex-col gap-4 h-full p-5 max-[540px]:p-3.5">
                    <DraftInvoicesList
                      :invoices="draftInvoices"
                      :loading="draftLoading"
                      :expanded-invoices="expandedInvoices"
                      @toggle="toggleInvoice"
                      @open-invoice="openDraftInvoice"
                      @delete-draft="deleteDraft"
                    />
                  </div>

                  <!-- ─────── B: RETURNABLE INVOICES ─────── -->
                  <div v-else-if="activeMode === 'return'" key="return" class="flex flex-col gap-4 h-full p-5 max-[540px]:p-3.5">
                    <ReturnInvoicesList
                      :invoices="returnInvoices"
                      :loading="returnLoading"
                      :selected-id="selectedReturnId"
                      :mode="mode"
                      @select="selectedReturnId = $event"
                      @process-return="handleProcessReturn"
                    />
                  </div>

                </Transition>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick, toRaw } from 'vue'
import { FileText, X, RotateCcw, ChevronRight } from 'lucide-vue-next'
import DraftInvoicesList from './Sections/DraftInvoicesList.vue'
import ReturnInvoicesList from './Sections/ReturnInvoicesList.vue'
import { useInvoicesStore } from '@/stores/invoices'
import { useShiftStore } from '@/stores/shift'
import { useCartStore } from '@/stores/cart'
import { useSettingsStore } from '@/stores/settings'
import { __ } from '@/i18n/index'
import { createDocumentResource } from 'frappe-ui'
// ─────────────────────────────────────────────────────────
// PROPS & EMITS
// ─────────────────────────────────────────────────────────
const props = defineProps({
  show: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'open-invoice', 'delete-draft', 'select-return'])

// ─────────────────────────────────────────────────────────
// STORES
// ─────────────────────────────────────────────────────────
const invoicesStore = useInvoicesStore()
const shiftStore     = useShiftStore()
const cartStore      = useCartStore()
const settingsStore  = useSettingsStore()

// ─────────────────────────────────────────────────────────
// THEME
// ─────────────────────────────────────────────────────────
const primaryColor = computed(() => {
  return settingsStore.settings.appearance.primaryColor || '#06b6d4'
})

// Soft tinted background for the active nav item (approx 12% opacity)
const primaryColorSoft = computed(() => {
  const hex = primaryColor.value?.replace('#', '')

  if (!hex || hex.length !== 6) {
    return 'rgba(6, 182, 212, 0.12)'
  }

  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)

  return `rgba(${r}, ${g}, ${b}, 0.12)`
})
const draftInvoices    = ref([])
const draftLoading     = ref(false)


// ─────────────────────────────────────────────────────────
// NAVIGATION MODES
// ─────────────────────────────────────────────────────────
const modes = computed(() => [
  { key: 'draft',  label: __('Draft Invoices'),       icon: FileText,  badge: draftInvoices.value.length || null },
  { key: 'return', label: __('Returnable Invoices'),  icon: RotateCcw, badge: returnInvoices.value.length || null },
])

const activeMode = ref('draft')

const switchMode = (key) => {
  activeMode.value = key
}

const close = () => emit('close')

// ─────────────────────────────────────────────────────────
// A: DRAFT INVOICES STATE
// ─────────────────────────────────────────────────────────
const draftLoaded      = ref(false)
const expandedInvoices = ref(new Set())

const toggleInvoice = (name) => {
  const s = new Set(expandedInvoices.value)
  s.has(name) ? s.delete(name) : s.add(name)
  expandedInvoices.value = s
}

/**
 * Load draft invoices for the current shift only.
 * Relies on currentShift from shiftStore — the parent only needs
 * to know the active shift, the component handles its own data.
 */
const currentShift = computed(() => shiftStore.currentShift)

const loadDraftInvoices = async () => {

  draftLoading.value = true

  try {
    draftInvoices.value = await invoicesStore.loadDraftInvoices(currentShift.value.name)

    draftLoading.value = false
    console.log("draftInvoices.value",draftInvoices.value)
    // Restrict to current shift if the API doesn't already filter
    draftInvoices.value = (draftInvoices.value || []).filter(inv =>
      !currentShift.value || !inv.posa_pos_opening_shift || inv.posa_pos_opening_shift === currentShift.value.name
      )
  } catch (e) {
    console.error('Error loading draft invoices:', e)
    draftInvoices.value = []
  } finally {
    draftLoading.value = false
    draftLoaded.value = true
  }
}

/**
 * Open a draft invoice — fixes the previously broken "open" button.
 * Loads the full invoice (items, taxes, payments) via the invoices store
 * before emitting so the parent / cart can hydrate correctly.
 */
const openDraftInvoice = (invoiceName) => {

  try {
    console.log("invoiceName",invoiceName)
     const invoice = draftInvoices.value.find(inv => inv.name === invoiceName)
      if (!invoice) return
      console.log("invoice",invoice)
      cartStore.loadDraftInvoice(invoice)
      emit('open-invoice', invoiceName)
      close()
  } catch (e) {
    console.error('Failed to open draft invoice:', e)
    emit('open-invoice', invoiceName)
  }
}

const deleteDraft = async (name) => {
  const doc = createDocumentResource({
    doctype: 'Sales Invoice',
    name: name,
  })
  await doc.get.fetch()
  if (doc.doc) {
    await doc.delete.submit()
  }
  draftInvoices.value = draftInvoices.value.filter(inv => inv.name !== name)
  expandedInvoices.value.delete(name)
}

// ─────────────────────────────────────────────────────────
// B: RETURNABLE INVOICES STATE
// ─────────────────────────────────────────────────────────
const returnInvoices   = ref([])
const returnLoading    = ref(false)
const returnLoaded     = ref(false)
const selectedReturnId = ref(null)

const loadReturnInvoices = async () => {
  returnLoading.value = true
  try {
    const invoices = await invoicesStore.allReturnableInvoices()
    // Restrict to the current shift only (e.g. POSA-OS-26-0000003)
    console.log("invoices (Return)",invoices)
    returnInvoices.value = (invoices || []).filter(inv =>
      !currentShift.value || inv.posa_pos_opening_shift === currentShift.value.name
    )
  } catch (e) {
    console.error('Error loading returnable invoices:', e)
    returnInvoices.value = []
  } finally {
    returnLoading.value = false
    returnLoaded.value = true
  }
}
const handleProcessReturn = async (invoice) => {

  const doc = createDocumentResource({
    doctype: 'Sales Invoice',
    name: invoice.name,
  })

  await doc.get.fetch()

  if (!doc.doc) {
    window.$toast?.error('Failed to load invoice for return')
    return
  }

  const fullInvoice = {
    ...doc.doc,
    returnable_items: invoice.returnable_items,
    total_returnable_qty: invoice.total_returnable_qty,
  }

  cartStore.loadReturnInvoice(toRaw(fullInvoice), shiftStore.pos_profile?.name)
  emit('select-return', fullInvoice)
  close()
}


// ─────────────────────────────────────────────────────────
// LIFECYCLE
// ─────────────────────────────────────────────────────────

// Load data lazily on first visit to each mode
watch(activeMode, (mode) => {
  if (mode === 'draft' && !draftLoaded.value) loadDraftInvoices()
  if (mode === 'return' && !returnLoaded.value) loadReturnInvoices()
})

// Reset & (re)load fresh data whenever the dialog opens
watch(() => props.show, (open) => {
  if (open) {
    activeMode.value = 'draft'
    selectedReturnId.value = null
    expandedInvoices.value = new Set()

    draftLoaded.value = false
    returnLoaded.value = false

    nextTick(() => {
      loadDraftInvoices()
    })
  }
})

// Escape to close
const onKeydown = (e) => { if (e.key === 'Escape' && props.show) close() }
onMounted(() => window.addEventListener('keydown', onKeydown))
</script>
