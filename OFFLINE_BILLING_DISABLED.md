# Offline Billing Disable - Change Log

**Date:** 2026-04-28
**Purpose:** Completely disable offline billing feature

## Changes Made

### 1. `POS/src/utils/offline/offlineState.js`

#### Change 1: Force `isOffline` to always return `false`

**Location:** Lines 509-513

**Before:**
```javascript
get isOffline() {
    return this._manualOffline || !this._browserOnline || !this._serverOnline
}
```

**After:**
```javascript
get isOffline() {
    return false
}
```

#### Change 2: Disable network monitor start

**Location:** Lines 78-91

**Before:**
```javascript
start() {
    if (this._isMonitoring) return

    this._isMonitoring = true
    this._initBroadcastChannel()
    this._initVisibilityListener()

    // Initial ping
    this._performPing()

    // Start adaptive interval
    this._scheduleNextPing()

    log.info('Network monitor started')
}
```

**After:**
```javascript
start() {
    if (this._isMonitoring) return

    // Offline billing disabled - no network monitoring needed
    log.info('Network monitor disabled (offline billing disabled)')
}
```

---

### 2. `POS/src/pages/POSSale.vue`

#### Change: Hide "Offline Invoices" menu item

**Location:** Lines 63-74

**Before:**
```vue
<button
    v-if="offlineStore.pendingInvoicesCount > 0"
    @click="uiStore.showOfflineInvoicesDialog = true; offlineStore.loadPendingInvoices()"
    class="w-full text-start px-4 py-2.5 text-sm text-gray-700 hover:bg-orange-50 flex items-center gap-3 transition-colors relative"
>
    <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
    <span>{{ __('Offline Invoices') }}</span>
    <span class="ms-auto text-xs bg-orange-600 text-white px-1.5 py-0.5 rounded-full">
        {{ offlineStore.pendingInvoicesCount }}
    </span>
</button>
```

**After:** Commented out (wrapped in `<!-- -->`)

---

## Effects

- `isOffline()` always returns `false` - system is always "online"
- Network monitoring/pinging to `/api/method/pos_next.api.ping` is disabled
- Offline invoice save path in `POSSale.vue:1651` will never execute
- "Offline Invoices" menu item is hidden from header
- POSHeader displays "Online - Click to sync" status

## To Revert

1. **`offlineState.js`**: Restore the original `isOffline` getter logic and `start()` method
2. **`POSSale.vue`**: Uncomment the "Offline Invoices" button section

## Build Note

After reverting, run `npm run build` in `apps/pos_next/POS` directory to rebuild the frontend assets.
