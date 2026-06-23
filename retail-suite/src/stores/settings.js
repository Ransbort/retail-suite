// stores/settings.js
import { defineStore } from "pinia";
import { reactive, watch, toRaw } from "vue";
import { useShiftStore } from "./shift";
import { changeLanguage } from "@/i18n/index";
import { createResource } from "frappe-ui";

function hexToHsl(hex) {
  let r = parseInt(hex.slice(1, 3), 16) / 255;
  let g = parseInt(hex.slice(3, 5), 16) / 255;
  let b = parseInt(hex.slice(5, 7), 16) / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;
  if (max === min) {
    h = s = 0;
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }
  return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
}

function hslToHex(h, s, l) {
  s /= 100; l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  const toHex = (x) => { const hex = Math.round(255 * f(x)).toString(16); return hex.length === 1 ? "0" + hex : hex; };
  return `#${toHex(0)}${toHex(8)}${toHex(4)}`.toUpperCase();
}

function applyColorShades(hexColor) {
  const { h, s } = hexToHsl(hexColor);
  const lightnessMap = { 50: 95, 100: 90, 200: 80, 300: 70, 400: 60, 500: 50, 600: 45, 700: 35, 800: 25, 900: 15 };
  Object.entries(lightnessMap).forEach(([level, targetL]) => {
    document.documentElement.style.setProperty(`--primary-${level}`, hslToHex(h, s, targetL));
  });
}

function applyFontSize(size) {
  const fontSizeMap = { small: "14px", normal: "16px", large: "18px" };
  document.documentElement.style.setProperty("--base-font-size", fontSizeMap[size] || "16px");
}

function applyTheme(theme) {
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
}

function applyVisualSettings(appearance) {
  applyColorShades(appearance.primaryColor);
  applyFontSize(appearance.fontSize);
  applyTheme(appearance.theme);
}

export const useSettingsStore = defineStore("settings", () => {

  const shiftStore = useShiftStore();

  const settings = reactive({
    store: {
      name:         "",
      storeLogo:    "",
      address:      "",
      phone:        "",
      email:        "",
      taxId:        "",
    },
    receipt: {
      showLogo:      true,
      showThankYou:  true,
      footerMessage: "",
    },
    pricing: {
      enableTax:   false,
      taxCategory: "",
      taxName:     "",
      currency:    "",
      price_list:  "",
      roundPrices: false,
    },
    appearance: {
      theme:        "light",
      primaryColor: "#06b6d4",
    },
    printer: {
      printerIP:      "",
      paperSize:      "",
      printerPort:    "",
      printerType:    "",
      width:           80,
      height:          0,
    },
    system: {
      offlineMode:       false,
      soundEffects:      true,
      language:          "en",
      itemsPerPage:      20,
    },
  });

const syncPOSSettings = (p) => {
    console.log("p.posa_paper_size",p.posa_paper_size)
    if (!p) {
      console.warn("No POS profile to sync")
      return
    }
    // Store
    settings.store.name = p.posa_store_name || "";
    settings.store.storeLogo = p.posa_store_logo || "";
    settings.store.address = p.posa_store_address || "";
    settings.store.phone = (p.posa_store_phone ?? "")|| "";
    settings.store.email = p.posa_store_email || "";
    settings.store.taxId   = p.posa_tax_id || "";

    // Receipt
    settings.receipt.showLogo      = Boolean(p.posa_show_store_logo);
    settings.receipt.showThankYou  = Boolean(p.posa_show_thank_you);
    settings.receipt.footerMessage = p.posa_footer_message || "";

    // Appearance
    settings.appearance.theme        = p.posa_theme         || "light";
    settings.appearance.primaryColor = p.posa_primary_color || "#06b6d4";

    // Pricing
    settings.pricing.price_list = p.selling_price_list  || "";
    settings.pricing.currency   = p.currency            || "";
    settings.pricing.taxName    = p.taxes_and_charges   || "";
    settings.pricing.taxCategory = p.tax_category        || "";
    settings.pricing.enableTax  = Boolean(p.posa_tax_inclusive);

    // Printer
    settings.printer.printerIP        = p.posa_printer_ip || "";
    settings.printer.paperSize        = p.posa_paper_size || "";
    settings.printer.printerPort      = p.posa_printer_port || "";
    settings.printer.printerType      = p.posa_printer_type || "";
    settings.printer.width            = p.posa_paper_width || 80;
    settings.printer.height           = p.posa_paper_height || 0;

    // System
    settings.system.offlineMode       = Boolean(p.posa_offline_mode);
    settings.system.soundEffects      = Boolean(p.posa_sound_effects);
    settings.system.language          = p.posa_language      || "en";
    settings.system.itemsPerPage      = p.posa_items_per_page || 20;

    applyVisualSettings(settings.appearance);
  };

  const saveToPOSProfile = async () => {
    if (!shiftStore.pos_profile?.name) {
      console.warn("❌ no pos_profile — cannot save");
      return;
    }
    console.log("Names",shiftStore.pos_profile.name)
    const posProfileResource = createResource({
      url: "retail.retail.api.setting.update_pos_profile_settings",
    });

    await posProfileResource.submit({
      pos_profile_name: shiftStore.pos_profile.name,

      settings: JSON.stringify({
        // Store
        posa_store_name:            settings.store.name,
        posa_store_logo:            settings.store.storeLogo,
        posa_store_address:         settings.store.address,
        posa_store_phone:           settings.store.phone,
        posa_store_email:           settings.store.email,
        posa_tax_id: settings.store.taxId ? parseInt(settings.store.taxId) : 0,
        // Receipt
        posa_show_store_logo:       settings.receipt.showLogo,
        posa_show_thank_you:        settings.receipt.showThankYou,
        posa_footer_message:        settings.receipt.footerMessage,
        // Appearance
        posa_theme:                 settings.appearance.theme,
        posa_primary_color:         settings.appearance.primaryColor,
        // Pricing
        selling_price_list:         settings.pricing.price_list,
        currency:                   settings.pricing.currency,
        taxes_and_charges:          settings.pricing.taxName,
        tax_category:               settings.pricing.taxCategory,
        posa_tax_inclusive:         settings.pricing.enableTax,
        // Printer
        posa_printer_ip:            settings.printer.printerIP,
        posa_printer_port: settings.printer.printerPort ? parseInt(settings.printer.printerPort) : 0,
        posa_printer_type:          settings.printer.printerType,
        posa_paper_size:            settings.printer.paperSize,
        posa_paper_width:           settings.printer.width,
        posa_paper_height:          settings.printer.height,
        // System
        posa_items_per_page:        settings.system.itemsPerPage,
        posa_offline_mode:          settings.system.offlineMode,
        posa_sound_effects:         settings.system.soundEffects,
        posa_language:              settings.system.language,
      }),
    });

    console.log("posa_tax_id",settings.store.taxId)
  };

  const saveSettings = async () => {
    try {
      changeLanguage(settings.system.language);
      applyVisualSettings(settings.appearance);
      await saveToPOSProfile();
      return true;
    } catch (e) {
      console.error("❌ saveSettings failed:", e);
      return false;
    }
  };

  const updateSettings = async (patch) => {
    for (const section of Object.keys(patch)) {
      if (settings[section]) {
        Object.assign(settings[section], patch[section])
      }
    }
    await saveSettings()
  }

  const resetSettings = (profile) => {
    syncPOSSettings(profile);
    applyVisualSettings(settings.appearance);
  };

  return {
    settings,
    saveSettings,
    updateSettings,
    resetSettings,
    applyVisualSettings,
    syncPOSSettings,
    saveToPOSProfile,
  };
});
