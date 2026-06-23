<template>
  <Teleport to="body">
    <Transition name="sd-overlay">
      <div
         v-if="open"
         class="sd-overlay"
         @click.self="$emit('update:modelValue', false)"
       >
       <Transition name="sd-dialog">
         <div class="sd-shell" :class="isDark ? 'theme-dark' : 'theme-light'">

           <!-- ══════════════════════════════════
                LOADING STATE
           ══════════════════════════════════ -->
           <div v-if="loading" class="sd-loader">
             <div class="sd-loader__ring" :style="{ borderTopColor: primaryColor }"></div>
             <span class="sd-loader__text">{{ __('Loading shift details...') }}</span>
           </div>

           <!-- ══════════════════════════════════
                EMPTY STATE
           ══════════════════════════════════ -->
           <div v-else-if="!shift" class="sd-loader">
             <div class="sd-empty-icon">📋</div>
             <span class="sd-loader__text">{{ __('No shift data available') }}</span>
             <Button variant="ghost" @click="$emit('update:modelValue', false)">{{ __('Close') }}</Button>
           </div>

           <!-- ══════════════════════════════════
                MAIN CONTENT
           ══════════════════════════════════ -->
           <template v-else>
             <!-- ── HERO BAND ─────────────────────────── -->
             <div class="sd-hero" :style="{ background: `linear-gradient(135deg, ${primaryColor}18 0%, ${primaryColor}06 100%)` }">
               <div class="sd-hero__left">
                 <!-- Status pill -->
                 <div class="sd-status-pill" :class="shift.status === 'open' ? 'sd-status--open' : 'sd-status--closed'">
                   <span class="sd-status-pill__dot"></span>
                   {{ shift.status === 'open' ? __('Open Shift') : __('Closed Shift') }}
                 </div>
                 <div class="sd-hero__id">{{ __('Shift') }} <span class="sd-hero__num">#{{ shift.id || shift.name }}</span></div>
                 <div class="sd-hero__period">
                   <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                   {{ formatDate(shift.period_start_date) }}
                   <span class="sd-hero__arrow">→</span>
                   {{ shift.period_end_date ? formatDate(shift.period_end_date) : __('Now') }}
                 </div>
               </div>

               <!-- Hero financials -->
               <div class="sd-hero__financials">
                 <div class="sd-hero__stat">
                   <span class="sd-hero__stat-label">{{ __('Total Sales') }}</span>
                   <span class="sd-hero__stat-val" >
                     {{ formatCurrency(shift.total_sales, currencyCode, locale) }}
                   </span>
                   <span class="sd-hero__stat-sub">{{ invoices.length }} {{ __('invoices') }}</span>
                 </div>
                 <div class="sd-hero__divider"></div>
                 <div class="sd-hero__stat">
                   <span class="sd-hero__stat-label">{{ __('Opening Balance') }}</span>
                   <span class="sd-hero__stat-val">{{ formatCurrency(shift.opening_cash, currencyCode, locale) }}</span>
                   <span class="sd-hero__stat-sub">{{ shift.opened_by_name || '—' }}</span>
                 </div>
                 <div v-if="shift.status === 'closed'" class="sd-hero__divider"></div>
                 <div v-if="shift.status === 'closed'" class="sd-hero__stat">
                   <span class="sd-hero__stat-label">{{ __('Closing Balance') }}</span>
                   <span class="sd-hero__stat-val">{{ formatCurrency(shift.closing_cash, currencyCode, locale) }}</span>
                   <span class="sd-hero__stat-sub" :class="cashDifference < 0 ? 'sd-neg' : cashDifference > 0 ? 'sd-pos' : ''">
                     {{ cashDifference >= 0 ? '+' : '' }}{{ formatCurrency(cashDifference, currencyCode, locale) }}
                     {{ cashDifference === 0 ? __('Balanced') : cashDifference > 0 ? __('Surplus') : __('Deficit') }}
                   </span>
                 </div>
               </div>

               <!-- Close button -->
               <button class="sd-close-x" @click="$emit('update:modelValue', false)">
                 <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
               </button>
             </div>

             <!-- ── MINI KPI ROW ───────────────────────── -->
             <div class="sd-kpi-row">
               <div class="sd-kpi" v-for="kpi in kpiCards" :key="kpi.label">
                 <div class="sd-kpi__icon" :style="{ background: kpi.color + '18', color: kpi.color }">
                   <component :is="kpi.icon" />
                 </div>
                 <div class="sd-kpi__body">
                   <span class="sd-kpi__val" :style="kpi.valColor ? { color: kpi.valColor } : {}">{{ kpi.value }}</span>
                   <span class="sd-kpi__label">{{ kpi.label }}</span>
                 </div>
               </div>
             </div>

             <!-- ── BODY (scrollable) ──────────────────── -->
             <div class="sd-body">

               <!-- LEFT COLUMN: charts + staff -->
               <div class="sd-col sd-col--left">

                 <!-- Payment breakdown -->
                 <div class="sd-card">
                   <div class="sd-card__head">
                     <span class="sd-card__title">{{ __('Payment Methods') }}</span>
                   </div>
                   <div class="sd-pm-list">
                     <div v-for="pm in paymentBreakdown" :key="pm.mode_of_payment" class="sd-pm-item">
                       <div class="sd-pm-item__label-row">
                         <div class="sd-pm-item__dot" :style="{ background: pm.color }"></div>
                         <span class="sd-pm-item__name">{{ pm.mode_of_payment }}</span>
                         <span class="sd-pm-item__pct" :style="{ color: pm.color }">{{ pm.pct }}%</span>
                         <span class="sd-pm-item__val">{{ formatCurrency(pm.expected_amount, currencyCode, locale) }}</span>
                       </div>
                       <div class="sd-pm-track">
                         <div class="sd-pm-fill" :style="{ width: pm.pct + '%', background: pm.color }"></div>
                       </div>
                     </div>
                     <p v-if="!paymentBreakdown.length" class="sd-empty">{{ __('No payments recorded') }}</p>
                   </div>
                 </div>

                 <!-- Hourly sales -->
                 <div class="sd-card">
                   <div class="sd-card__head">
                     <span class="sd-card__title">{{ __('Sales by Hour') }}</span>
                   </div>
                   <div class="sd-chart" v-if="hourlySales.length">
                     <div v-for="h in hourlySales" :key="h.hour" class="sd-bar-col"
                       :title="`${h.hour}:00 — ${formatCurrency(h.total, currencyCode, locale)}`">
                       <div class="sd-bar-fill" :style="{ height: h.pct + '%', background: primaryColor }"></div>
                       <span class="sd-bar-label">{{ h.hour }}</span>
                     </div>
                   </div>
                   <p v-else class="sd-empty">{{ __('No data available') }}</p>
                 </div>

                 <!-- Staff performance -->
                 <div class="sd-card">
                   <div class="sd-card__head">
                     <span class="sd-card__title">{{ __('Cashier Performance') }}</span>
                   </div>
                   <div class="sd-staff-list">
                     <div v-for="(s, i) in staffPerformance" :key="s.owner" class="sd-staff-row">
                       <span class="sd-staff-rank" :style="i === 0 ? { color: '#f59e0b' } : {}">
                         {{ i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i + 1}` }}
                       </span>
                       <Avatar :label="s.fullName || s.owner" size="sm" />
                       <div class="sd-staff-info">
                         <span class="sd-staff-name">{{ s.fullName || s.owner }}</span>
                         <span class="sd-staff-sub">{{ s.count }} {{ __('invoices') }}</span>
                       </div>
                       <span class="sd-staff-total" :style="{ color: primaryColor }">{{ formatCurrency(s.total, currencyCode, locale) }}</span>
                     </div>
                     <p v-if="!staffPerformance.length" class="sd-empty">{{ __('No data available') }}</p>
                   </div>
                 </div>

               </div>

               <!-- RIGHT COLUMN: tabbed tables -->
               <div class="sd-col sd-col--right">

                 <!-- Tab bar -->
                 <div class="sd-tab-bar">
                   <button
                     v-for="tab in tabs"
                     :key="tab.key"
                     class="sd-tab"
                     :class="{ 'sd-tab--active': activeTab === tab.key, 'sd-tab--alert': tab.alert }"
                     :style="activeTab === tab.key ? { color: primaryColor, borderBottomColor: primaryColor } : {}"
                     @click="activeTab = tab.key"
                   >
                     {{ tab.label }}
                     <span class="sd-tab-badge" :class="tab.alert ? 'sd-tab-badge--warn' : ''">{{ tab.count }}</span>
                   </button>
                 </div>

                 <!-- ─ INVOICES ─ -->
                 <div v-show="activeTab === 'invoices'" class="sd-table-panel">
                   <!-- Toolbar -->
                   <div class="sd-toolbar">
                     <div class="sd-search-box">
                       <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                       <input v-model="invoiceSearch" class="sd-search-input" :placeholder="__('Search invoice, customer...')" />
                       <button v-if="invoiceSearch" class="sd-clear-btn" @click="invoiceSearch = ''">✕</button>
                     </div>
                     <select v-model="invoiceStatusFilter" class="sd-select">
                       <option value="">{{ __('All Statuses') }}</option>
                       <option value="Paid">{{ __('Paid') }}</option>
                       <option value="Return">{{ __('Returned') }}</option>
                       <option value="Draft">{{ __('Draft') }}</option>
                       <option value="credit note issued">{{ __('Credit Note') }}</option>
                       <option value="unpaid">{{ __('Unpaid') }}</option>
                     </select>
                     <select v-model="invoiceSortBy" class="sd-select">
                       <option value="date_desc">{{ __('Newest') }}</option>
                       <option value="date_asc">{{ __('Oldest') }}</option>
                       <option value="total_desc">{{ __('Highest') }}</option>
                       <option value="total_asc">{{ __('Lowest') }}</option>
                     </select>
                     <button class="sd-icon-action" @click="exportInvoices" :title="__('Export CSV')">
                       <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                     </button>
                   </div>

                   <!-- Table -->
                   <div class="sd-scroll-area">
                     <table class="sd-table">
                       <thead>
                         <tr>
                           <th>{{ __('Invoice') }}</th>
                           <th>{{ __('Date') }}</th>
                           <th>{{ __('Customer') }}</th>
                           <th>{{ __('Total') }}</th>
                           <th>{{ __('Payment') }}</th>
                           <th>{{ __('Status') }}</th>
                           <th></th>
                         </tr>
                       </thead>
                       <tbody>
                         <tr v-for="inv in paginatedInvoices" :key="inv.name"
                           class="sd-tr" :class="{ 'sd-tr--return': flt(inv.total) < 0 }">
                           <td>
                             <button class="sd-link" @click="viewInvoice(inv)">{{ inv.name }}</button>
                           </td>
                           <td class="sd-muted">{{ formatDate(inv.posting_date) }} <span class="sd-time">{{ formatTime(inv.posting_time) }}</span></td>
                           <td>{{ inv.customer_name || __('Unknown') }}</td>
                           <td class="sd-amount" :class="flt(inv.grand_total) < 0 ? 'sd-neg' : ''">
                             {{ formatCurrency(inv.grand_total, currencyCode, locale) }}
                           </td>
                           <td>
                             <div class="sd-chips-wrap">
                               <template v-if="inv.all_payments?.length">
                                 <span v-for="(p, pi) in getUniquePayments(inv)" :key="pi"
                                   class="sd-chip sd-chip--info">{{ p.mode_of_payment }}</span>
                               </template>
                               <span v-else class="sd-chip sd-chip--info">{{ inv.payment_method || '—' }}</span>
                             </div>
                           </td>
                           <td><span class="sd-chip" :class="getStatusClass(inv)">{{ getStatusLabel(inv) }}</span></td>
                           <td>
                             <div class="sd-row-acts">
                               <button class="sd-act-btn" @click="viewInvoice(inv)" :title="__('View')">
                                 <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                               </button>
                               <button class="sd-act-btn sd-act-btn--green" @click="printInvoice(inv)" :title="__('Print')">
                                 <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                               </button>
                             </div>
                           </td>
                         </tr>
                         <tr v-if="!filteredInvoices.length">
                           <td colspan="7" class="sd-empty-cell">{{ __('No matching invoices') }}</td>
                         </tr>
                       </tbody>
                       <tfoot v-if="filteredInvoices.length">
                         <tr>
                           <td colspan="3" class="sd-foot-label">{{ filteredInvoices.length }} {{ __('invoices') }}</td>
                           <td class="sd-foot-val" :style="{ color: primaryColor }">{{ formatCurrency(filteredInvoicesTotal, currencyCode, locale) }}</td>
                           <td colspan="3"></td>
                         </tr>
                       </tfoot>
                     </table>
                   </div>

                   <!-- Pagination -->
                   <div class="sd-pager" v-if="invoiceTotalPages > 1">
                     <button class="sd-page-btn" :disabled="invoicePage === 1" @click="invoicePage--">‹</button>
                     <button v-for="p in invoiceTotalPages" :key="p"
                       class="sd-page-btn" :class="{ 'sd-page-btn--on': p === invoicePage }"
                       :style="p === invoicePage ? { background: primaryColor, borderColor: primaryColor } : {}"
                       @click="invoicePage = p">{{ p }}</button>
                     <button class="sd-page-btn" :disabled="invoicePage === invoiceTotalPages" @click="invoicePage++">›</button>
                   </div>
                 </div>

                 <!-- ─ PAYMENTS ─ -->
                 <div v-show="activeTab === 'payments'" class="sd-table-panel">
                   <div class="sd-scroll-area">
                     <table class="sd-table">
                       <thead>
                         <tr>
                           <th>{{ __('Method') }}</th>
                           <th>{{ __('Opening') }}</th>
                           <th>{{ __('Expected') }}</th>
                           <th>{{ __('Actual') }}</th>
                           <th>{{ __('Diff') }}</th>
                         </tr>
                       </thead>
                       <tbody>
                         <tr v-for="pm in payments" :key="pm.mode_of_payment" class="sd-tr">
                           <td><span class="sd-chip sd-chip--info">{{ pm.mode_of_payment }}</span></td>
                           <td class="sd-muted">{{ formatCurrency(pm.opening_amount || 0, currencyCode, locale) }}</td>
                           <td>{{ formatCurrency(pm.expected_amount || 0, currencyCode, locale) }}</td>
                           <td>{{ formatCurrency(pm.closing_amount || 0, currencyCode, locale) }}</td>
                           <td>
                             <span :class="(pm.difference||0) < 0 ? 'sd-neg' : (pm.difference||0) > 0 ? 'sd-pos' : 'sd-muted'">
                               {{ (pm.difference||0) >= 0 ? '+' : '' }}{{ formatCurrency(pm.difference || 0, currencyCode, locale) }}
                             </span>
                           </td>
                         </tr>
                         <tr v-if="!payments.length"><td colspan="5" class="sd-empty-cell">{{ __('No data') }}</td></tr>
                       </tbody>
                     </table>
                   </div>
                 </div>

                 <!-- ─ TRANSACTIONS ─ -->
                 <div v-show="activeTab === 'transactions'" class="sd-table-panel">
                   <div class="sd-toolbar">
                     <div class="sd-search-box">
                       <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                       <input v-model="txSearch" class="sd-search-input" :placeholder="__('Search transactions...')" />
                       <button v-if="txSearch" class="sd-clear-btn" @click="txSearch = ''">✕</button>
                     </div>
                     <select v-model="txTypeFilter" class="sd-select">
                       <option value="">{{ __('All Types') }}</option>
                       <option value="in">{{ __('In') }}</option>
                       <option value="out">{{ __('Out') }}</option>
                     </select>
                     <div class="sd-tx-summary">
                       <span class="sd-pos">↑ {{ formatCurrency(txTotalIn, currencyCode, locale) }}</span>
                       <span class="sd-neg">↓ {{ formatCurrency(txTotalOut, currencyCode, locale) }}</span>
                     </div>
                   </div>
                   <div class="sd-scroll-area">
                     <table class="sd-table">
                       <thead>
                         <tr>
                           <th>{{ __('Type') }}</th>
                           <th>{{ __('Description') }}</th>
                           <th>{{ __('Method') }}</th>
                           <th>{{ __('Amount') }}</th>
                           <th>{{ __('Date') }}</th>
                           <th>{{ __('By') }}</th>
                         </tr>
                       </thead>
                       <tbody>
                         <tr v-for="(tx, i) in filteredTransactions" :key="i" class="sd-tr">
                           <td>
                             <div class="sd-tx-badge" :class="tx.type === 'in' ? 'sd-tx-badge--in' : 'sd-tx-badge--out'">
                               {{ tx.type === 'in' ? __('In') : __('Out') }}
                             </div>
                           </td>
                           <td>{{ tx.description }}</td>
                           <td><span class="sd-chip sd-chip--info">{{ tx.mode_of_payment }}</span></td>
                           <td class="sd-amount" :class="tx.type === 'in' ? 'sd-pos' : 'sd-neg'">
                             {{ tx.type === 'in' ? '+' : '−' }}{{ formatCurrency(tx.amount, currencyCode, locale) }}
                           </td>
                           <td class="sd-muted">{{ formatDate(tx.created_at) }}</td>
                           <td class="sd-muted">{{ tx.user_name }}</td>
                         </tr>
                         <tr v-if="!filteredTransactions.length"><td colspan="6" class="sd-empty-cell">{{ __('No transactions found') }}</td></tr>
                       </tbody>
                       <tfoot v-if="filteredTransactions.length">
                         <tr>
                           <td colspan="3" class="sd-foot-label">{{ __('Net') }}</td>
                           <td class="sd-foot-val" :class="txNet >= 0 ? 'sd-pos' : 'sd-neg'">
                             {{ txNet >= 0 ? '+' : '−' }}{{ formatCurrency(Math.abs(txNet), currencyCode, locale) }}
                           </td>
                           <td colspan="2"></td>
                         </tr>
                       </tfoot>
                     </table>
                   </div>
                 </div>

                 <!-- ─ ISSUES ─ -->
                 <div v-show="activeTab === 'issues'" class="sd-table-panel">

                    <!-- Banner لازم يكون flex-shrink: 0 — وهو كذلك في الـ CSS -->
                    <div v-if="shift.reconciliation_issues?.length" class="sd-warn-banner">
                      ⚠️ {{ __('There are {0} invoices with payment discrepancies', [shift.reconciliation_issues.length]) }}
                    </div>

                    <!-- الـ scroll-area لازم تاخد الباقي -->
                    <div class="sd-scroll-area">
                      <table class="sd-table">
                        <thead>
                          <tr>
                            <th>{{ __('Invoice') }}</th>
                            <th>{{ __('Customer') }}</th>
                            <th>{{ __('Invoice Total') }}</th>
                            <th>{{ __('Collected') }}</th>
                            <th>{{ __('Diff') }}</th>
                            <th>{{ __('Type') }}</th>
                          </tr>
                        </thead>
                        <tbody>
                          <!-- reconciliation issues -->
                          <tr v-for="issue in shift.reconciliation_issues" :key="issue.invoice" class="sd-tr">
                            <td><button class="sd-link" @click="viewInvoice(issue)">{{ issue.invoice }}</button></td>
                            <td>{{ issue.customer }}</td>
                            <td>{{ formatCurrency(issue.invoice_total, currencyCode, locale) }}</td>
                            <td>{{ formatCurrency(issue.total_collected, currencyCode, locale) }}</td>
                            <td :class="issue.issue_type === 'overpaid' ? 'sd-pos' : 'sd-neg'">
                              {{ formatCurrency(Math.abs(issue.difference), currencyCode, locale) }}
                            </td>
                            <td>
                              <span class="sd-chip" :class="issue.issue_type === 'overpaid' ? 'sd-chip--success' : 'sd-chip--danger'">
                                {{ issue.issue_type === 'overpaid' ? __('Overpaid') : __('Underpaid') }}
                              </span>
                            </td>
                          </tr>

                          <!-- unallocated divider -->
                          <tr v-if="shift.unallocated_payments?.length">
                            <td colspan="6" class="sd-section-divider">
                              ⚠️ {{ __('Unallocated Payments ({0})', [shift.unallocated_payments.length]) }}
                            </td>
                          </tr>

                          <!-- unallocated rows -->
                          <tr v-for="pe in shift.unallocated_payments" :key="pe.payment_entry" class="sd-tr sd-tr--return">
                            <td>{{ pe.payment_entry }}</td>
                            <td>{{ pe.party_name || pe.party }}</td>
                            <td>{{ formatCurrency(pe.paid_amount, currencyCode, locale) }}</td>
                            <td class="sd-neg">{{ formatCurrency(pe.unallocated_amount, currencyCode, locale) }}</td>
                            <td colspan="2"><span class="sd-chip sd-chip--warn">{{ __('Unallocated') }}</span></td>
                          </tr>

                          <!-- empty state -->
                          <tr v-if="!shift.reconciliation_issues?.length && !shift.unallocated_payments?.length">
                            <td colspan="6" class="sd-empty-cell sd-pos">✓ {{ __('All payments are matched') }}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>

                 </div>

               </div>
             </div>

             <!-- ── FOOTER ACTIONS ────────────────────── -->
             <div class="sd-footer">
               <Button variant="ghost" theme="red" size="sm" @click="printShiftReport">
                 <template #prefix>
                   <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
                 </template>
                 {{ __('Print Report') }}
               </Button>
             </div>

           </template>
         </div>
       </Transition>
     </div>
    </Transition>
  </Teleport>
  <!-- ═════════════════InvoiceTemplate═════════════════ -->
  <template>
    <div class="flex justify-center p-6 bg-gray-50 min-h-screen">
      <InvoiceTemplate v-if="receipt" ref="invoiceRef" :receipt="receipt" />
      <div v-else class="text-gray-400 mt-20">Loading...</div>
    </div>
  </template>
</template>

<script setup>
import { ref, computed, watch, onMounted, h, toRaw } from 'vue'
import { useRouter } from 'vue-router'
import { Avatar, Button, Dialog, createDocumentResource, call } from 'frappe-ui'
import { useShiftStore } from '@/stores/shift'
import { formatCurrency } from '@/utils/formatters'
import { useSettingsStore } from '@/stores/settings'
import { useDark } from '@vueuse/core'
import InvoiceTemplate from '@/components/modals/invoiceTemplate.vue'
// ── Props & Emits ──
const receipt = ref(null)
const props = defineProps({
  modelValue: { type: Boolean, default: false },
  shiftId:    { type: [String, Number], required: true },
})
const emit = defineEmits(['update:modelValue'])

const open = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const router       = useRouter()
const settingsStore = useSettingsStore()
const shiftStore = useShiftStore()


const isDark       = useDark({ selector: 'html', attribute: 'class', valueDark: 'dark', valueLight: '' })

const currencyCode = settingsStore?.settings?.pricing?.currency || 'USD'
const locale       = settingsStore?.settings?.system?.language || 'en'
const primaryColor = computed(() => settingsStore?.settings?.appearance?.primaryColor || '#06b6d4')

// ── State ──
const shift               = ref(null)
const loading             = ref(false)

const activeTab           = ref('invoices')

const invoiceSearch        = ref('')
const invoiceStatusFilter  = ref('')
const invoiceSortBy        = ref('date_desc')
const invoicePage          = ref(1)
const INVOICE_PAGE_SIZE    = 10

const txSearch     = ref('')
const txTypeFilter = ref('')

// ── Helpers ──
const flt = (v) => parseFloat(v) || 0

const formatDate = (d) => {
  if (!d) return '—'
  try { return new Date(d).toLocaleDateString(locale, { day: '2-digit', month: '2-digit', year: 'numeric' }) }
  catch { return d }
}
const formatTime = (t) => t ? String(t).substring(0, 5) : ''

// ── Core computed ──
const invoices     = computed(() => shift.value?.invoices     || [])
const transactions = computed(() => shift.value?.transactions || [])
const payments     = computed(() => shift.value?.payments     || [])

const salesCount   = computed(() => invoices.value.filter(i => flt(i.grand_total) >= 0).length)
const returnsCount = computed(() => invoices.value.filter(i => flt(i.grand_total) < 0).length)
const totalReturns = computed(() => invoices.value.filter(i => flt(i.grand_total) < 0).reduce((s, i) => s + Math.abs(flt(i.grand_total)), 0))
const totalQty     = computed(() => invoices.value.reduce((s, i) => s + flt(i.total_qty), 0))
const avgInvoice   = computed(() => {
  const sales = invoices.value.filter(i => flt(i.grand_total) > 0)
  return sales.length ? sales.reduce((s, i) => s + flt(i.grand_total), 0) / sales.length : 0
})
const expectedCash   = computed(() => flt(shift.value?.opening_cash) + flt(shift.value?.total_cash_collected))
const cashDifference = computed(() => {
  if (!shift.value || shift.value.status !== 'closed') return 0
  return flt(shift.value.closing_cash) - expectedCash.value
})

// Inline SVG icon components for KPI cards
const IconTrend  = { render: () => h('svg', { width:14, height:14, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':2 }, [h('polyline',{points:'23 6 13.5 15.5 8.5 10.5 1 18'}),h('polyline',{points:'17 6 23 6 23 12'})]) }
const IconAvg    = { render: () => h('svg', { width:14, height:14, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':2 }, [h('circle',{cx:12,cy:12,r:10}),h('polyline',{points:'12 6 12 12 16 14'})]) }
const IconCart   = { render: () => h('svg', { width:14, height:14, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':2 }, [h('path',{d:'M3 3h2l.4 2M7 13h10l4-8H5.4'}),h('circle',{cx:9,cy:19,r:1}),h('circle',{cx:20,cy:19,r:1})]) }
const IconReturn = { render: () => h('svg', { width:14, height:14, viewBox:'0 0 24 24', fill:'none', stroke:'currentColor', 'stroke-width':2 }, [h('polyline',{points:'1 4 1 10 7 10'}),h('path',{d:'M3.51 15a9 9 0 102.13-9.36L1 10'})]) }

const kpiCards = computed(() => {
  const cards = [
    { label: __('Avg Invoice'),    value: formatCurrency(avgInvoice.value, currencyCode, locale), color: '#06b6d4', icon: IconAvg },
    { label: __('Items Sold'),     value: totalQty.value,                                          color: '#f97316', icon: IconCart },
    { label: __('Sales'),          value: salesCount.value,                                        color: '#10b981', icon: IconTrend },
  ]
  if (returnsCount.value > 0) {
    cards.push({ label: __('Returns'), value: formatCurrency(totalReturns.value, currencyCode, locale), color: '#ef4444', valColor: '#ef4444', icon: IconReturn })
  }
  return cards
})

// ── Payment breakdown ──
const COLORS = ['#3b82f6','#10b981','#f59e0b','#8b5cf6','#ef4444','#06b6d4','#f97316']
const paymentBreakdown = computed(() => {
  const list  = payments.value.filter(p => flt(p.expected_amount) > 0)
  const total = list.reduce((s, p) => s + flt(p.expected_amount), 0) || 1
  return list.map((p, i) => ({
    ...p,
    pct:   Math.round(flt(p.expected_amount) / total * 100),
    color: COLORS[i % COLORS.length],
  }))
})

// ── Hourly sales ──
const hourlySales = computed(() => {
  const map = {}
  invoices.value.forEach(inv => {
    if (!inv.posting_time) return
    const h = parseInt(String(inv.posting_time).split(':')[0]) || 0
    map[h] = (map[h] || 0) + flt(inv.grand_total)
  })
  const hours = Object.entries(map).filter(([, v]) => v > 0).map(([h, v]) => ({ hour: +h, total: v })).sort((a,b) => a.hour - b.hour)
  const max   = Math.max(...hours.map(h => h.total)) || 1
  return hours.map(h => ({ ...h, pct: Math.round(h.total / max * 100) }))
})

// ── Staff performance ──
const staffPerformance = computed(() =>
  (shift.value?.staff_performance || [])
    .map(s => ({ owner: s.user_id, fullName: s.name, count: s.invoices_count, total: s.total_sales }))
    .sort((a, b) => b.total - a.total)
)

// ── Tabs ──
const tabs = computed(() => [
  { key: 'invoices',     label: __('Invoices'),             count: invoices.value.length },
  { key: 'payments',     label: __('Payments'),             count: payments.value.length },
  { key: 'transactions', label: __('Transactions'),         count: transactions.value.length },
  { key: 'issues',       label: __('Issues'),               count: shift.value?.reconciliation_issues?.length || 0, alert: shift.value?.has_issues },
])

// ── Invoice table ──
const getUniquePayments = (inv) => {
  const all = inv.all_payments || inv.payments || []
  const seen = new Set()
  return all.filter(p => { const k = `${p.mode_of_payment}-${p.source}`; if (seen.has(k)) return false; seen.add(k); return true })
}

const getStatusLabel = (inv) => {
  if (flt(inv.grand_total) < 0) return __('Return')
  return { paid: __('Paid'), unpaid: __('Unpaid'), 'partly paid': __('Partly Paid'), return: __('Return'), draft: __('Draft'), cancelled: __('Cancelled'), 'credit note issued': __('Credit Note') }[(inv.status||'').toLowerCase()] || inv.status || '—'
}
const getStatusClass = (inv) => {
  if (flt(inv.grand_total) < 0) return 'sd-chip--warn'
  return { paid: 'sd-chip--success', unpaid: 'sd-chip--muted', 'partly paid': 'sd-chip--info', return: 'sd-chip--warn', draft: 'sd-chip--muted', cancelled: 'sd-chip--danger', 'credit note issued': 'sd-chip--info' }[(inv.status||'').toLowerCase()] || 'sd-chip--info'
}

const filteredInvoices = computed(() => {
  let list = [...invoices.value]
  const q = invoiceSearch.value.trim().toLowerCase()
  if (q) list = list.filter(i => (i.name||'').toLowerCase().includes(q) || (i.customer_name||'').toLowerCase().includes(q))
  if (invoiceStatusFilter.value) {
    list = list.filter(i => invoiceStatusFilter.value === 'Return' ? flt(i.grand_total) < 0 : (i.status||'').toLowerCase() === invoiceStatusFilter.value.toLowerCase())
  }
  const [field, dir] = invoiceSortBy.value.split('_')
  list.sort((a, b) => {
    const av = field === 'total' ? flt(a.grand_total) : (String(a.posting_date||'') + String(a.posting_time||''))
    const bv = field === 'total' ? flt(b.grand_total) : (String(b.posting_date||'') + String(b.posting_time||''))
    return dir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
  })
  return list
})

const filteredInvoicesTotal = computed(() => filteredInvoices.value.reduce((s, i) => s + flt(i.grand_total), 0))
const invoiceTotalPages     = computed(() => Math.max(1, Math.ceil(filteredInvoices.value.length / INVOICE_PAGE_SIZE)))
const paginatedInvoices     = computed(() => {
  const offset = (invoicePage.value - 1) * INVOICE_PAGE_SIZE
  return filteredInvoices.value.slice(offset, offset + INVOICE_PAGE_SIZE)
})

// ── Transactions ──
const filteredTransactions = computed(() => {
  let list = [...transactions.value]
  const q = txSearch.value.trim().toLowerCase()
  if (q) list = list.filter(t => (t.description||'').toLowerCase().includes(q) || (t.user_name||'').toLowerCase().includes(q))
  if (txTypeFilter.value) list = list.filter(t => t.type === txTypeFilter.value)
  return list
})
const txTotalIn  = computed(() => filteredTransactions.value.filter(t => t.type === 'in').reduce((s, t) => s + flt(t.amount), 0))
const txTotalOut = computed(() => filteredTransactions.value.filter(t => t.type === 'out').reduce((s, t) => s + flt(t.amount), 0))
const txNet      = computed(() => txTotalIn.value - txTotalOut.value)

// ── Actions ──
const loadShiftData = async (id) => {
  if (!id) return
  loading.value = true
  try {

    shift.value =
     await shiftStore.getShiftDetails(id)
  } catch (e) {
    console.error('Failed to load shift:', e)
  } finally {
    loading.value = false
  }
}
const viewInvoice = async (invoice) => {
  const printer = settingsStore.settings.printer
  console.log("Printer :", printer)
  const html = await call('retail.retail.api.setting.view_invoice', {
    invoice_name: invoice.name,
    printer: JSON.stringify(printer),
  })

  const tab = window.open('', '_blank')
  tab.document.write(html)
  tab.document.close()
}

// const viewInvoice = async (invoice) => {
//   const receipt = toRaw(invoice)
//   const doc = createDocumentResource({
//     doctype: 'Sales Invoice',
//     name: receipt.name,
//   })
//   await doc.get.fetch()
//   const full = toRaw(doc.doc)

//   const html = buildInvoiceHTML(full)
//   const win = window.open('', '_blank')
//   win.document.write(html)
//   win.document.close()
// }

// const viewInvoice = (invoice) => {
//   const url = `/printview?doctype=Sales+Invoice&name=${invoice.name}&trigger_print=0`
//   window.open(url, '_blank')
// }

const buildInvoiceHTML = (inv) => {
  const items = (inv.items || []).map(i => `
    <tr>
      <td>${i.item_name}</td>
      <td class="center">${i.qty}</td>
      <td class="right">${inv.currency} ${i.rate.toFixed(2)}</td>
      <td class="right bold">${inv.currency} ${(i.qty * i.rate).toFixed(2)}</td>
    </tr>
  `).join('')

  return `<!DOCTYPE html>
<html dir="${inv.language === 'ar' ? 'rtl' : 'ltr'}">
<head>
  <meta charset="UTF-8">
  <title>Invoice ${inv.name}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: system-ui, sans-serif;
      background: #f3f4f6;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .wrap { width: 100%; max-width: 420px; background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb; }
    .header { background: #876EAB; color: #fff; padding: 18px 20px 14px; }
    .header h1 { font-size: 16px; font-weight: 700; letter-spacing: 0.03em; }
    .header p  { font-size: 10px; opacity: 0.75; margin-top: 2px; }
    .badge { display: flex; justify-content: space-between; align-items: baseline; background: rgba(0,0,0,0.15); border-radius: 7px; padding: 6px 12px; margin-top: 12px; }
    .badge-label { font-size: 10px; font-weight: 700; letter-spacing: 0.1em; opacity: 0.85; }
    .badge-num   { font-size: 13px; font-weight: 700; font-family: monospace; }
    .meta { display: flex; padding: 10px 20px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; flex-wrap: wrap; }
    .meta-item { display: flex; flex-direction: column; gap: 1px; padding: 4px 12px; }
    .meta-item:first-child { padding-left: 0; }
    .meta-label { font-size: 9px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: #9ca3af; }
    .meta-val   { font-size: 11px; font-weight: 600; color: #111827; white-space: nowrap; }
    .items { padding: 0 20px; }
    .items table { width: 100%; border-collapse: collapse; }
    .items thead th { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #6b7280; padding: 8px 0 6px; border-bottom: 1.5px solid #111827; }
    .items tbody td { font-size: 11px; color: #111827; padding: 7px 0; border-bottom: 1px dashed #e5e7eb; }
    .center { text-align: center; }
    .right  { text-align: right; }
    .bold   { font-weight: 700; }
    .summary { padding: 12px 20px 0; border-top: 1.5px solid #111827; margin: 0 20px; }
    .summary-row { display: flex; justify-content: space-between; padding: 3px 0; font-size: 11px; color: #6b7280; }
    .summary-total { display: flex; justify-content: space-between; align-items: center; padding: 10px 0 8px; margin-top: 4px; border-top: 1px solid #e5e7eb; border-bottom: 1px solid #e5e7eb; }
    .summary-total span:first-child { font-size: 12px; font-weight: 700; letter-spacing: 0.06em; color: #111827; }
    .summary-total-val { font-size: 18px; font-weight: 700; color: #876EAB; }
    .summary-payment { padding: 8px 0 12px; }
    .footer { padding: 14px 20px 18px; background: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center; }
    .footer-note { font-size: 11px; font-weight: 600; color: #374151; margin-bottom: 4px; }
    .footer-tax  { font-size: 9px; color: #9ca3af; margin-bottom: 12px; }
    .actions { width: 100%; max-width: 420px; display: flex; gap: 8px; margin-top: 12px; }
    .print-btn { flex: 1; padding: 10px 0; background: #876EAB; color: #fff; border: none; border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer; }
    .close-btn { flex: 1; padding: 10px 0; background: #fff; color: #374151; border: 1px solid #e5e7eb; border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer; }
    @media print {
      .actions { display: none; }
      body { background: #fff; padding: 0; justify-content: flex-start; }
      .wrap { border: none; border-radius: 0; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1>${inv.company || ''}</h1>
      <div class="badge">
        <span class="badge-label">${inv.is_return ? 'RETURN' : 'INVOICE'}</span>
        <span class="badge-num">#${inv.name}</span>
      </div>
    </div>

    <div class="meta">
      <div class="meta-item"><span class="meta-label">Date</span><span class="meta-val">${inv.posting_date}</span></div>
      <div class="meta-item"><span class="meta-label">Time</span><span class="meta-val">${inv.posting_time?.slice(0,5)}</span></div>
      <div class="meta-item"><span class="meta-label">Cashier</span><span class="meta-val">${inv.owner || '—'}</span></div>
      <div class="meta-item"><span class="meta-label">Customer</span><span class="meta-val">${inv.customer_name || '—'}</span></div>
    </div>

    <div class="items">
      <table>
        <thead><tr>
          <th>Item</th><th class="center">Qty</th><th class="right">Price</th><th class="right">Total</th>
        </tr></thead>
        <tbody>${items}</tbody>
      </table>
    </div>

    <div class="summary">
      <div class="summary-row"><span>Subtotal</span><span>${inv.currency} ${(inv.net_total || 0).toFixed(2)}</span></div>
      ${inv.total_taxes_and_charges > 0 ? `<div class="summary-row"><span>Tax</span><span>${inv.currency} ${inv.total_taxes_and_charges.toFixed(2)}</span></div>` : ''}
      ${inv.discount_amount > 0 ? `<div class="summary-row" style="color:#10b981"><span>Discount</span><span>-${inv.currency} ${inv.discount_amount.toFixed(2)}</span></div>` : ''}
      <div class="summary-total">
        <span>TOTAL</span>
        <span class="summary-total-val">${inv.currency} ${(inv.grand_total || 0).toFixed(2)}</span>
      </div>
      <div class="summary-payment">
        <div class="summary-row"><span>${inv.payments?.[0]?.mode_of_payment || 'Cash'}</span><span>${inv.currency} ${(inv.paid_amount || 0).toFixed(2)}</span></div>
        ${inv.change_amount > 0 ? `<div class="summary-row" style="color:#10b981;font-weight:600"><span>Change</span><span>${inv.currency} ${inv.change_amount.toFixed(2)}</span></div>` : ''}
      </div>
    </div>

    <div class="footer">
      <p class="footer-note">Thank you for your purchase!</p>
      ${inv.tax_id ? `<p class="footer-tax">CR: ${inv.tax_id}</p>` : ''}
    </div>
  </div>

  <div class="actions">
    <button class="print-btn" onclick="window.print()">🖨 Print</button>
    <button class="close-btn" onclick="window.close()">✕ Close</button>
  </div>
</body>
</html>`
}


const printInvoice = async (invoice) => {
  const printer = settingsStore.settings.printer

  if (!printer?.name) {
    console.warn('No printer configured')
    return
  }

  try {
    await call('retail.retail.api.setting.print_with_ip', {
      invoice_name: invoice.name,
      printer: JSON.stringify(printer),
    })
    console.log('Printed:', invoice.name)
  } catch (err) {
    console.error('Print failed:', err)
  }
}

const printShiftReport = () => {
  const s = toRaw(shift.value)
  const html = buildShiftReportHTML(s)
  const win = window.open('', '_blank')
  win.document.write(html)
  win.document.close()
}

const buildShiftReportHTML = (s) => {
  const currency = 'SAR'

  const fmt = (val) => `${currency} ${(val || 0).toFixed(2)}`

  // Payment rows
  const paymentRows = (s.payments || []).map(pm => `
    <tr>
      <td>${pm.mode_of_payment}</td>
      <td class="right">${fmt(pm.opening_amount)}</td>
      <td class="right">${fmt(pm.expected_amount)}</td>
      <td class="right">${fmt(pm.closing_amount)}</td>
      <td class="right ${pm.difference < 0 ? 'neg' : pm.difference > 0 ? 'pos' : 'muted'}">
        ${pm.difference >= 0 ? '+' : ''}${fmt(pm.difference)}
      </td>
    </tr>
  `).join('')

  // Staff rows
  const staffRows = (s.staff_performance || []).map((st, i) => `
    <tr>
      <td>${i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${i+1}`}</td>
      <td>${st.name}</td>
      <td class="center">${st.invoices_count}</td>
      <td class="right bold">${fmt(st.total_sales)}</td>
    </tr>
  `).join('')

  // Invoice rows
  const invoiceRows = (s.invoices || []).map((inv, i) => `
    <tr>
      <td class="mono">${inv.name}</td>
      <td>${inv.posting_date}</td>
      <td>${inv.customer_name}</td>
      <td class="right bold ${inv.grand_total < 0 ? 'neg' : ''}">${fmt(inv.grand_total)}</td>
      <td>${inv.payments?.[0]?.mode_of_payment || '—'}</td>
      <td><span class="badge badge-${inv.status === 'Paid' ? 'success' : inv.status === 'Return' ? 'danger' : 'warn'}">${inv.status}</span></td>
    </tr>
  `).join('')

  // Issues rows
  const issueRows = (s.reconciliation_issues || []).map(issue => `
    <tr>
      <td class="mono">${issue.invoice}</td>
      <td>${issue.customer}</td>
      <td class="right">${fmt(issue.invoice_total)}</td>
      <td class="right">${fmt(issue.total_collected)}</td>
      <td class="right ${issue.issue_type === 'overpaid' ? 'pos' : 'neg'}">${fmt(issue.difference)}</td>
      <td><span class="badge badge-${issue.issue_type === 'overpaid' ? 'success' : 'danger'}">${issue.issue_type}</span></td>
    </tr>
  `).join('')

  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Shift Report - ${s.name}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: system-ui, sans-serif; background: #f3f4f6; display: flex; flex-direction: column; align-items: center; padding: 24px; gap: 12px; }
    .wrap { width: 100%; max-width: 860px; background: #fff; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb; }

    .header { background: #876EAB; color: #fff; padding: 20px 24px; display: flex; justify-content: space-between; align-items: flex-start; }
    .header-left h1 { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
    .header-left p  { font-size: 11px; opacity: 0.75; }
    .header-right   { text-align: right; font-size: 11px; opacity: 0.8; line-height: 1.8; }
    .status-pill { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 10px; font-weight: 700; letter-spacing: 0.06em; margin-bottom: 6px; }
    .status-open   { background: rgba(16,185,129,0.25); color: #6ee7b7; }
    .status-closed { background: rgba(239,68,68,0.25);  color: #fca5a5; }

    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); border-bottom: 1px solid #e5e7eb; }
    .kpi { padding: 16px 20px; border-right: 1px solid #e5e7eb; }
    .kpi:last-child { border-right: none; }
    .kpi-label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #9ca3af; margin-bottom: 6px; }
    .kpi-val   { font-size: 18px; font-weight: 700; color: #111827; }
    .kpi-sub   { font-size: 10px; color: #9ca3af; margin-top: 3px; }
    .kpi-accent { color: #876EAB; }
    .kpi-pos    { color: #10b981; }
    .kpi-neg    { color: #ef4444; }

    .section { padding: 16px 24px; border-bottom: 1px solid #e5e7eb; }
    .section:last-child { border-bottom: none; }
    .section-title { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #9ca3af; margin-bottom: 12px; }

    table { width: 100%; border-collapse: collapse; font-size: 11px; }
    thead th { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #6b7280; padding: 6px 8px; border-bottom: 1.5px solid #111827; text-align: left; white-space: nowrap; }
    tbody td { padding: 7px 8px; border-bottom: 1px solid #f3f4f6; color: #111827; vertical-align: middle; }
    tbody tr:last-child td { border-bottom: none; }
    tbody tr:hover td { background: #f9fafb; }
    tfoot td { padding: 8px; background: #f9fafb; font-weight: 700; font-size: 11px; border-top: 1.5px solid #e5e7eb; }

    .right  { text-align: right; }
    .center { text-align: center; }
    .bold   { font-weight: 700; }
    .mono   { font-family: monospace; font-size: 10px; }
    .muted  { color: #9ca3af; }
    .pos    { color: #10b981; font-weight: 600; }
    .neg    { color: #ef4444; font-weight: 600; }

    .badge { display: inline-block; padding: 2px 7px; border-radius: 999px; font-size: 9px; font-weight: 700; white-space: nowrap; }
    .badge-success { background: rgba(16,185,129,0.12); color: #10b981; }
    .badge-danger  { background: rgba(239,68,68,0.1);  color: #ef4444; }
    .badge-warn    { background: rgba(245,158,11,0.12); color: #f59e0b; }

    .warn-banner { background: rgba(245,158,11,0.1); color: #f59e0b; font-size: 11px; font-weight: 600; padding: 8px 12px; border-radius: 6px; margin-bottom: 10px; }

    .footer-section { padding: 12px 24px; background: #f9fafb; text-align: center; font-size: 10px; color: #9ca3af; }

    .actions { width: 100%; max-width: 860px; display: flex; gap: 8px; }
    .print-btn { flex: 1; padding: 10px 0; background: #876EAB; color: #fff; border: none; border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer; }
    .close-btn { flex: 1; padding: 10px 0; background: #fff; color: #374151; border: 1px solid #e5e7eb; border-radius: 7px; font-size: 13px; font-weight: 600; cursor: pointer; }

    @media print {
      .actions { display: none; }
      body { background: #fff; padding: 0; }
      .wrap { border: none; border-radius: 0; }
      thead { background: #f9fafb !important; }
    }
  </style>
</head>
<body>
  <div class="wrap">

    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <div class="status-pill ${s.status === 'open' ? 'status-open' : 'status-closed'}">
          ● ${s.status === 'open' ? 'Open Shift' : 'Closed Shift'}
        </div>
        <h1>Shift #${s.id || s.name}</h1>
        <p>${s.period_start_date?.slice(0,10)} → ${s.period_end_date ? s.period_end_date.slice(0,10) : 'Now'}</p>
      </div>
      <div class="header-right">
        <div>Opened by: <strong>${s.opened_by_name || '—'}</strong></div>
        ${s.closed_by_name ? `<div>Closed by: <strong>${s.closed_by_name}</strong></div>` : ''}
        <div style="margin-top:6px;opacity:0.6">Printed: ${new Date().toLocaleString()}</div>
      </div>
    </div>

    <!-- KPI -->
    <div class="kpi-row">
      <div class="kpi">
        <div class="kpi-label">Total Sales</div>
        <div class="kpi-val kpi-accent">${fmt(s.total_sales)}</div>
        <div class="kpi-sub">${s.invoices_count || s.invoices?.length || 0} invoices</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Cash Collected</div>
        <div class="kpi-val">${fmt(s.total_cash_collected)}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Opening Balance</div>
        <div class="kpi-val">${fmt(s.opening_cash)}</div>
        <div class="kpi-sub">${s.opened_by_name || '—'}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Issues</div>
        <div class="kpi-val ${s.has_issues ? 'kpi-neg' : 'kpi-pos'}">
          ${s.reconciliation_issues?.length || 0}
        </div>
        <div class="kpi-sub">${s.has_issues ? 'Needs attention' : 'All clear'}</div>
      </div>
    </div>

    <!-- Payment Methods -->
    <div class="section">
      <div class="section-title">Payment Methods</div>
      <table>
        <thead><tr>
          <th>Method</th>
          <th class="right">Opening</th>
          <th class="right">Expected</th>
          <th class="right">Actual</th>
          <th class="right">Difference</th>
        </tr></thead>
        <tbody>${paymentRows || '<tr><td colspan="5" style="text-align:center;color:#9ca3af;padding:16px">No payment data</td></tr>'}</tbody>
      </table>
    </div>

    <!-- Staff Performance -->
    ${staffRows ? `
    <div class="section">
      <div class="section-title">Cashier Performance</div>
      <table>
        <thead><tr>
          <th>#</th><th>Cashier</th><th class="center">Invoices</th><th class="right">Total Sales</th>
        </tr></thead>
        <tbody>${staffRows}</tbody>
      </table>
    </div>` : ''}

    <!-- Invoices -->
    <div class="section">
      <div class="section-title">Invoices (${s.invoices?.length || 0})</div>
      <table>
        <thead><tr>
          <th>Invoice</th>
          <th>Date</th>
          <th>Customer</th>
          <th class="right">Total</th>
          <th>Payment</th>
          <th>Status</th>
        </tr></thead>
        <tbody>${invoiceRows || '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:16px">No invoices</td></tr>'}</tbody>
        <tfoot>
          <tr>
            <td colspan="3">Total (${s.invoices?.length || 0} invoices)</td>
            <td class="right" style="color:#876EAB">${fmt(s.total_sales)}</td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- Reconciliation Issues -->
    ${s.has_issues ? `
    <div class="section">
      <div class="section-title">Reconciliation Issues</div>
      <div class="warn-banner">⚠️ ${s.reconciliation_issues?.length} invoices with payment discrepancies</div>
      <table>
        <thead><tr>
          <th>Invoice</th>
          <th>Customer</th>
          <th class="right">Invoice Total</th>
          <th class="right">Collected</th>
          <th class="right">Difference</th>
          <th>Type</th>
        </tr></thead>
        <tbody>${issueRows}</tbody>
      </table>
    </div>` : ''}

    <!-- Footer -->
    <div class="footer-section">
      Generated on ${new Date().toLocaleString()} · Shift ${s.name}
    </div>

  </div>

  <div class="actions">
    <button class="print-btn" onclick="window.print()">🖨 Print Report</button>
    <button class="close-btn" onclick="window.close()">✕ Close</button>
  </div>
</body>
</html>`
}
const exportInvoices   = () => {
  const rows = [['Invoice','Date','Customer','Total','Payment','Status']]
  filteredInvoices.value.forEach(inv => rows.push([inv.name, inv.posting_date, inv.customer_name||'', inv.grand_total, inv.payment_method||'', inv.status||'']))
  const csv  = rows.map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = Object.assign(document.createElement('a'), { href: url, download: `shift-${props.shiftId}-invoices.csv` })
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url)
}

// Load when opened
watch(() => props.modelValue, (v) => { if (v && props.shiftId) loadShiftData(props.shiftId) })
onMounted(() => { if (props.modelValue && props.shiftId) loadShiftData(props.shiftId) })
</script>

<style scoped>
/* ═══════════════════════════════════════
   SHELL
═══════════════════════════════════════ */
/* احذف الـ Dialog wrapper القديم وخلي sd-shell هو الـ dialog */
.sd-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(3px);
}

.sd-shell {
  width: 95vw;
  max-width: 1500px;
  height: 92vh;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: 0 24px 64px rgba(0,0,0,0.35);
}

/* Transitions */
.sd-overlay-enter-active,
.sd-overlay-leave-active { transition: opacity 0.2s ease; }
.sd-overlay-enter-from,
.sd-overlay-leave-to { opacity: 0; }

.sd-dialog-enter-active,
.sd-dialog-leave-active { transition: opacity 0.2s ease, transform 0.22s ease; }
.sd-dialog-enter-from,
.sd-dialog-leave-to { opacity: 0; transform: scale(0.97) translateY(8px); }

/* ═══════════════════════════════════════
   LOADER / EMPTY
═══════════════════════════════════════ */
.sd-loader {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
}
.sd-loader__ring {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 3px solid var(--card-border);
  border-top-color: var(--focus-ring);
  animation: sd-spin .7s linear infinite;
}
@keyframes sd-spin { to { transform: rotate(360deg) } }
.sd-loader__text  { font-size: 13px; color: var(--text-muted); }
.sd-empty-icon    { font-size: 32px; }

/* ═══════════════════════════════════════
   HERO BAND
═══════════════════════════════════════ */
.sd-hero {
  position: relative;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
}
.sd-hero__left { display: flex; flex-direction: column; gap: 4px; flex-shrink: 0; }
.sd-hero__id {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1;
}
.sd-hero__num { opacity: .7; }
.sd-hero__period {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: var(--text-muted);
}
.sd-hero__arrow { opacity: .5; }

.sd-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: .03em;
  text-transform: uppercase;
  width: fit-content;
}
.sd-status-pill__dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.sd-status--open   { background: rgba(16,185,129,.12); color: #10b981; }
.sd-status--open .sd-status-pill__dot   { background: #10b981; animation: sd-pulse 1.8s infinite; }
.sd-status--closed { background: rgba(239,68,68,.1);  color: #ef4444; }
.sd-status--closed .sd-status-pill__dot{ background: #ef4444; }
@keyframes sd-pulse { 0%,100%{opacity:1}50%{opacity:.3} }

.sd-hero__financials {
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
  justify-content: flex-end;
  padding-right: 44px;
}
.sd-hero__stat { display: flex; flex-direction: column; gap: 2px; align-items: flex-end; padding: 0 20px; }
.sd-hero__stat-label { font-size: 10px; color: var(--text-muted); font-weight: 500; }
.sd-hero__stat-val   { font-size: 15px; font-weight: 700; color: var(--text-main); white-space: nowrap; }
.sd-hero__stat-sub   { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
.sd-hero__divider    { width: 1px; height: 36px; background: var(--card-border); flex-shrink: 0; }

.sd-close-x {
  position: absolute;
  top: 12px; right: 14px;
  width: 28px; height: 28px;
  border-radius: 7px;
  border: none;
  background: var(--item-bg);
  color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all .15s;
}
.sd-close-x:hover { background: var(--nav-item-hover-bg); color: var(--text-main); }

/* ═══════════════════════════════════════
   KPI ROW
═══════════════════════════════════════ */
.sd-kpi-row {
  display: flex;
  gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
  overflow-x: auto;
}
.sd-kpi {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 9px;
  background: var(--item-bg);
  border: 1px solid var(--card-border);
  white-space: nowrap;
  flex-shrink: 0;
  transition: transform .15s;
}
.sd-kpi:hover { transform: translateY(-1px); }
.sd-kpi__icon {
  width: 30px; height: 30px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.sd-kpi__body  { display: flex; flex-direction: column; gap: 1px; }
.sd-kpi__val   { font-size: 14px; font-weight: 700; color: var(--text-main); line-height: 1.1; }
.sd-kpi__label { font-size: 10px; color: var(--text-muted); }

/* ═══════════════════════════════════════
   BODY (two-column)
═══════════════════════════════════════ */
.sd-body {
  display: grid;
  grid-template-columns: 220px 1fr;
  flex: 1;
  overflow: hidden;
}

/* ─ LEFT COLUMN ─ */
.sd-col--left {
  border-right: 1px solid var(--card-border);
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.sd-col--left::-webkit-scrollbar { width: 3px; }
.sd-col--left::-webkit-scrollbar-thumb { background: var(--card-border); border-radius: 3px; }

/* ─ RIGHT COLUMN ─ */
.sd-col--right {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ─ Cards ─ */
.sd-card { border-radius: 8px; background: var(--card-bg); border: 1px solid var(--card-border); overflow: hidden; }
.sd-card__head { padding: 8px 12px 4px; }
.sd-card__title {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: .06em;
}

/* Payment bars */
.sd-pm-list { padding: 6px 12px 12px; display: flex; flex-direction: column; gap: 8px; }
.sd-pm-item__label-row { display: flex; align-items: center; gap: 5px; margin-bottom: 3px; }
.sd-pm-item__dot  { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.sd-pm-item__name { font-size: 11px; color: var(--text-sub); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-pm-item__pct  { font-size: 10px; font-weight: 700; }
.sd-pm-item__val  { font-size: 10px; color: var(--text-muted); white-space: nowrap; }
.sd-pm-track { height: 5px; background: var(--item-bg); border-radius: 3px; overflow: hidden; }
.sd-pm-fill  { height: 100%; border-radius: 3px; transition: width .6s cubic-bezier(.4,0,.2,1); }

/* Hourly chart */
.sd-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  padding: 6px 12px 12px;
  height: 72px;
}
.sd-bar-col   { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 3px; height: 100%; }
.sd-bar-fill  { width: 100%; border-radius: 3px 3px 0 0; min-height: 3px; opacity: .7; transition: height .5s ease; }
.sd-bar-fill:hover { opacity: 1; }
.sd-bar-label { font-size: 8px; color: var(--text-muted); }

/* Staff */
.sd-staff-list { padding: 6px 12px 12px; display: flex; flex-direction: column; gap: 8px; }
.sd-staff-row  { display: grid; grid-template-columns: 20px 28px 1fr auto; align-items: center; gap: 7px; }
.sd-staff-rank { font-size: 13px; text-align: center; }
.sd-staff-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.sd-staff-name { font-size: 11px; font-weight: 600; color: var(--text-main); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sd-staff-sub  { font-size: 10px; color: var(--text-muted); }
.sd-staff-total{ font-size: 11px; font-weight: 700; white-space: nowrap; }

/* ═══════════════════════════════════════
   TABS
═══════════════════════════════════════ */
.sd-tab-bar {
  display: flex;
  border-bottom: 1px solid var(--card-border);
  background: var(--card-bg);
  padding: 0 12px;
  flex-shrink: 0;
  overflow-x: auto;
}
.sd-tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 9px 12px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all .15s;
  white-space: nowrap;
}
.sd-tab:hover { color: var(--text-main); }
.sd-tab--active { color: var(--text-main); }
.sd-tab--alert  { color: #ef4444 !important; }
.sd-tab-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 99px;
  background: var(--item-bg);
  color: var(--text-muted);
  min-width: 18px;
  text-align: center;
}
.sd-tab--active .sd-tab-badge { background: rgba(255,255,255,.1); }
.sd-tab-badge--warn { background: rgba(239,68,68,.12); color: #ef4444; }

/* ═══════════════════════════════════════
   TABLE PANELS
═══════════════════════════════════════ */
.sd-table-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.sd-toolbar {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
  flex-wrap: wrap;
}
.sd-search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 7px;
  padding: 4px 9px;
  flex: 1;
  min-width: 140px;
}
.sd-search-input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 12px;
  color: var(--text-main);
  width: 100%;
}
.sd-search-input::placeholder { color: var(--text-muted); }
.sd-clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 10px;
  padding: 0;
  line-height: 1;
}
.sd-select {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 7px;
  padding: 4px 7px;
  font-size: 11px;
  color: var(--text-main);
  outline: none;
  cursor: pointer;
}
.sd-icon-action {
  width: 28px; height: 28px;
  border-radius: 7px;
  border: 1px solid var(--card-border);
  background: var(--item-bg);
  color: var(--text-muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: all .15s;
  flex-shrink: 0;
}
.sd-icon-action:hover { color: var(--text-main); }
.sd-tx-summary { display: flex; gap: 8px; font-size: 11px; font-weight: 600; margin-left: auto; }

.sd-scroll-area { flex: 1; overflow-y: auto; overflow-x: auto; }
.sd-scroll-area::-webkit-scrollbar       { width: 3px; height: 3px; }
.sd-scroll-area::-webkit-scrollbar-thumb { background: var(--card-border); border-radius: 3px; }

.sd-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.sd-table thead th {
  padding: 7px 10px;
  text-align: start;
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: .04em;
  background: var(--item-bg);
  border-bottom: 1px solid var(--card-border);
  white-space: nowrap;
  position: sticky;
  top: 0;
  z-index: 2;
}
.sd-table tbody td {
  padding: 7px 10px;
  color: var(--text-main);
  border-bottom: 1px solid var(--card-border);
  vertical-align: middle;
}
.sd-tr:hover td            { background: var(--nav-item-hover-bg); }
.sd-tr--return td          { background: rgba(239,68,68,.03); }
.sd-tr--return:hover td    { background: rgba(239,68,68,.07); }
.sd-muted                  { color: var(--text-muted) !important; font-size: 11px; }
.sd-time                   { opacity: .6; }
.sd-amount                 { font-weight: 700; }
.sd-pos                    { color: #10b981 !important; }
.sd-neg                    { color: #ef4444 !important; }

.sd-foot-label { color: var(--text-muted) !important; text-transform: uppercase; font-size: 10px; letter-spacing: .04em; font-weight: 700; background: var(--item-bg) !important; }
.sd-foot-val   { font-weight: 700 !important; font-size: 13px !important; background: var(--item-bg) !important; }
.sd-empty-cell { text-align: center; color: var(--text-muted); padding: 24px !important; font-size: 12px; }

.sd-link {
  background: none; border: none; cursor: pointer;
  color: var(--focus-ring); font-weight: 600; font-size: 12px; padding: 0;
}
.sd-link:hover { text-decoration: underline; }
.sd-row-acts  { display: flex; gap: 3px; }
.sd-act-btn {
  width: 22px; height: 22px;
  border-radius: 5px; border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  background: transparent;
  color: var(--focus-ring);
  transition: background .12s;
}
.sd-act-btn:hover             { background: var(--info-bg); }
.sd-act-btn--green            { color: #10b981; }
.sd-act-btn--green:hover      { background: rgba(16,185,129,.1); }

.sd-chips-wrap { display: flex; flex-wrap: wrap; gap: 3px; }

/* chips */
.sd-chip         { display: inline-block; padding: 2px 7px; border-radius: 99px; font-size: 10px; font-weight: 600; white-space: nowrap; }
.sd-chip--info   { background: var(--info-bg); color: var(--focus-ring); border: 1px solid var(--info-border); }
.sd-chip--success{ background: rgba(16,185,129,.12); color: #10b981; }
.sd-chip--warn   { background: rgba(245,158,11,.12); color: #f59e0b; }
.sd-chip--danger { background: rgba(239,68,68,.1);  color: #ef4444; }
.sd-chip--muted  { background: var(--item-bg); color: var(--text-muted); border: 1px solid var(--card-border); }

.sd-tx-badge       { display: inline-flex; align-items: center; gap: 3px; padding: 2px 8px; border-radius: 99px; font-size: 10px; font-weight: 700; }
.sd-tx-badge--in   { background: rgba(16,185,129,.1);  color: #10b981; }
.sd-tx-badge--out  { background: rgba(239,68,68,.1);   color: #ef4444; }

.sd-warn-banner {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(245,158,11,.1);
  color: #f59e0b;
  font-size: 11px;
  font-weight: 600;
  border-bottom: 1px solid rgba(245,158,11,.2);
  flex-shrink: 0;
}
.sd-section-divider {
  background: rgba(245,158,11,.06) !important;
  color: #f59e0b !important;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
}

/* ═══════════════════════════════════════
   PAGINATION
═══════════════════════════════════════ */
.sd-pager {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 3px;
  padding: 8px;
  border-top: 1px solid var(--card-border);
  flex-shrink: 0;
}
.sd-page-btn {
  width: 26px; height: 26px;
  border-radius: 6px;
  border: 1px solid var(--card-border);
  background: var(--item-bg);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  transition: all .15s;
}
.sd-page-btn:hover:not(:disabled) { color: #fff; }
.sd-page-btn--on  { color: #fff !important; }
.sd-page-btn:disabled { opacity: .3; cursor: not-allowed; }

/* ═══════════════════════════════════════
   FOOTER
═══════════════════════════════════════ */
.sd-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-top: 1px solid var(--card-border);
  flex-shrink: 0;
  background: var(--card-bg);
}
.sd-footer__right { display: flex; align-items: center; gap: 8px; }

.sd-empty { font-size: 11px; color: var(--text-muted); text-align: center; padding: 12px; }

/* ═══════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════ */
@media (max-width: 700px) {
  .sd-body { grid-template-columns: 1fr; }
  .sd-col--left { border-right: none; border-bottom: 1px solid var(--card-border); }
  .sd-hero__financials { display: none; }
}

@media print {
  .sd-close-x, .sd-footer, .sd-tab-bar, .sd-toolbar { display: none !important; }
}
</style>
