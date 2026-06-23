<!-- ItemModal.vue -->
<template>
  <div
    v-if="show"
    class="fixed inset-0 flex items-center justify-center z-50 p-4"
    style="background: rgba(0,0,0,0.5);"
    @click.self="$emit('close')"
  >
    <div
      class="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl shadow-2xl"
      style="scrollbar-width: thin;"
      :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }"
    >
      <!-- ══════════ HEADER ══════════ -->
      <div
        class="flex items-center justify-between px-5 py-3 sticky top-0 z-10"
        :style="{ background: 'var(--card-bg)', borderBottom: '1px solid var(--card-border)' }"
      >
        <h3 class="text-sm font-semibold" :style="{ color: 'var(--text-main)' }">
          {{ isEditing ? 'Edit Item' : 'Add New Item' }}
        </h3>
        <button
          @click="$emit('close')"
          class="w-6 h-6 flex items-center justify-center rounded transition-colors"
          :style="{ color: 'var(--text-muted)' }"
          @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
          @mouseleave="$event.currentTarget.style.background = 'transparent'"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- ══════════ FORM ══════════ -->
      <form @submit.prevent="handleSubmit" class="p-5 space-y-4">

        <!-- Series / Item Code + Item Name -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">

          <!-- Item Code (Edit only) -->
          <div v-if="isEditing">
            <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Item Code</label>
            <input
              type="text"
              :value="form.item_code"
              disabled
              class="w-full px-3 py-1.5 rounded-md text-xs cursor-not-allowed opacity-60"
              :style="{
                background: 'var(--item-bg)',
                color: 'var(--text-sub)',
                border: '1px solid var(--item-border)'
              }"
            />
          </div>

          <!-- Series (Add only) -->
          <div v-else>
            <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">
              Series <span style="color: #ef4444;">*</span>
            </label>
            <select
              v-model="form.naming_series"
              required
              class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--input-border)'
              }"
            >
              <option disabled value="">Select Series</option>
              <option v-for="s in getSeriesArray()" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <!-- Item Name -->
          <div>
            <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">
              Item Name <span style="color: #ef4444;">*</span>
            </label>
            <input
              v-model="form.item_name"
              type="text"
              required
              placeholder="e.g., Coffee Beans"
              class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--input-border)'
              }"
            />
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="Item description"
            class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none resize-none"
            :style="{
              background: 'var(--input-bg)',
              color: 'var(--text-main)',
              border: '1px solid var(--input-border)'
            }"
          />
        </div>

        <!-- Category + UOM -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">
              Category <span style="color: #ef4444;">*</span>
            </label>
            <select
              v-model="form.item_group"
              required
              class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--input-border)'
              }"
            >
              <option value="">Select Category</option>
              <option v-for="cat in categories" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">
              Unit of Measure <span style="color: #ef4444;">*</span>
            </label>
            <select
              v-model="form.stock_uom"
              required
              class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--input-border)'
              }"
            >
              <option value="">Select UOM</option>
              <option v-for="uom in uoms" :key="uom.name" :value="uom.name">{{ uom.name }}</option>
            </select>
          </div>
        </div>

        <!-- Valuation Rate + Disabled -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Valuation Rate</label>
            <input
              v-model.number="form.valuation_rate"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              class="w-full px-3 py-1.5 rounded-md text-xs focus:outline-none"
              :style="{
                background: 'var(--input-bg)',
                color: 'var(--text-main)',
                border: '1px solid var(--input-border)'
              }"
            />
          </div>
          <div v-if="isEditing" class="flex items-end pb-1">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="form.disabled"
                type="checkbox"
                class="w-3.5 h-3.5 rounded"
                :style="{ accentColor: 'var(--focus-ring)' }"
              />
              <span class="text-xs font-medium" :style="{ color: 'var(--text-sub)' }">Disabled</span>
            </label>
          </div>
        </div>

        <!-- Image Upload -->
        <div>
          <label class="block text-xs font-medium mb-1" :style="{ color: 'var(--text-muted)' }">Image</label>
          <div
            class="rounded-lg p-5 text-center cursor-pointer transition-colors"
            :style="{
              background: 'var(--item-bg)',
              border: '2px dashed var(--card-border)'
            }"
            @click="$refs.imageInput?.click()"
            @mouseover="$event.currentTarget.style.borderColor = 'var(--focus-ring)'"
            @mouseleave="$event.currentTarget.style.borderColor = 'var(--card-border)'"
          >
            <!-- No image -->
            <div v-if="!form.image">
              <svg class="w-7 h-7 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                :style="{ color: 'var(--text-muted)' }">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
              </svg>
              <p class="text-xs" :style="{ color: 'var(--text-muted)' }">Click to upload or drag and drop</p>
              <p class="text-xs mt-0.5" :style="{ color: 'var(--text-muted)', opacity: 0.6 }">PNG, JPG, GIF up to 5MB</p>
            </div>

            <!-- Has image -->
            <div v-else class="flex flex-col items-center">
              <img
                :src="form.image"
                :alt="form.item_name"
                class="h-28 w-28 object-cover rounded-lg mb-2"
                :style="{ border: '1px solid var(--card-border)' }"
                @error="handleImageError"
              />
              <p class="text-xs mb-1.5" :style="{ color: 'var(--text-muted)' }">{{ getImageFileName() }}</p>
              <button
                type="button"
                @click.stop="form.image = ''"
                class="text-xs font-medium px-2 py-0.5 rounded transition-colors"
                style="color: #ef4444;"
                @mouseover="$event.currentTarget.style.background = '#fef2f2'"
                @mouseleave="$event.currentTarget.style.background = 'transparent'"
              >
                Remove Image
              </button>
            </div>
          </div>
          <input
            ref="imageInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="handleImageUpload"
          />
        </div>

        <!-- ══════════ FOOTER ══════════ -->
        <div
          class="flex justify-end gap-2 pt-3"
          :style="{ borderTop: '1px solid var(--card-border)' }"
        >
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-1.5 text-xs rounded-md transition-colors"
            :style="{
              background: 'var(--item-bg)',
              color: 'var(--text-sub)',
              border: '1px solid var(--item-border)'
            }"
            @mouseover="$event.currentTarget.style.background = 'var(--nav-item-hover-bg)'"
            @mouseleave="$event.currentTarget.style.background = 'var(--item-bg)'"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isSaving || !isFormValid()"
            class="px-4 py-1.5 text-xs text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :style="{ background: 'var(--focus-ring)' }"
          >
            {{ isSaving ? 'Saving...' : (isEditing ? 'Update' : 'Add') }} Item
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  show:       { type: Boolean, default: false },
  item:       { type: Object,  default: null  },
  isEditing:  { type: Boolean, default: false },
  categories: { type: Array,   default: () => [] },
  uoms:       { type: Array,   default: () => [] },
  series:     { type: String,  default: ''    },
})

const emit = defineEmits(['save', 'close'])

const isSaving     = ref(false)
const imageInput   = ref(null)
const previousItem = ref(null)

const defaultForm = {
  naming_series:  '',
  item_code:      '',
  item_name:      '',
  description:    '',
  item_group:     '',
  stock_uom:      '',
  valuation_rate: 0,
  image:          '',
  disabled:       false,
}

const form = reactive({ ...defaultForm })

watch(
  () => props.show,
  (isOpen) => {
    console.log('show:', isOpen)
    if (isOpen && props.item) {
      const data = props.item._raw || props.item
      console.log('item:', data)
      Object.assign(form, {
        ...data,
        disabled: Boolean(data.disabled),
      })
    } else if (isOpen && !props.item) {
      Object.assign(form, defaultForm)
    }
  },
  { immediate: true }
)

const getSeriesArray = () => {
  if (!props.series) return []
  if (typeof props.series === 'string') return props.series.split(' ').filter(s => s.trim())
  return Array.isArray(props.series) ? props.series : []
}

const getImageFileName = () => {
  if (!form.image) return ''
  if (form.image.startsWith('data:')) return 'New image selected'
  return form.image.split('/').pop()
}

const handleImageError = (e) => { console.warn('Image failed to load:', e) }

const isFormValid = () => {
  if (props.isEditing) return form.item_name && form.item_group && form.stock_uom
  return form.naming_series && form.item_name && form.item_group && form.stock_uom
}

const handleImageUpload = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { alert('File size must be less than 5MB'); return }
  if (!file.type.startsWith('image/')) { alert('Please select a valid image file'); return }
  const reader = new FileReader()
  reader.onload  = (e) => { if (typeof e.target?.result === 'string') form.image = e.target.result }
  reader.onerror = ()  => { alert('Failed to read file') }
  reader.readAsDataURL(file)
}

const handleSubmit = async () => {
  if (!isFormValid()) { alert('Please fill in all required fields'); return }
  isSaving.value = true
  try {
    console.log("🧾 props.item",props.item)
    let payload = {}
    if (props.isEditing && props.item) {
      payload = {
        item_code:      form.item_code,
        item_name:      form.item_name,
        description:    form.description,
        item_group:     form.item_group,
        stock_uom:      form.stock_uom,
        valuation_rate: form.valuation_rate,
        disabled:       form.disabled,
      }
      if (form.image && form.image !== props.item.image) payload.image = form.image
    } else {
      payload = {
        naming_series:  form.naming_series,
        item_name:      form.item_name,
        description:    form.description,
        item_group:     form.item_group,
        stock_uom:      form.stock_uom,
        valuation_rate: form.valuation_rate || 0,
      }
      if (form.image) payload.image = form.image
    }
    emit('save', payload)
  } catch (error) {
    console.error('Error submitting form:', error)
    alert('Error saving item. Please try again.')
  } finally {
    isSaving.value = false
  }
}
</script>
