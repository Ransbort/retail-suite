<template>
  <div class="space-y-3">

    <p>{{ __('Products & Barcodes') }}</p>
    <!-- Filters -->
    <div
      class="rounded-lg shadow-sm p-3"
      :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
    >
      <div class="grid grid-cols-2 md:grid-cols-5 gap-2 mb-2">

        <!-- Search -->
        <div class="col-span-2">
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Search</label>
          <div class="relative">
            <Search class="absolute left-2.5 top-2 w-3 h-3 pointer-events-none" :style="{ color: 'var(--text-muted)' }" />
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="__('SKU / barcode / item name...')"
              class="w-full pl-8 pr-3 py-1.5 rounded-md focus:outline-none text-xs transition-all"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--input-border)'
              }"
            />
          </div>
        </div>

        <!-- Product -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Product</label>
          <select
            v-model="filterProduct"
            class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
          >
            <option value="">{{ __('All Products') }}</option>
            <option v-for="p in allProducts" :key="p.item_code" :value="p.item_code">{{ p.item_name }}</option>
          </select>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Status</label>
          <select
            v-model="filterStatus"
            class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
          >
            <option value="">{{ __('All') }}</option>
            <option value="active">{{ __('Active') }}</option>
            <option value="inactive">{{ __('Inactive') }}</option>
          </select>
        </div>

        <!-- Count -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">{{ __('Count') }}</label>
          <div
            class="px-2 py-1.5 rounded-md font-semibold text-xs"
            :style="{
              background: 'var(--item-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--item-border)'
            }"
          >
            {{ __('rows', [filteredRows.length]) }}
          </div>
        </div>

      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 gap-2">

        <!-- Barcode Type -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">{{ __('Barcode Type') }}</label>
          <select
            v-model="filterType"
            class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
          >
            <option value="">{{ __('All Types') }}</option>
            <option v-for="t in barcodeTypes" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <!-- Item Group -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Item Group</label>
          <select
            v-model="filterGroup"
            class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
          >
            <option value="">{{ __('All Groups') }}</option>
            <option v-for="g in itemGroups" :key="g.name" :value="g.name">{{ g.name }}</option>
          </select>
        </div>

        <!-- Clear Filters -->
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full px-3 py-1.5 rounded-md text-xs transition-colors"
            :style="{
              background: 'var(--item-bg)',
              color: 'var(--text-sub)',
              border: '1px solid var(--item-border)'
            }"
            @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
            @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
          >
            {{ __('Clear Filters') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div
      class="rounded-lg shadow-sm flex flex-col overflow-hidden"
      :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
    >
      <!-- Table Header Bar -->
      <div
        class="px-4 py-2 flex items-center gap-2"
        :style="{ borderBottom: '1px solid var(--card-border)' }"
      >
        <BarChart2 class="w-4 h-4" :style="{ color: 'var(--text-muted)' }" />
        <span class="text-xs font-semibold" :style="{ color: 'var(--text-sub)' }">{{ __('Items & Barcodes') }}</span>
        <span class="text-xs" :style="{ color: 'var(--text-muted)' }">({{ filteredRows.length }})</span>
        <span v-if="isLoading" class="text-xs ml-auto" :style="{ color: 'var(--text-muted)' }">{{ __('Loading...') }}</span>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto" style="scrollbar-width: thin;">
        <table class="w-full border-collapse" style="font-size: 12px; min-width: 750px;">
          <thead class="sticky top-0 z-10" :style="{ background: 'var(--item-bg)' }">
            <tr>
              <th
                v-for="label in ['Product', 'SKU', 'Barcode', 'Type', 'UOM', 'Preview', 'Status', 'Actions']"
                :key="label"
                class="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide whitespace-nowrap"
                :style="{ color: 'var(--text-muted)', borderBottom: '1px solid var(--card-border)' }"
              >
                {{ label }}
              </th>
            </tr>
          </thead>

          <tbody>
            <!-- Loading -->
            <tr v-if="isLoading">
              <td colspan="8" class="py-10 text-center">
                <LoadingSpinner />
              </td>
            </tr>

            <!-- Empty -->
            <tr v-else-if="paginatedRows.length === 0">
              <td colspan="8" class="py-14 text-center">
                <div class="flex flex-col items-center gap-2">
                  <div
                    class="w-10 h-10 flex items-center justify-center rounded-full mb-1"
                    :style="{ background: 'var(--item-bg)' }"
                  >
                    <PackageSearch class="w-5 h-5" :style="{ color: 'var(--text-muted)', opacity: 0.5 }" />
                  </div>
                  <p class="text-xs font-medium" :style="{ color: 'var(--text-sub)' }">{{ __('No Items Found') }}</p>
                  <p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ __('Try adjusting your filters') }}</p>
                </div>
              </td>
            </tr>
            <!-- print first row  -->
            <template v-else v-for="row in paginatedRows" :key="row.rowKey">
              <tr
                class="transition-colors"
                :style="{ borderBottom: '1px solid var(--card-border)' }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'var(--card-bg)'"
              >
                <!-- Product -->
                <td class="px-3 py-2">
                  <template v-if="row.isFirstRow">
                    <div class="flex items-center gap-2">
                      <img
                        :src="row.image"
                        class="h-8 w-8 rounded-md object-cover flex-shrink-0"
                        :style="{ border: '1px solid var(--card-border)' }"
                        :alt="row.productName"
                      />
                      <div>
                        <div class="font-medium" :style="{ color: 'var(--text-main)' }">{{ row.productName }}</div>
                        <div style="font-size:10px;" :style="{ color: 'var(--text-muted)' }">{{ row.item_group || '—' }}</div>
                        <span
                          v-if="row.totalBarcodes > 0"
                          class="inline-block mt-0.5 text-xs px-1.5 py-0.5 rounded-full font-medium"
                          style="font-size:10px;"
                          :style="{ background: 'var(--info-bg)', color: 'var(--focus-ring)' }"
                        >
                          {{ row.totalBarcodes }} barcode{{ row.totalBarcodes > 1 ? 's' : '' }}
                        </span>
                        <span
                          v-else
                          class="inline-block mt-0.5 text-xs px-1.5 py-0.5 rounded-full font-medium"
                          style="font-size:10px;"
                          :style="{ background: 'var(--warning-bg)', color: 'var(--warning-border)' }"
                        >
                          {{ __('No barcodes') }}
                        </span>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="flex items-center gap-1 pl-10">
                      <div class="w-px h-5 mr-1" :style="{ background: 'var(--focus-ring)', opacity: 0.3 }"></div>
                      <span style="font-size:10px;" :style="{ color: 'var(--text-muted)' }">↳</span>
                    </div>
                  </template>
                </td>

                <!-- SKU -->
                <td class="px-3 py-2">
                  <template v-if="row.isFirstRow">
                    <span
                      class="font-mono text-xs px-2 py-1 rounded"
                      :style="{ background: 'var(--item-bg)', color: 'var(--text-sub)', border: '1px solid var(--item-border)' }"
                    >{{ row.sku }}</span>
                  </template>
                </td>

                <!-- Barcode -->
                <td class="px-3 py-2 font-mono" style="font-size:11px;" :style="{ color: 'var(--text-sub)' }">
                  <span v-if="row.hasBarcode">{{ row.barcode.code }}</span>
                  <span v-else :style="{ color: 'var(--text-muted)' }">—</span>
                </td>

                <!-- Type -->
                <td class="px-3 py-2">
                  <span
                    v-if="row.hasBarcode && row.barcode.type"
                    class="inline-block px-2 py-0.5 rounded text-xs font-semibold"
                    :style="{ background: 'var(--info-bg)', color: 'var(--focus-ring)' }"
                  >{{ row.barcode.type }}</span>
                  <span v-else :style="{ color: 'var(--text-muted)' }">—</span>
                </td>

                <!-- UOM -->
                <td class="px-3 py-2 text-xs" :style="{ color: 'var(--text-muted)' }">
                  {{ row.hasBarcode ? (row.barcode.uom || '—') : '—' }}
                </td>

                <!-- Preview -->
                <td class="px-3 py-2">
                  <div
                    v-if="row.hasBarcode && row.barcode.preview"
                    class="flex items-center justify-center rounded p-1 w-24"
                    :style="{ background: 'var(--item-bg)', border: '1px solid var(--item-border)' }"
                  >
                    <img :src="row.barcode.preview" class="max-w-full max-h-10 object-contain" :alt="row.barcode.code" />
                  </div>
                  <span v-else :style="{ color: 'var(--text-muted)' }">—</span>
                </td>

                <!-- Status -->
                <td class="px-3 py-2">
                  <template v-if="row.isFirstRow">
                    <span
                      class="inline-flex items-center px-2 py-0.5 rounded-full font-medium"
                      style="font-size:10px;"
                      :style="row.status === 'active'
                        ? { background: 'var(--icon-bg-green)', color: 'var(--icon-color-green)' }
                        : { background: 'var(--item-bg)', color: 'var(--text-muted)' }"
                    >
                      <span
                        class="w-1.5 h-1.5 rounded-full mr-1 inline-block"
                        :style="{ background: row.status === 'active' ? 'var(--icon-color-green)' : 'var(--text-muted)' }"
                      />
                      {{ capitalizeFirst(row.status) }}
                    </span>
                  </template>
                </td>

                <!-- Actions -->
                <td class="px-3 py-2">
                  <div class="flex items-center gap-1">
                    <template v-if="row.isFirstRow">
                      <button @click="openEditItemModal(row)" title="Edit Item"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        :style="{ color: 'var(--warning-border)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <Edit2 class="w-3.5 h-3.5" />
                      </button>
                      <button @click="deleteItem(row)" title="Delete Item"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        style="color: #ef4444;"
                        @mouseover="$event.currentTarget.style.background = '#fef2f2'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <Trash2 class="w-3.5 h-3.5" />
                      </button>
                      <button @click="openAddBarcodeForItem(row)" title="Add Barcode"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        :style="{ color: 'var(--focus-ring)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--info-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <Plus class="w-3.5 h-3.5" />
                      </button>
                    </template>
                    <template v-if="row.hasBarcode">
                      <button @click="viewBarcode(row.barcode)" :title="__('View')"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        :style="{ color: 'var(--focus-ring)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--info-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <Eye class="w-3.5 h-3.5" />
                      </button>
                      <button @click="downloadBarcode(row.barcode)" :title="__('Download')"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        :style="{ color: 'var(--icon-color-green)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--icon-bg-green)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <Download class="w-3.5 h-3.5" />
                      </button>
                      <button @click="editBarcodeRow(row.barcode)" :title="__('Edit Barcode')"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        :style="{ color: 'var(--warning-border)' }"
                        @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <Settings2 class="w-3.5 h-3.5" />
                      </button>
                      <button @click="deleteBarcodeRow(row.barcode)" :title="__('Delete Barcode')"
                        class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                        style="color: #ef4444;"
                        @mouseover="$event.currentTarget.style.background = '#fef2f2'"
                        @mouseleave="$event.currentTarget.style.background = 'transparent'"
                      >
                        <X class="w-3.5 h-3.5" />
                      </button>
                    </template>
                  </div>
                </td>

              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        v-if="totalPages > 1"
        class="px-4 py-2.5"
        :style="{ borderTop: '1px solid var(--card-border)', background: 'var(--item-bg)' }"
      >
        <div class="flex items-center justify-between">
          <span class="text-xs" :style="{ color: 'var(--text-muted)' }">
            {{ __('Showing') }}
            {{ ((currentPage - 1) * itemsPerPage) + 1 }}–{{ Math.min(currentPage * itemsPerPage, filteredRows.length) }}
            {{ __('of') }}
            {{ filteredRows.length }}
          </span>
          <div class="flex items-center gap-1">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
              :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
            >{{__('Prev')}}</button>

            <button
              v-for="page in visiblePages"
              :key="page"
              @click="currentPage = page"
              class="px-2 py-1 text-xs rounded transition-colors font-medium"
              :style="currentPage === page
                ? { background: 'var(--focus-ring)', color: '#fff', border: '1px solid var(--focus-ring)' }
                : { background: 'var(--card-bg)', color: 'var(--text-sub)', border: '1px solid var(--card-border)' }"
            >{{ page }}</button>

            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
              :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
            >{{__('Next')}}</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, toRaw } from 'vue'
import { BarChart2, Search, PackageSearch, Edit2, Trash2, Plus, Eye, Download, Settings2, X } from 'lucide-vue-next'
import { useToast }             from 'vue-toastification'
import LoadingSpinner from '@/components/icons/LoadingSpinner.vue'
import { getBarcodesFromFrappeDB } from '@/composables/barcode'
// ─── Props ───────────────────────────────────────────────
const props = defineProps({
  products:     { type: Array,   default: () => [] },
  barcodeTypes: { type: Array, default: () => [] },
  uoms:         { type: Array, default: () => [] },
})

// ─── Emits ───────────────────────────────────────────────
const emit = defineEmits([
  'edit-item',         // openEditItemModal
  'delete-item',       // deleteItem
  'add-barcode',       // openAddBarcodeForItem
  'view-barcode',      // viewBarcode
  'download-barcode',  // downloadBarcode
  'edit-barcode',      // editBarcodeRow
  'delete-barcode',    // deleteBarcodeRow
  'refresh',
])

// ─── State ───────────────────────────────────────────────
const toast          = useToast()
const isLoading      = ref(false)
const allProducts    = ref([])
const itemGroups     = ref([])

const searchQuery    = ref('')
const filterProduct  = ref('')
const filterStatus   = ref('')
const filterType     = ref('')
const filterGroup    = ref('')

const currentPage    = ref(1)
const itemsPerPage   = ref(20)

// ─── Helpers ─────────────────────────────────────────────
const capitalizeFirst = (str) => str ? str.charAt(0).toUpperCase() + str.slice(1) : ''

const clearFilters = () => {
  searchQuery.value   = ''
  filterProduct.value = ''
  filterStatus.value  = ''
  filterType.value    = ''
  filterGroup.value   = ''
  currentPage.value   = 1
}

// ─── Flat rows ───────────────────────────────────────────
const flatRows = computed(() => {
  const rows = []
  allProducts.value.forEach(product => {
    const barcodes = product.barcodes || []
    if (barcodes.length === 0) {
      rows.push({
        rowKey: `${product.item_code}__none`,
        isFirstRow: true, isLastRow: true,
        sku: product.item_code, productName: product.item_name,
        image: product.image || '', item_group: product.item_group || '',
        status: product?.disabled === 1 ? 'inactive' : 'active',
        totalBarcodes: 0, hasBarcode: false, barcode: null,
        item_code: product.item_code, item_name: product.item_name,
        disabled: product.disabled, _raw: product,
      })
    } else {
      barcodes.forEach((bc, idx) => {
        rows.push({
          rowKey: `${product.item_code}__${bc.barcode || idx}`,
          isFirstRow: idx === 0, isLastRow: idx === barcodes.length - 1,
          sku: product.item_code, productName: product.item_name,
          image: product.image || '', item_group: product.item_group || '',
          status: product?.disabled === 1 ? 'inactive' : 'active',
          totalBarcodes: barcodes.length, hasBarcode: true,
          barcode: {
            id:          `${product.item_code}_${bc.barcode || idx}`,
            code:        bc.barcode      || '',
            type:        bc.barcode_type || '',
            uom:         bc.uom          || '',
            preview:     bc.preview      || '',
            sku:         product.item_code,
            productName: product.item_name,
            image:       product.image || '',
          },
          item_code: product.item_code, item_name: product.item_name,
          disabled: product.disabled, _raw: product,
        })
      })
    }
  })
  return rows
})

const filteredRows = computed(() => {
  const q      = searchQuery.value.toLowerCase().trim()
  const fProd  = filterProduct.value
  const fStat  = filterStatus.value
  const fType  = filterType.value
  const fGroup = filterGroup.value

  const matchingProducts = new Set(
    allProducts.value
      .filter(p => {
        const matchSearch  = !q      || p.item_code?.toLowerCase().includes(q) || p.item_name?.toLowerCase().includes(q)
        const matchProduct = !fProd  || p.item_code === fProd
        const matchStatus  = !fStat  || (fStat === 'active' ? p.disabled !== 1 : p.disabled === 1)
        const matchGroup   = !fGroup || p.item_group === fGroup
        return matchSearch && matchProduct && matchStatus && matchGroup
      })
      .map(p => p.item_code)
  )

  return flatRows.value.filter(row => {
    if (!matchingProducts.has(row.sku)) return false
    if (fType && row.hasBarcode  && row.barcode.type !== fType) return false
    if (fType && !row.hasBarcode) return false
    return true
  })
})

// ─── Pagination ──────────────────────────────────────────
const totalPages = computed(() => Math.ceil(filteredRows.value.length / itemsPerPage.value))

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredRows.value.slice(start, start + itemsPerPage.value)
})

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end   = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// ─── Actions (emit للـ parent) ───────────────────────────
const openEditItemModal    = (row)     => emit('edit-item',        row)
const deleteItem           = (row)     => emit('delete-item',      row)
const openAddBarcodeForItem= (row)     => emit('add-barcode',      row)
const viewBarcode          = (barcode) => emit('view-barcode',     barcode)
const downloadBarcode      = (barcode) => emit('download-barcode', barcode)
const editBarcodeRow       = (barcode) => emit('edit-barcode',     barcode)
const deleteBarcodeRow     = (barcode) => emit('delete-barcode',   barcode)

// ─── Load data ───────────────────────────────────────────
onMounted(async () => {
  isLoading.value = true
  try {
  console.log("Products for barcode fetching", props.products)
    console.log("Products for barcode fetching", props.products)
    const bRes = await getBarcodesFromFrappeDB(toRaw(props.products))
    if (!bRes || bRes.status !== 'success') {
      toast.error('Failed to load barcode data')
      return
    }
    console.log("Barcode response", bRes)
    const bcProducts = bRes.data || []
    console.log("bcProducts",bcProducts)

    const bcMap = {}
    bcProducts.forEach(p => {
      bcMap[p.sku] = p
    })

    console.log("bcMap",bcMap)
    allProducts.value = props.products.map(item => {
      const bcData = bcMap[item.item_code] || {}

      return {
        ...item,
        barcodes: bcData.barcodes || []
      }
    })

    const groups = [...new Set(allProducts.value.map(p => p.item_group).filter(Boolean))]
    itemGroups.value = groups.map(name => ({ name }))

  } finally {
    isLoading.value = false
  }
})
</script>
