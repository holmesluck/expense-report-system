<template>
  <div class="admin-wrapper">
    <!-- Background layer for custom image -->
    <div class="background-layer"></div>
    
    <div class="admin-container">
      <!-- Header with logout button -->
      <header class="admin-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p class="subtitle">Real-time Expense Report Management</p>
        </div>
        <button @click="logout" class="btn-logout">Logout</button>
      </header>

      <!-- Statistics cards -->
      <section class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_count }}</div>
          <div class="stat-label">Total Records</div>
        </div>
        <div class="stat-card highlight">
          <div class="stat-value">${{ formatNumber(stats.total_amount) }}</div>
          <div class="stat-label">Total Amount</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${{ formatNumber(stats.avg_amount) }}</div>
          <div class="stat-label">Average Amount</div>
        </div>
      </section>

      <!-- Category breakdown section -->
      <section class="breakdown-section" v-if="Object.keys(stats.item_breakdown).length > 0">
        <h3>Category Breakdown</h3>
        <div class="breakdown-grid">
          <div v-for="(data, item) in stats.item_breakdown" :key="item" class="breakdown-item">
            <div class="breakdown-name">{{ item }}</div>
            <div class="breakdown-stats">
              <span class="count">{{ data.count }} items</span>
              <span class="total">${{ formatNumber(data.total) }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Filter section -->
      <section class="filter-section">
        <h3>Filter Reports</h3>
        <div class="filter-grid">
          <!-- GPN Search Input -->
          <div class="filter-group gpn-search">
            <label>GPN Search</label>
            <div class="gpn-input-wrapper">
              <input 
                type="text" 
                v-model="gpnSearchInput"
                placeholder="Enter GPN to search..."
                @keyup.enter="searchGpn"
                maxlength="8"
              />
              <button @click="searchGpn" class="btn-search" :disabled="!gpnSearchInput.trim()">
                Search
              </button>
            </div>
            <small class="hint">Enter 7-8 digit GPN and press Enter or click Search</small>
          </div>
          
          <!-- GPN Dropdown Filter -->
          <div class="filter-group">
            <label>GPN Filter (Dropdown)</label>
            <select v-model="filters.gpn" @change="onGpnSelectChange">
              <option value="">All GPNs</option>
              <option v-for="gpn in gpnList" :key="gpn" :value="gpn">{{ gpn }}</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>Category</label>
            <select v-model="filters.item">
              <option value="">All Categories</option>
              <option v-for="item in itemList" :key="item" :value="item">{{ item }}</option>
            </select>
          </div>
          
          <!-- Date inputs with English locale -->
          <div class="filter-group">
            <label>Start Date</label>
            <input 
              type="date" 
              v-model="filters.start_date"
              lang="en-US"
              placeholder="MM/DD/YYYY"
            />
          </div>
          
          <div class="filter-group">
            <label>End Date</label>
            <input 
              type="date" 
              v-model="filters.end_date"
              lang="en-US"
              placeholder="MM/DD/YYYY"
            />
          </div>
          
          <div class="filter-group">
            <label>Min Amount</label>
            <input type="number" v-model.number="filters.min_amount" placeholder="0" />
          </div>
          
          <div class="filter-group">
            <label>Max Amount</label>
            <input type="number" v-model.number="filters.max_amount" placeholder="Max" />
          </div>
        </div>
        
        <div class="filter-actions">
          <button @click="applyFilters" class="btn-primary">Apply Filters</button>
          <button @click="resetFilters" class="btn-secondary">Reset</button>
          <button @click="refreshData" class="btn-refresh" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>↻ Refresh</span>
          </button>
        </div>
      </section>

      <!-- Data table section -->
      <section class="table-section">
        <div class="table-header">
          <h3>All Reports ({{ reports.length }})</h3>
          <div class="table-controls">
            <select v-model="sortBy" @change="applyFilters">
              <option value="created_at">Sort by Date</option>
              <option value="amount">Sort by Amount</option>
              <option value="gpn">Sort by GPN</option>
              <option value="item">Sort by Category</option>
            </select>
            <select v-model="sortOrder" @change="applyFilters">
              <option value="desc">Descending</option>
              <option value="asc">Ascending</option>
            </select>
          </div>
        </div>
        
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>GPN</th>
                <th>Title</th>
                <th>Category</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in reports" :key="report.id">
                <td>{{ report.id }}</td>
                <td>{{ report.gpn }}</td>
                <td>{{ report.report_title || '-' }}</td>
                <td><span class="category-tag">{{ report.item }}</span></td>
                <td>{{ formatDate(report.report_date) }}</td>
                <td class="amount">${{ formatNumber(report.amount) }}</td>
                <td>{{ formatDateTime(report.created_at) }}</td>
                <td>
                  <button @click="viewDetail(report)" class="btn-view">View</button>
                  <button @click="deleteReport(report.id)" class="btn-delete">Delete</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="reports.length === 0" class="empty-state">
          No records found matching your criteria.
        </div>
      </section>

      <!-- Detail modal -->
      <div v-if="selectedReport" class="modal-overlay" @click.self="closeDetail">
        <div class="modal-content">
          <h3>Report Details #{{ selectedReport.id }}</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>GPN:</label>
              <span>{{ selectedReport.gpn }}</span>
            </div>
            <div class="detail-item">
              <label>Report Title:</label>
              <span>{{ selectedReport.report_title || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>Invoice Number:</label>
              <span>{{ selectedReport.invoice_number || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>Category:</label>
              <span>{{ selectedReport.item }}</span>
            </div>
            <div class="detail-item">
              <label>Report Date:</label>
              <span>{{ formatDate(selectedReport.report_date) }}</span>
            </div>
            <div class="detail-item">
              <label>Amount:</label>
              <span class="highlight-amount">${{ formatNumber(selectedReport.amount) }}</span>
            </div>
            <div class="detail-item full-width">
              <label>Details:</label>
              <p>{{ selectedReport.details || 'No details provided' }}</p>
            </div>
            <div class="detail-item full-width" v-if="selectedReport.attachment">
              <label>Attachment:</label>
              <span>{{ selectedReport.attachment }}</span>
            </div>
          </div>
          <button @click="closeDetail" class="btn-close">Close</button>
        </div>
      </div>

      <!-- Alert message -->
      <div v-if="message" :class="['alert', message.type]">
        {{ message.text }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = 'http://localhost:8000/admin'

// Reactive state variables
const loading = ref(false)
const reports = ref([])
const stats = ref({
  total_count: 0,
  total_amount: 0,
  avg_amount: 0,
  item_breakdown: {}
})
const gpnList = ref([])
const itemList = ref([])
const selectedReport = ref(null)
const message = ref(null)

// GPN search input state
const gpnSearchInput = ref('')

// Filter state
const filters = reactive({
  gpn: '',
  item: '',
  start_date: '',
  end_date: '',
  min_amount: null,
  max_amount: null
})

// Sorting state
const sortBy = ref('created_at')
const sortOrder = ref('desc')

// Format number with 2 decimal places
function formatNumber(num) {
  return Number(num).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Format date only (MM/DD/YYYY)
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US')
}

// Format date and time
function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('en-US')
}

// Show alert message with auto-hide
function showMessage(text, type) {
  message.value = { text, type }
  setTimeout(() => { message.value = null }, 3000)
}

// Check if user is authenticated
function checkAuth() {
  const token = localStorage.getItem('admin_token')
  if (!token) {
    router.push('/admin')
    return null
  }
  return token
}

// Fetch with authentication header
async function fetchWithAuth(url, options = {}) {
  const token = checkAuth()
  if (!token) return
  
  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  }
  
  const response = await fetch(url, options)
  
  // Handle 401 unauthorized
  if (response.status === 401) {
    localStorage.removeItem('admin_token')
    router.push('/admin')
    return null
  }
  
  return response
}

// Fetch statistics from backend
async function fetchStats() {
  try {
    const params = new URLSearchParams()
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)
    
    const response = await fetchWithAuth(`${API_BASE_URL}/stats?${params}`)
    if (response && response.ok) {
      stats.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// Fetch filter dropdown options
async function fetchFilterOptions() {
  try {
    const [gpnRes, itemRes] = await Promise.all([
      fetchWithAuth(`${API_BASE_URL}/gpns`),
      fetchWithAuth(`${API_BASE_URL}/items`)
    ])
    
    if (gpnRes && gpnRes.ok) gpnList.value = await gpnRes.json()
    if (itemRes && itemRes.ok) itemList.value = await itemRes.json()
  } catch (error) {
    console.error('Failed to fetch filter options:', error)
  }
}

// Fetch reports list with filters
async function fetchReports() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    
    // Add filter parameters
    if (filters.gpn) params.append('gpn', filters.gpn)
    if (filters.item) params.append('item', filters.item)
    if (filters.start_date) params.append('start_date', filters.start_date)
    if (filters.end_date) params.append('end_date', filters.end_date)
    if (filters.min_amount !== null && filters.min_amount !== '') params.append('min_amount', filters.min_amount)
    if (filters.max_amount !== null && filters.max_amount !== '') params.append('max_amount', filters.max_amount)
    
    // Add sorting parameters
    params.append('sort_by', sortBy.value)
    params.append('sort_order', sortOrder.value)
    params.append('limit', '1000')
    
    const response = await fetchWithAuth(`${API_BASE_URL}/reports?${params}`)
    
    if (response && response.ok) {
      reports.value = await response.json()
    } else {
      showMessage('Failed to fetch reports', 'error')
    }
  } catch (error) {
    console.error('Failed to fetch reports:', error)
    showMessage('Network error', 'error')
  } finally {
    loading.value = false
  }
}

// Search GPN by input
function searchGpn() {
  const gpn = gpnSearchInput.value.trim()
  
  // Validate GPN format (7-8 digits)
  if (!/^\d{7,8}$/.test(gpn)) {
    showMessage('Please enter a valid 7-8 digit GPN', 'error')
    return
  }
  
  // Set the filter and clear dropdown selection
  filters.gpn = gpn
  
  // If GPN not in list, add it temporarily for display
  if (!gpnList.value.includes(gpn)) {
    gpnList.value = [...gpnList.value, gpn].sort()
  }
  
  applyFilters()
  showMessage(`Searching for GPN: ${gpn}`, 'success')
}

// Handle GPN dropdown change
function onGpnSelectChange() {
  // Clear search input when dropdown is used
  if (filters.gpn) {
    gpnSearchInput.value = ''
  }
  applyFilters()
}

// Apply filters and refresh data
function applyFilters() {
  fetchReports()
  fetchStats()
}

// Reset all filters to default
function resetFilters() {
  filters.gpn = ''
  filters.item = ''
  filters.start_date = ''
  filters.end_date = ''
  filters.min_amount = null
  filters.max_amount = null
  sortBy.value = 'created_at'
  sortOrder.value = 'desc'
  gpnSearchInput.value = '' // Clear search input
  applyFilters()
}

// Refresh all data
function refreshData() {
  fetchFilterOptions()
  applyFilters()
  showMessage('Data refreshed', 'success')
}

// View report details in modal
function viewDetail(report) {
  selectedReport.value = report
}

// Close detail modal
function closeDetail() {
  selectedReport.value = null
}

// Delete report by ID
async function deleteReport(id) {
  if (!confirm(`Are you sure you want to delete report #${id}?`)) return
  
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/reports/${id}`, {
      method: 'DELETE'
    })
    
    if (response && response.ok) {
      showMessage('Report deleted successfully', 'success')
      refreshData()
    } else {
      showMessage('Failed to delete report', 'error')
    }
  } catch (error) {
    console.error('Delete error:', error)
    showMessage('Network error', 'error')
  }
}

// Logout and clear token
function logout() {
  localStorage.removeItem('admin_token')
  router.push('/admin')
}

// Initialize on component mount
onMounted(() => {
  const token = checkAuth()
  if (token) {
    fetchFilterOptions()
    refreshData()
  }
})
</script>

<style scoped>
/* Admin page wrapper */
.admin-wrapper {
  min-height: 100vh;
  position: relative;
  padding: 20px;
}

/* Background layer - customizable with your own image */
.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* Local image path - put your image in public/images/ */
  background-image: url('/images/bg.jpg');
  background-size: cover;        /* Cover entire screen */
  background-position: center;   /* Center the image */
  background-repeat: no-repeat;  /* Do not repeat */
  background-attachment: fixed;  /* Fixed background on scroll */
  z-index: -1;
}

/* Main container with glass effect */
.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

/* Header with logout button */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 3px solid #e60012;
}

.admin-header h1 {
  font-size: 2.2rem;
  color: #000;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin: 8px 0 0 0;
}

.btn-logout {
  background: #000;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  text-transform: uppercase;
}

.btn-logout:hover {
  background: #e60012;
}

/* Statistics grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #000;
  color: #fff;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  border-left: 5px solid #e60012;
}

.stat-card.highlight {
  background: #e60012;
  border-left-color: #000;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  opacity: 0.9;
}

/* Category breakdown section */
.breakdown-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f8f8;
  border-radius: 12px;
}

.breakdown-section h3 {
  margin: 0 0 15px 0;
  color: #000;
  font-size: 1.2rem;
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.breakdown-item {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #e60012;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.breakdown-name {
  font-weight: 600;
  color: #000;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.breakdown-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #666;
}

.breakdown-stats .total {
  color: #e60012;
  font-weight: 600;
}

/* Filter section */
.filter-section {
  background: #f0f0f0;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.filter-section h3 {
  margin: 0 0 20px 0;
  color: #000;
  font-size: 1.2rem;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #333;
  text-transform: uppercase;
}

.filter-group input,
.filter-group select {
  padding: 10px;
  border: 2px solid #000;
  border-radius: 6px;
  font-size: 0.95rem;
  background: #fff;
}

.filter-group input:focus,
.filter-group select:focus {
  outline: none;
  border-color: #e60012;
}

/* GPN Search Input Styles */
.gpn-search {
  grid-column: 1 / -1;
}

.gpn-input-wrapper {
  display: flex;
  gap: 10px;
}

.gpn-input-wrapper input {
  flex: 1;
  padding: 10px;
  border: 2px solid #000;
  border-radius: 6px;
  font-size: 0.95rem;
}

.gpn-input-wrapper input:focus {
  outline: none;
  border-color: #e60012;
  box-shadow: 0 0 0 3px rgba(230, 0, 18, 0.1);
}

.btn-search {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.btn-search:hover:not(:disabled) {
  background: #000;
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint {
  font-size: 0.75rem;
  color: #666;
  font-style: italic;
}

.filter-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:hover {
  background: #000;
}

.btn-secondary {
  background: #fff;
  color: #000;
  border: 2px solid #000;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #000;
  color: #fff;
}

.btn-refresh {
  background: #000;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Table section */
.table-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.table-header h3 {
  margin: 0;
  color: #000;
  font-size: 1.3rem;
}

.table-controls {
  display: flex;
  gap: 10px;
}

.table-controls select {
  padding: 8px 12px;
  border: 2px solid #000;
  border-radius: 6px;
  background: #fff;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

thead {
  background: #000;
  color: #fff;
}

th {
  padding: 15px;
  text-align: left;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

td {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
}

tbody tr:hover {
  background: #f8f8f8;
}

.category-tag {
  background: #e60012;
  color: #fff;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.amount {
  font-weight: 700;
  color: #e60012;
}

.btn-view {
  background: #000;
  color: #fff;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 5px;
  font-size: 0.8rem;
}

.btn-delete {
  background: #fff;
  color: #e60012;
  border: 2px solid #e60012;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-delete:hover {
  background: #e60012;
  color: #fff;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

/* Detail modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: #fff;
  border-radius: 16px;
  padding: 30px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #000;
  font-size: 1.5rem;
  border-bottom: 3px solid #e60012;
  padding-bottom: 10px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 0.8rem;
  color: #666;
  text-transform: uppercase;
  font-weight: 600;
}

.detail-item span {
  font-size: 1rem;
  color: #000;
  font-weight: 500;
}

.highlight-amount {
  color: #e60012;
  font-size: 1.3rem;
  font-weight: 700;
}

.detail-item p {
  margin: 0;
  padding: 10px;
  background: #f8f8f8;
  border-radius: 6px;
  line-height: 1.5;
}

.btn-close {
  width: 100%;
  background: #000;
  color: #fff;
  border: none;
  padding: 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 10px;
}

.btn-close:hover {
  background: #e60012;
}

/* Alert message */
.alert {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 8px;
  font-weight: 600;
  animation: slideIn 0.3s ease;
  z-index: 1001;
}

.alert.success {
  background: #000;
  color: #fff;
  border-left: 4px solid #e60012;
}

.alert.error {
  background: #e60012;
  color: #fff;
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* Loading spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive design */
@media (max-width: 768px) {
  .admin-container {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-grid {
    grid-template-columns: 1fr;
  }
  
  .gpn-input-wrapper {
    flex-direction: column;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .table-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .admin-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
}
</style>
