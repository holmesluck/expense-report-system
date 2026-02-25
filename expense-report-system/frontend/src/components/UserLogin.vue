<template>
  <div class="login-wrapper">
    <div class="background-layer"></div>
    
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <h1>Review Your Requests</h1>
          <p class="subtitle">Enter your GPN and password to view your expense reports</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label>GPN</label>
            <input 
              v-model="gpn" 
              type="text" 
              placeholder="12345678"
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <label>Password</label>
            <input 
              v-model="password" 
              type="password" 
              placeholder="Enter password from email"
              :disabled="loading"
            />
          </div>
          
          <button 
            type="submit" 
            class="btn-login"
            :disabled="loading || !gpn || !password"
          >
            <span v-if="loading" class="spinner"></span>
            <span v-else>Login</span>
          </button>
        </form>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="login-footer">
          <p>Password was sent to your email when you submitted your first report</p>
          <router-link to="/" class="back-link">← Back to Submit Report</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = 'http://localhost:8000'

const gpn = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        gpn: gpn.value,
        password: password.value
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Login failed')
    }
    
    const data = await response.json()
    
    // Save token and GPN
    localStorage.setItem('user_token', data.access_token)
    localStorage.setItem('user_gpn', data.gpn)
    
    // Redirect to request management page
    router.push('/requests')
    
  } catch (err) {
    error.value = err.message || 'Invalid GPN or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Similar to AdminLogin.vue with same styling */
.login-wrapper {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.background-layer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/images/bg.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  z-index: -1;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-box {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 1.8rem;
  color: #000;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.login-header h1::after {
  content: '';
  display: block;
  width: 50px;
  height: 4px;
  background: #e60012;
  margin: 10px auto 0;
  border-radius: 2px;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
  margin-top: 10px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #000;
  text-transform: uppercase;
}

.form-group input {
  padding: 14px;
  border: 2px solid #000;
  border-radius: 10px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #e60012;
}

.btn-login {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 16px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  text-transform: uppercase;
}

.btn-login:hover:not(:disabled) {
  background: #000;
}

.error-message {
  background: #fee;
  color: #e60012;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  text-align: center;
  border-left: 4px solid #e60012;
}

.login-footer {
  text-align: center;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-footer p {
  color: #999;
  font-size: 0.8rem;
  margin: 0 0 10px 0;
}

.back-link {
  color: #e60012;
  text-decoration: none;
  font-weight: 600;
}

.back-link:hover {
  text-decoration: underline;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
