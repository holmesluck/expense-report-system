<template>
  <div class="page-wrapper">
    <!-- Background layer for custom image -->
    <div class="background-layer"></div>
    
    <div class="glass-container">
      <header class="header">
        <h1>Expense Reporting System</h1>
        <p class="subtitle">Streamlined expense management for finance team</p>
      </header>

      <main>
        <!-- GPN input section with red accent -->
        <section class="gpn-section">
          <label class="gpn-label">
            <span class="label-text">GPN (7-8 digits)</span>
            <input 
              v-model="gpn" 
              placeholder="12345678" 
              maxlength="8"
              class="gpn-input"
              :class="{ 'error': gpnError }"
            />
            <span v-if="gpnError" class="error-msg">Please enter 7-8 digits</span>
          </label>
        </section>

        <!-- Report title and action buttons -->
        <section class="controls">
          <label class="title-label">
            <span class="label-text">Report Title</span>
            <input v-model="reportTitle" placeholder="Trip to client site" class="title-input" />
          </label>
          <div class="buttons">
            <button @click="addRow" class="btn-add">
              <span class="icon">+</span> Add Row
            </button>
            <button 
              @click="submit" 
              class="btn-submit"
              :disabled="isSubmitting || rows.length === 0"
            >
              <span v-if="isSubmitting" class="spinner"></span>
              <span v-else>Submit Report</span>
            </button>
          </div>
        </section>

        <!-- Expense items table with invoice number column -->
        <section class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Invoice Number</th>
                <th>Category</th>
                <th>Description</th>
                <th>Amount (USD)</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in rows" :key="row.id">
                <td>
                  <input 
                    type="date" 
                    v-model="row.date" 
                    class="table-input"
                  />
                </td>
                <td>
                  <input 
                    v-model="row.invoiceNumber" 
                    placeholder="INV-001" 
                    class="table-input"
                  />
                </td>
                <td>
                  <select v-model="row.category" class="table-select">
                    <option disabled value="">Select</option>
                    <option>Travel</option>
                    <option>Meals</option>
                    <option>Accommodation</option>
                    <option>Supplies</option>
                    <option>Other</option>
                  </select>
                </td>
                <td>
                  <input 
                    v-model="row.description" 
                    placeholder="Short description" 
                    class="table-input"
                  />
                </td>
                <td>
                  <input 
                    type="number" 
                    v-model.number="row.amount" 
                    min="0" 
                    step="0.01"
                    placeholder="0.00"
                    class="table-input amount-input"
                  />
                </td>
                <td>
                  <button 
                    class="btn-remove" 
                    @click="removeRow(idx)"
                    :disabled="rows.length === 1"
                  >
                    ×
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- Summary card with total amount -->
        <section class="summary-card">
          <div class="total-section">
            <span class="total-label">Total Amount:</span>
            <span class="total-value">${{ total.toFixed(2) }}</span>
          </div>
          <div class="count-section">
            <span>{{ rows.length }} item(s)</span>
          </div>
        </section>

        <!-- Alert message display -->
        <div v-if="message" :class="['alert', message.type]">
          {{ message.text }}
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'

// API base URL configuration
const API_BASE_URL = 'http://localhost:8000'

// Reactive state variables
const reportTitle = ref('')
const gpn = ref('')
const gpnError = ref(false)
const isSubmitting = ref(false)
const message = ref(null)

// Counter for unique row IDs
let idCounter = 1

// Initialize with one empty row including invoiceNumber
const rows = reactive([
  { 
    id: idCounter++, 
    date: '', 
    invoiceNumber: '',
    category: '', 
    description: '', 
    amount: 0 
  }
])

// Add a new empty row to the table
function addRow() {
  rows.push({ 
    id: idCounter++, 
    date: '', 
    invoiceNumber: '',
    category: '', 
    description: '', 
    amount: 0 
  })
}

// Remove a row from the table (prevent removing last row)
function removeRow(index) {
  if (rows.length > 1) {
    rows.splice(index, 1)
  }
}

// Calculate total amount from all rows
const total = computed(() => {
  return rows.reduce((sum, row) => sum + (Number(row.amount) || 0), 0)
})

// Validate GPN format (7-8 digits)
function validateGpn() {
  const gpnStr = gpn.value.trim()
  const isValid = /^\d{7,8}$/.test(gpnStr)
  gpnError.value = !isValid
  return isValid
}

// Validate all rows have required fields including invoiceNumber
function validateRows() {
  return rows.every(row => 
    row.date && 
    row.invoiceNumber.trim() &&
    row.category && 
    row.description.trim() && 
    row.amount > 0
  )
}

// Submit form data to backend API
async function submit() {
  // Validation checks
  if (!validateGpn()) {
    showMessage('Please enter a valid 7-8 digit GPN', 'error')
    return
  }
  
  if (!validateRows()) {
    showMessage('Please fill in all required fields (Date, Invoice Number, Category, Description, Amount)', 'error')
    return
  }

  isSubmitting.value = true
  message.value = null

  try {
    // Build payload from form data
    const payload = rows.map(row => ({
      gpn: gpn.value.trim(),
      report_title: reportTitle.value || 'Untitled Report',
      invoice_number: row.invoiceNumber.trim(),
      item: row.category,
      details: row.description,
      amount: Number(row.amount),
      attachment: null,
      report_date: row.date
    }))

    // Send POST request to backend
    const response = await fetch(`${API_BASE_URL}/reports/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }

    const result = await response.json()
    
    showMessage(`Successfully submitted ${result.length} expense item(s)!`, 'success')
    
    // Reset form after successful submission
    resetForm()
    
  } catch (error) {
    console.error('Submit error:', error)
    showMessage(`Failed to submit: ${error.message}`, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Reset form to initial state
function resetForm() {
  reportTitle.value = ''
  gpn.value = ''
  rows.length = 0
  rows.push({ 
    id: idCounter++, 
    date: '', 
    invoiceNumber: '',
    category: '', 
    description: '', 
    amount: 0 
  })
}

// Display alert message with auto-hide
function showMessage(text, type) {
  message.value = { text, type }
  setTimeout(() => {
    if (message.value?.text === text) {
      message.value = null
    }
  }, 3000)
}
</script>

<style scoped>
/* Page wrapper with full height */
.page-wrapper {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
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

/* Glass morphism container with red, white, black theme */
.glass-container {
  width: 100%;
  max-width: 1200px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Header styling with red accent */
.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #000000;
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  position: relative;
  display: inline-block;
}

.header h1::after {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: #e60012;
  border-radius: 2px;
}

.subtitle {
  color: #333333;
  font-size: 1.1rem;
  margin: 16px 0 0 0;
  font-weight: 500;
}

/* GPN input section with red accent border */
.gpn-section {
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(230, 0, 18, 0.05);
  border-radius: 12px;
  border-left: 4px solid #e60012;
}

.gpn-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-text {
  font-weight: 600;
  color: #000000;
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.gpn-input {
  padding: 12px 16px;
  border: 2px solid #000000;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  max-width: 200px;
  background: #ffffff;
  color: #000000;
}

.gpn-input:focus {
  outline: none;
  border-color: #e60012;
  box-shadow: 0 0 0 3px rgba(230, 0, 18, 0.2);
}

.gpn-input.error {
  border-color: #e60012;
  background: rgba(230, 0, 18, 0.05);
}

.error-msg {
  color: #e60012;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Control section with title input and buttons */
.controls {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  gap: 20px;
  flex-wrap: wrap;
}

.title-label {
  flex: 1;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-input {
  padding: 12px 16px;
  border: 2px solid #000000;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #ffffff;
  color: #000000;
}

.title-input:focus {
  outline: none;
  border-color: #e60012;
  box-shadow: 0 0 0 3px rgba(230, 0, 18, 0.2);
}

/* Button styling with red, white, black theme */
.buttons {
  display: flex;
  gap: 12px;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  border: 2px solid #000000;
  background: #ffffff;
  color: #000000;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-add:hover {
  background: #000000;
  color: #ffffff;
}

.icon {
  font-size: 1.2rem;
  font-weight: 700;
  color: #e60012;
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #e60012;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 15px rgba(230, 0, 18, 0.4);
}

.btn-submit:hover:not(:disabled) {
  background: #000000;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #cccccc;
}

/* Loading spinner animation */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Table styling with black header and red accents */
.table-wrap {
  background: #ffffff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  border: 1px solid #000000;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #000000;
  color: #ffffff;
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 3px solid #e60012;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #eeeeee;
  color: #000000;
}

tr:hover {
  background: rgba(230, 0, 18, 0.03);
}

/* Table input fields styling */
.table-input, .table-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #000000;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: #ffffff;
  color: #000000;
}

.table-input:focus, .table-select:focus {
  outline: none;
  border-color: #e60012;
  box-shadow: 0 0 0 3px rgba(230, 0, 18, 0.1);
}

.amount-input {
  text-align: right;
  font-weight: 600;
  color: #e60012;
}

/* Remove button with red theme */
.btn-remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid #e60012;
  background: #ffffff;
  color: #e60012;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  font-weight: 700;
}

.btn-remove:hover:not(:disabled) {
  background: #e60012;
  color: #ffffff;
}

.btn-remove:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  border-color: #cccccc;
  color: #cccccc;
}

/* Summary card with black background and red accent */
.summary-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #000000;
  border-radius: 16px;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border-left: 5px solid #e60012;
}

.total-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-label {
  font-size: 0.9rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.total-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #e60012;
}

.count-section {
  font-size: 0.95rem;
  opacity: 0.8;
}

/* Alert message styling */
.alert {
  margin-top: 20px;
  padding: 16px 20px;
  border-radius: 12px;
  font-weight: 600;
  animation: slideIn 0.3s ease;
  border-left: 5px solid;
}

.alert.success {
  background: #000000;
  color: #ffffff;
  border-left-color: #e60012;
}

.alert.error {
  background: rgba(230, 0, 18, 0.1);
  color: #e60012;
  border-left-color: #000000;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive design for mobile devices */
@media (max-width: 768px) {
  .glass-container {
    padding: 24px;
  }
  
  .header h1 {
    font-size: 1.8rem;
  }
  
  .controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .buttons {
    justify-content: stretch;
  }
  
  .btn-add, .btn-submit {
    flex: 1;
    justify-content: center;
  }
  
  table {
    font-size: 0.85rem;
  }
  
  th, td {
    padding: 10px;
  }
  
  .summary-card {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
}
</style>
