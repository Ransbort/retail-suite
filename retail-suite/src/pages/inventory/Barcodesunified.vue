<!-- BarcodesUnified.vue -->
<template>

    <div class="w-full flex min-h-screen" style="font-size: 13px;" :style="{ background: 'var(--item-bg)' }">
      <main class="flex flex-col flex-1 min-h-screen">

        <!-- ══════════════════ HEADER ══════════════════ -->
        <header
          class="mx-3 mt-3 sticky top-0 z-10 rounded-lg shadow-sm"
          :style="{
            background: 'var(--card-bg)',
            border: '1px solid var(--card-border)'
          }"
        >
          <div class="px-4 py-2 flex justify-between items-center">
            <div class="flex items-center gap-2">
              <button
                @click="goBack"
                class="p-1.5 rounded-md transition-colors"
                :style="{ color: 'var(--text-muted)' }"
                @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
                @mouseleave="$event.currentTarget.style.background = 'transparent'"
              >
                <ArrowLeft class="w-4 h-4" />
              </button>
              <div>
                <h1 class="text-sm font-bold" :style="{ color: 'var(--text-main)' }">Items & Barcodes Management</h1>
                <p class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ allProducts.length }} registered products</p>
              </div>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button @click="showBarcodeScanner = true"
                class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                style="background: #16a34a;"
                @mouseover="$event.currentTarget.style.background = '#15803d'"
                @mouseleave="$event.currentTarget.style.background = '#16a34a'"
              >
                <ScanLine class="w-3 h-3" /> Scan Barcode
              </button>
              <button @click="openGenerateModal"
                class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                style="background: #9333ea;"
                @mouseover="$event.currentTarget.style.background = '#7e22ce'"
                @mouseleave="$event.currentTarget.style.background = '#9333ea'"
              >
                <BarChart2 class="w-3 h-3" /> Generate Barcode
              </button>
              <button @click="openAddItemModal"
                class="inline-flex items-center gap-1.5 text-white px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                :style="{ background: 'var(--focus-ring)' }"
              >
                <Plus class="w-3 h-3" /> Add Item
              </button>
            </div>
          </div>
        </header>

        <!-- ══════════════════ STATISTICS ══════════════════ -->
        <section class="px-3 pt-3">
          <div
            class="rounded-lg shadow-sm p-3"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <h2 class="text-xs font-semibold uppercase tracking-wide mb-2" :style="{ color: 'var(--text-muted)' }">
              Statistics
            </h2>
            <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
              <StatsCard title="Total Products"  :value="allProducts.length"                           icon="Package"    color="blue"   />
              <StatsCard title="With Barcodes"   :value="productsWithBarcodes"                         icon="BarChart2"  color="green"  />
              <StatsCard title="Total Barcodes"  :value="flatRows.length"                              icon="TrendingUp" color="purple" />
              <StatsCard title="No Barcode"      :value="allProducts.length - productsWithBarcodes"    icon="AlertCircle" color="orange" />
            </div>
          </div>
        </section>

        <!-- ══════════════════ TABS ══════════════════ -->
        <section class="px-3 pt-3">
          <div
            class="rounded-lg shadow-sm"
            :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
          >
            <div class="px-4 flex gap-1" :style="{ borderBottom: '1px solid var(--card-border)' }">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                @click="activeTab = tab.key"
                class="px-4 py-2.5 text-xs font-medium transition-all duration-200 -mb-px border-b-2"
                :style="activeTab === tab.key
                  ? { color: 'var(--focus-ring)', borderColor: 'var(--focus-ring)' }
                  : { color: 'var(--text-muted)', borderColor: 'transparent' }"
                @mouseover="activeTab !== tab.key && ($event.currentTarget.style.color = 'var(--text-sub)')"
                @mouseleave="activeTab !== tab.key && ($event.currentTarget.style.color = 'var(--text-muted)')"
              >
                {{ tab.label }}
              </button>
            </div>
          </div>
        </section>

        <!-- ══════════════════ TAB CONTENT ══════════════════ -->
        <section class="px-3 pt-3 pb-3">

          <!-- ─────────── LIST TAB ─────────── -->
          <div v-if="activeTab === 'list'" class="space-y-3">

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
                      placeholder="SKU / barcode / item name..."
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
                    <option value="">All Products</option>
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
                    <option value="">All</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                  </select>
                </div>

                <!-- Count -->
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Count</label>
                  <div
                    class="px-2 py-1.5 rounded-md font-semibold text-xs"
                    :style="{
                      background: 'var(--item-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--item-border)'
                    }"
                  >
                    {{ filteredRows.length }} rows
                  </div>
                </div>

              </div>

              <div class="grid grid-cols-2 md:grid-cols-3 gap-2">

                <!-- Barcode Type -->
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Barcode Type</label>
                  <select
                    v-model="filterType"
                    class="w-full px-2 py-1.5 rounded-md focus:outline-none text-xs"
                    :style="{
                      background: 'var(--input-bg)',
                      color: 'var(--text-main)',
                      border: '1px solid var(--input-border)'
                    }"
                  >
                    <option value="">All Types</option>
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
                    <option value="">All Groups</option>
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
                    Clear Filters
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
                <span class="text-xs font-semibold" :style="{ color: 'var(--text-sub)' }">Items & Barcodes</span>
                <span class="text-xs" :style="{ color: 'var(--text-muted)' }">({{ filteredRows.length }})</span>
                <span v-if="isLoading" class="text-xs ml-auto" :style="{ color: 'var(--text-muted)' }">Loading...</span>
              </div>

              <!-- Table -->
              <div class="overflow-x-auto" style="scrollbar-width: thin;">
                <table class="w-full border-collapse" style="font-size: 12px; min-width: 750px;">
                  <thead class="sticky top-0 z-10" :style="{ background: 'var(--item-bg)' }">
                    <tr>
                      <th v-for="label in ['Product', 'SKU', 'Barcode', 'Type', 'UOM', 'Preview', 'Status', 'Actions']"
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
                          <p class="text-xs font-medium" :style="{ color: 'var(--text-sub)' }">No Items Found</p>
                          <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Try adjusting your filters</p>
                        </div>
                      </td>
                    </tr>

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
                                @error="handleImageError"
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
                                  No barcodes
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
                              <button @click="viewBarcode(row.barcode)" title="View"
                                class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                                :style="{ color: 'var(--focus-ring)' }"
                                @mouseover="$event.currentTarget.style.background = 'var(--info-bg)'"
                                @mouseleave="$event.currentTarget.style.background = 'transparent'"
                              >
                                <Eye class="w-3.5 h-3.5" />
                              </button>
                              <button @click="downloadBarcode(row.barcode)" title="Download"
                                class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                                :style="{ color: 'var(--icon-color-green)' }"
                                @mouseover="$event.currentTarget.style.background = 'var(--icon-bg-green)'"
                                @mouseleave="$event.currentTarget.style.background = 'transparent'"
                              >
                                <Download class="w-3.5 h-3.5" />
                              </button>
                              <button @click="editBarcodeRow(row.barcode)" title="Edit Barcode"
                                class="w-6 h-6 flex items-center justify-center rounded transition-colors"
                                :style="{ color: 'var(--warning-border)' }"
                                @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
                                @mouseleave="$event.currentTarget.style.background = 'transparent'"
                              >
                                <Settings2 class="w-3.5 h-3.5" />
                              </button>
                              <button @click="deleteBarcodeRow(row.barcode)" title="Delete Barcode"
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
                    Showing {{ ((currentPage - 1) * itemsPerPage) + 1 }}–{{ Math.min(currentPage * itemsPerPage, filteredRows.length) }}
                    of {{ filteredRows.length }}
                  </span>
                  <div class="flex items-center gap-1">
                    <button
                      @click="currentPage = Math.max(1, currentPage - 1)"
                      :disabled="currentPage === 1"
                      class="px-2 py-1 text-xs rounded disabled:opacity-40 transition-colors"
                      :style="{ border: '1px solid var(--card-border)', color: 'var(--text-sub)', background: 'var(--card-bg)' }"
                    >Prev</button>

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
                    >Next</button>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- ─────────── GENERATE TAB ─────────── -->
          <div v-if="activeTab === 'generate'">
            <div
              class="rounded-lg shadow-sm p-5"
              :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
            >
              <h3 class="text-sm font-semibold mb-4" :style="{ color: 'var(--text-main)' }">Generate Barcode</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-3">

                  <div>
                    <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Product *</label>
                    <select v-model="generateForm.item_code"
                      class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                      :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                      <option value="">Select Product</option>
                      <option v-for="p in allProducts" :key="p.item_code" :value="p.item_code">{{ p.item_name }} ({{ p.item_code }})</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Barcode Type *</label>
                    <select v-model="generateForm.type"
                      class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                      :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                      <option value="">Select Type</option>
                      <option v-for="t in barcodeTypes" :key="t" :value="t">{{ t }}</option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Barcode Value</label>
                    <div class="flex gap-2">
                      <input v-model="generateForm.value" type="text" placeholder="Auto-generate if empty"
                        class="flex-1 px-3 py-1.5 rounded-md text-xs focus:outline-none"
                        :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }" />
                      <button @click="autoGenerateValue"
                        class="px-3 py-1.5 text-white rounded-md text-xs transition-colors"
                        :style="{ background: 'var(--focus-ring)' }">
                        <RefreshCcw class="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div>
                    <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Unit of Measure</label>
                    <select v-model="generateForm.posa_uom"
                      class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
                      :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                      <option value="">Select UOM</option>
                      <option v-for="u in uoms" :key="u.name" :value="u.name">{{ u.name }}</option>
                    </select>
                  </div>

                  <button @click="runGenerateBarcode"
                    class="w-full py-2 text-white rounded-md text-xs font-medium transition-colors"
                    :style="{ background: 'var(--focus-ring)' }">
                    Generate & Save
                  </button>
                </div>

                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Preview</label>
                  <div
                    class="rounded-lg min-h-48 flex items-center justify-center"
                    :style="{ background: 'var(--item-bg)', border: '1px dashed var(--card-border)' }"
                  >
                    <div v-if="generatedPreview" class="text-center p-4">
                      <img :src="generatedPreview" class="max-w-full mb-2" />
                      <p class="text-xs font-mono" :style="{ color: 'var(--text-muted)' }">{{ generateForm.value }}</p>
                    </div>
                    <p v-else class="text-xs" :style="{ color: 'var(--text-muted)' }">Select product & type to preview</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ─────────── PRINT TAB ─────────── -->
          <div v-if="activeTab === 'print'">
            <div
              class="rounded-lg shadow-sm p-5"
              :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
            >
              <h3 class="text-sm font-semibold mb-4" :style="{ color: 'var(--text-main)' }">Print Barcode Labels</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="flex flex-col gap-3">

                  <div class="flex gap-2">
                    <div class="relative flex-1">
                      <Search class="absolute left-2.5 top-2 w-3 h-3 pointer-events-none" :style="{ color: 'var(--text-muted)' }" />
                      <input v-model="printSearch" type="text" placeholder="Search SKU or barcode..."
                        class="w-full pl-8 pr-3 py-1.5 text-xs rounded-md focus:outline-none"
                        :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }" />
                    </div>
                    <select v-model="printFilterType"
                      class="px-2 py-1.5 text-xs rounded-md focus:outline-none"
                      :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                      <option value="">All Types</option>
                      <option v-for="t in barcodeTypes" :key="t" :value="t">{{ t }}</option>
                    </select>
                  </div>

                  <div class="flex justify-between items-center">
                    <span class="text-xs" :style="{ color: 'var(--text-muted)' }">{{ filteredPrintBarcodes.length }} barcode(s)</span>
                    <div class="flex gap-3">
                      <button @click="selectAllPrint" class="text-xs font-medium" :style="{ color: 'var(--focus-ring)' }">Select All</button>
                      <span :style="{ color: 'var(--card-border)' }">|</span>
                      <button @click="printForm.selectedBarcodes = []" class="text-xs" style="color: #ef4444;">Clear</button>
                    </div>
                  </div>

                  <div
                    class="rounded-lg overflow-y-auto max-h-64 divide-y"
                    :style="{ border: '1px solid var(--card-border)', divideColor: 'var(--card-border)' }"
                  >
                    <div v-if="filteredPrintBarcodes.length === 0" class="py-8 text-center text-xs" :style="{ color: 'var(--text-muted)' }">
                      No barcodes match your search
                    </div>
                    <label
                      v-for="bc in filteredPrintBarcodes"
                      :key="bc.rowKey"
                      class="flex items-center gap-3 px-3 py-2 cursor-pointer transition-colors"
                      :style="{
                        background: printForm.selectedBarcodes.includes(bc.rowKey) ? 'var(--info-bg)' : 'transparent',
                        borderBottom: '1px solid var(--card-border)'
                      }"
                      @mouseover="!printForm.selectedBarcodes.includes(bc.rowKey) && ($event.currentTarget.style.background = 'var(--nav-item-hover-bg)')"
                      @mouseleave="$event.currentTarget.style.background = printForm.selectedBarcodes.includes(bc.rowKey) ? 'var(--info-bg)' : 'transparent'"
                    >
                      <input type="checkbox" :value="bc.rowKey" v-model="printForm.selectedBarcodes"
                        class="rounded" :style="{ accentColor: 'var(--focus-ring)' }" />
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2">
                          <span class="text-xs font-medium truncate" :style="{ color: 'var(--text-main)' }">{{ bc.sku }}</span>
                          <span v-if="bc.barcode.type"
                            class="text-xs px-1.5 py-0.5 rounded font-medium"
                            :style="{ background: 'var(--info-bg)', color: 'var(--focus-ring)' }">
                            {{ bc.barcode.type }}
                          </span>
                        </div>
                        <span class="text-xs font-mono" :style="{ color: 'var(--text-muted)' }">{{ bc.barcode.code }}</span>
                      </div>
                      <img v-if="bc.barcode.preview" :src="bc.barcode.preview" class="w-14 h-7 object-contain" />
                    </label>
                  </div>

                  <span class="text-xs" :style="{ color: 'var(--text-muted)' }">
                    {{ printForm.selectedBarcodes.length }} selected
                    <template v-if="printForm.selectedBarcodes.length">
                      × {{ printForm.copies }} = <strong :style="{ color: 'var(--text-sub)' }">{{ printForm.selectedBarcodes.length * printForm.copies }} labels</strong>
                    </template>
                  </span>
                </div>

                <div class="flex flex-col gap-3">
                  <div>
                    <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Label Size</label>
                    <select v-model="printForm.labelSize"
                      class="w-full px-3 py-1.5 text-xs rounded-md focus:outline-none"
                      :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                      <option value="4x6">4×6 in (Standard)</option>
                      <option value="3x5">3×5 in (Small)</option>
                      <option value="2x2">2×2 in (Mini)</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Copies per Label</label>
                    <input
                      :value="printForm.copies"
                      @input="printForm.copies = Math.max(1, Math.min(20, parseInt($event.target.value) || 1))"
                      type="number" min="1" max="20"
                      class="w-full px-3 py-1.5 text-xs rounded-md focus:outline-none"
                      :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }"
                    />
                  </div>
                  <label class="flex items-center gap-2 cursor-pointer">
                    <input v-model="printForm.includePrice" type="checkbox" :style="{ accentColor: 'var(--focus-ring)' }" />
                    <span class="text-xs" :style="{ color: 'var(--text-sub)' }">Show price on label</span>
                  </label>

                  <!-- Print Summary -->
                  <div
                    v-if="printForm.selectedBarcodes.length"
                    class="rounded-md p-3 text-xs"
                    :style="{ background: 'var(--icon-bg-green)', border: '1px solid var(--icon-color-green)', color: 'var(--icon-color-green)' }"
                  >
                    <div class="font-semibold mb-1">Print Summary</div>
                    <div class="space-y-0.5" style="opacity: 0.85;">
                      <div>Selected: <strong>{{ printForm.selectedBarcodes.length }}</strong></div>
                      <div>Copies: <strong>{{ printForm.copies }}</strong></div>
                      <div>Size: <strong>{{ printForm.labelSize }}</strong></div>
                      <div class="pt-1 font-bold" :style="{ borderTop: '1px solid var(--icon-color-green)' }">
                        Total: {{ printForm.selectedBarcodes.length * printForm.copies }} labels
                      </div>
                    </div>
                  </div>

                  <button
                    @click="printLabels"
                    :disabled="!printForm.selectedBarcodes.length"
                    class="mt-auto w-full py-2 text-white rounded-md text-xs font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    :style="{ background: 'var(--icon-color-green)' }"
                  >
                    <Printer class="w-3.5 h-3.5" />
                    Print Labels
                    <span v-if="printForm.selectedBarcodes.length" class="text-xs opacity-75">
                      ({{ printForm.selectedBarcodes.length * printForm.copies }})
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- ─────────── SETTINGS TAB ─────────── -->
          <div v-if="activeTab === 'settings'">
            <div
              class="rounded-lg shadow-sm p-5"
              :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
            >
              <h3 class="text-sm font-semibold mb-4" :style="{ color: 'var(--text-main)' }">Barcode Settings</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Default Barcode Type</label>
                  <select v-model="settings.defaultType"
                    class="w-full px-3 py-1.5 text-xs rounded-md focus:outline-none"
                    :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                    <option value="">Select</option>
                    <option v-for="t in barcodeTypes" :key="t" :value="t">{{ t }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">SKU Prefix</label>
                  <input v-model="settings.skuPrefix" type="text" placeholder="e.g., PRD"
                    class="w-full px-3 py-1.5 text-xs rounded-md focus:outline-none"
                    :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }" />
                </div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input v-model="settings.autoGenerateSku" type="checkbox" :style="{ accentColor: 'var(--focus-ring)' }" />
                  <span class="text-xs" :style="{ color: 'var(--text-sub)' }">Auto-generate SKU for new products</span>
                </label>
                <div>
                  <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Default Label Size</label>
                  <select v-model="settings.defaultLabelSize"
                    class="w-full px-3 py-1.5 text-xs rounded-md focus:outline-none"
                    :style="{ background: 'var(--input-bg)', color: 'var(--text-main)', border: '1px solid var(--input-border)' }">
                    <option value="4x6">4×6</option>
                    <option value="3x5">3×5</option>
                    <option value="2x2">2×2</option>
                  </select>
                </div>
              </div>
              <button
                @click="saveSettings"
                class="mt-4 px-5 py-1.5 text-white rounded-md text-xs font-medium transition-colors"
                :style="{ background: 'var(--focus-ring)' }"
              >
                Save Settings
              </button>
            </div>
          </div>

        </section>

        <!-- ══════════════════ MODALS ══════════════════ -->
        <BarcodeScanner
          v-if="showBarcodeScanner"
          :products="allProducts"
          :barcodeTypes="barcodeTypes"
          :uoms="uoms"
          @scan="handleBarcodeScan"
          @assign="handleAssignBarcode"
          @close="showBarcodeScanner = false"
        />
        <GenerateBarcodeModal
          v-if="showGenerateModal"
          :products="allProducts"
          :barcodeTypes="barcodeTypes"
          :uoms="uoms"
          @generate="handleGenerateBarcode"
          @close="showGenerateModal = false"
          @refreshBarcodes="loadData"
        />
        <ViewBarcodeModal
          v-if="showViewModal"
          :barcode="selectedBarcode"
          @close="showViewModal = false"
        />
        <EditBarcodeModal
          v-if="showEditModal && barcodeToEdit"
          :barcode="barcodeToEdit"
          :barcodeTypes="barcodeTypes"
          :uoms="uoms"
          :is-submitting="editIsSubmitting"
          :is-generating="editIsGenerating"
          :external-error="editExternalError"
          :generated-value="editGeneratedValue"
          :generated-preview="editGeneratedPreview"
          @update="handleUpdateBarcode"
          @autoGenerate="handleEditAutoGenerate"
          @close="closeEditModal"
        />
        <ItemModal
          v-if="showItemModal"
          :show="showItemModal"
          :item="editingItem"
          :uoms="uoms"
          :series="series"
          :categories="categories"
          :is-editing="!!editingItem"
          @save="saveItem"
          @close="closeItemModal"
        />
        <GenerateBarcodeModal
          v-if="showAddBarcodeModal && addBarcodeForItem"
          :products="allProducts"
          :barcodeTypes="barcodeTypes"
          :uoms="uoms"
          :preselectedItem="addBarcodeForItem.item_code"
          @generate="handleGenerateBarcode"
          @close="showAddBarcodeModal = false"
          @refreshBarcodes="loadData"
        />

      </main>
    </div>

</template>

<script setup>
import { ref, reactive, computed, onMounted, toRaw, shallowRef, watch } from 'vue'
import {
  Download, Eye, Edit2, Trash2, RefreshCcw, Plus,
  Search, Printer, Settings2, X, ScanLine, BarChart2, PackageSearch, ArrowLeft, XCircle
} from 'lucide-vue-next'
import MainLayout           from '@/layout/MainLayout.vue'
import BarcodeScanner       from '@/components/modals/BarcodeScanner.vue'
import GenerateBarcodeModal from '@/components/modals/GenerateBarcodeModal.vue'
import ViewBarcodeModal     from '@/components/modals/ViewBarcodeModal.vue'
import EditBarcodeModal     from '@/components/modals/EditBarcodeModal.vue'
import ItemModal            from '@/components/modals/ItemModal.vue'
import LoadingSpinner       from '@/components/icons/LoadingSpinner.vue'
import StatsCard            from '@/layout/StatsCard.vue'
import { useRouter }           from 'vue-router'
import { useShiftStore }       from '@/stores/shift'
import { useCartStore }        from '@/stores/cart'
import { useInventoryStore }   from '@/stores/inventory'
import { useToast }            from 'vue-toastification'
import {getItemGroup} from '@/composables/pos'
import {
  generateBarcodePreview,
  generateBarcodeValue,
  addItemBarcode,
  updateItemBarcode,
  getBarcodesFromFrappeDB,
  getBarcodeTypes,
  handleDeleteBarcodeFrappe
} from '@/composables/barcode'
import { useConfirm } from '@/composables/useConfirm'
import { storeToRefs } from 'pinia'
// ────────────────────────────────────────────
// STORES & HELPERS
// ────────────────────────────────────────────
const router         = useRouter()
const toast          = useToast()
const shiftStore     = useShiftStore()
const inventoryStore = useInventoryStore()
const cartStore      = useCartStore()
const { confirm } = useConfirm()
const handleImageError = (e) => { e.target.src = 'https://via.placeholder.com/40?text=?' }


const { isShiftOpen } = storeToRefs(shiftStore)

// ────────────────────────────────────────────
// TABS
// ────────────────────────────────────────────
const tabs = [
  { key: 'list',     label: 'Items & Barcodes' },
  { key: 'generate', label: 'Generate Barcodes' },
  { key: 'print',    label: 'Print Labels' },
  { key: 'settings', label: 'Settings' },
]
const activeTab = ref('list')

// ────────────────────────────────────────────
// GLOBAL DATA
// ────────────────────────────────────────────
const isLoading    = ref(false)
const allProducts  = ref([])
const barcodeTypes = ref([])
const itemGroups   = ref([])
const uoms         = ref([])
const series       = ref([])
const categories   = ref([])

// ────────────────────────────────────────────
// FILTERS
// ────────────────────────────────────────────
const searchQuery   = ref('')
const filterProduct = ref('')
const filterStatus  = ref('')
const filterType    = ref('')
const filterGroup   = ref('')

// ────────────────────────────────────────────
// PAGINATION
// ────────────────────────────────────────────
const currentPage = ref(1)
const itemsPerPage = ref(20)

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  return filteredRows.value.slice(start, start + itemsPerPage.value)
})

const totalPages = computed(() => Math.ceil(filteredRows.value.length / itemsPerPage.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end   = Math.min(totalPages.value, start + maxVisible - 1)
  if (end - start < maxVisible - 1) start = Math.max(1, end - maxVisible + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

// Reset page on filter change
const resetPage = () => { currentPage.value = 1 }

// ────────────────────────────────────────────
// FLAT ROWS
// ────────────────────────────────────────────
const flatRows = computed(() => {
  const rows = []
  allProducts.value.forEach(product => {
    const barcodes = product.barcodes || []
    if (barcodes.length === 0) {
      rows.push({
        rowKey:        `${product.item_code}__none`,
        isFirstRow:    true,
        isLastRow:     true,
        sku:           product.item_code,
        productName:   product.item_name,
        image:  product.image       || '',
        item_group:    product.item_group  || '',
        status:        product?.disabled === 1 ? 'inactive' : 'active',
        totalBarcodes: 0,
        hasBarcode:    false,
        barcode:       null,
        item_code:     product.item_code,
        item_name:     product.item_name,
        disabled:      product.disabled,
        _raw:          product,
      })
    } else {
      barcodes.forEach((bc, idx) => {
        rows.push({
          rowKey:        `${product.item_code}__${bc.barcode || idx}`,
          isFirstRow:    idx === 0,
          isLastRow:     idx === barcodes.length - 1,
          sku:           product.item_code,
          productName:   product.item_name,
          image:  product.image      || '',
          item_group:    product.item_group || '',
          status:        product?.disabled === 1 ? 'inactive' : 'active',
          totalBarcodes: barcodes.length,
          hasBarcode:    true,
          barcode: {
            id:           `${product.item_code}_${bc.barcode || idx}`,
            code:         bc.barcode      || '',
            type:         bc.barcode_type || '',
            uom:          bc.uom          || '',
            preview:      bc.preview      || '',
            sku:          product.item_code,
            productName:  product.item_name,
            image: product.image || '',
          },
          item_code:  product.item_code,
          item_name:  product.item_name,
          disabled:   product.disabled,
          _raw:       product,
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
    if (fType && row.hasBarcode && row.barcode.type !== fType) return false
    if (fType && !row.hasBarcode) return false
    return true
  })
})

const productsWithBarcodes = computed(() =>
  allProducts.value.filter(p => p.barcodes && p.barcodes.length > 0).length
)

// ────────────────────────────────────────────
// DATA LOADING
// ────────────────────────────────────────────
const loadData = async () => {
  try {
    isLoading.value = true
    const bRes = await getBarcodesFromFrappeDB()
    if (!bRes || bRes.status !== 'success') { toast.error('Failed to load barcode data'); return }

    const bcProducts = bRes.data || []
    // await inventoryStore.loadItems()
    const storeItems = JSON.parse(JSON.stringify(toRaw(inventoryStore.items))) || []
    console.log("storeItems[0]",storeItems[0])

    const bcMap = {}
    bcProducts.forEach(p => { bcMap[p.sku] = p })

    allProducts.value = storeItems.map(item => {
      const bcData = bcMap[item.item_code] || {}
      return {
        ...toRaw(item),
        barcodes:   (bcData.barcodes || []).map(bc => ({ ...bc, preview: bc.preview || '' })),
      }
    })
  } catch (err) {
    console.error('loadData error:', err)
    toast.error('Error loading data')
  } finally {
    isLoading.value = false
  }
}

// ────────────────────────────────────────────
// ITEM MODAL
// ────────────────────────────────────────────
const showItemModal = ref(false)
const editingItem   = shallowRef(null)

const openAddItemModal   = () => { editingItem.value = null; showItemModal.value = true }
const openEditItemModal = (row) => {
  editingItem.value = JSON.parse(JSON.stringify(toRaw(row)))
  console.log('editingItem set:', editingItem.value)
  showItemModal.value = true
}

const closeItemModal     = () => { showItemModal.value = false; editingItem.value = null }

const saveItem = async (itemData) => {
  try {
    if (editingItem.value) {
      await inventoryStore.updateItem(editingItem.value.name || editingItem.value.item_code, itemData)
      toast.success('Item updated')
    } else {
      const res = await inventoryStore.addItem(itemData)
      if (res?.status === 'error') return toast.warning(res.message || 'Failed')
      toast.success(res?.message || 'Item added')
    }
    closeItemModal()
    await loadData()
  } catch (e) { console.error(e); toast.error('Error saving item') }
}

const deleteItem = async (row) => {
  const confirmed = await confirm({
    type: 'delete',
    title: 'Delete Item',
    message: `Delete item "${row.productName}"?\nThis will also remove all its barcodes.`,
    confirmLabel: 'Delete',
  })
  if (!confirmed) return
  try {
    const res = await inventoryStore.deleteItem(row.item_code)
    if (res?.status === '200' || res?.data?.status === '200 ') {
      toast.success(`"${row.productName}" deleted`)
      await loadData()
    } else {
      toast.warning(res?.message || 'Failed to delete')
    }
  } catch (e) { console.error(e); toast.error('Error deleting item') }
}

// ────────────────────────────────────────────
// ADD BARCODE FOR ITEM
// ────────────────────────────────────────────
const showAddBarcodeModal = ref(false)
const addBarcodeForItem   = ref(null)

const openAddBarcodeForItem = (row) => {
  addBarcodeForItem.value = { item_code: row.item_code, item_name: row.productName }
  showAddBarcodeModal.value = true
}

// ────────────────────────────────────────────
// BARCODE EDIT / VIEW MODAL
// ────────────────────────────────────────────
const showEditModal        = ref(false)
const barcodeToEdit        = ref(null)
const editIsSubmitting     = ref(false)
const editIsGenerating     = ref(false)
const editExternalError    = ref('')
const editGeneratedValue   = ref('')
const editGeneratedPreview = ref('')
const showViewModal        = ref(false)
const selectedBarcode      = ref(null)

const viewBarcode     = (bc) => { selectedBarcode.value = bc; showViewModal.value = true }
const downloadBarcode = (bc) => {
  if (!bc.preview) return toast.warning('No preview available')
  const a = document.createElement('a'); a.href = bc.preview; a.download = `${bc.code}.png`; a.click()
}
const editBarcodeRow  = (bc) => {
  barcodeToEdit.value = bc; editExternalError.value = ''; editGeneratedValue.value = ''; editGeneratedPreview.value = ''; showEditModal.value = true
}
const closeEditModal  = () => {
  if (editIsSubmitting.value || editIsGenerating.value) return
  showEditModal.value = false; barcodeToEdit.value = null
  editExternalError.value = ''; editGeneratedValue.value = ''; editGeneratedPreview.value = ''
}

const handleEditAutoGenerate = async ({ type }) => {
  if (!type) return toast.warning('Select a barcode type first')
  editIsGenerating.value = true; editGeneratedValue.value = ''; editGeneratedPreview.value = ''
  try {
    const vRes = await generateBarcodeValue(type)
    if (vRes.status !== 'success' || !vRes.value) return toast.error(`Failed to generate value for "${type}"`)
    editGeneratedValue.value = vRes.value
    const preview = await generateBarcodePreview({ value: vRes.value, type })
    if (preview) editGeneratedPreview.value = preview
  } catch (e) { console.error(e); toast.error('Failed to auto-generate barcode') }
  finally { editIsGenerating.value = false }
}

const handleUpdateBarcode = async ({ id, sku, old_barcode, barcode, barcode_type, uom }) => {
  editIsSubmitting.value = true; editExternalError.value = ''
  const res = await updateItemBarcode(sku, old_barcode, { barcode, barcode_type, uom })
  editIsSubmitting.value = false
  if (res.status === 'success') {
    toast.success('Barcode updated'); showEditModal.value = false; barcodeToEdit.value = null
    editGeneratedValue.value = ''; editGeneratedPreview.value = ''; await loadData()
  } else { editExternalError.value = res.message || 'Failed to update barcode' }
}

const deleteBarcodeRow = async (bc) => {

  const confirmed = await confirm({
    type: 'delete',
    title: 'Delete Barcode',
    message: `Delete barcode "${bc.code}"?`,
    confirmLabel: 'Delete',
  })
  if (!confirmed) return
  try {
    await handleDeleteBarcodeFrappe(bc.sku, bc.code); toast.success('Barcode deleted'); await loadData()
  } catch (e) { console.error(e); toast.error('Failed to delete barcode') }
}

// ────────────────────────────────────────────
// GENERATE TAB
// ────────────────────────────────────────────
const showGenerateModal = ref(false)
const openGenerateModal = () => { showGenerateModal.value = true }
const generateForm      = reactive({ item_code: '', type: '', value: '', posa_uom: '' })
const generatedPreview  = ref('')

const autoGenerateValue = async () => {
  if (!generateForm.type) return toast.warning('Select barcode type first')
  try {
    const vRes = await generateBarcodeValue(generateForm.type)
    if (vRes.status !== 'success' || !vRes.value) return toast.error('Failed to generate value')
    generateForm.value = vRes.value
    const preview = await generateBarcodePreview({ value: generateForm.value, type: generateForm.type })
    if (preview) generatedPreview.value = preview
  } catch (e) { toast.error('Failed') }
}

const runGenerateBarcode = async () => {
  if (!generateForm.item_code) return toast.warning('Select a product')
  if (!generateForm.type)      return toast.warning('Select barcode type')
  if (!generateForm.value)     return toast.warning('Enter or auto-generate a value')
  try {
    const res = await addItemBarcode(generateForm)
    if (res.status === 'success') { generatedPreview.value = res.data?.image || ''; toast.success(res.message); await loadData() }
    else toast.warning(res.message)
  } catch (e) { toast.error('Error generating barcode') }
}

const handleGenerateBarcode = async (data) => {
  try {
    const res = await addItemBarcode(data)
    if (res.status === 'success') { toast.success(res.message); await loadData() }
    else toast.warning(res.message)
  } catch (e) { toast.error('Error generating barcode') }
}

// ────────────────────────────────────────────
// SCANNER
// ────────────────────────────────────────────
const showBarcodeScanner = ref(false)
const isProcessing       = ref(false)

const handleBarcodeScan = async (code, { onNotFound } = {}) => {
  if (isProcessing.value) return
  isProcessing.value = true
  try {
    let foundProduct = null, foundBc = null
    for (const p of allProducts.value) {
      const bc = (p.barcodes || []).find(b => b.barcode === code)
      if (bc) { foundProduct = p; foundBc = bc; break }
    }
    if (foundProduct) {
      await cartStore.addToCart({ item_code: foundProduct.item_code, item_name: foundProduct.item_name, rate: foundProduct.rate || 0, image: foundProduct.image || '', item_group: foundProduct.item_group || '', qty: 1 }, foundBc)
      toast.success(`✓ ${foundProduct.item_name} added to cart`)
    } else { onNotFound?.() }
  } finally { isProcessing.value = false }
}

const handleAssignBarcode = async ({ item_code, barcode_type, uom, barcode }) => {
  try {
    const res = await addItemBarcode({ item_code, type: barcode_type, value: barcode, posa_uom: uom })
    if (res.status === 'success') { toast.success('Barcode assigned successfully ✓'); showBarcodeScanner.value = false; await loadData() }
    else toast.warning(res.message)
  } catch (e) { toast.error('Failed to assign barcode') }
}

const clearFilters = () => {
  searchQuery.value = ''; filterProduct.value = ''; filterStatus.value = ''
  filterType.value = ''; filterGroup.value = ''; resetPage()
}

// ────────────────────────────────────────────
// PRINT
// ────────────────────────────────────────────
const printSearch     = ref('')
const printFilterType = ref('')
const printForm       = reactive({ selectedBarcodes: [], labelSize: '4x6', copies: 1, includePrice: false })

const filteredPrintBarcodes = computed(() => {
  const q = printSearch.value.toLowerCase().trim()
  const t = printFilterType.value
  return flatRows.value.filter(row => {
    if (!row.hasBarcode) return false
    const matchSearch = !q || row.sku?.toLowerCase().includes(q) || row.barcode.code?.toLowerCase().includes(q)
    const matchType   = !t || row.barcode.type === t
    return matchSearch && matchType
  })
})

const selectAllPrint = () => {
  const keys = filteredPrintBarcodes.value.map(r => r.rowKey)
  printForm.selectedBarcodes = [...new Set([...printForm.selectedBarcodes, ...keys])]
}

const printLabels = async () => {
  const selected = printForm.selectedBarcodes
  if (!selected.length) return toast.warning('Select at least one barcode')
  const data = filteredPrintBarcodes.value.filter(r => selected.includes(r.rowKey))
  if (!data.length) return toast.warning('No barcodes found')
  const html = generatePrintHTML(data, printForm.labelSize, printForm.copies, printForm.includePrice)
  const win = window.open('', '_blank', 'height=700,width=900,scrollbars=yes')
  if (!win) { toast.error('Popup blocked — allow popups and retry'); return }
  win.document.open(); win.document.write(html); win.document.close()
  win.onload = () => setTimeout(() => { win.focus(); win.print(); setTimeout(() => win.close(), 2000) }, 300)
  toast.success(`Print job: ${selected.length * printForm.copies} labels`)
}

const generatePrintHTML = (rows, labelSize, copies, includePrice) => {
  const d = ({ '4x6': {w:'4in',h:'6in',f:'14px'}, '3x5': {w:'3in',h:'5in',f:'12px'}, '2x2': {w:'2in',h:'2in',f:'10px'} })[labelSize] || {w:'4in',h:'6in',f:'14px'}
  let body = ''
  rows.forEach(row => {
    for (let i = 0; i < copies; i++) {
      body += `<div class="label">
        <div class="lb">${row.barcode.preview ? `<img src="${row.barcode.preview}" />` : '<span>No Preview</span>'}</div>
        <div class="sku">SKU: ${row.sku}</div>
        <div class="code">${row.barcode.code}</div>
        <div class="name">${row.productName}</div>
        ${row.barcode.type ? `<div class="type">${row.barcode.type}${row.barcode.uom ? ' · ' + row.barcode.uom : ''}</div>` : ''}
        ${includePrice && row._price != null ? `<div class="price">$${Number(row._price).toFixed(2)}</div>` : ''}
      </div>`
    }
  })
  return `<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
    *{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;padding:.2in}
    .c{display:grid;grid-template-columns:repeat(auto-fill,minmax(${d.w},1fr));gap:.1in}
    .label{width:${d.w};border:1px solid #ddd;display:flex;flex-direction:column;align-items:center;padding:.15in;background:white;font-size:${d.f};text-align:center;gap:3px}
    .lb{width:100%;display:flex;align-items:center;justify-content:center;margin-bottom:.08in}
    .lb img{max-width:100%;max-height:80px;object-fit:contain}
    .sku{font-weight:bold;font-size:.8em}.code{font-family:monospace;font-size:.75em}
    .name{font-size:.75em;color:#555}.type{font-size:.7em;color:#888}.price{font-weight:bold;color:#d32f2f}
    @media print{body{padding:0}.label{border:.5px solid #999}}
  </style></head><body><div class="c">${body}</div></body></html>`
}

// ────────────────────────────────────────────
// SETTINGS
// ────────────────────────────────────────────
const settings = ref({ defaultType: '', skuPrefix: 'PRD', autoGenerateSku: true, defaultLabelSize: '4x6' })
const saveSettings = () => { localStorage.setItem('barcodeSettings', JSON.stringify(settings.value)); toast.success('Settings saved') }

// ────────────────────────────────────────────
// HELPERS
// ────────────────────────────────────────────
const capitalizeFirst = (s) => String(s || '').charAt(0).toUpperCase() + String(s || '').slice(1)
const getStatusBadge  = (s) => ({ active: 'bg-green-100 text-green-800', inactive: 'bg-red-100 text-red-800' })[s] || 'bg-gray-100 text-gray-800'

const goBack = () => { router.back() }

// ────────────────────────────────────────────
// MOUNTED
// ────────────────────────────────────────────
onMounted(async () => {
  const isOpen = await shiftStore.loadActiveShifts()
  console.log("isOpen", isOpen)
  await loadData()

  const [typesRes, groupsRes, fetchedUoms, fetchedSeries, fetchedCats] = await Promise.allSettled([
    getBarcodeTypes(),
    getItemGroup(),
    inventoryStore.loadUOM(),
    inventoryStore.defaultItemSeries(),
    inventoryStore.loadCategories(),
  ])

  if (typesRes.status  === 'fulfilled') barcodeTypes.value = typesRes.value?.data  || []
  if (groupsRes.status === 'fulfilled') itemGroups.value   = groupsRes.value?.data || []
  if (fetchedUoms.status   === 'fulfilled') uoms.value       = fetchedUoms.value   || []
  if (fetchedSeries.status === 'fulfilled') series.value     = fetchedSeries.value ? [fetchedSeries.value] : []
  if (fetchedCats.status   === 'fulfilled') categories.value = fetchedCats.value   || []

  const saved = localStorage.getItem('barcodeSettings')
  if (saved) { try { Object.assign(settings.value, JSON.parse(saved)) } catch {} }
})

watch(
  () => shiftStore.isShiftOpen,
  (val) => {
    if (val) {
      console.log("✅ Shift opened, payment methods:", toRaw(payment_methods.value))
    }
  },
  { immediate: true }
)

</script>
