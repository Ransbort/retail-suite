<template>
  <div class="fixed w-full h-screen left-0 top-0 z-50 flex flex-wrap justify-center content-center p-4 md:p-24">
    <!-- Background Overlay -->
    <transition
      name="overlay"
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-300"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
    <div
      class="fixed w-full h-screen left-0 top-0 z-0 bg-opacity-50"
      @click="handleBackgroundClick"
      />
    </transition>

    <!-- Modal Content -->
    <transition
      name="modal"
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0 transform scale-90"
      enter-to-class="opacity-100 transform scale-100"
      leave-active-class="transition ease-in duration-300"
      leave-from-class="opacity-100 transform scale-100"
      leave-to-class="opacity-0 transform scale-90"
    >
      <div class="w-full max-w-md rounded-3xl bg-white shadow-2xl overflow-hidden z-10 mx-auto relative">
        <!-- Receipt Content -->
        <div
          id="receipt-content"
          ref="receiptContent"
          class="text-left w-full text-sm p-6 overflow-x-hidden"
          >
          <!-- :style="{
            class="text-left w-full text-sm p-6 overflow-auto max-h-96"
            width: receiptConfig.width,
            maxWidth: receiptConfig.maxWidth,
            fontSize: receiptConfig.fontSize
          }" -->
          <!-- Receipt Header -->
          <div class="text-center mb-4">
            <img
              v-if="showLogo"
              :src="storeLogo"
              class="mb-3 w-8 h-8 inline-block"
              crossorigin="use-credentials"
              :alt="storeName"
              @error="handleLogoError"
            />
            <div v-if="logoError" class="mb-3 w-8 h-8 inline-block">
              <ReceiptLogoIcon class="w-8 h-8 text-cyan-600" />
            </div>
            <h2 class="text-xl font-semibold text-gray-800">{{ storeName }}</h2>
          </div>

          <!-- Receipt Info -->
          <div class="flex mt-4 text-xs text-gray-600 border-b pb-2 mb-4">
            <div class="flex-grow">
              <!-- {{ receiptData }} -->
              <span class="font-semibold">No:</span> {{ receiptData?.invoiceNo || generateReceiptNo() }}
            </div>
            <div>{{ formatDate(receiptData?.timestamp) }}</div>
          </div>

          <!-- Items Table -->
          <div class="mb-4">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b">
                  <th class="py-1 w-1/12 text-center">#</th>
                  <th class="py-1 text-left">Item</th>
                  <th class="py-1 w-2/12 text-center">Qty</th>
                  <th class="py-1 w-3/12 text-right">Subtotal</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(item, index) in receiptData?.items || []"
                  :key="item.item_code"
                  class="border-b border-gray-100"
                >
                  <td class="py-2 text-center text-gray-500">{{ index + 1 }}</td>
                  <td class="py-2 text-left">
                    <div class="font-medium">{{ item.item_name }}</div>
                    <small class="text-gray-500">{{ formatPrice(item.rate) }}</small>
                  </td>
                  <td class="py-2 text-center">{{ item.qty }}</td>
                  <td class="py-2 text-right font-medium">{{ formatPrice(item.qty * item.rate) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Summary -->
          <div class="border-t pt-4">
            <div class="space-y-2">
              <!-- Subtotal -->
              <div class="flex justify-between text-sm">
                <span>Subtotal:</span>
                <span>{{ formatPrice(summary?.subtotal || 0) }}</span>
              </div>

              <!-- Tax (if applicable) -->
              <div v-if="summary?.tax > 0" class="flex justify-between text-sm">
                <span>Tax:</span>
                <span>{{ formatPrice(summary.tax) }}</span>
              </div>

              <!-- Discount (if applicable) -->
              <div v-if="summary?.discount > 0" class="flex justify-between text-sm text-green-600">
                <span>Discount:</span>
                <span>-{{ formatPrice(summary.discount) }}</span>
              </div>

              <!-- Total -->
              <div class="flex justify-between font-semibold text-base border-t pt-2">
                <span>TOTAL:</span>
                <span>{{ formatPrice(summary?.total || 0) }}</span>
              </div>

              <!-- Payment Info -->
              <div class="flex justify-between text-sm border-t pt-2">
                <span>Cash:</span>
                <span>{{ formatPrice(summary?.cash || 0) }}</span>
              </div>

              <div class="flex justify-between text-sm font-medium">
                <span>Change:</span>
                <span class="text-green-600">{{ formatPrice(summary?.change || 0) }}</span>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="mt-6 pt-5 border-t border-dashed border-gray-300 text-center text-xs text-gray-900">

            <p v-if="showThankYou" class="tracking-wide uppercase text-[11px] text-gray-700">
              {{footerMessage}}
            </p>

            <div class="mt-3 space-y-1 leading-relaxed">
              <p>{{ storeAddress }}</p>

              <div class="flex items-center justify-center gap-2 flex-wrap">
                <span>{{ storePhone }}</span>

                <span class="text-gray-500">|</span>

                <span>{{ storeEmail }}</span>
              </div>

              <p class="text-[11px] text-gray-700">
                {{ getCurrentDateTime() }}
              </p>
            </div>

          </div>
        </div>

        <!-- Action Buttons -->
        <div class="p-4 w-full bg-gray-50 border-t">
          <div class="flex space-x-3">
            <!-- Print Button -->
            <button data-print-btn
              class="flex-1 bg-cyan-500 text-white text-lg px-4 py-3 rounded-2xl focus:outline-none hover:bg-cyan-600 transition-colors duration-200 flex items-center justify-center"
              @click="handlePrint"
              :disabled="isProcessing"
            >
              <PrintIcon class="w-5 h-5 mr-2" />
              {{ isProcessing ? 'Printing...' : 'Print' }}
            </button>

            <!-- Proceed Button -->
            <button
              v-if="!props.receiptData?.isFastMode"
              class="flex-1 bg-green-500 text-white text-lg px-4 py-3 rounded-2xl focus:outline-none hover:bg-green-600 transition-colors duration-200 flex items-center justify-center"
              @click="handleProceed"
              @keydown.enter="handleProceed"
              :disabled="isProcessing"
            >
              <CheckIcon class="w-5 h-5 mr-2" />
              Proceed
            </button>
          </div>

          <!-- Alternative Actions -->
          <div class="flex justify-center mt-3 space-x-4">
            <button
              class="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
              @click="handleEmailReceipt"
              :disabled="isProcessing"
            >
              Email Receipt
            </button>
            <button
              class="text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
              @click="handleSaveReceipt"
              :disabled="isProcessing"
            >
              Save Copy
            </button>
          </div>
        </div>

        <!-- Close Button -->
       <button
          class="absolute top-4 right-4 z-50 text-gray-400 hover:text-gray-600 focus:outline-none p-1 rounded-full hover:bg-gray-100 transition-colors duration-200"
          @click="handleClose"
          :disabled="isProcessing"
        >
          <CloseIcon class="w-5 h-5 text-black" />
        </button>

      </div>
    </transition>
  </div>

  <!-- Hidden Print Area -->
  <div id="print-area" class="print-area hidden">
    <div v-html="printContent"></div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { formatPrice } from '../../utils/formatters';
import ReceiptLogoIcon from '@/components/icons/ReceiptLogoIcon.svg'
import PrintIcon from '@/components/icons/PrintIcon.svg'
import CheckIcon from '@/components/icons/CheckIcon.svg'
import CloseIcon from '@/components/icons/CloseIcon.svg'
import { useSettingsStore } from '@/stores/settings'

const props = defineProps({
    receiptData: {
      type: Object,
      default: () => ({})
    },
    autoShow: {
      type: Boolean,
      default: true
    },
     isFastMode: {
      type: Boolean,
      default: false
    }
})
const emit = defineEmits(['close', 'proceed', 'print', 'email', 'save'])

// Stores
const settingsStore = useSettingsStore()
const settings = computed(() => settingsStore.settings)
const storeName = computed(() => settings.value?.store?.name || 'TAILWIND POS')
const storeLogo = computed(() =>  settings.value?.store?.storeLogo)


console.log('storeLogo', storeLogo.value)
const storeAddress = computed(() => settings.value?.store?.address || 'CABANG KONOHA SELATAN')
const storePhone = computed(() => settings.value?.store?.phone || '+1 (555) 000-0000')
const storeEmail = computed(() => settings.value?.store?.email || 'info@tailwindpos.com')
const showLogo = computed(() => settings.value?.receipt?.showLogo)
console.log('showLogo', showLogo.value)
const showThankYou = computed(() => settings.value?.receipt?.showThankYou)
const footerMessage = computed(() => settings.value?.receipt?.footerMessage || 'Thank You For Shopping With Us')
const receiptSize = computed(() => settings.value?.receipt?.size || '80mm')
const receiptConfig = computed(() => {
  const receipt = settings.value?.receipt

  return (
    receipt?.sizes?.[receipt?.size] ||
    receipt?.sizes?.["80mm"]
  )
})
const invoiceTemplateRef = ref(null)
const receiptContent = ref(null)
const isProcessing = ref(false)
const logoError = ref(false)

// Computed properties
const summary = computed(() => props.receiptData?.summary || {})

const printContent = computed(() => {
  if (!receiptContent.value) return ''
  return receiptContent.value.innerHTML
})
// Format date
const formatDate = (timestamp) => {
  if (!timestamp) return new Date().toLocaleString('id-ID')
  return new Date(timestamp).toLocaleString('id-ID')
}

// Get current date time
const getCurrentDateTime = () => {
  return new Date().toLocaleString('id-ID')
}

// Generate receipt number
const generateReceiptNo = () => {
  const now = new Date()
  const timestamp = now.getTime().toString().slice(-6)
  return `TW${timestamp}`
}

// Handle logo error
const handleLogoError = () => {
  logoError.value = true
}

// Handle background click
const handleBackgroundClick = () => {
  if (!isProcessing.value) {
    handleClose()
  }
}

// Handle close
const handleClose = () => {
  if (isProcessing.value) return
  emit('close')
}

// Handle email receipt
const handleEmailReceipt = () => {
  if (isProcessing.value) return

  // This would typically open an email dialog or send to server
  const emailBody = `Receipt from ${props.storeName}\n\nTotal: ${formatPrice(summary.value.total)}\nDate: ${formatDate(props.receiptData?.timestamp)}`
  const emailSubject = `Receipt #${props.receiptData?.receiptNo || generateReceiptNo()}`
  const mailtoLink = `mailto:?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`

  window.open(mailtoLink)
  emit('email', props.receiptData)
}

// Handle save receipt
const isSaved = ref(false)  // هل اتحفظت في Frappe
const savedInvoiceName = ref(null)  // الـ name بتاع الـ draft

const handleSaveReceipt = async () => {
  if (isProcessing.value) return
  isProcessing.value = true
  try {
    const result = await emit('save', props.receiptData)
    isSaved.value = true
    savedInvoiceName.value = result?.name
    // تحميل نسخة نصية
    const receiptText = generateReceiptText()
    const blob = new Blob([receiptText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `receipt_${props.receiptData?.invoiceNo || generateReceiptNo()}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Save failed:', error)
    alert('Save failed. Please try again.')
  } finally {
    isProcessing.value = false
  }
}


// const handlePrint = async () => {
//   if (isProcessing.value) return

//   try {
//     isProcessing.value = true
//     await nextTick()

//     const content = receiptContent.value?.innerHTML
//     if (!content) return



//     const styles = Array.from(document.styleSheets)
//       .map(sheet => {
//         try {
//           return Array.from(sheet.cssRules).map(rule => rule.cssText).join('\n')
//         } catch {
//           return sheet.href ? `@import url("${sheet.href}");` : ''
//         }
//       })
//       .join('\n')

//     const win = window.open('', '_blank')
//     win.document.write(`
//       <!DOCTYPE html>
//       <html>
//         <head>
//           <title>Receipt</title>
//           <style>
//             ${styles}

//             /* ── Reset & Layout ── */
//             body {
//               background: white !important;
//               display: flex;
//               justify-content: center;
//               padding: 16px;
//               font-family: 'Courier New', monospace;
//             }
//             #receipt-print-wrapper {
//               width: 100%;
//               max-width: 360px;
//             }
//             * {
//               overflow: visible !important;
//               max-height: none !important;
//             }

//             /* ── Table borders ── */
//             table {
//               width: 100%;
//               border-collapse: collapse !important;
//             }
//             thead tr {
//               border-bottom: 2px solid #000 !important;
//             }
//             th {
//               padding: 6px 4px !important;
//               font-weight: 700 !important;
//               font-size: 11px !important;
//               border-bottom: 2px solid #000 !important;
//             }
//             td {
//               padding: 6px 4px !important;
//               font-size: 11px !important;
//               border-bottom: 1px solid #d1d5db !important;
//             }
//             tbody tr:last-child td {
//               border-bottom: none !important;
//             }

//             /* ── Summary section ── */
//             .border-t {
//               border-top: 1px solid #d1d5db !important;
//             }
//             .border-b {
//               border-bottom: 1px solid #d1d5db !important;
//             }

//             @media print {
//               body { padding: 0; }
//               @page { margin: 8mm; size: 80mm auto; }
//             }
//           </style>
//         </head>
//         <body>
//           <div id="receipt-print-wrapper">
//             ${content}
//           </div>
//         </body>
//       </html>
//     `)

//     win.document.close()
//     win.focus()
//     setTimeout(() => { win.print(); win.close() }, 600)

//     emit('print', props.receiptData)

//   } catch (error) {
//     console.error('Print failed:', error)
//     alert('Print failed. Please try again.')
//   } finally {
//     setTimeout(() => { isProcessing.value = false }, 1000)
//   }
// }
const handlePrint = async () => {
  if (isProcessing.value) return

  try {
    isProcessing.value = true
    await nextTick()

    const content = receiptContent.value?.innerHTML
    if (!content) return

    // ─────────────────────────────────────
    // Receipt Size Config
    // ─────────────────────────────────────
    const receiptSize = settings.value?.receipt?.size || '80mm'

    let pageSize = '80mm auto'
    let maxWidth = '320px'
    let padding = '8px'

    switch (receiptSize) {
      case '58mm':
        pageSize = '58mm auto'
        maxWidth = '220px'
        padding = '4px'
        break

      case 'A4':
        pageSize = 'A4'
        maxWidth = '800px'
        padding = '20px'
        break

      default:
        pageSize = '80mm auto'
        maxWidth = '320px'
        padding = '8px'
    }

    const styles = Array.from(document.styleSheets)
      .map(sheet => {
        try {
          return Array.from(sheet.cssRules)
            .map(rule => rule.cssText)
            .join('\n')
        } catch {
          return sheet.href
            ? `@import url("${sheet.href}");`
            : ''
        }
      })
      .join('\n')

    const win = window.open('', '_blank')

    win.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Receipt</title>

          <style>
            ${styles}

            * {
              overflow: visible !important;
              max-height: none !important;
              box-sizing: border-box;
            }

            body {
              background: white !important;
              display: flex;
              justify-content: center;
              padding: ${padding};
              margin: 0;
              font-family: 'Courier New', monospace;
            }

            #receipt-print-wrapper {
              width: 100%;
              max-width: ${maxWidth};
            }

            table {
              width: 100%;
              border-collapse: collapse !important;
            }

            thead tr {
              border-bottom: 2px solid #000 !important;
            }

            th {
              padding: 6px 4px !important;
              font-weight: 700 !important;
              font-size: 11px !important;
              border-bottom: 2px solid #000 !important;
            }

            td {
              padding: 6px 4px !important;
              font-size: 11px !important;
              border-bottom: 1px solid #d1d5db !important;
            }

            tbody tr:last-child td {
              border-bottom: none !important;
            }

            .border-t {
              border-top: 1px solid #d1d5db !important;
            }

            .border-b {
              border-bottom: 1px solid #d1d5db !important;
            }

            @media print {
              body {
                padding: 0;
              }

              @page {
                margin: 5mm;
                size: ${pageSize};
              }
            }
          </style>
        </head>

        <body>
          <div id="receipt-print-wrapper">
            ${content}
          </div>
        </body>
      </html>
    `)

    win.document.close()
    win.focus()

    setTimeout(() => {
      win.print()
      win.close()
    }, 600)

    emit('print', props.receiptData)

  } catch (error) {
    console.error('Print failed:', error)
    alert('Print failed. Please try again.')
  } finally {
    setTimeout(() => {
      isProcessing.value = false
    }, 1000)
  }
}
const handleProceed = () => {
  if (isProcessing.value) return
  emit('proceed', { ...props.receiptData, savedInvoiceName: savedInvoiceName.value })
}

// Generate receipt text for saving
const generateReceiptText = () => {
const lines = []
lines.push(`${props.storeName}`)
lines.push(`${props.storeAddress}`)
lines.push(`${props.storePhone}`)
lines.push(`${props.storeEmail}`)
lines.push(``)
lines.push(`Subtotal: ${formatPrice(summary.value.subtotal)}`)
if (summary.value.tax > 0) {
  lines.push(`Tax: ${formatPrice(summary.value.tax)}`)
}
if (summary.value.discount > 0) {
  lines.push(`Discount: -${formatPrice(summary.value.discount)}`)
}
lines.push(`Total: ${formatPrice(summary.value.total)}`)
lines.push(`Cash: ${formatPrice(summary.value.cash)}`)
lines.push(`Change: ${formatPrice(summary.value.change)}`)
lines.push(``)
lines.push(`Thank you for your visit!`)

return lines.join('\n')
}

const handleKeydown = (event) => {
  if (isProcessing.value) return
  if (event.key === 'Escape') handleClose()
  if (event.key === 'Enter') handleProceed()
  if (event.key === 'p' && !event.ctrlKey) handlePrint()
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
