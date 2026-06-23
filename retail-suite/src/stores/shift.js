import { defineStore } from 'pinia'
import { toRaw } from 'vue'
import {call, createResource, createListResource, createDocumentResource} from 'frappe-ui'
import { cacheOfflineData } from '@/db/sync'
import { db } from '@/db/indexedDB'
import { isOffline } from '@/db/network'
import { session } from '@/services/auth'
import { useCartStore } from './cart'
export const useShiftStore = defineStore('shift', {
  state: () => ({
    availableShifts: [],
    currentShift: null,
    pos_profile: null,
    warehouses: [],
    products: [],
    company: null,
    pos_profile_name:null,
    pos_opening_shift: null,
    closingShift: null,
    // Actions
    currentCustomer: null,
    pos_profiles_list: [],
    CurrentUserInfo: null,
    shifts: [],
    customers: [],
    summary: null,
    isShiftOpen: false,
    statistics: {},
    users: [],
    showOpeningVoucherDialog: false,
    payment_methods: [],
    _currentUserResource: null,
    _userDocResource: null,
  }),

  getters: {

    currentShiftInfo: (state) => {
      if (!state.currentShift) return null

      return {
        ...state.currentShift,
        duration: state.currentShift.period_start_date ?
          Date.now() - new Date(state.currentShift.period_start_date).getTime() : 0,
        isActive: state.isShiftOpen
      }
    },

    // Calculate expected cash
    expectedCash: (state) => {
      if (!state.currentShift) return 0

      return (state.currentShift.openingBalance || 0) +
        (state.currentShift.totalSales || 0)
    },

    // Calculate cash difference
    cashDifference: (state) => {
      if (!state.currentShift || !state.currentShift.closingBalance) return 0

      const expected = (state.currentShift.openingBalance || 0) +
        (state.currentShift.totalSales || 0)
      const actual = state.currentShift.closingBalance || 0

      return actual - expected
    },

    // Today's shifts
    todaysShifts: (state) => {
      const today = new Date().toDateString()
      return state.shifts.filter(shift =>
        new Date(shift.period_start_date).toDateString() === today
      )
    },

    // Shift statistics
    shiftStats: (state) => {
      if (!state.currentShift) return null

      return {
        transactionCount: state.currentShift.transactions?.length || 0,
        totalSales: state.currentShift.totalSales || 0,
        averageTransaction: state.currentShift.transactions?.length > 0 ?
          (state.currentShift.totalSales || 0) / state.currentShift.transactions.length : 0,
        duration: state.currentShift.period_start_date ?
          Date.now() - new Date(state.currentShift.period_start_date).getTime() : 0
      }
    }
  },

  actions: {

    async setCustomer(customer) {
      this.currentCustomer = customer
    },

    async getAvailablePosprofiles(company, currency) {
      try {
          const posProfiles = await call('retail.retail.api.payment_entry.get_available_pos_profiles',
            {company,currency}
          )

          this.pos_profiles_list = posProfiles
      }
      catch (error) {
          console.error("❌ Get POS Profiles error:", error)
      }
    },
    // في الـ store — فنكشن جديدة مش بتأثر على القديمة
   async getCurrentUser(){
        // frappe.session.user دايماً موجود
        return frappe.session.user || null
    },
    async get_user_opening_shift(user){
        try {
            const response = await call('retail.retail.api.shifts.check_opening_shift',
                {user: user}
                );
            console.log('Api Get User Opening Shift:', response);
            return response;
        } catch (error) {
            console.error('Error Api Get User Opening Shift:', error);
            throw error;
        }

    },

    async get_shift_summary(pos_opening_shift) {
        try {
            const shiftParam =
                typeof pos_opening_shift === 'string'
                    ? pos_opening_shift
                    : pos_opening_shift.name;

            const response = await call(
                'retail.retail.doctype.pos_closing_shift.pos_closing_shift.get_shift_summary',
                { pos_opening_shift_name: shiftParam }

            );

            console.log('API Get Shift Summary:', response);
            return response;
        } catch (error) {
            console.error('Error API Get Shift Summary:', error);
            throw error;
        }
    },

    // need refactor u can get user from session this getCurrentUserInfo not needed
    // refactor: is it needed to git summary of this shiftممكن نعزل النفكشن عناها
    // refactor: get_shift_summaryهل ممكن نعزله ولا لازم تكون جوه الفنكشن
    async loadActiveShifts() {
      try {

        if (this.isShiftOpen && this.currentShift) {
          console.log('✅ Shift already loaded, skipping...')
          return true
        }

        const currentUser = session.user
        if (!currentUser) {
            console.warn('⚠️ No logged user')
            this.showOpeningVoucherDialog = true
            return false
        }
        const result = await this.get_user_opening_shift(currentUser);

        console.log('Result:', result)

         if (!result || result.count === 0) {
            this.isShiftOpen             = false
            this.currentShift            = null
            this.showOpeningVoucherDialog = true
            return false
        }else{
            this.availableShifts          = result.shifts
            this.showShiftSelectionDialog = true
            return true
        }
      } catch (error) {
        console.error('Error fetching opening shift:', error);
        this.isShiftOpen = false
        this.showOpeningVoucherDialog = true
        return false
      }
    },

    async setActiveShift(shiftData) {
        this.pos_profile      = shiftData.pos_profile || null
        this.pos_profile_name = shiftData.pos_profile?.name || null
        this.pos_opening_shift = shiftData.pos_opening_shift || null

        const shift          = this.pos_opening_shift || {}
        const balanceDetails = shift.balance_details || []
        const openingBalance = balanceDetails.reduce((sum, b) => sum + (b.amount || 0), 0)

        if (shift.name) {
            this.summary = await this.get_shift_summary(shift.name)
        }

        this.currentShift = {
            name:             shift.name,
            user:             shift.user,
            company:          shift.company,
            pos_profile:      shift.pos_profile,
            period_start_date: shift.period_start_date,
            period_end_date:  shift.period_end_date || null,
            status:           shift.status,
            posting_date:     shift.posting_date,
            posting_time:     shift.posting_time,
            all:              shift,
            openingBalance,
            totalSales:       this.summary?.total_sales || 0,
            closingBalance:   0,
            transactions:     this.summary?.transactions || [],
            balance_details:  balanceDetails,
            payments:         this.summary?.payments || []
        }

        this.isShiftOpen             = true
        this.showOpeningVoucherDialog = false
        this.showShiftSelectionDialog = false

        await cacheOfflineData(
            this.pos_profile,
            this.getItemsFromFrappeDB.bind(this),
            this.getCustomers.bind(this),
        )
        this.set_payment_methods()
        try {
            const taxData = await call(
              'retail.retail.api.invoice.get_pos_profile_taxes',
              { pos_profile_name: this.pos_profile.name }
            )
            const cartStore = useCartStore()
            cartStore.applyPOSProfileTax(taxData)
          } catch (e) {
            console.error('Could not load POS taxes:', e)
        }
        this.getAvailablePosprofiles(this.pos_profile.company, this.pos_profile.currency)
    },

    async getOpeningDialogData() {
        try {
            const response = await call('retail.retail.api.shifts.get_opening_dialog_data');
            console.log('Api Get Opening Dialog Data:', response);
            return response;
        }
        catch (error) {
            console.error('Error Api Get Opening Dialog Data:', error);
            throw error;
        }
    },

    async openShift(shiftData){
        try {
          const response = await call('retail.retail.api.shifts.create_opening_voucher',
              {
                  pos_profile: shiftData.pos_profile,
                  company: shiftData.company,
                  balance_details: shiftData.balance_details
              }
          );
          console.log('Api Open Shift:', response);
          return response;
        } catch (error) {
            console.error('Error Api opening shift:', error);
            throw error;
        }
    },

    set_payment_methods() {

      if (!this.pos_profile.posa_allow_make_new_payments) return;
      this.payment_methods = [];

      this.pos_profile.payments.forEach((method) => {
        this.payment_methods.push({
          row_id: method.name,
          mode_of_payment: method.mode_of_payment,
          default: method.default,
          allow_in_returns: method.allow_in_returns,
          amount: 0
        });
      });
    },

    setShowOpeningVoucherDialog(value) {
      this.showOpeningVoucherDialog = value
    },

    async fetchShiftStatistics() {
      try {
        const stats = await call('retail.retail.api.shifts.get_shift_statistics');
        this.statistics = stats || {}
        return this.statistics
      } catch (error) {
        console.error('Error fetching shift statistics:', error)
      }
    },
    async closingOpenShift(opening_shift, closing_details) {
      try {
        const closing_shift = await call('retail.retail.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening', {
            opening_shift: opening_shift,
            closing_details: closing_details
        });
        console.log('Closing shift created:', closing_shift);
        this.pos_opening_shift = null
        return closing_shift;
      } catch (error) {
        console.error('Error creating closing shift:', error);
        throw error;
      }
    },

    // Get shift by ID
    getShiftById(name) {
      return this.shifts.find(shift => shift.name === name)
    },

    // Get shifts by date range
    getShiftsByDateRange(startDate, endDate) {
      const start = new Date(startDate).getTime()
      const end = new Date(endDate).getTime()

      return this.shifts.filter(shift => {
        const shiftDate = new Date(shift.period_start_date).getTime()
        return shiftDate >= start && shiftDate <= end
      })
    },

    // Calculate shift duration
    getShiftDuration(shift) {
      const start = new Date(shift.period_start_date)
      const end = shift.period_end_date ? new Date(shift.period_end_date) : new Date()

      return end.getTime() - start.getTime()
    },

    // Format shift duration
    formatShiftDuration(shift) {
      const duration = this.getShiftDuration(shift)
      console.log('duration (ms):', duration)
      const hours = Math.floor(duration / (3600000))
      const minutes = Math.floor((duration % (3600000)) / (60000))
      const seconds = Math.floor((duration % (60000)) / 1000)
      return `${hours}h ${minutes}m ${seconds}s`
    },

    // Validate shift operations
    validateShiftOperation(operation, data = {}) {
      const validations = {
        open: () => {
          if (this.isShiftOpen) {
            return { valid: false, message: 'There is already an open shift' }
          }
          if (!data.userId) {
            return { valid: false, message: 'User is required' }
          }
          if (data.openingBalance < 0) {
            return { valid: false, message: 'Opening balance cannot be negative' }
          }
          return { valid: true }
        },

        close: () => {
          if (!this.isShiftOpen) {
            return { valid: false, message: 'No active shift to close' }
          }
          if (data.closingBalance < 0) {
            return { valid: false, message: 'Closing balance cannot be negative' }
          }
          return { valid: true }
        }
      }

      return validations[operation] ? validations[operation]() : { valid: true }
    },

    // Export shift data
    async exportShiftData(shiftId = null) {
      try {
        const shiftsToExport = shiftId ?
        [this.getShiftById(shiftId)].filter(Boolean) :
        this.shifts

        const exportData = {
          shifts: shiftsToExport,
          exportedAt: new Date().toISOString(),
          exportedBy: this.currentShift?.userName || 'System',
          totalShifts: shiftsToExport.length,
          dateRange: {
            from: shiftsToExport.length > 0 ?
              shiftsToExport[shiftsToExport.length - 1].period_start_date : null,
            to: shiftsToExport.length > 0 ?
              shiftsToExport[0].period_start_date : null
          }
        }

        return exportData
      } catch (error) {
        console.error('Failed to export shift data:', error)
        throw error
      }
    },

    async getCustomers(pos_profile) {
      try {
          if (isOffline.value) {
              return await db.customers.toArray()
          }

          const response = await call('retail.retail.api.posapp.get_customer_names',
              { pos_profile: pos_profile}
          )
          console.log("API Get Customers from Frappe DB", response)
          this.customers = response
          return response
      }
      catch (error) {
         if (error instanceof TypeError && error.message.includes('NetworkError')) {
            console.log('📴 Network error, falling back to IndexedDB')
            return await db.customers.toArray()
          }
          console.error("❌ Error API Get Customers from Frappe DB:", error)
      }
    },

    async createUpdateCustomer(args) {
          const {
        method = 'create',
        customer_id,
        customer_name,
        pos_profile_doc,
        company,
        first_mobile,
        second_mobile,
        email_id,
        city,
        address_line1,
        address_line2,
        state,
        country,
        pincode,
        first_name,
        last_name,
        customer_group,
        territory,
        customer_type,
        gender,
        note,
      } = args
      try{
        const res = await call('retail.retail.api.posapp.create_customer', {
          method,
          customer_id    : customer_id   || '',
          customer_name,
          pos_profile_doc: typeof pos_profile_doc === 'string'
                            ? pos_profile_doc
                            : JSON.stringify(pos_profile_doc || {}),
          company        : company       || '',
          first_mobile   : first_mobile  || '',
          second_mobile  : second_mobile || '',
          email_id       : email_id      || '',
          city           : city          || '',
          address_line1  : address_line1 || '',
          address_line2  : address_line2 || '',
          state          : state         || '',
          country        : country       || 'Egypt',
          pincode        : pincode       || '',
          first_name     : first_name    || '',
          last_name      : last_name     || '',
          customer_group : customer_group || '',
          territory      : territory      || '',
          customer_type  : customer_type  || 'Individual',
          gender         : gender         || '',
          note           : note           || '',
        })
        console.log("✅ API Create Update Customer in Frappe DB:", res)
        return res

      }catch (e){
        console.error("❌ Error Api Create Update Customer in Frappe DB:", e)
      }
    },

    async getItemsFromFrappeDB(
      currentPOSProfile,
      currentPriceList,
      currentCustomer,
      searchValue = '',
      selectedWarehouse = null
    ){
      try {
        const response = await call('retail.retail.api.posapp.get_items',{
                        pos_profile: JSON.stringify(currentPOSProfile),
                        price_list: currentPriceList,
                        search_value: searchValue,
                        item_group: '',
                        customer: currentCustomer,
                        warehouse: selectedWarehouse || '',
                    })


        const items = response?.message || response || []
        console.log("response items",items)
        return items
      } catch (error) {
        console.error('❌ getItemsFromFrappeDB:', error)
        return []
      }
    },

    async loadWarehouses(){
        error.value = null
        console.log("loadWarehouses", pos_profile)
        try{
            const resource = createListResource({
                doctype: 'Warehouse',
                fields: JSON.stringify(["name"]),
                filters: JSON.stringify({company: pos_profile.company}),
                auto: true,
                debug: 0,
            })
             resource.fetch()
            await resource.list.promise
            console.log("API Get Notifications: ", resource.data)
            warehouses.value = resource.data || []
            return resource.data || []
        }catch(error){
            console.log("error",error)
        }
    },
    async getShiftDetails(shift_id){
        try {
            const response = await call('retail.retail.api.shifts.get_shift_details',
                { shift_id }
            );
            console.log('API Get Shift Dtails:', response);
            return response;

        } catch (error) {
            console.error('Error API Get Shift Dtails:', error);
            throw error;
        }

    }

  },

  persist: {
    paths: ['isShiftOpen', 'currentShift', 'pos_profile', 'availableShifts']
  }
})
