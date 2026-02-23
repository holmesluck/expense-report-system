<template>
  <div class="management-wrapper">
    <div class="management-bg"></div>
    
    <div class="management-container">
      <header class="management-header">
        <div>
          <h1>My Expense Requests</h1>
          <p class="subtitle">GPN: {{ userGpn }}</p>
        </div>
        <div class="header-actions">
          <button @click="goToSubmit" class="btn-secondary">Submit New</button>
          <button @click="logout" class="btn-logout">Logout</button>
        </div>
      </header>

      <!-- Requests list -->
      <section class="requests-list">
        <div v-if="loading" class="loading">Loading...</div>
        
        <div v-else-if="requests.length === 0" class="empty-state">
          No requests found. <router-link to="/">Submit your first report</router-link>
        </div>
        
        <div v-else class="request-cards">
          <div 
            v-for="request in requests" 
            :key="request.id" 
            class="request-card"
            @click="viewDetail(request.id)"
          >
            <div class="card-header">
              <span class="request-id">#{{ request.id }}</span>
              <span :class="['status-badge', request.status]">{{ request.status }}</span>
            </div>
            
            <div class="card-body">
              <h4>{{ request.report_title || 'Untitled' }}</h4>
              <p class="invoice-info">Invoice: {{ request.invoice_number }}</p>
              <p class="category">{{ request.item }}</p>
              <p class="amount">${{ formatAmount(request.amount) }}</p>
              <p class="date">{{ formatDate(request.report_date) }}</p>
            </div>
            
            <div class="card-actions" @click.stop>
              <button 
                v-if="request.status === 'pending'"
                @click="editRequest(request)" 
                class="btn-edit"
              >
                Edit
              </button>
              <button 
                v-if="request.status === 'pending'"
                @click="cancelRequest(request.id)" 
                class="btn-cancel"
              >
                Cancel
              </button>
              <button @click="viewDetail(request.id)" class="btn-view">
                View Details
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Edit Modal -->
      <div v-if="editingRequest" class="modal-overlay" @click.self="closeEdit">
        <div class="modal-content">
          <h3>Edit Request #{{ editingRequest.id }}</h3>
          
          <div class="form-group">
            <label>Report Title</label>
            <input v-model="editForm.report_title" />
          </div>
          
          <div class="form-group">
            <label>Invoice Number</label>
            <input v-model="editForm.invoice_number" />
          </div>
          
          <div class="form-group">
            <label>Category</label>
            <select v-model="editForm.item">
              <option>Travel</option>
              <option>Meals</option>
              <option>Accommodation</option>
              <option>Supplies</option>
              <option>Other</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Details</label>
            <textarea v-model="editForm.details" rows="3"></textarea>
          </div>
          
          <div class="form-group">
            <label>Amount</label>
            <input type="number" v-model.number="editForm.amount" step="0.01" />
          </div>
          
          <div class="form-group">
            <label>Report Date</label>
            <input type="date" v-model="editForm.report_date" />
          </div>
          
          <div class="modal-actions">
            <button @click="closeEdit" class="btn-secondary">Cancel</button>
            <button @click="saveEdit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = 'http://localhost:8000'

const requests = ref([])
const loading = ref(true)
const userGpn = ref('')
const message = ref(null)
const editingRequest = ref(null)
const editForm = ref({})
const saving = ref(false)

// Check authentication on mount
onMounted(() => {
  const token = localStorage.getItem('user_token')
  const gpn = localStorage.getItem('user_gpn')
  
  if (!token || !gpn) {
    router.push('/login')
    return
  }
  
  userGpn.value = gpn
  loadRequests(gpn)
})

async function loadRequests(gpn) {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/user/requests?gpn=${gpn}`)
    if (response) {
      requests.value = await response.json()
    }
  } catch (error) {
    showMessage('Failed to load requests', 'error')
  } finally {
    loading.value = false
  }
}

async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('user_token')
  
  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
  
  const response = await fetch(url, options)
  
  if (response.status === 401) {
    localStorage.removeItem('user_token')
    localStorage.removeItem('user_gpn')
    router.push('/login')
    return null
  }
  
  return response
}

function viewDetail(id) {
  router.push(`/requests/${id}`)
}

function editRequest(request) {
  editingRequest.value = request
  editForm.value = { ...request }
}

function closeEdit() {
  editingRequest.value = null
  editForm.value = {}
}

async function saveEdit() {
  saving.value = true
  
  try {
    const response = await fetchWithAuth(
      `${API_BASE_URL}/user/requests/${editingRequest.value.id}?gpn=${userGpn.value}`,
      {
        method: 'PUT',
        body: JSON.stringify(editForm.value)
      }
    )
    
    if (response && response.ok) {
      showMessage('Request updated successfully', 'success')
      closeEdit()
      loadRequests(userGpn.value)
    } else {
      const error = await response.json()
      throw new Error(error.detail || 'Update failed')
    }
  } catch (err) {
    showMessage(err.message, 'error')
  } finally {
    saving.value = false
  }
}

async function cancelRequest(id) {
  if (!confirm('Are you sure you want to cancel this request?')) return
  
  try {
    const response = await fetchWithAuth(
      `${API_BASE_URL}/user/requests/${id}?gpn=${userGpn.value}`,
      { method: 'DELETE' }
    )
    
    if (response && response.ok) {
      showMessage('Request cancelled successfully', 'success')
      loadRequests(userGpn.value)
    }
  } catch (error) {
    showMessage('Failed to cancel request', 'error')
  }
}

function goToSubmit() {
  router.push('/')
}

function logout() {
  localStorage.removeItem('user_token')
  localStorage.removeItem('user_gpn')
  router.push('/login')
}

function formatAmount(amount) {
  return Number(amount).toFixed(2)
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US')
}

function showMessage(text, type) {
  message.value = { text, type }
  setTimeout(() => { message.value = null }, 3000)
}
</script>

<style scoped>
.management-wrapper {
  min-height: 100vh;
  position: relative;
  padding: 20px;
}

.management-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  z-index: -1;
}

.management-container {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 3px solid #e60012;
}

.management-header h1 {
  font-size: 2rem;
  color: #000;
  margin: 0;
}

.subtitle {
  color: #666;
  margin: 5px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn-secondary {
  background: #fff;
  color: #000;
  border: 2px solid #000;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.btn-secondary:hover {
  background: #000;
  color: #fff;
}

.btn-logout {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.request-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.request-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s;
  border-left: 4px solid #e60012;
}

.request-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.request-id {
  font-weight: 700;
  color: #000;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.approved {
  background: #d4edda;
  color: #155724;
}

.status-badge.rejected {
  background: #f8d7da;
  color: #721c24;
}

.card-body h4 {
  margin: 0 0 10px 0;
  color: #000;
}

.card-body p {
  margin: 5px 0;
  color: #666;
  font-size: 0.9rem;
}

.card-body .amount {
  color: #e60012;
  font-weight: 700;
  font-size: 1.2rem;
}

.card-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.btn-edit, .btn-cancel, .btn-view {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-edit {
  background: #000;
  color: #fff;
}

.btn-cancel {
  background: #fff;
  color: #e60012;
  border: 2px solid #e60012;
}

.btn-view {
  background: #e60012;
  color: #fff;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 30px;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  color: #000;
  border-bottom: 3px solid #e60012;
  padding-bottom: 10px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 2px solid #000;
  border-radius: 8px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #e60012;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-primary {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.alert {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 8px;
  font-weight: 600;
  animation: slideIn 0.3s;
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
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
