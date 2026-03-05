<template>
	<Dialog v-model="show" :options="{ title: isEditMode ? __('Edit Customer') : __('New Customer'), size: 'lg' }">
		<template #body-content>
			<div class="flex flex-col gap-4 max-h-[70vh] overflow-y-auto px-1">
				<!-- Mode Toggle: Non-GST / GST -->
				<div class="flex gap-2 p-1 bg-gray-100 rounded-lg">
					<button
						type="button"
						@click="!isEditMode && (formMode = 'non-gst')"
						:disabled="isEditMode"
						:class="[
							'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
							formMode === 'non-gst'
								? 'bg-white text-blue-600 shadow-sm'
								: 'text-gray-600 hover:text-gray-800'
						]"
					>
						{{ __('Non-GST') }}
					</button>
					<button
						type="button"
						@click="!isEditMode && (formMode = 'gst')"
						:disabled="isEditMode"
						:class="[
							'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-all',
							formMode === 'gst'
								? 'bg-white text-blue-600 shadow-sm'
								: 'text-gray-600 hover:text-gray-800'
						]"
					>
						{{ __('GST') }}
					</button>
				</div>

				<!-- ============================================ -->
				<!-- NON-GST FORM -->
				<!-- ============================================ -->
				<template v-if="formMode === 'non-gst'">
					<!-- Customer Phone Number (maps to customer_name and mobile_no) -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Customer Phone Number") }} <span class="text-red-500">*</span>
						</label>
						<input
							v-model="nonGstData.phone_number"
							type="tel"
							:placeholder="__('Enter 10-digit phone number')"
							maxlength="10"
							class="w-full px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							:class="nonGstPhoneError ? 'border-red-300 bg-red-50' : 'border-gray-300'"
							@input="validateNonGstPhone"
						/>
						<p v-if="nonGstPhoneError" class="mt-1 text-xs text-red-600">
							{{ nonGstPhoneError }}
						</p>
					</div>

					<!-- Customer Name (maps to custom_party_name_for_print) -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Customer Name") }}
						</label>
						<input
							v-model="nonGstData.customer_name"
							type="text"
							:placeholder="__('Enter customer name')"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Email ID -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Email ID") }} <span class="text-red-500">*</span>
						</label>
						<input
							v-model="nonGstData.email_id"
							type="email"
							:placeholder="__('Enter email address')"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Profession -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Profession") }} <span class="text-red-500">*</span>
						</label>
						<select
							v-model="nonGstData.custom_profession"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
						>
							<option value="">{{ __("Select Profession") }}</option>
							<option v-for="prof in professions" :key="prof" :value="prof">
								{{ prof }}
							</option>
						</select>
					</div>

					<!-- Address Section -->
					<div class="border-t border-gray-200 pt-4 mt-2">
						<h3 class="text-sm font-semibold text-gray-800 mb-3">{{ __("Address Details") }}</h3>

						<!-- Address Line 1 -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("Address Line 1") }} <span class="text-red-500">*</span>
							</label>
							<input
								v-model="nonGstData.address_line1"
								type="text"
								:placeholder="__('Enter address line 1')"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>

						<!-- Address Line 2 -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("Address Line 2") }}
							</label>
							<input
								v-model="nonGstData.address_line2"
								type="text"
								:placeholder="__('Enter address line 2')"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>

						<!-- City, State, Country, and Pincode are hidden - auto-filled from POS Profile -->
						<!-- These fields are populated automatically from POS Profile's company address -->
					</div>
				</template>

				<!-- ============================================ -->
				<!-- GST FORM -->
				<!-- ============================================ -->
				<template v-else>
					<!-- GSTIN / UIN -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("GSTIN / UIN") }} <span class="text-red-500">*</span>
						</label>
						<div class="flex gap-2">
							<input
								v-model="gstData.gstin"
								type="text"
								:placeholder="__('Enter 15-digit GSTIN')"
								maxlength="15"
								class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-start uppercase"
								@input="gstData.gstin = gstData.gstin.toUpperCase()"
							/>
							<button
								type="button"
								@click="fetchGSTINInfo"
								:disabled="!gstData.gstin || gstData.gstin.length !== 15 || fetchingGSTIN"
								class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
							>
								{{ fetchingGSTIN ? __("...") : __("Fetch") }}
							</button>
						</div>
						<p v-if="gstinStatus" class="mt-1 text-xs" :class="gstinStatus.includes('Status') || gstinStatus.includes('success') ? 'text-green-600' : 'text-red-600'">
							{{ gstinStatus }}
						</p>
					</div>

					<!-- Party Name (from GSTIN, maps to customer_name) -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Party Name") }} <span class="text-red-500">*</span>
						</label>
						<input
							v-model="gstData.party_name"
							type="text"
							:placeholder="__('Auto-filled from GSTIN')"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Phone Number -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Phone Number") }} <span class="text-red-500">*</span>
						</label>
						<div class="flex gap-2">
							<!-- Country Code Dropdown -->
							<div class="relative" ref="dropdownRef">
								<button
									type="button"
									@click="showCountryDropdown = !showCountryDropdown"
									class="flex items-center gap-1 w-24 ps-2 pe-1 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white hover:bg-gray-50"
								>
									<img
										:src="`https://flagcdn.com/h24/${currentCountryCode}.png`"
										:alt="currentCountryCode"
										class="w-6 h-auto rounded-sm"
										@error="handleFlagError"
									/>
									<span class="flex-1 text-start">{{ selectedCountryCode || "+91" }}</span>
									<svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
									</svg>
								</button>

								<!-- Country Search Dropdown -->
								<div
									v-if="showCountryDropdown"
									class="absolute start-0 z-50 mt-1 w-80 max-h-80 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
								>
									<div class="sticky top-0 bg-white border-b border-gray-200 p-2">
										<input
											ref="countrySearchRef"
											v-model="countrySearchQuery"
											type="text"
											:placeholder="__('Search country...')"
											class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
											@keydown.escape="showCountryDropdown = false"
										/>
									</div>
									<div class="overflow-y-auto max-h-64">
										<button
											v-for="country in filteredCountries"
											:key="country.code"
											type="button"
											@click="selectCountry(country)"
											class="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-gray-50 transition-colors text-start"
											:class="{ 'bg-blue-50': selectedCountryCode === country.isd }"
										>
											<img
												:src="`https://flagcdn.com/h24/${country.code.toLowerCase()}.png`"
												:alt="country.name"
												class="w-6 h-auto rounded-sm shadow-sm"
												@error="(e) => (e.target.style.display = 'none')"
											/>
											<span class="flex-1 text-sm font-medium text-gray-700">{{ country.name }}</span>
											<span class="text-sm text-gray-500">{{ country.isd }}</span>
										</button>
										<div v-if="filteredCountries.length === 0" class="px-4 py-8 text-center text-sm text-gray-500">
											{{ __("No countries found") }}
										</div>
									</div>
								</div>
							</div>

							<!-- Phone Number Input -->
							<input
								v-model="gstPhoneNumber"
								type="tel"
								:placeholder="__('Enter phone number')"
								class="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-start"
								@input="updateGstMobileNumber"
							/>
						</div>
					</div>

					<!-- Email ID -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Email ID") }} <span class="text-red-500">*</span>
						</label>
						<input
							v-model="gstData.email_id"
							type="email"
							:placeholder="__('Enter email address')"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Customer Type -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Customer Type") }}
						</label>
						<select
							v-model="gstData.customer_type"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
						>
							<option v-for="type in customerTypes" :key="type" :value="type">
								{{ type }}
							</option>
						</select>
					</div>

					<!-- GST Category -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("GST Category") }}
						</label>
						<select
							v-model="gstData.gst_category"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
						>
							<option v-for="category in gstCategories" :key="category" :value="category">
								{{ category }}
							</option>
						</select>
					</div>

					<!-- Profession -->
					<div>
						<label class="block text-start text-sm font-medium text-gray-700 mb-1">
							{{ __("Profession") }} <span class="text-red-500">*</span>
						</label>
						<select
							v-model="gstData.custom_profession"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
						>
							<option value="">{{ __("Select Profession") }}</option>
							<option v-for="prof in professions" :key="prof" :value="prof">
								{{ prof }}
							</option>
						</select>
					</div>

					<!-- Address Section -->
					<div class="border-t border-gray-200 pt-4 mt-2">
						<h3 class="text-sm font-semibold text-gray-800 mb-3">{{ __("Address Details") }}</h3>

						<!-- Address Line 1 -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("Address Line 1") }} <span class="text-red-500">*</span>
							</label>
							<input
								v-model="gstData.address_line1"
								type="text"
								:placeholder="__('Enter address line 1')"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
								required
							/>
						</div>

						<!-- Address Line 2 -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("Address Line 2") }}
							</label>
							<input
								v-model="gstData.address_line2"
								type="text"
								:placeholder="__('Enter address line 2')"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>

						<!-- City -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("City") }} <span class="text-red-500">*</span>
							</label>
							<input
								v-model="gstData.city"
								type="text"
								:placeholder="__('Enter city')"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>

						<!-- State -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("State") }} <span class="text-red-500">*</span>
							</label>
							<div class="relative" ref="gstStateDropdownRef">
								<input
									v-model="gstStateSearchQuery"
									type="text"
									:placeholder="__('Search state...')"
									class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
									@focus="showGstStateDropdown = true"
									@input="handleGstStateInput"
									@blur="validateGstStateOnBlur"
								/>
								<div
									v-if="showGstStateDropdown && filteredGstStates.length > 0"
									class="absolute z-50 mt-1 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-48 overflow-y-auto"
								>
									<button
										v-for="state in filteredGstStates"
										:key="state"
										type="button"
										@click="selectGstState(state)"
										class="w-full px-3 py-2 text-start text-sm hover:bg-gray-50"
										:class="{ 'bg-blue-50': gstData.state === state }"
									>
										{{ state }}
									</button>
								</div>
							</div>
						</div>

						<!-- Post Code -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("Post Code") }}
							</label>
							<input
								v-model="gstData.pincode"
								type="text"
								:placeholder="__('Enter postal code')"
								class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
						</div>

						<!-- Country -->
						<div class="mb-3">
							<label class="block text-start text-sm font-medium text-gray-700 mb-1">
								{{ __("Country") }} <span class="text-red-500">*</span>
							</label>
							<div class="relative" ref="countryAddressDropdownRef">
								<input
									v-model="countryAddressSearchQuery"
									type="text"
									:placeholder="__('Search country...')"
									class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
									@focus="showCountryAddressDropdown = true"
									@input="showCountryAddressDropdown = true"
								/>
								<div
									v-if="showCountryAddressDropdown && filteredAddressCountries.length > 0"
									class="absolute z-50 mt-1 w-full bg-white rounded-lg shadow-lg border border-gray-200 max-h-48 overflow-y-auto"
								>
									<button
										v-for="country in filteredAddressCountries"
										:key="country.name"
										type="button"
										@click="selectAddressCountry(country)"
										class="w-full px-3 py-2 text-start text-sm hover:bg-gray-50 flex items-center gap-2"
										:class="{ 'bg-blue-50': gstData.country === country.name }"
									>
										<img
											:src="`https://flagcdn.com/h24/${country.code.toLowerCase()}.png`"
											:alt="country.name"
											class="w-5 h-auto rounded-sm"
											@error="(e) => (e.target.style.display = 'none')"
										/>
										{{ country.name }}
									</button>
								</div>
							</div>
						</div>
					</div>
				</template>
			</div>
		</template>

		<template #actions>
			<div class="flex flex-col gap-2">
				<!-- Permission Warning -->
				<div v-if="!hasPermission" class="px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg">
					<div class="flex items-start gap-2">
						<svg class="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
							<path
								fill-rule="evenodd"
								d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
								clip-rule="evenodd"
							/>
						</svg>
						<div class="flex-1">
							<p class="text-sm font-medium text-amber-900">{{ __("Permission Required") }}</p>
							<p class="text-xs text-amber-700 mt-0.5">
								{{ __("You don't have permission to create customers. Contact your administrator.") }}
							</p>
						</div>
					</div>
				</div>

				<div class="flex gap-2">
					<Button
						variant="solid"
						@click="handleCreate"
						:loading="creating"
						:disabled="!canSubmit"
					>
						{{ isEditMode ? __("Update Customer") : __("Create Customer") }}
					</Button>
					<Button variant="subtle" @click="show = false">
						{{ __("Cancel") }}
					</Button>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
/**
 * CreateCustomerDialog - Quick customer creation from POS
 *
 * Features:
 * - Two modes: Non-GST (default) and GST
 * - Non-GST: Phone number as customer_name, simplified form
 * - GST: GSTIN autofill from India Compliance API
 * - Address creation with customer
 * - Country code selector with flag icons (GST mode)
 * - State/Country search dropdowns
 */

import { usePOSPermissions } from "@/composables/usePermissions"
import { useToast } from "@/composables/useToast"
import { useCountriesStore } from "@/stores/countries"
import { logger } from "@/utils/logger"
import { Button, Dialog, call } from "frappe-ui"
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue"

const log = logger.create("CreateCustomerDialog")

// =============================================================================
// Composables & Stores
// =============================================================================

const countriesStore = useCountriesStore()
const { canCreateCustomer } = usePOSPermissions()
const { showSuccess, showError } = useToast()

// =============================================================================
// Props & Emits
// =============================================================================

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	initialName: String,
	editCustomer: { type: Object, default: null },
})

const emit = defineEmits(["update:modelValue", "customer-created", "customer-updated"])

// =============================================================================
// State
// =============================================================================

// Form mode toggle
const formMode = ref("non-gst") // 'non-gst' or 'gst'

const hasPermission = ref(true)
const checkingPermission = ref(false)
const creating = ref(false)

// Phone country code (for GST mode)
const selectedCountryCode = ref("+91")
const gstPhoneNumber = ref("")
const showCountryDropdown = ref(false)
const countrySearchQuery = ref("")
const dropdownRef = ref(null)
const countrySearchRef = ref(null)

// Non-GST State dropdown
const showNonGstStateDropdown = ref(false)
const nonGstStateSearchQuery = ref("")
const nonGstStateDropdownRef = ref(null)

// GST State dropdown
const showGstStateDropdown = ref(false)
const gstStateSearchQuery = ref("")
const gstStateDropdownRef = ref(null)

// Country address dropdown (GST mode)
const showCountryAddressDropdown = ref(false)
const countryAddressSearchQuery = ref("India")
const countryAddressDropdownRef = ref(null)

// Customer Types and Options
const customerTypes = ref(["Individual", "Company", "Partnership"])
const gstCategories = ref(["Unregistered", "Registered Regular", "Registered Composition", "SEZ", "Overseas", "Deemed Export", "UIN Holders"])
const professions = ref([])
const fetchingGSTIN = ref(false)
const gstinStatus = ref("")

// Non-GST phone validation
const nonGstPhoneError = ref("")

// Indian States for GST
const indianStates = ref([
	"Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam",
	"Bihar", "Chandigarh", "Chhattisgarh", "Dadra and Nagar Haveli and Daman and Diu",
	"Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir",
	"Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", "Madhya Pradesh",
	"Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha",
	"Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
	"Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
])

// Non-GST Form Data
const nonGstData = ref({
	phone_number: "",        // Will be used as customer_name and mobile_no
	customer_name: "",       // Maps to custom_party_name_for_print
	email_id: "",
	custom_profession: "",
	address_line1: "",
	address_line2: "",
	city: "",                // Auto-filled from POS Profile company address
	state: "",               // Auto-filled from POS Profile company address
	pincode: "",             // Auto-filled from POS Profile company address
	country: "India",        // Always India for Non-GST, not shown in form
})

// GST Form Data
const gstData = ref({
	gstin: "",
	party_name: "",           // Maps to customer_name
	mobile_no: "",
	email_id: "",
	customer_type: "Individual",
	gst_category: "Unregistered",
	custom_profession: "",
	address_line1: "",
	address_line2: "",
	city: "",
	state: "",
	pincode: "",
	country: "India",
})

// =============================================================================
// Computed
// =============================================================================

const show = computed({
	get: () => props.modelValue,
	set: (val) => emit("update:modelValue", val),
})

const isEditMode = computed(() => !!props.editCustomer)

const currentCountryCode = computed(() => {
	const country = countriesStore.countries.find((c) => c.isd === selectedCountryCode.value)
	return country?.code.toLowerCase() || "in"
})

const filteredCountries = computed(() => {
	if (!countrySearchQuery.value) return countriesStore.countries
	const query = countrySearchQuery.value.toLowerCase()
	return countriesStore.countries.filter(
		(c) => c.name.toLowerCase().includes(query) || c.isd.includes(query) || c.code.toLowerCase().includes(query)
	)
})

const filteredNonGstStates = computed(() => {
	if (!nonGstStateSearchQuery.value) return indianStates.value
	const query = nonGstStateSearchQuery.value.toLowerCase()
	return indianStates.value.filter((s) => s.toLowerCase().includes(query))
})

const filteredGstStates = computed(() => {
	if (!gstStateSearchQuery.value) return indianStates.value
	const query = gstStateSearchQuery.value.toLowerCase()
	return indianStates.value.filter((s) => s.toLowerCase().includes(query))
})

const filteredAddressCountries = computed(() => {
	if (!countryAddressSearchQuery.value) return countriesStore.countries
	const query = countryAddressSearchQuery.value.toLowerCase()
	return countriesStore.countries.filter((c) => c.name.toLowerCase().includes(query))
})

const canSubmit = computed(() => {
	if (!hasPermission.value) return false

	// In edit mode, just need minimal data
	if (isEditMode.value) {
		if (formMode.value === "non-gst") {
			return /^\d{10}$/.test(nonGstData.value.phone_number)
		} else {
			return !!(gstData.value.party_name && gstData.value.gstin && gstData.value.gstin.length === 15)
		}
	}

	if (formMode.value === "non-gst") {
		// Non-GST validation: phone (10 digits), email, profession, address_line1
		// City, state, country, pincode are auto-filled from POS profile
		const phoneValid = /^\d{10}$/.test(nonGstData.value.phone_number)
		const emailValid = nonGstData.value.email_id && 
			nonGstData.value.email_id.trim() !== "" &&
			/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(nonGstData.value.email_id.trim())
		return (
			phoneValid &&
			emailValid &&
			nonGstData.value.custom_profession &&
			nonGstData.value.address_line1 &&
			nonGstData.value.city // Auto-filled from POS profile
		)
	} else {
		// GST validation: gstin, party_name, profession, address_line1, city, state, phone, email
		const phoneValid = gstData.value.mobile_no && gstData.value.mobile_no.trim() !== ""
		const emailValid = gstData.value.email_id && 
			gstData.value.email_id.trim() !== "" &&
			/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(gstData.value.email_id.trim())
		return (
			gstData.value.gstin &&
			gstData.value.gstin.length === 15 &&
			gstData.value.party_name &&
			gstData.value.custom_profession &&
			gstData.value.address_line1 &&
			gstData.value.city &&
			gstData.value.state &&
			phoneValid &&
			emailValid
		)
	}
})

// =============================================================================
// Non-GST Phone Validation
// =============================================================================

const validateNonGstPhone = () => {
	const phone = nonGstData.value.phone_number
	if (!phone) {
		nonGstPhoneError.value = ""
		return
	}

	// Remove any non-digit characters for validation
	const digitsOnly = phone.replace(/\D/g, "")
	nonGstData.value.phone_number = digitsOnly

	if (digitsOnly.length > 0 && digitsOnly.length !== 10) {
		nonGstPhoneError.value = __("Phone number must be exactly 10 digits")
	} else if (digitsOnly.length === 10 && !/^[6-9]\d{9}$/.test(digitsOnly)) {
		nonGstPhoneError.value = __("Please enter a valid Indian mobile number")
	} else {
		nonGstPhoneError.value = ""
	}
}

// =============================================================================
// Country & Phone Methods (GST Mode)
// =============================================================================

const handleFlagError = (e) => (e.target.style.display = "none")

const selectCountry = (country) => {
	selectedCountryCode.value = country.isd
	showCountryDropdown.value = false
	countrySearchQuery.value = ""
	updateGstMobileNumber()
}

const updateGstMobileNumber = () => {
	gstData.value.mobile_no = gstPhoneNumber.value ? `${selectedCountryCode.value}-${gstPhoneNumber.value}` : ""
}

const handleClickOutside = (event) => {
	// Phone country dropdown
	if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
		showCountryDropdown.value = false
		countrySearchQuery.value = ""
	}
	// Non-GST State dropdown
	if (nonGstStateDropdownRef.value && !nonGstStateDropdownRef.value.contains(event.target)) {
		showNonGstStateDropdown.value = false
	}
	// GST State dropdown
	if (gstStateDropdownRef.value && !gstStateDropdownRef.value.contains(event.target)) {
		showGstStateDropdown.value = false
	}
	// Country address dropdown
	if (countryAddressDropdownRef.value && !countryAddressDropdownRef.value.contains(event.target)) {
		showCountryAddressDropdown.value = false
	}
}

// =============================================================================
// State & Country Selection
// =============================================================================

const selectNonGstState = (state) => {
	nonGstData.value.state = state
	nonGstStateSearchQuery.value = state
	showNonGstStateDropdown.value = false
}

const selectGstState = (state) => {
	gstData.value.state = state
	gstStateSearchQuery.value = state
	showGstStateDropdown.value = false
}

const selectAddressCountry = (country) => {
	gstData.value.country = country.name
	countryAddressSearchQuery.value = country.name
	showCountryAddressDropdown.value = false
}

// =============================================================================
// GSTIN Autofill Methods
// =============================================================================

const fetchGSTINInfo = async () => {
	const gstin = gstData.value.gstin?.trim()

	if (!gstin || gstin.length !== 15) {
		gstinStatus.value = ""
		return
	}

	fetchingGSTIN.value = true
	gstinStatus.value = "Fetching..."

	try {
		const csrfToken = window.frappe?.csrf_token || window.csrf_token || ""

		const response = await fetch("/api/method/pos_next.api.gstin.get_gstin_info_for_pos", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-Frappe-CSRF-Token": csrfToken,
			},
			body: JSON.stringify({ gstin }),
		})

		if (!response.ok) {
			throw new Error(`HTTP ${response.status}: ${response.statusText}`)
		}

		const data = await response.json()

		if (data.exc || data._server_messages) {
			let errorMsg = "Unable to verify GSTIN"
			if (data._server_messages) {
				try {
					const messages = JSON.parse(data._server_messages)
					if (messages.length > 0) {
						const parsedMsg = JSON.parse(messages[0])
						errorMsg = parsedMsg.message || errorMsg
					}
				} catch (e) {
					log.warn("Could not parse server messages", e)
				}
			}
			gstinStatus.value = errorMsg
			return
		}

		if (data.message && !data.message.error) {
			const gstinInfo = data.message

			// Set business name as party name
			if (gstinInfo.business_name) {
				gstData.value.party_name = gstinInfo.business_name
			}

			// Set GST Category
			if (gstinInfo.gst_category) {
				gstData.value.gst_category = gstinInfo.gst_category
			}

			// Set customer type based on GSTIN 6th character
			const gstinTypeChar = gstin[5]
			if (gstinTypeChar === "F") {
				gstData.value.customer_type = "Partnership"
			} else if (gstinTypeChar === "C") {
				gstData.value.customer_type = "Company"
			}

			// Set address if available
			if (gstinInfo.permanent_address) {
				const addr = gstinInfo.permanent_address
				if (addr.line1) gstData.value.address_line1 = addr.line1
				if (addr.line2) gstData.value.address_line2 = addr.line2
				if (addr.city) gstData.value.city = addr.city
				if (addr.state) {
					gstData.value.state = addr.state
					gstStateSearchQuery.value = addr.state
				}
				if (addr.pincode) gstData.value.pincode = addr.pincode
				gstData.value.country = "India"
				countryAddressSearchQuery.value = "India"
			}

			gstinStatus.value = gstinInfo.status ? `Status: ${gstinInfo.status}` : "Details fetched successfully"
			showSuccess(__("GSTIN details fetched successfully"))
		} else {
			gstinStatus.value = data.message?.message || "Invalid GSTIN or unable to fetch details"
		}
	} catch (error) {
		log.error("Error fetching GSTIN info", error)
		gstinStatus.value = error.message || "Network error"
		showError(__("Error: {0}", [error.message]))
	} finally {
		fetchingGSTIN.value = false
	}
}

// =============================================================================
// Load Professions (Custom Field Options)
// =============================================================================

const loadProfessions = async () => {
	try {
		// Use the new API endpoint that bypasses Custom Field permissions
		const result = await call("pos_next.api.customers.get_profession_options")

		if (result && Array.isArray(result) && result.length > 0) {
			professions.value = result
			log.info("Professions loaded successfully", professions.value)
		} else {
			// Use default professions if API returns empty
			professions.value = ["Doctor", "Accountant", "Business", "CA", "Student"]
			log.warn("API returned empty, using default professions")
		}
	} catch (error) {
		log.error("Error loading professions, using defaults", error)
		// Use default professions if API fails (e.g., permission error)
		professions.value = ["Doctor", "Accountant", "Business", "CA", "Student"]
	}
}

// =============================================================================
// Create Customer & Address
// =============================================================================

const handleCreate = async () => {
	if (isEditMode.value) {
		await updateCustomer()
	} else if (formMode.value === "non-gst") {
		await createNonGstCustomer()
	} else {
		await createGstCustomer()
	}
}

const prefillFromCustomer = async (customer) => {
	if (!customer) return

	// Determine mode: GST if customer has gstin, otherwise non-gst
	if (customer.gstin) {
		formMode.value = "gst"
		Object.assign(gstData.value, {
			gstin: customer.gstin || "",
			party_name: customer.customer_name || "",
			mobile_no: customer.mobile_no || "",
			email_id: customer.email_id || "",
			customer_type: customer.customer_type || "Individual",
			gst_category: customer.gst_category || "Unregistered",
			custom_profession: customer.custom_profession || "",
			address_line1: "",
			address_line2: "",
			city: "",
			state: "",
			pincode: "",
			country: "India",
		})
		// Parse mobile_no for country code and number
		if (customer.mobile_no && customer.mobile_no.includes("-")) {
			const parts = customer.mobile_no.split("-")
			selectedCountryCode.value = parts[0] || "+91"
			gstPhoneNumber.value = parts.slice(1).join("-")
		} else {
			gstPhoneNumber.value = customer.mobile_no || ""
		}
	} else {
		formMode.value = "non-gst"
		const phone = customer.mobile_no || ""
		// Strip country code prefix like +91-
		const phoneNumber = phone.includes("-") ? phone.split("-").slice(1).join("") : phone.replace(/^\+91/, "")
		Object.assign(nonGstData.value, {
			phone_number: phoneNumber,
			customer_name: customer.custom_party_name_for_print || "",
			email_id: customer.email_id || "",
			custom_profession: customer.custom_profession || "",
			address_line1: "",
			address_line2: "",
			city: "",
			state: "",
			pincode: "",
			country: "India",
		})
	}

	// Try to fetch existing address
	try {
		const addresses = await call("frappe.client.get_list", {
			doctype: "Address",
			filters: [["Dynamic Link", "link_doctype", "=", "Customer"], ["Dynamic Link", "link_name", "=", customer.name]],
			fields: ["name", "address_line1", "address_line2", "city", "state", "pincode", "country"],
			limit: 1,
		})
		if (addresses && addresses.length > 0) {
			const addr = addresses[0]
			if (formMode.value === "gst") {
				Object.assign(gstData.value, {
					address_line1: addr.address_line1 || "",
					address_line2: addr.address_line2 || "",
					city: addr.city || "",
					state: addr.state || "",
					pincode: addr.pincode || "",
					country: addr.country || "India",
				})
				if (addr.state) gstStateSearchQuery.value = addr.state
				if (addr.country) countryAddressSearchQuery.value = addr.country
			} else {
				Object.assign(nonGstData.value, {
					address_line1: addr.address_line1 || "",
					address_line2: addr.address_line2 || "",
					city: addr.city || "",
					state: addr.state || "",
					pincode: addr.pincode || "",
					country: addr.country || "India",
				})
			}
		}
	} catch (err) {
		log.warn("Could not load customer address for edit", err)
	}
}

const updateCustomer = async () => {
	if (!props.editCustomer?.name) return

	creating.value = true
	try {
		const customerName = props.editCustomer.name
		let updates = {}
		let addressData = null

		if (formMode.value === "non-gst") {
			if (!/^\d{10}$/.test(nonGstData.value.phone_number)) {
				return showError(__("Customer Phone Number must be exactly 10 digits"))
			}
			updates = {
				customer_name: nonGstData.value.phone_number,
				mobile_no: `+91-${nonGstData.value.phone_number}`,
				email_id: nonGstData.value.email_id || "",
				custom_profession: nonGstData.value.custom_profession || "",
				custom_party_name_for_print: nonGstData.value.customer_name || "",
			}
			addressData = {
				address_line1: nonGstData.value.address_line1,
				address_line2: nonGstData.value.address_line2 || "",
				city: nonGstData.value.city || "",
				state: nonGstData.value.state || "",
				pincode: nonGstData.value.pincode || "",
				country: nonGstData.value.country || "India",
			}
		} else {
			if (!gstData.value.party_name) {
				return showError(__("Party Name is required"))
			}
			updates = {
				customer_name: gstData.value.party_name,
				customer_type: gstData.value.customer_type || "Individual",
				mobile_no: gstData.value.mobile_no || "",
				email_id: gstData.value.email_id || "",
				gstin: gstData.value.gstin || "",
				gst_category: gstData.value.gst_category || "Unregistered",
				custom_profession: gstData.value.custom_profession || "",
			}
			addressData = {
				address_line1: gstData.value.address_line1,
				address_line2: gstData.value.address_line2 || "",
				city: gstData.value.city,
				state: gstData.value.state,
				pincode: gstData.value.pincode || "",
				country: gstData.value.country || "India",
			}
		}

		// Use backend API that handles email update via Contact
		const updatedDoc = await call("pos_next.api.customers.update_customer", {
			customer_name: customerName,
			updates,
		})

		// Update address if address fields present
		if (addressData?.address_line1) {
			try {
				const addresses = await call("frappe.client.get_list", {
					doctype: "Address",
					filters: [["Dynamic Link", "link_doctype", "=", "Customer"], ["Dynamic Link", "link_name", "=", customerName]],
					fields: ["name"],
					limit: 1,
				})
				if (addresses && addresses.length > 0) {
					await call("frappe.client.set_value", {
						doctype: "Address",
						name: addresses[0].name,
						fieldname: addressData,
					})
				}
			} catch (addrError) {
				log.warn("Could not update customer address", addrError)
			}
		}

		// Emit the freshly fetched customer from backend
		const mergedCustomer = updatedDoc || { ...props.editCustomer, ...updates, name: customerName }
		emit("customer-updated", mergedCustomer)
		show.value = false
	} catch (error) {
		log.error("Error updating customer", error)
		showError(error.message || __("Failed to update customer"))
	} finally {
		creating.value = false
	}
}

const createNonGstCustomer = async () => {
	// Validate phone number
	if (!/^\d{10}$/.test(nonGstData.value.phone_number)) {
		return showError(__("Customer Phone Number must be exactly 10 digits"))
	}

	if (!nonGstData.value.email_id || nonGstData.value.email_id.trim() === "") {
		return showError(__("Email ID is required"))
	}

	if (!nonGstData.value.custom_profession) {
		return showError(__("Profession is required"))
	}

	if (!nonGstData.value.address_line1 || nonGstData.value.address_line1.trim() === "") {
		return showError(__("Address Line 1 is required"))
	}

	if (!nonGstData.value.city) {
		return showError(__("City is required. Please ensure POS Profile has a company address with city."))
	}

	creating.value = true

	try {
		// Create Customer document
		// Phone number is used as customer_name and mobile_no
		const customerDoc = {
			doctype: "Customer",
			customer_name: nonGstData.value.phone_number,
			customer_type: "Individual",  // Always Individual for Non-GST
			customer_group: "Customers",
			territory: "All Territories",
			mobile_no: `+91-${nonGstData.value.phone_number}`,
			email_id: nonGstData.value.email_id || "",
			gst_category: "Unregistered",  // Non-GST is always Unregistered
			custom_profession: nonGstData.value.custom_profession || "",
			custom_party_name_for_print: nonGstData.value.customer_name || "",
		}

		const customerResult = await call("frappe.client.insert", { doc: customerDoc })
		log.info("Non-GST Customer created", customerResult)

		// Create Address linked to Customer
		// City, state, pincode are auto-filled from POS Profile company address
		const addressDoc = {
			doctype: "Address",
			address_title: nonGstData.value.phone_number,
			address_type: "Billing",
			address_line1: nonGstData.value.address_line1,
			address_line2: nonGstData.value.address_line2 || "",
			city: nonGstData.value.city || "",  // Auto-filled from POS Profile
			state: nonGstData.value.state || "",  // Auto-filled from POS Profile
			country: nonGstData.value.country || "India",  // Always India for Non-GST
			pincode: nonGstData.value.pincode || "",  // Auto-filled from POS Profile
			is_primary_address: 1,
			is_shipping_address: 1,
			gst_category: "Unregistered",
			links: [
				{
					link_doctype: "Customer",
					link_name: customerResult.name,
				},
			],
		}

		try {
			const addressResult = await call("frappe.client.insert", { doc: addressDoc })
			log.info("Address created successfully", addressResult)
		} catch (addrError) {
			log.error("Failed to create address", addrError)
			showError(__("Customer created but address could not be saved: {0}", [addrError.message || "Unknown error"]))
		}

		showSuccess(__("Customer {0} created successfully", [customerResult.customer_name]))
		emit("customer-created", customerResult)
		show.value = false
	} catch (error) {
		log.error("Error creating Non-GST customer", error)
		showError(error.message || __("Failed to create customer"))
	} finally {
		creating.value = false
	}
}

const createGstCustomer = async () => {
	if (!gstData.value.gstin || gstData.value.gstin.length !== 15) {
		return showError(__("Valid 15-digit GSTIN is required"))
	}

	if (!gstData.value.party_name) {
		return showError(__("Party Name is required"))
	}

	if (!gstData.value.mobile_no || gstData.value.mobile_no.trim() === "") {
		return showError(__("Phone Number is required"))
	}

	if (!gstData.value.email_id || gstData.value.email_id.trim() === "") {
		return showError(__("Email ID is required"))
	}

	if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(gstData.value.email_id.trim())) {
		return showError(__("Please enter a valid email address"))
	}

	if (!gstData.value.custom_profession) {
		return showError(__("Profession is required"))
	}

	if (!gstData.value.address_line1 || gstData.value.address_line1.trim() === "") {
		return showError(__("Address Line 1 is required"))
	}

	if (!gstData.value.city) {
		return showError(__("City is required"))
	}

	if (!gstData.value.state) {
		return showError(__("State is required for GST customers"))
	}

	creating.value = true

	try {
		// Create Customer document
		const customerDoc = {
			doctype: "Customer",
			customer_name: gstData.value.party_name,
			customer_type: gstData.value.customer_type || "Individual",
			customer_group: "Customers",
			territory: "All Territories",
			mobile_no: gstData.value.mobile_no || "",
			email_id: gstData.value.email_id || "",
			gstin: gstData.value.gstin,
			gst_category: gstData.value.gst_category || "Registered Regular",
			custom_profession: gstData.value.custom_profession || "",
		}

		const customerResult = await call("frappe.client.insert", { doc: customerDoc })
		log.info("GST Customer created", customerResult)

		// Create Address linked to Customer
		const addressDoc = {
			doctype: "Address",
			address_title: gstData.value.party_name,
			address_type: "Billing",
			address_line1: gstData.value.address_line1,
			address_line2: gstData.value.address_line2 || "",
			city: gstData.value.city,
			state: gstData.value.state,
			country: gstData.value.country || "India",
			pincode: gstData.value.pincode || "",
			is_primary_address: 1,
			is_shipping_address: 1,
			gst_category: gstData.value.gst_category || "Registered Regular",
			gstin: gstData.value.gstin,
			links: [
				{
					link_doctype: "Customer",
					link_name: customerResult.name,
				},
			],
		}

		try {
			const addressResult = await call("frappe.client.insert", { doc: addressDoc })
			log.info("Address created successfully", addressResult)
		} catch (addrError) {
			log.error("Failed to create address", addrError)
			showError(__("Customer created but address could not be saved: {0}", [addrError.message || "Unknown error"]))
		}

		showSuccess(__("Customer {0} created successfully", [customerResult.customer_name]))
		emit("customer-created", customerResult)
		show.value = false
	} catch (error) {
		log.error("Error creating GST customer", error)
		showError(error.message || __("Failed to create customer"))
	} finally {
		creating.value = false
	}
}

// =============================================================================
// Dialog Lifecycle
// =============================================================================

const loadPosProfileAddress = async () => {
	if (!props.posProfile) return

	try {
		// Fetch POS Profile to get company_address
		const posProfileDoc = await call("frappe.client.get", {
			doctype: "POS Profile",
			name: props.posProfile,
		})

		if (posProfileDoc && posProfileDoc.company_address) {
			// Fetch the company address details
			const addressDoc = await call("frappe.client.get", {
				doctype: "Address",
				name: posProfileDoc.company_address,
			})

			if (addressDoc) {
				// Auto-populate non-GST form fields from POS profile address
				if (addressDoc.city) {
					nonGstData.value.city = addressDoc.city
				}
				if (addressDoc.state) {
					nonGstData.value.state = addressDoc.state
				}
				if (addressDoc.pincode) {
					nonGstData.value.pincode = addressDoc.pincode
				}
				// Country is always India for Non-GST
				nonGstData.value.country = "India"
			}
		}
	} catch (error) {
		log.warn("Could not load POS Profile address", error)
		// Continue without address data - user will need to enter manually
	}
}

const loadDialogData = async () => {
	countriesStore.loadCountries()
	loadProfessions()
	checkPermissions()
	await loadPosProfileAddress()
}

const checkPermissions = async () => {
	checkingPermission.value = true
	try {
		hasPermission.value = await canCreateCustomer()
	} catch (err) {
		log.error("Permission check failed", err)
		hasPermission.value = false
	} finally {
		checkingPermission.value = false
	}
}

const resetForm = () => {
	// Reset form mode to default
	formMode.value = "non-gst"

	// Reset Non-GST data
	Object.assign(nonGstData.value, {
		phone_number: "",
		customer_name: "",
		email_id: "",
		custom_profession: "",
		address_line1: "",
		address_line2: "",
		city: "",
		state: "",
		pincode: "",
		country: "India",
	})
	nonGstStateSearchQuery.value = ""
	nonGstPhoneError.value = ""

	// Reset GST data
	Object.assign(gstData.value, {
		gstin: "",
		party_name: "",
		mobile_no: "",
		email_id: "",
		customer_type: "Individual",
		gst_category: "Unregistered",
		custom_profession: "",
		address_line1: "",
		address_line2: "",
		city: "",
		state: "",
		pincode: "",
		country: "India",
	})
	selectedCountryCode.value = "+91"
	gstPhoneNumber.value = ""
	gstinStatus.value = ""
	gstStateSearchQuery.value = ""
	countryAddressSearchQuery.value = "India"
}

// =============================================================================
// Watchers
// =============================================================================

watch(
	() => props.editCustomer,
	async (customer) => {
		if (customer && props.modelValue) {
			await prefillFromCustomer(customer)
		}
	},
	{ immediate: true }
)

watch(
	() => props.initialName,
	(name) => {
		if (name) {
			// If initial name looks like a phone number, put in phone field
			if (/^\d{10}$/.test(name)) {
				nonGstData.value.phone_number = name
			} else {
				nonGstData.value.customer_name = name
				gstData.value.party_name = name
			}
		}
	}
)

watch(showCountryDropdown, async (isOpen) => {
	if (isOpen) {
		await nextTick()
		countrySearchRef.value?.focus()
	}
})

watch(
	() => props.modelValue,
	async (isOpen) => {
		show.value = isOpen
		if (isOpen) {
			await loadDialogData()
			// If editing, pre-fill form after base data is loaded
			if (props.editCustomer) {
				await prefillFromCustomer(props.editCustomer)
			}
		} else {
			resetForm()
		}
	}
)

watch(
	() => props.posProfile,
	async () => {
		// Reload address data when POS profile changes
		if (props.modelValue && props.posProfile) {
			await loadPosProfileAddress()
		}
	}
)

watch(show, (val) => emit("update:modelValue", val))

// =============================================================================
// Lifecycle Hooks
// =============================================================================

onMounted(() => {
	loadDialogData()
	document.addEventListener("click", handleClickOutside)
})

onBeforeUnmount(() => {
	document.removeEventListener("click", handleClickOutside)
})
</script>

<style scoped>
.sr-only {
	position: absolute;
	width: 1px;
	height: 1px;
	padding: 0;
	margin: -1px;
	overflow: hidden;
	clip: rect(0, 0, 0, 0);
	white-space: nowrap;
	border-width: 0;
}
</style>
