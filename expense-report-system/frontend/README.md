# Vue Vite Minimal App (configured)

说明：下面的命令用于在本机启动开发服务器和构建项目。

Commands:

```bash
npm install
npm run dev
```

Files added:

- [index.html](index.html)
- [src/main.js](src/main.js)
- [src/App.vue](src/App.vue)
- [src/pages/Homepage.vue](src/pages/Homepage.vue)

Code and comments are in English; this README and explanations are in Chinese.
# Expense Reporting System (Homepage)

This is a minimalist Vue single-file component for an "Expense Reporting System" (English UI). It provides a table-like form where users can add expense rows (date, category, description, amount) and preview the submission payload.

How to use:

- Add `homepage.vue` into a Vue 3 project (Vite / Vue CLI).
- Import and mount the component in your router or main app. Example:

```js
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import Homepage from './homepage.vue'

createApp(App).component('Homepage', Homepage).mount('#app')
```

- Open the app in the browser. The component is self-contained and uses only core Vue features.

Notes:
- All text is English. The site name shown on the page is "Expense Reporting System" (the requested English version of 报销填报系统).
- No validation or backend submission is implemented — there is a placeholder `submit()` where you can add logic and constraints later.
