<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div
        v-if="modelValue"
        class="settings-dialog-backdrop"
        @click.self="closeDialog"
      >
        <Transition name="dialog-slide">
          <div
            v-if="modelValue"
            class="settings-dialog"
            :class="isDark ? 'theme-dark' : 'theme-light'"
            role="dialog"
            aria-modal="true"
            aria-label="POS Settings"
          >
            <!-- ── Dialog Header ── -->
            <div class="dialog-header" :style="{ borderBottomColor: 'var(--card-border)' }">
              <div class="dialog-header-left">
                <div class="header-icon" :style="{ background: primaryColor + '22', color: primaryColor }">
                  <Settings class="w-5 h-5" />
                </div>
                <div>
                  <h2 class="dialog-title" :style="{ color: 'var(--text-main)' }">{{ __('System Settings') }}</h2>
                  <p class="dialog-subtitle" :style="{ color: 'var(--text-muted)' }">{{ __('POS Settings') }}</p>
                </div>
              </div>
              <div class="dialog-header-right">
                <button
                  @click="saveAllSettings"
                  class="btn-save"
                  :style="{ background: primaryColor }"
                  :disabled="isSaving"
                >
                  <Save class="w-4 h-4" />
                  {{ isSaving ? __('Saving...') : __('Save Settings') }}
                </button>
                <button
                  @click="closeDialog"
                  class="btn-close"
                  :style="{ color: 'var(--text-muted)', background: 'var(--item-bg)' }"
                >
                  <X class="w-5 h-5" />
                </button>
              </div>
            </div>

            <!-- ── Dialog Body ── -->
            <div class="dialog-body">
              <!-- Sidebar Nav -->
              <nav class="dialog-nav" :style="{ borderRightColor: 'var(--card-border)', background: 'var(--sidebar-bg)' }">
                <button
                  v-for="cat in settingsCategories"
                  :key="cat.id"
                  @click="activeCategory = cat.id"
                  class="nav-btn"
                  :class="{ 'nav-btn-active': activeCategory === cat.id }"
                  :style="activeCategory === cat.id
                    ? { background: primaryColor + '18', color: primaryColor, borderLeftColor: primaryColor }
                    : { color: 'var(--nav-item-color)', borderLeftColor: 'transparent' }"
                >
                  <component :is="cat.icon" class="w-4 h-4 flex-shrink-0" />
                  <span>{{ cat.name }}</span>
                  <span v-if="hasErrors(cat.id)" class="nav-error-dot" />
                </button>
              </nav>

              <!-- Content Panel -->
              <div class="dialog-content">

                <!-- ══ 1. Store Info ══ -->
                <section v-if="activeCategory === 'store'" class="settings-section">
                  <div class="section-header">
                    <Store class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Store Information') }}</h3>
                  </div>

                  <div class="form-grid">
                    <div class="form-group">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Store Name') }}</label>
                      <input
                        v-model="settings.store.name"
                        type="text"
                        :placeholder="__('Store Name')"
                        class="form-input"
                        :class="{ 'input-error': errors.storeName }"
                        :style="inputStyle"
                        @blur="validateStore"
                      />
                      <span v-if="errors.storeName" class="error-msg">{{ errors.storeName }}</span>
                    </div>

                    <div class="form-group">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Store Address') }}</label>
                      <input
                        v-model="settings.store.address"
                        type="text"
                        :placeholder="__('Store Address')"
                        class="form-input"
                        :class="{ 'input-error': errors.storeAddress }"
                        :style="inputStyle"
                        @blur="validateStore"
                      />
                      <span v-if="errors.storeAddress" class="error-msg">{{ errors.storeAddress }}</span>
                    </div>

                    <div class="form-group">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">
                        {{ __('Phone Number') }}
                      </label>

                      <div class="flex gap-2">

                        <!-- Flag selector -->
                        <div class="relative flex-shrink-0">
                          <select
                            v-model="selectedCountry"
                            class="form-input appearance-none pr-6 cursor-pointer"
                            style="width: 80px; text-align: center;"
                            :style="inputStyle"
                          >
                            <option v-for="c in countryList" :key="c.iso" :value="c">
                              {{ c.flag }} {{ c.iso }}
                            </option>
                          </select>
                          <svg class="absolute right-1.5 top-1/2 -translate-y-1/2 pointer-events-none w-3 h-3"
                            style="color: var(--text-muted);"
                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                            <path d="M6 9l6 6 6-6"/>
                          </svg>
                        </div>

                        <!-- Number input -->
                        <div class="relative flex-1">
                          <input
                            ref="inputRef"
                            v-model="rawPhone"
                            type="tel"
                            class="form-input w-full"
                            :class="{ 'input-error': errors.storePhone, 'input-valid': phoneInfo.valid }"
                            :style="inputStyle"
                            @blur="validateStore"
                          />
                          <svg v-if="phoneInfo.valid"
                            class="absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
                            style="color: #22c55e;"
                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                            <path d="M20 6L9 17l-5-5"/>
                          </svg>
                        </div>

                      </div>

                      <p v-if="phoneInfo.valid" class="text-[11px] mt-1" style="color: var(--text-muted);">
                        {{ phoneInfo.international }}
                      </p>

                      <span v-if="errors.storePhone" class="error-msg">{{ errors.storePhone }}</span>
                    </div>

                    <div class="form-group">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Email') }}</label>
                      <input
                        v-model="settings.store.email"
                        type="email"
                        placeholder="store@example.com"
                        class="form-input"
                        :class="{ 'input-error': errors.storeEmail }"
                        :style="inputStyle"
                        @blur="validateStore"
                      />
                      <span v-if="errors.storeEmail" class="error-msg">{{ errors.storeEmail }}</span>
                    </div>

                    <div class="form-group form-group-full">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Commercial Registration Number') }}</label>
                      <input
                        v-model="settings.store.taxId"
                        type="text"
                        :placeholder="__('Commercial Registration Number')"
                        class="form-input"
                        :class="{ 'input-error': errors.storeTaxId }"
                        :style="inputStyle"
                        @blur="validateStore"
                      />
                      <span v-if="errors.storeTaxId" class="error-msg">{{ errors.storeTaxId }}</span>
                    </div>
                  </div>
                </section>

                <!-- ══ 2. Receipt ══ -->
                <section v-if="activeCategory === 'receipt'" class="settings-section">
                  <div class="section-header">
                    <Receipt class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Receipt Settings') }}</h3>
                  </div>

                  <div class="toggle-list">
                    <div class="toggle-row" :style="toggleRowStyle">
                      <div>
                        <p class="toggle-label" :style="{ color: 'var(--text-sub)' }">{{ __('Show Store Logo on Receipt') }}</p>
                        <p class="toggle-desc" :style="{ color: 'var(--text-muted)' }">{{ __('Display your store logo on printed receipts') }}</p>
                      </div>
                      <ToggleSwitch v-model="settings.receipt.showLogo" />
                    </div>

                    <div class="toggle-row" :style="toggleRowStyle">
                      <div>
                        <p class="toggle-label" :style="{ color: 'var(--text-sub)' }">{{ __('Show Thank You Message') }}</p>
                        <p class="toggle-desc" :style="{ color: 'var(--text-muted)' }">{{ __('Add a thank you message at the bottom of receipts') }}</p>
                      </div>
                      <ToggleSwitch v-model="settings.receipt.showThankYou" />
                    </div>
                  </div>

                  <div class="form-group mt-4">
                    <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Custom Footer Message') }}</label>
                    <textarea
                      v-model="settings.receipt.footerMessage"
                      rows="3"
                      :placeholder="__('Thank you for your business!')"
                      class="form-input resize-none"
                      :style="inputStyle"
                    />
                  </div>

                  <div class="form-group mt-4">
                    <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Receipt Size') }}</label>
                    <select v-model="settings.printer.paperSize" class="form-input" :style="inputStyle">
                      <option value="80mm">{{ __('80mm (Thermal Printer)') }}</option>
                      <option value="58mm">{{ __('58mm (Small)') }}</option>
                      <option value="A4">{{ __('A4 (Standard)') }}</option>
                    </select>
                  </div>
                </section>

                <!-- ══ 3. Tax & Pricing ══ -->
                <section v-if="activeCategory === 'pricing'" class="settings-section">
                  <div class="section-header">
                    <BadgePercent class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Tax & Pricing') }}</h3>
                  </div>

                  <!-- Tax toggle -->
                  <div class="toggle-row mb-4" :style="toggleRowStyle">
                    <div>
                      <p class="toggle-label" :style="{ color: 'var(--text-sub)' }">{{ __('Enable Tax Calculation') }}</p>
                      <p class="toggle-desc" :style="{ color: 'var(--text-muted)' }">{{ __('Automatically calculate tax on transactions') }}</p>
                    </div>
                    <ToggleSwitch v-model="settings.pricing.enableTax" />
                  </div>

                  <div v-if="settings.pricing.enableTax" class="form-grid mb-4">
                    <div class="form-group">
                      <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Tax Category (%)') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <span>{{ settings.pricing.taxCategory || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                    </div>

                    <div class="form-group">
                      <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Tax Name') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <span>{{ settings.pricing.taxName || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                    </div>
                  </div>

                  <!-- Currency & Price List — read from POS Profile -->
                  <div class="info-banner mb-4" :style="{ background: primaryColor + '11', borderColor: primaryColor + '33' }">
                    <Info class="w-4 h-4 flex-shrink-0" :style="{ color: primaryColor }" />
                    <p class="text-xs" :style="{ color: 'var(--text-sub)' }">
                      {{ __('Currency and Price List are read from') }}
                      <a :href="`/desk/pos-profile/${posProfile.name}`" target="_blank" class="underline font-medium" :style="{ color: primaryColor }">POS Profile</a>
                      {{ __('and cannot be changed here.') }}
                    </p>
                  </div>

                  <div class="form-grid mb-4">
                    <div class="form-group">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Currency') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <DollarSign class="w-4 h-4" :style="{ color: 'var(--text-muted)' }" />
                        <span>{{ settings.pricing.currency || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                    </div>

                    <div class="form-group">
                      <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Price List') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <List class="w-4 h-4" :style="{ color: 'var(--text-muted)' }" />
                        <span>{{ settings.pricing.price_list || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                    </div>
                  </div>

                  <!-- Round Prices -->
                  <!-- <div class="form-group">
                    <label class="form-label required" :style="{ color: 'var(--text-sub)' }">{{ __('Round Prices') }}</label>
                    <div class="round-options">
                      <button
                        v-for="opt in roundOptions"
                        :key="opt.value"
                        @click="settings.pricing.roundMode = opt.value"
                        class="round-btn"
                        :class="{ 'round-btn-active': settings.pricing.roundMode === opt.value }"
                        :style="settings.pricing.roundMode === opt.value
                          ? { background: primaryColor, color: '#fff', borderColor: primaryColor }
                          : { background: 'var(--item-bg)', color: 'var(--text-sub)', borderColor: 'var(--item-border)' }"
                      >
                        <span class="round-example">{{ opt.example }}</span>
                        <span class="round-label">{{ opt.label }}</span>
                      </button>
                    </div>
                  </div> -->
                </section>

                <!-- ══ 4. Appearance ══ -->
                <section v-if="activeCategory === 'appearance'" class="settings-section">
                  <div class="section-header">
                    <Palette class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Appearance') }}</h3>
                  </div>

                  <div class="form-group mb-6">
                    <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Theme') }}</label>
                    <div class="theme-grid">
                      <div
                        v-for="t in themeOptions"
                        :key="t.value"
                        @click="settings.appearance.theme = t.value"
                        class="theme-card"
                        :class="{ 'theme-card-active': settings.appearance.theme === t.value }"
                        :style="settings.appearance.theme === t.value
                          ? { borderColor: primaryColor, background: primaryColor + '12' }
                          : { borderColor: 'var(--card-border)', background: 'var(--item-bg)' }"
                      >
                        <component :is="t.icon" class="w-6 h-6 mb-1" :style="{ color: t.value === 'dark' ? '#a0aec0' : '#f59e0b' }" />
                        <span class="text-sm font-medium" :style="{ color: 'var(--text-main)' }">{{ t.label }}</span>
                        <div v-if="settings.appearance.theme === t.value" class="theme-check" :style="{ background: primaryColor }">
                          <Check class="w-3 h-3 text-white" />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="form-group">
                    <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Primary Color') }}</label>
                    <div class="color-grid">
                      <button
                        v-for="color in colorOptions"
                        :key="color.value"
                        @click="settings.appearance.primaryColor = color.value"
                        class="color-dot"
                        :style="{ background: color.value }"
                        :title="color.name"
                      >
                        <Check
                          v-if="settings.appearance.primaryColor === color.value"
                          class="w-3.5 h-3.5 text-white drop-shadow"
                        />
                      </button>
                    </div>
                  </div>
                </section>

                <!-- ══ 5. Sound Effects ══ -->
                <section v-if="activeCategory === 'sound'" class="settings-section">
                  <div class="section-header">
                    <Volume2 class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Sound Effects') }}</h3>
                  </div>

                  <div class="toggle-list">
                    <div class="toggle-row" :style="toggleRowStyle">
                      <div>
                        <p class="toggle-label" :style="{ color: 'var(--text-sub)' }">{{ __('Enable Sound Effects') }}</p>
                        <p class="toggle-desc" :style="{ color: 'var(--text-muted)' }">{{ __('Play sounds on transactions and clicks') }}</p>
                      </div>
                      <ToggleSwitch v-model="settings.system.soundEffects" @update:modelValue="testSound" />
                    </div>
                  </div>

                  <div v-if="settings.system.soundEffects" class="sound-test-grid mt-4">
                    <button
                      v-for="sound in soundTests"
                      :key="sound.id"
                      @click="playSound(sound.freq, sound.duration, sound.type)"
                      class="sound-test-btn"
                      :style="{ background: 'var(--item-bg)', border: '1px solid var(--item-border)', color: 'var(--text-sub)' }"
                    >
                      <component :is="sound.icon" class="w-4 h-4" :style="{ color: primaryColor }" />
                      <span class="text-xs">{{ sound.label }}</span>
                    </button>
                  </div>
                </section>

                <!-- ══ 6. Printer ══ -->
                <section v-if="activeCategory === 'printer'" class="settings-section">
                  <div class="section-header">
                    <Printer class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Printer Settings') }}</h3>
                  </div>

                  <div class="form-grid mb-4">
                    <div class="form-group">
                      <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Printer Type') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <span>{{ settings.printer.printerType || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                      <span v-if="errors.printerType" class="error-msg">{{ errors.printerType }}</span>
                    </div>

                    <div class="form-group">
                      <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Printer IP') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <span>{{ settings.printer.printerIP || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                      <span v-if="errors.printerIP" class="error-msg">{{ errors.printerIP }}</span>
                    </div>

                    <div class="form-group">
                      <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Paper Width (mm)') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <span>{{ settings.printer.width || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                      <span v-if="errors.printerWidth" class="error-msg">{{ errors.printerWidth }}</span>
                    </div>

                    <div class="form-group">
                      <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Paper Height (mm)') }}</label>
                      <div class="readonly-field" :style="readonlyStyle">
                        <span>{{ settings.printer.height || '—' }}</span>
                        <Lock class="w-3.5 h-3.5 ml-auto" :style="{ color: 'var(--text-muted)' }" />
                      </div>
                    </div>
                  </div>

                 <div class="mb-4">
                  <button @click="testPrint" class="btn-test-print"
                    :style="{
                      background: 'var(--info-bg)',
                      border: '1px solid var(--info-border)',
                      color: 'var(--text-sub)',
                      padding: '.5rem 1rem',
                      borderRadius: '.625rem'
                    }"
                  >
                    <Printer class="w-4 h-4" :style="{ color: primaryColor }" />
                    {{ __('Test Print') }}
                  </button>
                </div>
                </section>

                <!-- ══ 7. Shortcuts ══ -->
                <section v-if="activeCategory === 'shortcuts'" class="settings-section">
                  <div class="section-header">
                    <Keyboard class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('Keyboard Shortcuts') }}</h3>
                  </div>

                  <div class="shortcuts-list">
                    <div
                      v-for="shortcut in keyboardShortcuts"
                      :key="shortcut.id"
                      class="shortcut-row"
                      :style="{ background: 'var(--item-bg)', border: '1px solid var(--item-border)' }"
                    >
                      <div class="shortcut-info">
                        <span class="shortcut-action" :style="{ color: 'var(--text-sub)' }">{{ shortcut.action }}</span>
                        <span
                          class="shortcut-status"
                          :style="{ color: shortcut.working ? '#10b981' : '#f59e0b' }"
                        >
                          {{ shortcut.working ? __('● Working') : __('● In Development') }}
                        </span>
                      </div>
                      <div class="shortcut-keys">
                        <kbd
                          v-for="(k, i) in shortcut.keys"
                          :key="i"
                          class="kbd"
                          :style="{ background: 'var(--kbd-bg)', color: 'var(--text-main)', borderColor: 'var(--card-border)' }"
                        >{{ k }}</kbd>
                      </div>
                    </div>
                  </div>

                  <div class="info-banner mt-4" :style="{ background: primaryColor + '11', borderColor: primaryColor + '33' }">
                    <Info class="w-4 h-4 flex-shrink-0" :style="{ color: primaryColor }" />
                    <p class="text-xs" :style="{ color: 'var(--text-sub)' }">
                      {{ __('Shortcuts work when the POS screen is open. Make sure no input field is focused when using Ctrl+F or Ctrl+N.') }}
                    </p>
                  </div>
                </section>

                <!-- ══ 8. System ══ -->
                <section v-if="activeCategory === 'system'" class="settings-section">
                  <div class="section-header">
                    <Cog class="w-5 h-5" :style="{ color: primaryColor }" />
                    <h3 class="section-title" :style="{ color: 'var(--text-main)' }">{{ __('System Settings') }}</h3>
                  </div>

                  <div class="toggle-list mb-6">
                    <div class="toggle-row" :style="toggleRowStyle">
                      <div>
                        <p class="toggle-label" :style="{ color: 'var(--text-sub)' }">{{ __('Offline Mode') }}</p>
                        <p class="toggle-desc" :style="{ color: 'var(--text-muted)' }">{{ __('Work offline when internet is not available') }}</p>
                      </div>
                      <ToggleSwitch v-model="settings.system.offlineMode" />
                    </div>
                  </div>

                  <!-- Language -->
                  <div class="form-group mb-6" style="border-top: 1px solid var(--divider); padding-top: 1rem;">
                    <label class="form-label text-sm font-medium" :style="{ color: 'var(--text-sub)' }">
                      {{ __('Language') }}
                    </label>

                    <div class="relative mt-2" ref="selectorRef">
                      <!-- Trigger -->
                      <button
                        @click="isOpen = !isOpen"
                        class="w-full flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-150 text-sm font-medium"
                        :class="isOpen
                          ? 'border-[var(--primary-400)] bg-[var(--card-bg)]'
                          : 'border-[var(--divider)] bg-[var(--input-bg)] hover:border-[var(--primary-300)]'"
                      >
                        <component :is="selectedOption?.flag" class="w-5 h-5" />
                        <span class="flex-1 text-left" :style="{ color: 'var(--text-main)' }">
                          {{ selectedOption?.label }}
                        </span>
                        <i
                          class="ti ti-chevron-down transition-transform duration-200"
                          :class="{ 'rotate-180': isOpen }"
                          :style="{ color: 'var(--text-sub)' }"
                        />
                      </button>

                      <!-- Dropdown -->
                      <Transition name="dropdown">
                        <div
                          v-if="isOpen"
                          class="absolute top-[calc(100%+6px)] left-0 right-0 z-50 rounded-xl border overflow-hidden"
                          :style="{
                            background: 'var(--card-bg)',
                            borderColor: 'var(--divider)',
                            boxShadow: '0 4px 24px rgba(0,0,0,0.08)'
                          }"
                        >
                          <button
                            v-for="opt in options"
                            :key="opt.value"
                            @mousedown.prevent="selectLanguage(opt.value)"
                            class="w-full flex items-center gap-3 px-4 py-3 text-sm transition-colors duration-100 text-left"
                            :class="[
                              settingsStore.settings.system.language === opt.value
                                ? 'bg-[var(--primary-50)]'
                                : 'hover:bg-[var(--hover-bg)]'
                            ]"
                          >
                            <component :is="opt.flag" class="w-5 h-5" />
                            <span class="flex-1">
                              <span class="block font-medium" :style="{ color: 'var(--text-main)' }">{{ opt.label }}</span>
                              <span class="block text-xs" :style="{ color: 'var(--text-sub)' }">{{ opt.native }}</span>
                            </span>
                            <i
                              v-if="settingsStore.settings.system.language === opt.value"
                              class="ti ti-check text-base"
                              :style="{ color: 'var(--primary-500)' }"
                            />
                          </button>
                        </div>
                      </Transition>
                    </div>
                  </div>
                  <!-- Items per page -->
                  <div class="form-group mb-6" style="border-top: 1px solid var(--divider); padding-top: 1rem;">
                    <label class="form-label" :style="{ color: 'var(--text-sub)' }">{{ __('Items Per Page') }}</label>
                    <div class="flex items-center gap-3 mt-1">
                      <input
                        v-model.number="settings.system.itemsPerPage"
                        type="number" min="10" max="100"
                        class="form-input w-24"
                        :style="inputStyle"
                      />
                      <span class="text-sm" :style="{ color: 'var(--text-muted)' }">{{ __('items') }}</span>
                    </div>
                  </div>
                  <!-- Data Management -->
                  <div style="border-top: 1px solid var(--divider); padding-top: 1rem;">
                    <p class="text-sm font-semibold mb-3" :style="{ color: 'var(--text-main)' }">{{ __('Data Management') }}</p>
                    <div class="data-actions-grid">
                      <button @click="creatSampleItems" class="data-btn data-btn-primary" :style="{ background: primaryColor }">
                        <Sparkles class="w-4 h-4" /> {{ __('Create Sample Data') }}
                      </button>
                      <button @click="exportData" class="data-btn" :style="{ background: 'var(--item-bg)', border: '1px solid var(--item-border)', color: 'var(--text-sub)' }">
                        <Download class="w-4 h-4" /> {{ __('Export Data') }}
                      </button>
                      <button @click="deleteSampleItems" class="data-btn" :style="{ background: 'var(--item-bg)', border: '1px solid var(--item-border)', color: 'var(--text-sub)' }">
                        <Trash2 class="w-4 h-4" /> {{ __('Delete Sample Items') }}
                      </button>
                      <button @click="clearAllData" class="data-btn data-btn-danger">
                        <RotateCcw class="w-4 h-4" /> {{ __('Reset All Data') }}
                      </button>
                    </div>
                  </div>
                </section>
              </div>
            </div>

            <!-- ── Saving Overlay ── -->
            <Transition name="dialog-fade">
              <div
                v-if="isSaving"
                class="saving-overlay"
              >
                <div class="saving-card" :style="{ background: 'var(--card-bg)', border: '1px solid var(--card-border)' }">
                  <div class="saving-spinner" :style="{ borderTopColor: primaryColor }" />
                  <p class="saving-text" :style="{ color: 'var(--text-main)' }">{{ __('Saving...') }}</p>
                </div>
              </div>
            </Transition>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick, toRaw } from 'vue'
import {
  Settings, Save, X, Store, Receipt, BadgePercent, Palette, Volume2,
  Printer, Keyboard, Cog, Sun, Moon, Check, Info, DollarSign, Lock,
  List, Sparkles, Download, Trash2, RotateCcw, ShoppingBag,
  Bell, BellOff, Music, Music2
} from 'lucide-vue-next'
import { useDark }          from '@vueuse/core'
import { useConfirm }       from '@/composables/useConfirm'
import ToggleSwitch         from '@/components/toggles/ToggleSwitch.vue'
import { useSettingsStore } from '@/stores/settings'
import { useProductsStore } from '@/stores/products'
import { useShiftStore } from '@/stores/shift'
import SaudiArabiaFlag from '@/components/icons/flag-saudi-arabia.svg'
import UnitedStatesFlag from '@/components/icons/flag-usa.svg'
import { useToast } from '@/composables/useToast'
import { storeToRefs } from 'pinia'
import { getCountries, getCountryCallingCode, AsYouType, parsePhoneNumber } from 'libphonenumber-js'
// ── Props & Emits ──
const props = defineProps({
  modelValue: { type: Boolean, default: false }
})
const emit = defineEmits(['update:modelValue'])

const { confirm } = useConfirm()
const { toast } = useToast()
const settingsStore = useSettingsStore()
const productsStore = useProductsStore()
const shiftStore = useShiftStore()
const isDark         = useDark({ selector: 'html', attribute: 'class', valueDark: 'dark', valueLight: '' })
const isSaving       = ref(false)
const activeCategory = ref('store')

const settings     = computed(() => settingsStore.settings)
const primaryColor = computed(() => settings.value?.appearance?.primaryColor || '#06b6d4')

// ── Language selector ──
const isOpen = ref(false)
const selectorRef = ref(null)

const options = [
  { label: 'English', native: 'English',  value: 'en', flag: UnitedStatesFlag },
  { label: 'Arabic',  native: 'العربية', value: 'ar', flag: SaudiArabiaFlag },
]

const selectedOption = computed(() =>
  options.find(o => o.value === settingsStore.settings.system.language)
  ?? options.find(o => o.value === 'en') // fallback لو فارغ
)

const selectLanguage = (lang) => {
  settingsStore.settings.system.language = lang
  isOpen.value = false
}

const handleClickOutside = (e) => {
  if (selectorRef.value && !selectorRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))
// ── Validation errors ──
const errors = ref({})

const hasErrors = (catId) => {
  const map = {
    store:   ['storeName', 'storeAddress', 'storePhone', 'storeEmail', 'storeTaxId'],
    pricing: ['taxCategory', 'taxName', 'currency', 'priceList'],
    printer: ['printerType', 'printerIP', 'printerWidth'],
  }
  return (map[catId] || []).some(k => errors.value[k])
}

// ──────── phone number ─────────────────────────────────────────────────────────

// ── Country list ──
const countryList = getCountries().map(code => ({
  iso:      code,
  flag:     code.toUpperCase().split('').map(c => String.fromCodePoint(0x1F1E6 + c.charCodeAt(0) - 65)).join(''),
  dialCode: '+' + getCountryCallingCode(code),
})).sort((a, b) => a.iso.localeCompare(b.iso))

// ── State ──
const selectedCountry = ref(countryList.find(c => c.iso === 'SA'))
const phoneNumber = ref('')
const rawPhone = ref('')
const inputRef        = ref(null)

watch(selectedCountry, (country) => {
  const local = rawPhone.value.replace(/^\+\d+\s*/, '')
  console.log("local", local)
  rawPhone.value = country.dialCode + ' ' + local
  console.log("RawPhone", rawPhone.value)
  nextTick(() => inputRef.value?.focus())
})


watch(
  () => settingsStore.settings.store.phone,
  (phone) => {

    if (!phone) return
    try {
    const parsed = parsePhoneNumber(phone, 'SA')
    if (!parsed) return

    selectedCountry.value = countryList.find(
      c => c.iso === parsed.country
    )

    rawPhone.value = phone.replace('/-/g', ' ')

    } catch{
      rawPhone.value = phone.replace('/-/g', ' ')
    }

  },
  { immediate: true }
)

const phoneInfo = computed(() => {
  const raw = rawPhone.value.replace(/\s/g, '')
  if (!raw || raw === selectedCountry.value?.dialCode) return { valid: false }
  try {
    const p = parsePhoneNumber(raw)
    console.log("p", p.isValid())
    console.log("p", p.formatInternational())
    console.log("p", p.formatNational())
    console.log("p", p.number.replace(/-/g, ''))
    console.log("p", p.country)
    return {
      valid:         p.isValid(),
      international: p.formatInternational(),
      national:      p.formatNational(),
      e164:          p.number.replace(/-/g, ''),  // ← هنا
      country:       p.country,
      phone:         `+${p.countryCallingCode}-${p.nationalNumber}`,
    }
  } catch { return { valid: false } }
})

watch(phoneInfo, (info) => {
  settingsStore.settings.store.phone = info.valid
    ? info.phone
    : rawPhone.value.replace(/\s/g, '')
}, { flush: 'sync' })

// ──────── validate Store ─────────────────────────────────────────────────────────

const validateStore = () => {
  const s = settings.value.store

  if (!s.name)    errors.value.storeName    = __('Store Name is required')
  else                    delete errors.value.storeName

  if (!s.address) errors.value.storeAddress = __('Address is required')
  else                    delete errors.value.storeAddress

  if (!s.phone)        errors.value.storePhone = __('Phone number is required')
  else if (!phoneInfo.value.valid) errors.value.storePhone = __('Invalid phone number (e.g. +966 50 000 0000)')
  else                         delete errors.value.storePhone

  if (!s.email)   errors.value.storeEmail   = __('Email is required')
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.email)) errors.value.storeEmail = __('Invalid email address')
  else                    delete errors.value.storeEmail

  if (!s.taxId) errors.value.storeTaxId = __('Commercial Registration Number is required')
  else          delete errors.value.storeTaxId
}

const validatePricing = () => {
  const p = settings.value.pricing
  if (p.enableTax) {
    if (!p.taxCategory) errors.value.taxCategory = __('Tax rate is required')
    else                               delete errors.value.taxCategory
    if (!p.taxName?.trim())            errors.value.taxName = __('Tax name is required')
    else                               delete errors.value.taxName
  } else {
    delete errors.value.taxCategory
    delete errors.value.taxName
  }
}

const validatePrinter = () => {
  const p = settings.value.printer
  if (!p.printerType)         errors.value.printerType  = __('Printer type is required')
  else                 delete errors.value.printerType
  if (!p.printerIP) errors.value.printerIP  = __('Printer IP is required')
  else                 delete errors.value.printerIP
  if (!p.width)        errors.value.printerWidth = __('Paper width is required')
  else                 delete errors.value.printerWidth
}

const validateAll = () => {
  errors.value = {}
  validateStore()
  validatePricing()
  return Object.keys(errors.value).length === 0
}

// ── Categories ──
const settingsCategories = computed(() => [
  { id: 'store',      name: __('Store Info'),      icon: Store },
  { id: 'receipt',    name: __('Receipt'),          icon: Receipt },
  { id: 'pricing',    name: __('Tax & Pricing'),    icon: BadgePercent },
  { id: 'appearance', name: __('Appearance'),       icon: Palette },
  { id: 'sound',      name: __('Sound Effects'),    icon: Volume2 },
  { id: 'printer',    name: __('Printer'),          icon: Printer },
  { id: 'shortcuts',  name: __('Shortcuts'),        icon: Keyboard },
  { id: 'system',     name: __('System'),           icon: Cog },
])

// ── Style helpers ──
const inputStyle = computed(() => ({
  background: 'var(--input-bg)',
  border: '1px solid var(--input-border)',
  color: 'var(--text-main)',
}))

const toggleRowStyle = computed(() => ({
  background: 'var(--info-bg)',
  border: '1px solid var(--info-border)',
}))

const readonlyStyle = computed(() => ({
  background: 'var(--item-bg)',
  border: '1px solid var(--item-border)',
  color: 'var(--text-muted)',
}))

// ── Options ──
const themeOptions = computed(() => [
  { value: 'light', label: __('Light Mode'), icon: Sun },
  { value: 'dark',  label: __('Dark Mode'),  icon: Moon },
])

const roundOptions = computed(() => [
  { value: 'none',    label: __('No Rounding'), example: '9.73' },
  { value: 'nearest', label: __('Nearest'),     example: '9.99' },
  { value: 'whole',   label: __('Whole Number'),example: '9.00' },
])

const colorOptions = [
  { name: 'Ocean Blue',      value: '#0a7ea4' },
  { name: 'Teal',            value: '#14b8a6' },
  { name: 'Emerald',         value: '#059669' },
  { name: 'Cyan',            value: '#06b6d4' },
  { name: 'Steel Blue',      value: '#2563eb' },
  { name: 'Indigo',          value: '#6366f1' },
  { name: 'Purple',          value: '#a855f7' },
  { name: 'Pink',            value: '#ec4899' },
  { name: 'Orange',          value: '#f97316' },
  { name: 'Amber',           value: '#FFB300' },
  { name: 'Gold',            value: '#D4AF37' },
  { name: 'Green',           value: '#10b981' },
  { name: 'Red',             value: '#ef4444' },
  { name: 'Graphite',        value: '#111827' },
  { name: 'Dusty Rose',      value: '#A1797A' },
  { name: 'Chocolate Mauve', value: '#5C3A3B' },
]

// ── Keyboard Shortcuts ──
const keyboardShortcuts = computed(() => [
  { id: 1, action: __('Complete Sale'),       keys: ['Enter'],       working: true  },
  { id: 2, action: __('Cancel Transaction'),  keys: ['Esc'],         working: true  },
  { id: 3, action: __('Quick Search'),        keys: ['Ctrl', 'F'],   working: false },
  { id: 4, action: __('New Transaction'),     keys: ['Ctrl', 'N'],   working: false },
  { id: 5, action: __('Save'),                keys: ['Ctrl', 'S'],   working: false },
  { id: 6, action: __('Print'),               keys: ['Ctrl', 'P'],   working: false },
])

// ── Sound Effects (Web Audio API) ──
const audioCtx = ref(null)

const getAudioCtx = () => {
  if (!audioCtx.value) {
    audioCtx.value = new (window.AudioContext || window.webkitAudioContext)()
  }
  return audioCtx.value
}

const playSound = (freq = 880, duration = 150, type = 'sine') => {
  try {
    const ctx        = getAudioCtx()
    const oscillator = ctx.createOscillator()
    const gainNode   = ctx.createGain()
    oscillator.connect(gainNode)
    gainNode.connect(ctx.destination)
    oscillator.type = type
    oscillator.frequency.setValueAtTime(freq, ctx.currentTime)
    gainNode.gain.setValueAtTime(0.3, ctx.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration / 1000)
    oscillator.start(ctx.currentTime)
    oscillator.stop(ctx.currentTime + duration / 1000)
  } catch (e) {
    console.error('Sound error:', e)
    toast({ title: __('Could not play sound'), icon: 'x', iconClasses: 'text-red-500' })
  }
}

const testSound = (val) => {
  if (val) playSound(660, 200, 'sine')
}

const soundTests = computed(() => [
  { id: 'sale',   label: __('Complete Sale'),  freq: 880,  duration: 200, type: 'sine',     icon: ShoppingBag },
  { id: 'scan',   label: __('Barcode Scan'),   freq: 1200, duration: 80,  type: 'square',   icon: Music },
  { id: 'error',  label: __('Error'),          freq: 220,  duration: 300, type: 'sawtooth', icon: BellOff },
  { id: 'notify', label: __('Notification'),   freq: 660,  duration: 150, type: 'triangle', icon: Bell },
])

// ── Printer Test ──
const testPrint = () => {
  const p = settings.value.printer
  if (!p.printerType || !p.printerIP) {
    toast({ title: __('Please enter printer details first'), icon: 'alert-triangle', iconClasses: 'text-yellow-500' })
    return
  }
  const w = window.open('', '_blank', `width=${p.width * 3},height=600`)
  if (!w) return
  w.document.write(`
    <html><head><title>${__('Test Print')}</title>
    <style>
      body { font-family: monospace; width: ${p.width}mm; margin: 0 auto; font-size: 12px; }
      .center { text-align: center; }
      .divider { border-top: 1px dashed #000; margin: 4px 0; }
    </style></head><body>
    <div class="center"><b>${settings.value.store?.name || __('Store')}</b></div>
    <div class="divider"></div>
    <div class="center">${__('Test Print')}</div>
    <div class="center">${new Date().toLocaleString()}</div>
    <div class="divider"></div>
    <div class="center">${__('Printer')}: ${p.printerIP} (${p.printerType})</div>
    <div class="center">${__('Width')}: ${p.width}mm</div>
    <div class="divider"></div>
    <div class="center">&#10003; ${__('Printer is working correctly')}</div>
    </body></html>
  `)
  w.document.close()
  setTimeout(() => { w.print(); w.close() }, 300)
}

// ── Save ──
const saveAllSettings = async () => {
  settingsStore.settings.store.phone = (phoneInfo.value.valid
      ? phoneInfo.value.e164
      : rawPhone.value
    ).replace(/\s/g, '').replace(/-/g, '')  // ← شيل - و spaces


  console.log('phone before validate:', settingsStore.settings.store.phone)
  const isValid = validateAll()
    console.log('errors:', JSON.stringify(errors.value))
  console.log("isValid", isValid)
  if (!isValid) {
    const firstErrorCat = ['store', 'pricing', 'printer'].find(c => hasErrors(c))
    if (firstErrorCat) activeCategory.value = firstErrorCat
    toast({ title: __('Please fill in all required fields'), icon: 'alert-triangle', iconClasses: 'text-yellow-500' })
    return
  }

  settingsStore.settings.store.phone = phoneInfo.value.valid
    ? phoneInfo.value.phone
    : rawPhone.value.replace(/\s/g, '')

  // احفظ اللغة القديمة قبل الحفظ
  const prevLang = localStorage.getItem('retail_language') || 'en'
  const newLang  = settingsStore.settings.system.language

  isSaving.value = true
  try {
    await new Promise(r => setTimeout(r, 600))
    settingsStore.saveSettings()
    toast({ title: __('Settings saved successfully'), icon: 'check', iconClasses: 'text-green-500' })

    // لو اللغة اتغيرت — reload بعد شوية عشان الـ toast يظهر
    if (prevLang !== newLang) {
      await new Promise(r => setTimeout(r, 800))
      location.reload()
    }
  } catch (e) {
    console.error('Save failed:', e)
    toast({ title: __('Failed to save settings'), icon: 'x', iconClasses: 'text-red-500' })
  } finally {
    isSaving.value = false
  }
}
// ── Theme watcher ──
watch(
  () => settings.value?.appearance?.theme,
  (theme) => {
    isDark.value = theme === 'dark'
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }
)

// ── Global keyboard handler ──
const handleKeydown = (e) => {
  if (!props.modelValue) return
  if (e.key === 'Escape')                        { closeDialog(); return }
  if (e.ctrlKey && e.key === 's')                { e.preventDefault(); saveAllSettings(); return }
  if (e.ctrlKey && e.key === 'f')                { e.preventDefault(); return }
  if (e.ctrlKey && e.key === 'n')                { e.preventDefault(); return }
  if (e.ctrlKey && e.key === 'p')                { e.preventDefault(); return }
}

watch(
  () => shiftStore.pos_profile,
  (profile) => {
    if (profile) {
      settingsStore.syncPOSSettings(profile)
    }
  },
  {
    immediate: true,
    deep: true
  }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  if (audioCtx.value) { audioCtx.value.close(); audioCtx.value = null }
})

// ── Data actions ──
const closeDialog = () => emit('update:modelValue', false)

const exportData = () => {
  try {
    const blob = new Blob(
      [JSON.stringify({ settings: settingsStore.settings, exportDate: new Date().toISOString(), version: '1.0' }, null, 2)],
      { type: 'application/json' }
    )
    const url = URL.createObjectURL(blob)
    const a   = Object.assign(document.createElement('a'), {
      href: url,
      download: `pos-backup-${new Date().toISOString().slice(0, 10)}.json`
    })
    document.body.appendChild(a); a.click(); document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast({ title: __('Data exported successfully'), icon: 'check', iconClasses: 'text-green-500' })
  } catch (e) { console.error(e) }
}
const { pos_profile } = storeToRefs(shiftStore)
const posProfile = computed(() => shiftStore.pos_profile)
watch(
  pos_profile,
  (profile) => {
    if (!profile) return

    console.log("profile ready", toRaw(profile))

    settingsStore.syncPOSSettings(toRaw(profile))
  },
  {
    immediate: true
  }
)

const clearAllData = async () => {
  const ok = await confirm({
    type: 'delete',
    title: __('Delete All Data'),
    message: __('This action cannot be undone.'),
    confirmLabel: __('Delete'),
  })
  if (!ok) return
  localStorage.clear()
  settingsStore.resetSettings(posProfile.value)
}

const creatSampleItems = async () => {
  const ok = await confirm({
    type: 'info',
    title: __('Create Sample Data'),
    message: __('Do you want to create sample items for testing?'),
    confirmLabel: __('Create'),
  })
  if (!ok) return
  await productsStore.createSampleData()
}

const deleteSampleItems = async () => {
  const ok = await confirm({
    type: 'delete',
    title: __('Delete Sample Items'),
    message: __('Are you sure you want to delete all sample items?'),
    confirmLabel: __('Delete'),
  })
  if (!ok) return
  await productsStore.deleteSampleData()
}
</script>

<style scoped>
/* ── Backdrop ── */
.settings-dialog-backdrop {
  position: fixed;
  inset: 0;
  z-index: 999;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

/* ── Dialog Shell ── */
.settings-dialog {
  width: 100%;
  max-width: 860px;
  height: 90vh;
  max-height: 700px;
  border-radius: 1.25rem;
  overflow: hidden;
  display: flex;
  position: relative;
  flex-direction: column;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  box-shadow: 0 32px 80px rgba(0,0,0,0.35);
}

/* ── Header ── */
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--card-border);
  flex-shrink: 0;
}
.dialog-header-left  { display: flex; align-items: center; gap: .75rem; }
.dialog-header-right { display: flex; align-items: center; gap: .5rem; }
.header-icon {
  width: 2.25rem; height: 2.25rem;
  border-radius: .625rem;
  display: flex; align-items: center; justify-content: center;
}
.dialog-title    { font-size: 1rem; font-weight: 700; line-height: 1.2; }
.dialog-subtitle { font-size: .7rem; }

.btn-save {
  display: flex; align-items: center; gap: .4rem;
  padding: .45rem 1rem;
  border-radius: .625rem;
  font-size: .8rem;
  font-weight: 600;
  color: #fff;
  transition: opacity .2s;
  cursor: pointer;
  border: none;
}
.btn-save:disabled          { opacity: .6; cursor: not-allowed; }
.btn-save:hover:not(:disabled) { opacity: .88; }

.btn-close {
  width: 2.1rem; height: 2.1rem;
  border-radius: .5rem;
  display: flex; align-items: center; justify-content: center;
  border: none; cursor: pointer;
  transition: opacity .15s;
}
.btn-close:hover { opacity: .7; }

/* ── Body ── */
.dialog-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ── Nav ── */
.dialog-nav {
  width: 11rem;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: .25rem;
  padding: .75rem .5rem;
  overflow-y: auto;
  border-right: 1px solid var(--card-border);
}

.nav-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: .5rem;
  padding: .5rem .65rem;
  border-radius: .5rem;
  border: none;
  border-left: 3px solid transparent;
  font-size: .78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all .15s;
  text-align: right;
  position: relative;
  background: transparent;
}
.nav-btn:hover { opacity: .85; }
.nav-error-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #f59e0b;
  margin-right: auto;
  flex-shrink: 0;
}

/* ── Content ── */
.dialog-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}

/* ── Sections ── */
.settings-section { animation: fadeIn .2s ease; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

.section-header {
  display: flex;
  align-items: center;
  gap: .5rem;
  margin-bottom: 1.25rem;
}
.section-title { font-size: 1rem; font-weight: 700; }

/* ── Forms ── */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: .875rem;
}
.form-group      { display: flex; flex-direction: column; gap: .35rem; }
.form-group-full { grid-column: 1 / -1; }

.form-label { font-size: .75rem; font-weight: 600; }
.form-label.required::after { content: ' *'; color: #ef4444; }

.form-input {
  padding: .45rem .75rem;
  border-radius: .5rem;
  font-size: .82rem;
  outline: none;
  transition: border-color .15s;
  width: 100%;
}
.form-input:focus { border-color: v-bind(primaryColor) !important; }
.input-error      { border-color: #ef4444 !important; }
.error-msg        { font-size: .7rem; color: #ef4444; }

/* ── Toggles ── */
.toggle-list { display: flex; flex-direction: column; gap: .5rem; }
.toggle-row  {
  display: flex; align-items: center; justify-content: space-between;
  padding: .65rem .875rem;
  border-radius: .625rem;
  gap: 1rem;
}
.toggle-label { font-size: .8rem; font-weight: 600; }
.toggle-desc  { font-size: .7rem; margin-top: .15rem; }

/* ── Readonly field ── */
.readonly-field {
  display: flex; align-items: center; gap: .5rem;
  padding: .45rem .75rem;
  border-radius: .5rem;
  font-size: .82rem;
  cursor: not-allowed;
}

/* ── Round options ── */
.round-options { display: flex; gap: .5rem; flex-wrap: wrap; }
.round-btn {
  display: flex; flex-direction: column; align-items: center;
  padding: .5rem .875rem;
  border-radius: .625rem;
  border: 1px solid;
  cursor: pointer;
  transition: all .15s;
  gap: .15rem;
}
.round-example { font-size: .9rem; font-weight: 700; font-family: monospace; }
.round-label   { font-size: .65rem; }

/* ── Theme grid ── */
.theme-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .625rem; }
.theme-card {
  position: relative;
  display: flex; flex-direction: column; align-items: center;
  padding: .875rem;
  border-radius: .75rem;
  border: 2px solid;
  cursor: pointer;
  transition: all .15s;
}
.theme-check {
  position: absolute; top: .4rem; right: .4rem;
  width: 1.1rem; height: 1.1rem;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}

/* ── Color grid ── */
.color-grid { display: flex; flex-wrap: wrap; gap: .5rem; }
.color-dot {
  width: 2rem; height: 2rem;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform .15s, box-shadow .15s;
}
.color-dot:hover { transform: scale(1.15); box-shadow: 0 0 0 3px rgba(0,0,0,.15); }

/* ── Sound tests ── */
.sound-test-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .5rem; }
.sound-test-btn {
  display: flex; flex-direction: column; align-items: center; gap: .35rem;
  padding: .625rem .5rem;
  border-radius: .625rem;
  cursor: pointer;
  transition: opacity .15s;
  font-size: .72rem;
}
.sound-test-btn:hover { opacity: .8; }

/* ── Printer test btn ── */
.btn-test-print {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .5rem;
  border-radius: .625rem;
  cursor: pointer;
  font-size: .82rem;
  font-weight: 500;
  transition: opacity .15s;
  padding: .5rem 1rem;   /* ← ضيف ده */
}
.btn-test-print:hover { opacity: .8; }

/* ── Shortcuts ── */
.shortcuts-list { display: flex; flex-direction: column; gap: .4rem; }
.shortcut-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: .625rem .875rem;
  border-radius: .625rem;
}
.shortcut-info   { display: flex; flex-direction: column; gap: .1rem; }
.shortcut-action { font-size: .82rem; font-weight: 600; }
.shortcut-status { font-size: .65rem; }
.shortcut-keys   { display: flex; align-items: center; gap: .3rem; }
.kbd {
  display: inline-flex; align-items: center; justify-content: center;
  padding: .2rem .45rem;
  border-radius: .3rem;
  border: 1px solid;
  font-size: .7rem;
  font-family: monospace;
  font-weight: 600;
  white-space: nowrap;
}
/* ── Data actions ── */
.data-actions-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .5rem; }
.data-btn {
  display: flex; align-items: center; justify-content: center; gap: .4rem;
  padding: .55rem .75rem;
  border-radius: .625rem;
  font-size: .78rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity .15s;
  border: none;
}
.data-btn:hover       { opacity: .85; }
.data-btn-primary     { color: #fff; }
.data-btn-danger      { background: var(--item-bg); border: 1px solid var(--item-border); color: #ef4444; }

/* ── Info banner ── */
.info-banner {
  display: flex; align-items: flex-start; gap: .5rem;
  padding: .625rem .875rem;
  border-radius: .625rem;
  border: 1px solid;
}

/* ── Transitions ── */
.dialog-fade-enter-active, .dialog-fade-leave-active { transition: opacity .25s ease; }
.dialog-fade-enter-from,   .dialog-fade-leave-to     { opacity: 0; }

.dialog-slide-enter-active { transition: all .3s cubic-bezier(.34,1.56,.64,1); }
.dialog-slide-leave-active { transition: all .2s ease; }
.dialog-slide-enter-from   { opacity: 0; transform: scale(.93) translateY(16px); }
.dialog-slide-leave-to     { opacity: 0; transform: scale(.96) translateY(8px); }

/* ── Scrollbar ── */
.dialog-content::-webkit-scrollbar,
.dialog-nav::-webkit-scrollbar         { width: 4px; }
.dialog-content::-webkit-scrollbar-track,
.dialog-nav::-webkit-scrollbar-track   { background: transparent; }
.dialog-content::-webkit-scrollbar-thumb,
.dialog-nav::-webkit-scrollbar-thumb   { background: var(--card-border); border-radius: 4px; }

@media (max-width: 640px) {
  .settings-dialog  { max-width: 100%; height: 100vh; max-height: 100vh; border-radius: 0; }
  .dialog-nav       { width: 2.75rem; }
  .nav-btn span     { display: none; }
  .form-grid        { grid-template-columns: 1fr; }
  .sound-test-grid  { grid-template-columns: repeat(2, 1fr); }
}


.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
.saving-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  background: rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1.25rem;
}
.saving-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: .75rem;
  padding: 1.5rem 2.5rem;
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.saving-spinner {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 3px solid var(--card-border);
  border-top-color: inherit;
  animation: spin .7s linear infinite;
}
.saving-text {
  font-size: .9rem;
  font-weight: 600;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
