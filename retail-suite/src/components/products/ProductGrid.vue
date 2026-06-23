<!-- ProductGrid.vue -->
<template>
  <div class="h-full flex flex-col overflow-hidden gap-3 mt-3">
    <!-- Filter Bar (pricelist + warehouse) -->
    <FilterBar
      v-model:selectedPriceList="selectedPriceList"
      v-model:selectedWarehouse="selectedWarehouse"
      :price-lists="productsStore.priceLists"
      :warehouses="productsStore.warehouses"
      :is-loading="productsStore.isLoading"
      @reload="productsStore.loadProductsFromFrappeDB(true)"
    />
    <!-- Category Filter -->
    <CategoryFilter v-model="selectedCategory" />

    <!-- Scrollable Grid Area -->
    <div class="flex-1 overflow-y-auto px-1">

      <!-- Empty DB -->
      <div
        v-if="productsStore.products.length === 0 && !productsStore.isLoading"
        class="select-noneflex flex-wrap content-center justify-center h-full opacity-25"
        :style="{ background: 'var(--item-bg)', color: 'var(--text-main)' }"
      >
        <div class="w-full flex flex-col items-center">
          <EmptyDatabaseIcon />
          <p class="text-xl mt-2">{{ __('There are no products') }}</p>
        </div>
      </div>

      <!-- Loading -->
      <div
        v-else-if="productsStore.isLoading"
        class="select-none flex flex-wrap content-center justify-center h-full opacity-40"
        :style="{ color: 'var(--text-main)' }"
      >
        <div class="w-full text-center">
          <LoadingSpinner />
          <p class="text-xl mt-4">{{ __('Loading products') }}</p>
        </div>
      </div>

      <!-- No Search Results -->
      <div
        v-else-if="filteredProducts.length === 0 && (searchKeyword || selectedCategory)"
        class="select-none flex flex-wrap content-center justify-center h-full opacity-25"
        :style="{ color: 'var(--text-main)' }"
      >
        <div class="w-full text-center">
          <EmptySearchIcon />
          <p class="text-xl mt-2">{{ __('No results') }}</p>
          <p class="text-sm mt-1" :style="{ color: 'var(--text-muted)' }">
            "{{ searchKeyword || selectedCategory }}"
          </p>
        </div>
      </div>

      <!-- Grid -->
      <div
        v-else
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 pb-4"
      >
        <ProductCard
          v-for="product in filteredProducts"
          :key="product.item_code"
          :product="product"
          :search-context="product.item_code === productsStore.searchContext?.item_code
          ? productsStore.searchContext
          : {}"
          :is-in-cart="cartStore.isInCart(product.item_code)"
          :cart-quantity="cartStore.getProductQuantity(product.item_code)"
          @add-to-cart="handleAddToCart"
          @remove-from-cart="handleRemoveFromCart"
          @view-details="handleViewDetails"
        />
      </div>

      <!-- Results count -->
      <div
        v-if="(searchKeyword || selectedCategory) && filteredProducts.length > 0"
        class="text-center text-xs mt-2 pb-2"
        :style="{ color: 'var(--text-muted)' }"
      >
        {{ filteredProducts.length }} {{ __('Products') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import ProductCard from './ProductCard.vue'
import CategoryFilter from './CategoryFilter.vue'
import FilterBar from './FilterBar.vue'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'
import EmptyDatabaseIcon from '@/components/icons/EmptyDatabaseIcon.svg'
import EmptySearchIcon from '@/components/icons/EmptySearchIcon.svg'
import { useShiftStore } from '@/stores/shift'
import { storeToRefs } from 'pinia'

const shiftStore = useShiftStore()
const { isShiftOpen } = storeToRefs(shiftStore)
const props = defineProps({
  searchKeyword: { type: String, default: '' }
})
const emit = defineEmits(['add-to-cart', 'remove-from-cart', 'view-details'])

const productsStore = useProductsStore()
const cartStore = useCartStore()
const selectedCategory = ref('')

const filteredProducts = computed(() => {
  let list = productsStore.products
  if (selectedCategory.value) {
    list = list.filter(p => p.item_group === selectedCategory.value)
  }
  return list
})

const selectedPriceList = computed({
  get: () => productsStore.selectedPriceList,
  set: (val) => {
    productsStore.selectedPriceList = val
  }
})

const selectedWarehouse = computed({
  get: () => productsStore.selectedWarehouse,
  set: (val) => {
    productsStore.selectedWarehouse = val
  }
})
const handleAddToCart = (p) => {
  const added = cartStore.addToCart(p)
  if (!added) {
    window.$toast?.warning(__('Quantity exceeds available stock'))
    return
  }
  emit('add-to-cart', p)
}

const handleRemoveFromCart = (p) => { cartStore.removeFromCart(p.item_code); emit('remove-from-cart', p) }
const handleViewDetails  = (p) => emit('view-details', p)

const LoadingSpinner = {
  template: `
    <div style="
      display:inline-block; width:5rem; height:5rem;
      border-radius:9999px; border:3px solid transparent;
      border-bottom-color:var(--text-muted);
      animation:spin 1s linear infinite;
    "></div>
    `
  }

watch(() => props.searchKeyword, async (kw) => {
  await productsStore.searchProducts(kw)
})

watch(
  () => [productsStore.selectedPriceList, productsStore.selectedWarehouse],
  () => productsStore.loadProductsFromFrappeDB(true)
)

watch(isShiftOpen, async (val) => {
  console.log('POS saw isShiftOpen change to:', val)

  if (!val) return

  try {
    const shiftStore = useShiftStore()
    const profile = shiftStore.pos_profile

    if (!profile) {
      console.warn('⏳ POS Profile not ready yet')
      return
    }

    await productsStore.loadFilterOptions(profile)


    if (!selectedPriceList.value)
      selectedPriceList.value = profile.selling_price_list

    if (!selectedWarehouse.value)
      selectedWarehouse.value = profile.warehouse

    await productsStore.loadProductsFromFrappeDB(true)

  } catch (err) {
    console.error('❌ POS init flow failed:', err)
  }
})
</script>
<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
