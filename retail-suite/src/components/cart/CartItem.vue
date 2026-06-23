<template>
  <div
    class="select-none mb-3 rounded-lg w-full py-2 px-2 flex justify-center transition-all duration-300"
    :style="{
      background: 'var(--item-bg)',
      color: 'var(--text-main)',
      border: '1px solid var(--item-border)'
    }"
    :class="{ 'animate-pulse': isUpdating }"
  >
    <!-- Product Image -->
    <div class="flex-shrink-0 mr-2">
      <img
        :src="item.image"
        :alt="item.item_name"
        class="rounded-lg h-10 w-10 shadow object-cover"
        :style="{ background: 'var(--card-bg)' }"
      />
    </div>

    <!-- Product Info -->
    <div class="flex-grow min-w-0">
      <div  class="flex flex-col">

        <!-- Product Name -->
        <h5
          class="text-sm font-medium truncate leading-tight"
          :title="item.item_name"
          :style="{ color: 'var(--text-main)' }"
        >
          {{ item.item_name }}
        </h5>

        <!-- Serial No -->
        <span
          v-if="item.serial_no"
          class="text-xs px-1.5 py-0.5 rounded mt-0.5 w-fit"
          :style="{ background: 'rgba(16,185,129,0.1)', color: '#0F6E56' }"
        >
          # {{ item.serial_no }}
        </span>

        <!-- Batch No -->
        <span
          v-if="item.batch_no"
          class="text-xs px-1.5 py-0.5 rounded mt-0.5 w-fit"
          :style="{ background: 'rgba(99,102,241,0.1)', color: '#4338ca' }"
        >
          Batch: {{ item.batch_no }}
        </span>

        <!-- UOM -->
        <span
          v-if="item.uom && item.uom !== item.stock_uom"
          class="text-xs px-1.5 py-0.5 rounded mt-0.5 w-fit"
          :style="{ background: 'rgba(245,158,11,0.1)', color: '#b45309' }"
        >
          {{ item.uom }}
        </span>

        <!-- Product Price & Category -->
        <div class="flex items-center justify-between mt-1" dir="ltr">
          <p class="text-xs font-semibold" :style="{ color: 'var(--text-sub)' }">
            {{ formatPrice(item.rate) }}
          </p>
          <span
            v-if="item.category"
            class="text-xs px-2 py-1 rounded-full"
            :style="{ background: 'var(--card-bg)', color: 'var(--text-muted)' }"
          >
            {{ item.category }}
          </span>
        </div>

        <!-- Item Total -->
        <p class="text-xs mt-1" :style="{ color: 'var(--text-muted)' }" dir="ltr">
          {{ __('Total') }}:
          <span class="font-semibold" :style="{ color: 'var(--primary-600)' }">
            {{ formatPrice(itemTotal) }}
          </span>
        </p>
      </div>
    </div>

    <!-- Quantity Controls -->
    <div class="py-1 ml-2 flex-shrink-0">
      <div class="w-28 grid grid-cols-3 gap-1">

        <!-- Decrease Button -->
        <button
          @click="decreaseQuantity"
          class="rounded-lg text-center py-1 focus:outline-none transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          :style="{
            background: 'var(--input-border)',
            color: 'var(--text-main)'
          }"
          :disabled="isUpdating || isSerialItem"
          :title="__('Decrease  Quantity')"
        >
          <MinusIcon class="w-3 h-3 mx-auto" />
        </button>

        <!-- Quantity Input -->
        <div class="relative">
          <input
            :value="displayQuantity"
            @input="handleQuantityInput"
            @blur="handleQuantityBlur"
            @keyup.enter="handleQuantityEnter"
            @keyup.escape="resetQuantity"
            type="number"
            min="1"
            max="999"
            class="rounded-lg text-center shadow focus:outline-none text-sm w-full py-1 transition-all duration-200"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: hasError ? '1px solid var(--warning-border)' : '1px solid var(--input-border)'
            }"
            :disabled="isUpdating || isSerialItem"
          >
          <!-- Error indicator -->
          <div
            v-if="hasError"
            class="absolute -bottom-1 -right-1 w-2 h-2 rounded-full"
            :style="{ background: 'var(--warning-border)' }"
          />
        </div>

        <!-- Increase Button -->
        <button
          @click="increaseQuantity"
          class="rounded-lg text-center py-1 focus:outline-none transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          :style="{
            background: 'var(--input-border)',
            color: 'var(--text-main)'
          }"
          :disabled="isUpdating || item.qty >= 999 || isSerialItem"
          :title="__('Increase  Quantity')"
        >
          <PlusIcon class="w-3 h-3 mx-auto" />
        </button>
      </div>

      <!-- Remove Button -->
      <button
        @click="handleRemove"
        class="w-full mt-1 text-xs rounded px-2 py-1 transition-colors duration-200 focus:outline-none"
        :style="{
          color: 'var(--warning-border)',
          background: 'transparent'
        }"
        @mouseover="$event.currentTarget.style.background = 'var(--warning-bg)'"
        @mouseleave="$event.currentTarget.style.background = 'transparent'"
        :disabled="isUpdating"
        :title="__('Remove this {0} from cart?', { 0: props.item.item_name })"
      >
        <TrashIcon class="w-3 h-3 inline mr-1" />
        {{ __('Remove') }}
      </button>
    </div>

    <!-- Loading Overlay -->
    <div
      v-if="isUpdating"
      class="absolute inset-0 rounded-lg flex items-center justify-center"
      :style="{ background: 'var(--card-bg)', opacity: 0.75 }"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import PlusIcon from '@/components/icons/PlusIcon.svg'
import MinusIcon from '@/components/icons/MinusIcon.svg'
import TrashIcon from '@/components/icons/TrashIcon.svg'
import ImageIcon from '@/components/icons/ImageIcon.svg'
import {formatPrice} from '@/utils/formatters'
import { useSettingsStore } from '@/stores/settings'
import config from '@/config/frappe'
import { useConfirm } from '@/composables/useConfirm'

const props = defineProps({
  mode: {
    type: String,
    default: 'sale', // 'sale' or 'return'
    validator: (value) => ['sale', 'return'].includes(value)
  },
  item: {
    type: Object,
    required: true,
    validator: (item) => {
      return item.item_code && item.item_name && item.rate && item.qty
    }
  }
})

const emit = defineEmits(['update-quantity', 'remove-item', 'quantity-error'])

const { confirm } = useConfirm()
const settingsStore = useSettingsStore()


const settings = computed(() => settingsStore.settings)
const primaryColor = computed(() => {
  return settings.value?.appearance?.primaryColor || '#06b6d4'
})
const isUpdating = ref(false)
const hasError = ref(false)
const displayQuantity = ref(props.item.qty)
const pendingQuantity = ref(props.item.qty)

const isSerialItem = computed(() => !!props.item.serial_no)

// Computed properties
const itemTotal = computed(() => {
  return props.item.rate * props.item.qty
})

watch(
  () => props.item.qty,
  (newQty) => {
    displayQuantity.value = newQty
    pendingQuantity.value = newQty
  }
)

const increaseQuantity = () => {

  if (isSerialItem.value) {
    window.$toast?.warning(__('Serial items cannot have quantity more than 1'))
    return
  }

  let newQty = props.item.qty

  if (props.mode === 'return') {
    if (newQty < props.item.originalQuantity) {
      newQty -= 1
    } else {
      window.$toast?.warning(__('You cannot return more than original quantity'))
    }
  } else {
    const cf = props.item.conversion_factor || 1
    const availableQty = Math.floor((props.item.actual_qty || 0) / cf)

    if (newQty >= availableQty) {
      window.$toast?.warning(__('Quantity exceeds available stock'))
      return
    }
    newQty += 1
  }

  emit('update-quantity', props.item.item_code, newQty, props.mode)
}

const decreaseQuantity = () => {

  if (isSerialItem.value) {
    emit('remove-item', props.item.item_code)
    return
  }

  let newQty = props.item.qty
  if (props.mode === 'return') {

    if (newQty < -1) {
      newQty += 1
    } else {
      if (window.$toast) window.$toast.info(__('Can not reduce Quantity below 1 Quantity'))
    }
  } else {
    if (newQty > 1) {
      newQty -= 1
    } else {
      emit('remove-item', props.item.item_code)
      return
    }
  }

  emit('update-quantity', props.item.item_code, newQty)
}

const handleQuantityInput = (event) => {
  const value = parseInt(event.target.value) || 0
  displayQuantity.value = value

  // Validate
  hasError.value = value < 1 || value > 999

  if (!hasError.value) {
    pendingQuantity.value = value
  }
}

const handleQuantityBlur = async () => {
  if (hasError.value) {
    resetQuantity()
    return
  }

  if (pendingQuantity.value !== props.item.qty) {
    // ← تحقق من الـ stock
    const cf = props.item.conversion_factor || 1
    const availableQty = Math.floor((props.item.actual_qty || 0) / cf)

    if (pendingQuantity.value > availableQty) {
      window.$toast?.warning(__('Quantity exceeds available stock'))
      resetQuantity()
      return
    }

    await updateQuantity(pendingQuantity.value)
  }
}
  // Handle enter key on quantity input
  const handleQuantityEnter = async (event) => {
    event.target.blur() // This will trigger handleQuantityBlur
  }

  // Reset quantity to current value
  const resetQuantity = () => {
    displayQuantity.value = props.item.qty
    pendingQuantity.value = props.item.qty
    hasError.value = false
  }

// Update quantity with validation
const updateQuantity = async (newQuantity) => {
  if (isUpdating.value) return

  const isReturnMode = props.mode === 'return'
  console.log('🟢 updateQuantity fired', props.mode, props.item.item_code, newQuantity)

  //  Validate quantity range
  if (!isReturnMode && (newQuantity < 1 || newQuantity > 999 || isNaN(newQuantity))) {
    emit('quantity-error', 'Quantity must be between 1 and 999')
    resetQuantity()
    return
  }

  //  In return mode, allow negative but still reasonable range
  if (isReturnMode && (newQuantity > -1 || isNaN(newQuantity))) {
    emit('quantity-error', 'Return quantity must be between -1 and -999')
    resetQuantity()
    return
  }


  if (newQuantity === props.item.qty) return // No change needed

  isUpdating.value = true
  hasError.value = false

  try {
    emit('update-quantity', props.item.item_code, newQuantity, props.mode)

    await new Promise(resolve => setTimeout(resolve, 200))
  } catch (error) {
    console.error('Failed to update quantity:', error)
    emit('quantity-error', 'Failed to update quantity')
    resetQuantity()
  } finally {
    isUpdating.value = false
  }
}


  // Handle remove item
  const handleRemove = async () => {
    console.log("! Removed")
    if (isUpdating.value) return

    // Show confirmation for expensive items
    if (itemTotal.value > 50000) {
      const confirmed = await confirm({
        type: 'delete',
        title: 'Remove Item',
        message: __(`Remove this ${0} from cart?`,[props.item.item_name]),
        confirmLabel: 'Remove Item',
      })
      if (!confirmed) return

    }

    isUpdating.value = true

    try {
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 300))

      emit('remove-item', props.item.item_code)
    } catch (error) {
      console.error('Failed to remove item:', error)
    } finally {
      isUpdating.value = false
    }
  }
</script>

<style scoped>
/* Item container styling */
.bg-gray-50 {
  background-color: #f8fafc;
}

.bg-gray-100 {
  background-color: #f1f5f9;
}

.bg-gray-200 {
  background-color: #e2e8f0;
}

.bg-gray-600 {
  background-color: #475569;
}

.bg-gray-700 {
  background-color: #334155;
}

.text-blue-gray-600 {
  color: #475569;
}

.text-blue-gray-700 {
  color: #334155;
}

.hover\:bg-gray-100:hover {
  background-color: #f1f5f9;
}

.hover\:bg-gray-700:hover {
  background-color: #334155;
}

/* Quantity input styling */
input[type="number"] {
  -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Focus states */
button:focus {
  outline: none;
}

input:focus {
  outline: none;
}

/* Error states */
.border-red-300 {
  border-color: #fca5a5;
}

.bg-red-50 {
  background-color: #fef2f2;
}

.text-red-500 {
  color: #ef4444;
}

.text-red-700 {
  color: #b91c1c;
}

.hover\:text-red-700:hover {
  color: #b91c1c;
}

.hover\:bg-red-50:hover {
  background-color: #fef2f2;
}

/* Loading animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Transition effects */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease;
}

/* Button disabled states */
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button:disabled:hover {
  background-color: inherit;
  color: inherit;
}

/* Category badge */
.text-xs.bg-gray-200 {
  font-size: 0.625rem;
  line-height: 1;
}

/* Truncate long text */
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.min-w-0 {
  min-width: 0;
}

/* Focus ring colors */
.focus\:ring-blue-gray-300:focus {
  --tw-ring-color: #cbd5e1;
}

.focus\:ring-cyan-300:focus {
  --tw-ring-color: #67e8f9;
}

.focus\:ring-red-300:focus {
  --tw-ring-color: #fca5a5;
}

/* Hover effects for buttons */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:active:not(:disabled) {
  transform: translateY(0);
}

/* Image styling */
img {
  object-fit: cover;
}

/* Error indicator */
.bg-red-500 {
  background-color: #ef4444;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .w-28 {
    width: 6rem;
  }

  .text-sm {
    font-size: 0.75rem;
  }

  .text-xs {
    font-size: 0.625rem;
  }
}

/* Loading overlay */
.bg-opacity-70 {
  background-opacity: 0.7;
}

.absolute.inset-0 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
</style>
