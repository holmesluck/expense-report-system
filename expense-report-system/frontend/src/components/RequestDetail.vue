<template>
  <div class="detail-wrapper">
    <div class="detail-bg"></div>
    
    <div class="detail-container">
      <header class="detail-header">
        <button @click="goBack" class="btn-back">← Back</button>
        <h1>Request Details</h1>
        <button @click="logout" class="btn-logout">Logout</button>
      </header>

      <div v-if="loading" class="loading">Loading...</div>
      
      <div v-else-if="request" class="detail-card">
        <div class="detail-section">
          <h2>Basic Information</h2>
          <div class="info-grid">
            <div class="info-item">
              <label>Request ID</label>
              <span>#{{ request.id }}</span>
            </div>
            <div class="info-item">
              <label>GPN</label>
              <span>{{ request.gpn }}</span>
            </div>
            <div class="info-item">
              <label>Status</label>
              <span :class="['status', request.status]">{{ request.status }}</span>
            </div>
            <div class="info-item">
              <label>Created At</label>
              <span>{{ formatDateTime(request.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h2>Report Details</h2>
          <div class="info-grid">
            <div class="info-item">
              <label>Report Title</label>
              <span>{{ request.report_title || '-' }}</span>
            </div>
            <div class="info-item">
              <label>Invoice Number</label>
              <span>{{ request.invoice_number }}</span>
            </div>
            <div class="info-item">
              <label>Category</label>
              <span>{{ request.item }}</span>
            </div>
            <div class="info-item">
              <label>Report Date</label>
              <span>{{ formatDate(request.report_date) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h2>Financial Information</h2>
          <div class="amount-display">
            <span class="amount-label">Amount</span>
            <span class="amount-value">${{ formatAmount(request.amount) }}</span>
          </div>
        </div>

        <div class="detail-section" v-if="request.details">
          <h2>Description</h2>
          <p class="description">{{ request.details }}</p>
        </div>

        <div class="detail-section" v-if="request.attachment">
          <h2>Attachment</h2>
          <p class="attachment">{{ request.attachment }}</p>
        </div>

        <div class="detail-actions" v-if="request.status === 'pending'">
          <button @click="goEdit" class="btn-primary">Edit Request</button>
          <button @click="cancelRequest" class="btn-danger">Cancel Request</button>
        </div>
      </div>

      <div v-else class="error-state">
        Request not found or you don't have permission to view it.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const API_BASE_URL = 'http://localhost:8000'

const request = ref(null)
const loading = ref(true)

onMounted(() => {
  const token = localStorage.getItem('user_token')
  const gpn = localStorage.getItem('user_gpn')
  
  if (!token || !gpn) {
    router.push('/login')
    return
  }
  
  loadRequest(route.params.id, gpn)
})

async function loadRequest(id, gpn) {
  try {
    const response = await fetchWithAuth(
      `${API_BASE_URL}/user/requests/${id}?gpn=${gpn}`
    )
    
    if (response && response.ok) {
      request.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to load request:', error)
  } finally {
    loading.value = false
  }
}

async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('user_token')
  
  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
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

function goBack() {
  router.push('/requests')
}

function goEdit() {
  // Pass request data to management page for editing
  router.push({
    path: '/requests',
    query: { edit: request.value.id }
  })
}

async function cancelRequest() {
  if (!confirm('Are you sure you want to cancel this request?')) return
  
  try {
    const gpn = localStorage.getItem('user_gpn')
    const response = await fetchWithAuth(
      `${API_BASE_URL}/user/requests/${request.value.id}?gpn=${gpn}`,
      { method: 'DELETE' }
    )
    
    if (response && response.ok) {
      alert('Request cancelled successfully')
      router.push('/requests')
    }
  } catch (error) {
    alert('Failed to cancel request')
  }
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

function formatDateTime(dateStr) {
  return new Date(dateStr).toLocaleString('en-US')
}
</script>

<style scoped>
.detail-wrapper {
  min-height: 100vh;
  position: relative;
  padding: 20px;
}

.detail-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  z-index: -1;
}

.detail-container {
  max-width: 800px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 3px solid #e60012;
}

.detail-header h1 {
  font-size: 1.8rem;
  color: #000;
  margin: 0;
}

.btn-back {
  background: transparent;
  color: #000;
  border: 2px solid #000;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-back:hover {
  background: #000;
  color: #fff;
}

.detail-card {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.detail-section {
  background: #f8f8f8;
  padding: 20px;
  border-radius: 12px;
}

.detail-section h2 {
  margin: 0 0 15px 0;
  color: #000;
  font-size: 1.2rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item label {
  font-size: 0.8rem;
  color: #666;
  text-transform: uppercase;
}

.info-item span {
  font-size: 1.1rem;
  color: #000;
  font-weight: 600;
}

.status {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.status.pending {
  background: #fff3cd;
  color: #856404;
}

.status.approved {
  background: #d4edda;
  color: #155724;
}

.amount-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #000;
  border-radius: 12px;
  color: #fff;
}

.amount-label {
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.amount-value {
  font-size: 2rem;
  font-weight: 700;
  color: #e60012;
}

.description, .attachment {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  line-height: 1.6;
  margin: 0;
}

.detail-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.btn-primary {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.btn-danger {
  background: #fff;
  color: #e60012;
  border: 2px solid #e60012;
  padding: 12px 30px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.btn-danger:hover {
  background: #e60012;
  color: #fff;
}

.loading, .error-state {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #666;
}
</style>
