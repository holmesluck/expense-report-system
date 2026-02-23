// import { createRouter, createWebHistory } from 'vue-router'
// import ExpenseReport from '../components/ExpenseReport.vue'
// import AdminLogin from '../components/AdminLogin.vue'
// import AdminPage from '../components/AdminPage.vue'

// // Route definitions
// const routes = [
// 	{
// 		path: '/',
// 		name: 'Home',
// 		component: ExpenseReport
// 	},
// 	{
// 		path: '/admin',           // This matches http://localhost:5173/admin
// 		name: 'AdminLogin',
// 		component: AdminLogin     // Make sure this component exists and has no errors
// 	},
// 	{
// 		path: '/admin/dashboard',
// 		name: 'AdminDashboard',
// 		component: AdminPage,
// 		meta: { requiresAuth: true }
// 	}
// ]

// const router = createRouter({
// 	history: createWebHistory(),
// 	routes
// })

// // Navigation guard for protected routes
// router.beforeEach((to, from, next) => {
// 	if (to.meta.requiresAuth) {
// 		const token = localStorage.getItem('admin_token')
// 		if (!token) {
// 			next('/admin')  // Redirect to login if no token
// 		} else {
// 			next()
// 		}
// 	} else {
// 		next()
// 	}
// })

// export default router

import { createRouter, createWebHistory } from 'vue-router'
import ExpenseReport from '../components/ExpenseReport.vue'
import UserLogin from '../components/UserLogin.vue'
import RequestManagement from '../components/RequestManagement.vue'
import RequestDetail from '../components/RequestDetail.vue'
import AdminLogin from '../components/AdminLogin.vue'
import AdminPage from '../components/AdminPage.vue'

const routes = [
	// Public routes
	{
		path: '/',
		name: 'Home',
		component: ExpenseReport,
		meta: { requiresAuth: false }
	},

	// User authentication routes
	{
		path: '/login',
		name: 'UserLogin',
		component: UserLogin,
		meta: { requiresAuth: false, isUserRoute: true }
	},
	{
		path: '/requests',
		name: 'RequestManagement',
		component: RequestManagement,
		meta: { requiresAuth: true, isUserRoute: true }
	},
	{
		path: '/requests/:id',
		name: 'RequestDetail',
		component: RequestDetail,
		meta: { requiresAuth: true, isUserRoute: true }
	},

	// Admin routes
	{
		path: '/admin',
		name: 'AdminLogin',
		component: AdminLogin,
		meta: { requiresAuth: false, isAdminRoute: true }
	},
	{
		path: '/admin/dashboard',
		name: 'AdminDashboard',
		component: AdminPage,
		meta: { requiresAuth: true, isAdminRoute: true }
	}
]

const router = createRouter({
	history: createWebHistory(),
	routes
})

// Route guard for authentication
router.beforeEach((to, from, next) => {
	// Check if route requires authentication
	if (to.meta.requiresAuth) {
		// Determine which token to check based on route type
		if (to.meta.isUserRoute) {
			const userToken = localStorage.getItem('user_token')
			if (!userToken) {
				next('/login')
				return
			}
		} else if (to.meta.isAdminRoute) {
			const adminToken = localStorage.getItem('admin_token')
			if (!adminToken) {
				next('/admin')
				return
			}
		}
	}

	next()
})

export default router
