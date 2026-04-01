<template>
	<Dialog
		v-model="show"
		:options="{ title: __('New Journal Entry'), size: '6xl' }"
	>
		<template #body-content>
			<div class="flex flex-col gap-4 max-h-[80vh] overflow-y-auto px-1">

				<!-- Loading defaults -->
				<div v-if="loadingDefaults" class="flex items-center justify-center py-10">
					<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
					<span class="ms-3 text-sm text-gray-500">{{ __('Loading...') }}</span>
				</div>

				<template v-else>
					<!-- Header Fields -->
					<div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
						<!-- Entry Type (fixed) -->
						<div>
							<label class="block text-start text-xs font-medium text-gray-600 mb-1">
								{{ __('Entry Type') }}
							</label>
							<input
								:value="__('Journal Entry')"
								type="text"
								readonly
								class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
							/>
						</div>

						<!-- Posting Date (read-only) -->
						<div>
							<label class="block text-start text-xs font-medium text-gray-600 mb-1">
								{{ __('Posting Date') }}
							</label>
							<input
								:value="form.posting_date"
								type="text"
								readonly
								class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
							/>
						</div>

						<!-- Company (read-only) -->
						<div>
							<label class="block text-start text-xs font-medium text-gray-600 mb-1">
								{{ __('Company') }}
							</label>
							<input
								:value="form.company"
								type="text"
								readonly
								class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
							/>
						</div>

						<!-- Branch (read-only) -->
						<div>
							<label class="block text-start text-xs font-medium text-gray-600 mb-1">
								{{ __('Branch') }}
							</label>
							<input
								:value="form.custom_branch"
								type="text"
								readonly
								class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
							/>
						</div>

						<!-- Cost Center (read-only) -->
						<div>
							<label class="block text-start text-xs font-medium text-gray-600 mb-1">
								{{ __('Cost Center') }}
							</label>
							<input
								:value="form.custom_cost_center"
								type="text"
								readonly
								class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
							/>
						</div>
					</div>

					<!-- Accounting Entries Table -->
					<div>
						<div class="flex items-center justify-between mb-2">
							<h3 class="text-sm font-semibold text-gray-800">{{ __('Accounting Entries') }}</h3>
							<button
								type="button"
								@click="addRow"
								class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
							>
								<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
								</svg>
								{{ __('Add Row') }}
							</button>
						</div>

						<div class="overflow-x-auto border border-gray-200 rounded-lg">
							<table class="w-full text-xs min-w-[700px]">
								<thead class="bg-gray-50 border-b border-gray-200">
									<tr>
										<th class="text-start px-2 py-2 font-semibold text-gray-600 w-48">{{ __('Account') }} <span class="text-red-500">*</span></th>
										<th class="text-start px-2 py-2 font-semibold text-gray-600 w-36">{{ __('Party (Customer)') }}</th>
											<th class="text-end px-2 py-2 font-semibold text-gray-600 w-28">{{ __('Debit') }}</th>
										<th class="text-end px-2 py-2 font-semibold text-gray-600 w-28">{{ __('Credit') }}</th>
										<th class="text-center px-2 py-2 font-semibold text-gray-600 w-24">{{ __('Is Advance') }}</th>
										<th class="w-8 px-2 py-2"></th>
									</tr>
								</thead>
								<tbody>
									<tr
										v-for="(row, idx) in form.accounts"
										:key="idx"
										class="border-b border-gray-100 hover:bg-gray-50"
									>
										<!-- Account (read-only, auto-filled from party) -->
										<td class="px-2 py-1.5">
											<input
												:value="row.account"
												type="text"
												readonly
												:placeholder="__('Auto from customer...')"
												class="w-full px-2 py-1.5 border border-gray-200 rounded text-xs bg-gray-50 text-gray-600 cursor-not-allowed"
											/>
										</td>

										<!-- Party (Customer only) -->
										<td class="px-2 py-1.5 relative">
											<div class="relative">
												<input
													v-model="row.party"
													type="text"
													:placeholder="__('Search customer...')"
													class="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
													@input="searchParty(idx, row.party)"
													@focus="activeSearchRow = idx; activeSearchField = 'party'"
													@blur="delayCloseSearch('party', idx)"
												/>
												<div
													v-if="activeSearchRow === idx && activeSearchField === 'party' && partySuggestions.length"
													class="absolute z-50 top-full left-0 w-56 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
												>
													<div
														v-for="p in partySuggestions"
														:key="p.name"
														@mousedown.prevent="selectParty(idx, p)"
														class="px-3 py-2 text-xs hover:bg-blue-50 cursor-pointer border-b border-gray-50 last:border-0"
													>
														<div class="font-medium text-gray-800">{{ p.customer_name || p.name }}</div>
														<div v-if="p.name !== p.customer_name" class="text-gray-400 text-[10px]">{{ p.name }}</div>
													</div>
												</div>
											</div>
										</td>

										<!-- Debit -->
										<td class="px-2 py-1.5">
											<input
												v-model.number="row.debit_in_account_currency"
												type="number"
												min="0"
												step="0.01"
												placeholder="0.00"
												:disabled="idx === 0 && !!props.selectedCustomer"
												:class="[
													'w-full px-2 py-1.5 border rounded text-xs text-end focus:outline-none focus:ring-1 focus:ring-blue-500',
													idx === 0 && !!props.selectedCustomer
														? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
														: 'border-gray-300'
												]"
											/>
										</td>

										<!-- Credit -->
										<td class="px-2 py-1.5">
											<input
												v-model.number="row.credit_in_account_currency"
												type="number"
												min="0"
												step="0.01"
												placeholder="0.00"
												class="w-full px-2 py-1.5 border border-gray-300 rounded text-xs text-end focus:outline-none focus:ring-1 focus:ring-blue-500"
												@input="onCreditInput(row)"
											/>
										</td>

										<!-- Is Advance -->
										<td class="px-2 py-1.5">
											<select
												v-model="row.is_advance"
												class="w-full px-2 py-1.5 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-blue-500 bg-white"
											>
												<option value="">-</option>
												<option value="Yes">{{ __('Yes') }}</option>
												<option value="No">{{ __('No') }}</option>
											</select>
										</td>

										<!-- Delete -->
										<td class="px-2 py-1.5 text-center">
											<button
												type="button"
												@click="removeRow(idx)"
												class="text-red-400 hover:text-red-600 transition-colors p-0.5"
												:title="__('Remove row')"
											>
												<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
													<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
												</svg>
											</button>
										</td>
									</tr>

									<!-- Empty state -->
									<tr v-if="form.accounts.length === 0">
										<td colspan="8" class="text-center text-xs text-gray-400 py-6">
											{{ __('No entries. Click "Add Row" to begin.') }}
										</td>
									</tr>
								</tbody>

								<!-- Totals footer -->
								<tfoot v-if="form.accounts.length > 0" class="bg-gray-50 border-t border-gray-200">
									<tr>
										<td colspan="4" class="px-2 py-2 text-xs font-semibold text-gray-600 text-end">{{ __('Total') }}</td>
										<td class="px-2 py-2 text-xs font-semibold text-end" :class="totalDebit !== totalCredit ? 'text-red-600' : 'text-gray-900'">
											{{ formatCurrency(totalDebit) }}
										</td>
										<td class="px-2 py-2 text-xs font-semibold text-end" :class="totalDebit !== totalCredit ? 'text-red-600' : 'text-gray-900'">
											{{ formatCurrency(totalCredit) }}
										</td>
										<td colspan="2"></td>
									</tr>
									<tr v-if="totalDebit !== totalCredit">
										<td colspan="8" class="px-2 py-1.5 text-xs text-red-500 text-center font-medium">
											{{ __('Difference (Dr - Cr): {0}', [formatCurrency(totalDebit - totalCredit)]) }}
										</td>
									</tr>
								</tfoot>
							</table>
						</div>
					</div>

					<!-- User Remark -->
					<div>
						<label class="block text-start text-xs font-medium text-gray-600 mb-1">
							{{ __('User Remark') }}
						</label>
						<textarea
							v-model="form.user_remark"
							rows="2"
							:placeholder="__('Optional remark...')"
							class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
						></textarea>
					</div>
				</template>
			</div>
		</template>

		<template #actions>
			<Button variant="subtle" @click="show = false">
				{{ __('Cancel') }}
			</Button>
			<Button
				variant="solid"
				theme="blue"
				:loading="saving"
				:disabled="loadingDefaults || form.accounts.length === 0"
				@click="saveJournalEntry"
			>
				{{ __('Save') }}
			</Button>
		</template>
	</Dialog>
</template>

<script setup>
import { call } from "@/utils/apiWrapper"
import { formatCurrency as formatCurrencyUtil } from "@/utils/currency"
import { useToast } from "@/composables/useToast"
import { Button, Dialog } from "frappe-ui"
import { computed, ref, watch } from "vue"

const props = defineProps({
	modelValue: Boolean,
	posProfile: String,
	currency: {
		type: String,
		default: "INR",
	},
	selectedCustomer: {
		type: String,
		default: "",
	},
})

const emit = defineEmits(["update:modelValue", "saved"])

const { showSuccess, showError } = useToast()

const show = ref(props.modelValue)
const loadingDefaults = ref(false)
const saving = ref(false)
const defaults = ref({})


// Search state
const activeSearchRow = ref(null)
const activeSearchField = ref(null)
const partySuggestions = ref([])
let searchTimeout = null

const form = ref({
	naming_series: "",
	voucher_type: "Journal Entry",
	posting_date: "",
	company: "",
	custom_branch: "",
	custom_cost_center: "",
	user_remark: "",
	accounts: [],
})

function formatCurrency(amount) {
	return formatCurrencyUtil(Number.parseFloat(amount || 0), props.currency)
}

const totalDebit = computed(() =>
	form.value.accounts.reduce((s, r) => s + (Number(r.debit_in_account_currency) || 0), 0),
)
const totalCredit = computed(() =>
	form.value.accounts.reduce((s, r) => s + (Number(r.credit_in_account_currency) || 0), 0),
)

function newRow() {
	return {
		account: "",
		party_type: "Customer",
		party: "",
		cost_center: form.value.custom_cost_center || "",
		debit_in_account_currency: 0,
		credit_in_account_currency: 0,
		is_advance: "",
	}
}

function addRow() {
	form.value.accounts.push(newRow())
}

function removeRow(idx) {
	form.value.accounts.splice(idx, 1)
}

async function loadDefaults() {
	if (!props.posProfile) return
	loadingDefaults.value = true
	try {
		const data = await call("pos_next.api.customers.get_journal_entry_defaults", {
			pos_profile: props.posProfile,
		})
		defaults.value = data
		form.value = {
			naming_series: data.naming_series_options?.[0] || "",
			voucher_type: "Journal Entry",
			posting_date: data.posting_date,
			company: data.company || "",
			custom_branch: data.branch || "",
			custom_cost_center: data.cost_center || "",
			user_remark: "",
			accounts: [],
		}
		// Start with two blank rows; pre-fill first row if cart has a customer
		form.value.accounts.push(newRow(), newRow())
		if (props.selectedCustomer) {
			const firstRow = form.value.accounts[0]
			firstRow.party = props.selectedCustomer
			try {
				const account = await call("pos_next.api.customers.get_customer_default_account", {
					customer: props.selectedCustomer,
					company: data.company,
				})
				firstRow.account = account || ""
			} catch {
				firstRow.account = "Debtors - IC"
			}
		}
	} catch (err) {
		console.error("Failed to load JE defaults:", err)
		showError(__("Failed to load Journal Entry defaults"))
	} finally {
		loadingDefaults.value = false
	}
}

// Party search (Customer only, filtered by POS branch)
async function searchParty(idx, term) {
	clearTimeout(searchTimeout)
	if (!term || term.length < 1) {
		partySuggestions.value = []
		return
	}
	const branch = form.value.custom_branch
	searchTimeout = setTimeout(async () => {
		try {
				// Build filters: match branch OR branch is empty/null
			const data = await call("frappe.client.get_list", {
				doctype: "Customer",
				filters: [
					["name", "like", `%${term}%`],
					...(branch ? [["custom_branch", "in", [branch, ""]]] : []),
				],
				fields: ["name", "customer_name", "custom_branch"],
				limit: 15,
			})
			partySuggestions.value = data || []
		} catch {
			partySuggestions.value = []
		}
	}, 250)
}

async function selectParty(idx, p) {
	const row = form.value.accounts[idx]
	row.party = p.name
	partySuggestions.value = []
	activeSearchRow.value = null

	try {
		const account = await call("pos_next.api.customers.get_customer_default_account", {
			customer: p.name,
			company: form.value.company,
		})
		row.account = account || ""
	} catch {
		row.account = "Debtors - IC"
	}
}

function onCreditInput(row) {
	if (Number(row.credit_in_account_currency) > 0) {
		row.is_advance = "Yes"
	}
}

function delayCloseSearch(field, idx) {
	setTimeout(() => {
		if (activeSearchField.value === field && activeSearchRow.value === idx) {
			activeSearchRow.value = null
			activeSearchField.value = null
			partySuggestions.value = []
		}
	}, 200)
}

async function saveJournalEntry() {
	if (form.value.accounts.length === 0) return

	const missingAccounts = form.value.accounts.some((r) => !r.account)
	if (missingAccounts) {
		showError(__("Please fill in Account for all rows"))
		return
	}

	saving.value = true
	try {
		const payload = {
			naming_series: form.value.naming_series,
			voucher_type: "Journal Entry",
			posting_date: form.value.posting_date,
			company: form.value.company,
			custom_branch: form.value.custom_branch,
			custom_cost_center: form.value.custom_cost_center,
			user_remark: form.value.user_remark,
			accounts: form.value.accounts.map((r) => ({
				account: r.account,
				party_type: r.party_type || null,
				party: r.party || null,
				cost_center: r.cost_center || null,
				debit_in_account_currency: Number(r.debit_in_account_currency) || 0,
				credit_in_account_currency: Number(r.credit_in_account_currency) || 0,
				is_advance: r.is_advance || null,
			})),
		}

		const result = await call("pos_next.api.customers.save_journal_entry", {
			data: JSON.stringify(payload),
		})

		showSuccess(__("Journal Entry {0} saved successfully", [result.name]))
		emit("saved")
		show.value = false
	} catch (err) {
		console.error("Failed to save JE:", err)
		showError(__("Failed to save Journal Entry"))
	} finally {
		saving.value = false
	}
}

watch(
	() => props.modelValue,
	(val) => {
		show.value = val
		if (val) loadDefaults()
	},
)

watch(show, (val) => {
	emit("update:modelValue", val)
})
</script>
