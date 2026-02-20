import { createRouter, createWebHistory } from 'vue-router'
import ExpenseReport from '../components/ExpenseReport.vue'
import AdminLogin from '../components/AdminLogin.vue'
import AdminPage from '../components/AdminPage.vue'

// Route definitions
const routes = [
	{
		path: '/',
		name: 'Home',
		component: ExpenseReport
	},
	{
		path: '/admin',           // This matches http://localhost:5173/admin
		name: 'AdminLogin',
		component: AdminLogin     // Make sure this component exists and has no errors
	},
	{
		path: '/admin/dashboard',
		name: 'AdminDashboard',
		component: AdminPage,
		meta: { requiresAuth: true }
	}
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

// Navigation guard for protected routes
router.beforeEach((to, from, next) => {
	if (to.meta.requiresAuth) {
		const token = localStorage.getItem('admin_token')
		if (!token) {
			next('/admin')  // Redirect to login if no token
		} else {
			next()
		}
	} else {
		next()
	}
})

export default router
