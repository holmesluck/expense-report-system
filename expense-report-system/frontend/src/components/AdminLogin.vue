<template>
  <div class="login-wrapper">
    <!-- Background layer -->
    <div class="login-bg"></div>
    
    <div class="login-container">
      <div class="login-box">
        <div class="login-header">
          <h1>Administrator Login</h1>
          <p class="subtitle">Expense Report Management System</p>
        </div>
        
        <!-- Login form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label>Username</label>
            <input 
              v-model="username" 
              type="text" 
              placeholder="Enter admin username"
              :disabled="loading"
            />
          </div>
          
          <div class="form-group">
            <label>Password</label>
            <input 
              v-model="password" 
              type="password" 
              placeholder="Enter password"
              :disabled="loading"
            />
          </div>
          
          <button 
            type="submit" 
            class="btn-login"
            :disabled="loading || !username || !password"
          >
            <span v-if="loading" class="spinner"></span>
            <span v-else>Login</span>
          </button>
        </form>
        
        <!-- Error message display -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <div class="login-footer">
          <p>Authorized personnel only</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = 'http://localhost:8000/admin'

// Reactive state variables
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

// Handle login form submission
async function handleLogin() {
  loading.value = true
  error.value = ''
  
  try {
    // Send login request to backend
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    
    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Login failed')
    }
    
    const data = await response.json()
    
    // Store JWT token in localStorage
    localStorage.setItem('admin_token', data.access_token)
    
    // Redirect to admin dashboard
    router.push('/admin/dashboard')
    
  } catch (err) {
    error.value = err.message || 'Invalid username or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Login page wrapper */
.login-wrapper {
  min-height: 100vh;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Dark background layer */
.login-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
  z-index: -1;
}

/* Centered login container */
.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

/* Glass morphism login box */
.login-box {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Header with red accent */
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

/* Form styling */
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
  letter-spacing: 0.5px;
}

.form-group input {
  padding: 14px;
  border: 2px solid #000;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #fff;
}

.form-group input:focus {
  outline: none;
  border-color: #e60012;
  box-shadow: 0 0 0 3px rgba(230, 0, 18, 0.1);
}

/* Login button with red theme */
.btn-login {
  background: #e60012;
  color: #fff;
  border: none;
  padding: 16px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: 10px;
}

.btn-login:hover:not(:disabled) {
  background: #000;
  transform: translateY(-2px);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Error message styling */
.error-message {
  background: #fee;
  color: #e60012;
  padding: 12px;
  border-radius: 8px;
  margin-top: 15px;
  text-align: center;
  font-weight: 600;
  border-left: 4px solid #e60012;
}

/* Footer text */
.login-footer {
  text-align: center;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-footer p {
  color: #999;
  font-size: 0.8rem;
  margin: 0;
}

/* Loading spinner */
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
