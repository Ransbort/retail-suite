<!-- ProductCard.vue -->
<template>
  <div
    class="select-none cursor-pointer transition-all duration-300 overflow-hidden rounded-2xl shadow group relative"
    :style="{ background: 'var(--card-bg)', color: 'var(--text-main)', border: '1px solid var(--card-border)' }"
    :title="product.name"
    @click="handleClick"
  >
    <!-- Product Image -->
    <div class="relative overflow-hidden" style="background: var(--item-bg);">
      <img
        :src="product.image"
        :alt="product.name"
        class="w-10/12 mx-auto h-24 sm:h-32 md:h-40 object-contain transition-transform duration-300 group-hover:scale-105"
        style="padding: 4px;"
      />
      <p>Hello Ahmed</p>
      <!-- Stock Badge -->
      <div
        class="absolute top-2 left-2 text-xs px-2 py-0.5 rounded-full font-semibold"
        :style="stockBadgeStyle"
      >
        {{ __(stockLabel) }}
      </div>

      <!-- Cart Qty Badge -->
      <transition name="pop">
        <div
          v-if="cartQuantity > 0"
          class="absolute top-2 right-2 text-xs w-6 h-6 rounded-full flex items-center justify-center font-bold"
          :style="{ background: 'var(--accent-green)', color: '#fff' }"
        >
          {{ __(cartQuantity) }}
        </div>
      </transition>

      <!-- Hover Overlay -->
      <div
        class="absolute inset-0 flex items-end justify-center pb-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        :style="{ background: 'var(--overlay-dark)' }"
      >
        <button
          class="flex items-center gap-1 px-4 py-1.5 rounded-full text-xs font-semibold transition-transform duration-150 active:scale-95"
          :style="{ background: 'var(--accent-cyan)', color: '#fff' }"
          :disabled="outOfStock"
          @click.stop="handleQuickAdd"
        >
          <PlusIcon class="w-3 h-3" />
          {{ outOfStock ? __('Out of Stock') : __('Add to Cart') }}
        </button>
      </div>

      <!-- Quick Add Button Overlay -->
      <div
        class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        :style="{ background: 'var(--overlay-dark)' }"
      >
        <button
          class="w-full px-4 py-12 rounded-full font-semibold"
          :style="{ background: 'var(--card-bg)', color: 'var(--accent-cyan)' }"
          @click.stop="handleQuickAdd"
        >
          <PlusIcon class="w-4 h-4 inline mr-1" />
          {{ __('Add to Cart') }}
        </button>
      </div>

    </div>

      <!-- Info Area -->
    <div class="px-3 pt-2 pb-3" :style="{ background: 'var(--card-bg)' }">
      <!-- Name -->
      <p
        class="font-semibold text-sm truncate leading-tight"
        :style="{ color: 'var(--text-main)' }"
        :title="product.item_name"
      >
        {{ product.item_name }}
      </p>

      <!-- UOM Selector -->
      <div v-if="hasMultipleUoms" class="flex flex-wrap gap-1 mt-2" @click.stop>
        <button
          v-for="(info, uom) in product.uom_prices"
          :key="uom"
          class="text-xs px-2 py-0.5 rounded-full border transition-all duration-150"
          :style="selectedUom === uom ? activeUomStyle : inactiveUomStyle"
          @click.stop="selectUom(uom)"
        >
          {{ uom }}
        </button>

       </div>
      <!-- Description -->
      <p
        v-if="product.description && product.description !== product.item_name"
        class="text-xs truncate mt-0.5"
        :style="{ color: 'var(--text-muted)' }"
      >
        {{ product.description }}
      </p>

      <!-- Price Row -->
      <div class="flex items-end justify-between mt-2">
        <div>
          <p
            v-if="discounted"
            class="text-xs line-through"
            :style="{ color: 'var(--text-muted)' }"
          >
            {{ formatPrice(currentUomInfo.original_rate)  }}
          </p>
          <p
            class="font-bold text-sm"
            :style="{ color: discounted ? 'var(--accent-red, #ef4444)' : 'var(--primary-600)' }"
          >
            {{ formatPrice(Rate) }}
          </p>
        </div>

        <div class="flex flex-col items-end gap-0.5">
          <span class="text-xs font-medium px-1.5 py-0.5 rounded" :style="qtyChipStyle">
            {{ availableQty }} {{ selectedUom }}
          </span>
          <span v-if="isInCart" class="text-xs font-semibold" :style="{ color: 'var(--accent-green)' }">
            ✓ {{ __('In Cart') }}
          </span>
        </div>
      </div>

      <!-- Discount Badge -->
      <div
        v-if="discounted"
        class="mt-1.5 inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full"
        :style="{ background: 'rgba(239,68,68,0.1)', color: 'var(--accent-red, #ef4444)' }"
      >
        <span v-if="discountPercentage > 0">-{{ discountPercentage }}%</span>
        <span v-else-if="discountAmount > 0">-{{ formatPrice(discountAmount) }}</span>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="isLoading"
      class="absolute inset-0 flex items-center justify-center"
      :style="{ background: 'var(--card-bg)', opacity: 0.85 }"
    >
      <LoadingSpinner class="w-6 h-6" />
    </div>
  </div>

<!-- Serial Picker Modal -->
<Teleport to="body">
  <div
    v-if="showSerialPicker"
    class="fixed inset-0 z-50 flex items-center justify-center"
    :style="{ background: 'rgba(0,0,0,0.5)' }"
    @click.self="showSerialPicker = false"
  >
    <div
      class="rounded-2xl shadow-xl w-full max-w-sm mx-4 overflow-hidden"
      :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
    >
      <!-- Header -->
      <div
        class="flex items-center justify-between px-4 py-3"
        :style="{ borderBottom: '1px solid var(--card-border)' }"
      >
        <p class="font-semibold text-sm" :style="{ color: 'var(--text-main)' }">
          {{ __('Select Serial No') }}
        </p>
        <button @click="showSerialPicker = false" :style="{ color: 'var(--text-muted)' }">✕</button>
      </div>

      <!-- Item Info -->
      <div class="px-4 py-2" :style="{ borderBottom: '1px solid var(--card-border)' }">
        <p class="text-xs font-medium" :style="{ color: 'var(--text-muted)' }">
          {{ product.item_name }}
        </p>
      </div>

      <!-- Serial List -->
      <div class="overflow-y-auto max-h-64">
        <button
          v-for="s in product.serial_no_data"
          :key="s.serial_no"
          class="w-full text-left px-4 py-2.5 text-sm transition-colors"
          :disabled="isSerialInCart(s.serial_no)"
          :style="{
            color: isSerialInCart(s.serial_no) ? 'var(--text-muted)' : 'var(--text-main)',
            borderBottom: '1px solid var(--card-border)',
            opacity: isSerialInCart(s.serial_no) ? 0.4 : 1,
            cursor: isSerialInCart(s.serial_no) ? 'not-allowed' : 'pointer'
          }"
          @click="!isSerialInCart(s.serial_no) && selectSerial(s.serial_no)"
        >
          # {{ s.serial_no }}
          <span v-if="isSerialInCart(s.serial_no)" class="text-xs ml-1">✓ {{ __('In Cart') }}</span>
        </button>
      </div>
    </div>
  </div>
</Teleport>
</template>
<script setup>
import { ref, computed} from 'vue'
import { formatPrice } from '@/utils/formatters'
import  PlusIcon from '@/components/icons/PlusIcon.svg';
import LoadingSpinner from '../icons/LoadingSpinner.vue';
import config from '@/config/frappe'
import { useCartStore } from '@/stores/cart'
import { useProductsStore } from '@/stores/products'


const cartStore = useCartStore()
const props = defineProps({
  product: { type: Object, required: true },
  isInCart: { type: Boolean, default: false },
  cartQuantity: { type: Number, default: 0 },
  searchContext: { type: Object, default: () => ({}) }
})


const emit = defineEmits(['add-to-cart', 'remove-from-cart', 'view-details'])
const store = useProductsStore()

const isLoading = ref(false)
const showSerialPicker = ref(false)
const showBatchPicker = ref(false)

const selectedUom = ref(
  props.searchContext?.uom && props.searchContext?.barcode
    ? props.searchContext.uom
    : props.product.stock_uom
)

const hasMultipleUoms = computed(() =>
  props.product.uom_prices && Object.keys(props.product.uom_prices).length > 1
)

const currentUomInfo = computed(() =>
  props.product.uom_prices?.[selectedUom.value] || {}
)

const Rate = computed(() => currentUomInfo.value.rate || 0)

const availableQty = computed(() => {
  const cf = currentUomInfo.value.conversion_factor || 1
  return Math.floor(props.product.actual_qty / cf)
})

const selectUom = (uom) => {
  selectedUom.value = uom
}

const activeUomStyle = {
  background: 'rgba(16,185,129,0.12)',
  color: '#0F6E56',
  borderColor: '#1D9E75',
}
const inactiveUomStyle = {
  background: 'transparent',
  color: 'var(--text-muted)',
  borderColor: 'var(--card-border)',
}


const stockLabel = computed(() => {
  const qty = props.product.actual_qty
  if (qty === undefined || qty === null) return ''
  if (qty <= 0) return 'Out of stock'
  if (qty <= 5) return 'Limited quantity'
  return 'Available'
})

const discounted = computed(() =>
  currentUomInfo.value.discount_percentage > 0 || currentUomInfo.value.discount_amount > 0
)

const discountPercentage = computed(() => {
  return currentUomInfo.value.discount_percentage || 0
})

const discountAmount = computed(() => {
  return currentUomInfo.value.discount_amount || 0
})
const cartQtyForCurrentUom = computed(() =>
  cartStore.getProductQuantity(props.product.item_code, selectedUom.value)
)

const outOfStock = computed(() =>
  availableQty.value <= 0 || cartQtyForCurrentUom.value >= availableQty.value
)

const stockBadgeStyle = computed(() => {
  const qty = availableQty.value
  if (qty === undefined || qty === null) return { display: 'none' }
  if (qty <= 0) return { background: 'rgba(239,68,68,0.15)', color: '#ef4444' }
  if (qty <= 5) return { background: 'rgba(245,158,11,0.15)', color: '#f59e0b' }
  return { background: 'rgba(16,185,129,0.15)', color: '#10b981' }
})

const qtyChipStyle = computed(() => {
  const qty = availableQty.value
  if (qty === undefined || qty === null) return {}
  if (qty <= 0) return { background: 'rgba(239,68,68,0.1)', color: '#ef4444' }
  if (qty <= 5) return { background: 'rgba(245,158,11,0.1)', color: '#f59e0b' }
  return { background: 'rgba(16,185,129,0.1)', color: '#10b981' }
})

const handleClick = () => emit('view-details', props.product)


const isSerialItem = computed(() => !!props.product.has_serial_no)
const isBatchItem  = computed(() => !!props.product.has_batch_no)

const selectSerial = (serial_no) => {
  const alreadyInCart = cartStore.cart.find(i => i.serial_no === serial_no)
  if (alreadyInCart) {
    window.$toast?.warning(__('Serial already in cart'))
    return
  }
  showSerialPicker.value = false
  emit('add-to-cart', { ...basePayload(), serial_no })
}

const isSerialInCart = (serial_no) => !!cartStore.cart.find(i => i.serial_no === serial_no)

const handleQuickAdd = async () => {
  if (isLoading.value || outOfStock.value) return
  isLoading.value = true

  try {

    if (isSerialItem.value) {
      const serials = props.product.serial_no_data || []
      if (serials.length === 1) {
        emit('add-to-cart', { ...basePayload(), serial_no: serials[0].serial_no })
      } else {
        showSerialPicker.value = true
      }
      return
    }

    if (isBatchItem.value) {
      const batches = props.product.batch_no_data || []
      if (batches.length === 1) {
        emit('add-to-cart', { ...basePayload(), batch_no: batches[0].batch_no })
      } else {
        showBatchPicker.value = true
      }
      return
    }

    emit('add-to-cart', basePayload())

  } finally {
    isLoading.value = false
  }
}

const basePayload = () => ({
  ...props.product,
  uom: selectedUom.value,
  rate: Rate.value,
  conversion_factor: currentUomInfo.value.conversion_factor || 1,
})
</script>

<style scoped>
/* Hover effects */
.group:hover .group-hover\:scale-105 {
  transform: scale(1.05);
}

.group:hover .group-hover\:opacity-100 {
  opacity: 1;
}

/* Card animations */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Price styling */
.text-cyan-600 {
  color: #0891b2;
}

/* Truncate text */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Badge animations */
.opacity-0 {
  opacity: 0;
}

.group:hover .opacity-0 {
  opacity: 1;
}

/* Smooth transitions for all elements */
* {
  transition: all 0.2s ease-in-out;
}

/* Focus states for accessibility */
.cursor-pointer:focus {
  outline: 2px solid #06b6d4;
  outline-offset: 2px;
}

button:focus {
  outline: 2px solid #06b6d4;
  outline-offset: 2px;
}

/* Loading overlay */
.bg-opacity-80 {
  background-opacity: 0.8;
}

/* Image aspect ratio */
.h-32 {
  height: 8rem;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .text-sm {
    font-size: 0.75rem;
  }

  .h-32 {
    height: 6rem;
  }
}

/* Error state for images */
img[src=""] {
  background: #f3f4f6;
}

/* Animation for cart quantity badge */
.bg-green-500 {
  animation: bounceIn 0.3s ease-out;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
