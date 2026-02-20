<template>
  <div class="page-wrapper">
    <!-- 背景层：您可以在这里添加自己的背景图 -->
    <div class="background-layer"></div>
    
    <div class="glass-container">
      <header class="header">
        <h1>Expense Reporting System</h1>
        <p class="subtitle">Streamlined expense management for modern teams</p>
      </header>

      <main>
        <!-- GPN 输入区域 -->
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

        <section class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
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

        <section class="summary-card">
          <div class="total-section">
            <span class="total-label">Total Amount:</span>
            <span class="total-value">${{ total.toFixed(2) }}</span>
          </div>
          <div class="count-section">
            <span>{{ rows.length }} item(s)</span>
          </div>
        </section>

        <!-- 状态提示 -->
        <div v-if="message" :class="['alert', message.type]">
          {{ message.text }}
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, ref } from 'vue'

// API 基础地址
const API_BASE_URL = 'http://localhost:8000'

const reportTitle = ref('')
const gpn = ref('')
const gpnError = ref(false)
const isSubmitting = ref(false)
const message = ref(null)

let idCounter = 1
const rows = reactive([
  { id: idCounter++, date: '', category: '', description: '', amount: 0 }
])

function addRow() {
  rows.push({ id: idCounter++, date: '', category: '', description: '', amount: 0 })
}

function removeRow(index) {
  if (rows.length > 1) {
    rows.splice(index, 1)
  }
}

const total = computed(() => {
  return rows.reduce((sum, row) => sum + (Number(row.amount) || 0), 0)
})

// 验证 GPN 格式
function validateGpn() {
  const gpnStr = gpn.value.trim()
  const isValid = /^\d{7,8}$/.test(gpnStr)
  gpnError.value = !isValid
  return isValid
}

// 验证所有行数据
function validateRows() {
  return rows.every(row => 
    row.date && 
    row.category && 
    row.description.trim() && 
    row.amount > 0
  )
}

// 提交功能
async function submit() {
  // 验证
  if (!validateGpn()) {
    showMessage('Please enter a valid 7-8 digit GPN', 'error')
    return
  }
  
  if (!validateRows()) {
    showMessage('Please fill in all required fields (Date, Category, Description, Amount)', 'error')
    return
  }

  isSubmitting.value = true
  message.value = null

  try {
    // 构建请求数据
    const payload = rows.map(row => ({
      gpn: gpn.value.trim(),
      report_title: reportTitle.value || 'Untitled Report',
      invoice_number: null,
      item: row.category,
      details: row.description,
      amount: Number(row.amount),
      attachment: null,
      report_date: row.date
    }))

    // 调用后端 API
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
    
    // 重置表单
    resetForm()
    
  } catch (error) {
    console.error('Submit error:', error)
    showMessage(`Failed to submit: ${error.message}`, 'error')
  } finally {
    isSubmitting.value = false
  }
}

function resetForm() {
  reportTitle.value = ''
  gpn.value = ''
  rows.length = 0
  rows.push({ id: idCounter++, date: '', category: '', description: '', amount: 0 })
}

function showMessage(text, type) {
  message.value = { text, type }
  // 3秒后自动清除消息
  setTimeout(() => {
    if (message.value?.text === text) {
      message.value = null
    }
  }, 3000)
}
</script>

<style scoped>
/* 页面整体包装 */
.page-wrapper {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: hidden;
}

/* 背景层 - 您可以在这里添加自己的背景图 */
.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* 默认渐变背景，您可以替换为图片 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  /* 如果要使用背景图，取消下面注释并修改路径 */
  /* background-image: url('/your-background-image.jpg'); */
  /* background-size: cover; */
  /* background-position: center; */
  z-index: -1;
}

/* 玻璃拟态容器 */
.glass-container {
  width: 100%;
  max-width: 1000px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* 头部样式 */
.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}

/* GPN 输入区域 */
.gpn-section {
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.gpn-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-text {
  font-weight: 600;
  color: #444;
  font-size: 0.95rem;
}

.gpn-input {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  max-width: 200px;
}

.gpn-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.gpn-input.error {
  border-color: #e74c3c;
}

.error-msg {
  color: #e74c3c;
  font-size: 0.85rem;
}

/* 控制区域 */
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
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.title-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 按钮样式 */
.buttons {
  display: flex;
  gap: 12px;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  border: 2px solid #667eea;
  background: transparent;
  color: #667eea;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-add:hover {
  background: #667eea;
  color: white;
}

.icon {
  font-size: 1.2rem;
  font-weight: 700;
}

.btn-submit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载动画 */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 表格样式 */
.table-wrap {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

tr:hover {
  background: rgba(102, 126, 234, 0.02);
}

/* 表格输入框 */
.table-input, .table-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  background: white;
}

.table-input:focus, .table-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.amount-input {
  text-align: right;
  font-weight: 600;
  color: #667eea;
}

/* 删除按钮 */
.btn-remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: none;
  background: #fee;
  color: #e74c3c;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-remove:hover:not(:disabled) {
  background: #e74c3c;
  color: white;
}

.btn-remove:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 汇总卡片 */
.summary-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.total-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.total-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.total-value {
  font-size: 1.8rem;
  font-weight: 700;
}

.count-section {
  font-size: 0.95rem;
  opacity: 0.9;
}

/* 提示消息 */
.alert {
  margin-top: 20px;
  padding: 16px 20px;
  border-radius: 12px;
  font-weight: 500;
  animation: slideIn 0.3s ease;
}

.alert.success {
  background: #d4edda;
  color: #155724;
  border-left: 4px solid #28a745;
}

.alert.error {
  background: #f8d7da;
  color: #721c24;
  border-left: 4px solid #dc3545;
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

/* 响应式设计 */
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
}
</style>
