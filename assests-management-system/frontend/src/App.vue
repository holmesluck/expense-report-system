<template>
  <div id="app-root" v-cloak>
    <header class="topbar">
      <div class="brand">库存管理系统</div>
      <div class="user-area" id="userArea">
        <template v-if="authed">
          <span>{{ user.username }}</span>
          <button class="btn" @click="logout">退出</button>
        </template>
      </div>
    </header>

    <main class="container">
      <!-- 登录模态 -->
      <div v-if="showLogin" class="modal">
        <div class="modal-card">
          <h2>用户登录</h2>
          <form @submit.prevent="login">
            <label>用户名
              <input v-model="loginForm.username" type="text" required />
            </label>
            <label>密码
              <input v-model="loginForm.password" type="password" required />
            </label>
            <div class="actions">
              <button type="submit" class="btn primary">登录</button>
              <button type="button" class="btn" @click="showLogin=false">取消</button>
            </div>
          </form>
        </div>
      </div>

      <!-- 主界面 -->
      <section v-if="authed" id="mainView">
        <div class="toolbar">
          <div class="left">
            <button class="btn primary" @click="openForm()">新增物品</button>
          </div>
          <div class="right">
            <input v-model="q" placeholder="搜索物品 / 编号" @input="fetchItems" />
          </div>
        </div>

        <div v-if="showForm" id="formArea" class="card">
          <h3>{{ editingItem ? '编辑物品' : '新增物品' }}</h3>
          <form @submit.prevent="saveItem">
            <label>名称
              <input v-model="form.name" type="text" required />
            </label>
            <label>编号
              <input v-model="form.code" type="text" required />
            </label>
            <label>数量
              <input v-model.number="form.qty" type="number" min="0" required />
            </label>
            <label>备注
              <input v-model="form.note" type="text" />
            </label>
            <div class="actions">
              <button type="submit" class="btn primary">保存</button>
              <button type="button" class="btn" @click="closeForm">取消</button>
            </div>
          </form>
        </div>

        <div class="card">
          <table>
            <thead>
              <tr>
                <th>编号</th>
                <th>名称</th>
                <th>数量</th>
                <th>备注</th>
                <th class="actions-col">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="items.length === 0">
                <td colspan="5" style="text-align:center;color:var(--muted)">暂无数据</td>
              </tr>
              <tr v-for="it in items" :key="it.id">
                <td>{{ it.code }}</td>
                <td>{{ it.name }}</td>
                <td>{{ it.qty }}</td>
                <td>{{ it.note }}</td>
                <td class="actions-col">
                  <button class="row-btn edit" @click="editItem(it)">编辑</button>
                  <button class="row-btn delete" @click="deleteItem(it)">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else class="container" style="padding-top:40px;">
        <div style="text-align:center">
          <p class="text-accent">请先登录以管理库存</p>
          <button class="btn primary" @click="showLogin = true">登录 / 注册</button>
        </div>
      </section>

      <footer class="footer">
        <span>简约时尚 · 黑白红配色</span>
      </footer>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      token: null,
      user: null,
      showLogin: false,
      loginForm: { username: '', password: '' },

      items: [],
      q: '',
      showForm: false,
      form: { id: null, name: '', code: '', qty: 0, note: '' },
      editingItem: null,
      loading: false,
    };
  },
  computed: {
    authed() { return !!this.user; }
  },
  mounted() {
    // set axios defaults if token exists
    const t = localStorage.getItem('ams_token');
    if (t) {
      this.setToken(t);
      this.fetchMe().then(() => this.fetchItems());
    }
  },
  methods: {
    setToken(t) {
      this.token = t;
      if (t) {
        localStorage.setItem('ams_token', t);
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + t;
      } else {
        localStorage.removeItem('ams_token');
        delete axios.defaults.headers.common['Authorization'];
      }
    },
    async login() {
      if (!this.loginForm.username || !this.loginForm.password) {
        alert('请输入用户名和密码');
        return;
      }
      try {
        const res = await axios.post('/api/login', {
          username: this.loginForm.username,
          password: this.loginForm.password
        });
        const { token, user } = res.data;
        this.setToken(token);
        this.user = user;
        this.showLogin = false;
        this.loginForm.username = '';
        this.loginForm.password = '';
        await this.fetchItems();
      } catch (err) {
        alert((err.response && err.response.data && err.response.data.error) || '登录失败');
      }
    },
    logout() {
      this.setToken(null);
      this.user = null;
      this.items = [];
      this.showForm = false;
    },
    async fetchMe() {
      try {
        const res = await axios.get('/api/me');
        this.user = res.data;
      } catch (err) {
        this.setToken(null);
        this.user = null;
      }
    },
    async fetchItems() {
      if (!this.authed) return;
      this.loading = true;
      try {
        const res = await axios.get('/api/items');
        let list = res.data || [];
        const q = (this.q || '').trim().toLowerCase();
        if (q) {
          list = list.filter(it =>
            (it.name && it.name.toLowerCase().includes(q)) ||
            (it.code && it.code.toLowerCase().includes(q))
          );
        }
        this.items = list;
      } catch (err) {
        alert('获取物品失败');
      } finally {
        this.loading = false;
      }
    },
    openForm() {
      this.editingItem = null;
      this.form = { id: null, name: '', code: '', qty: 0, note: '' };
      this.showForm = true;
    },
    closeForm() {
      this.showForm = false;
      this.editingItem = null;
      this.form = { id: null, name: '', code: '', qty: 0, note: '' };
    },
    editItem(it) {
      this.editingItem = it;
      this.form = { id: it.id, name: it.name, code: it.code, qty: it.qty, note: it.note || '' };
      this.showForm = true;
    },
    async saveItem() {
      if (!this.form.name || !this.form.code) {
        alert('请填写名称和编号');
        return;
      }
      try {
        if (this.editingItem && this.form.id) {
          const res = await axios.put(`/api/items/${this.form.id}`, {
            name: this.form.name,
            code: this.form.code,
            qty: this.form.qty,
            note: this.form.note
          });
          const idx = this.items.findIndex(i => i.id === res.data.id);
          if (idx >= 0) this.items.splice(idx, 1, res.data);
        } else {
          const res = await axios.post('/api/items', {
            name: this.form.name,
            code: this.form.code,
            qty: this.form.qty,
            note: this.form.note
          });
          this.items.unshift(res.data);
        }
        this.closeForm();
      } catch (err) {
        alert((err.response && err.response.data && err.response.data.error) || '保存失败');
      }
    },
    async deleteItem(it) {
      if (!confirm('确认删除该物品？')) return;
      try {
        await axios.delete(`/api/items/${it.id}`);
        this.items = this.items.filter(x => x.id !== it.id);
      } catch (err) {
        alert('删除失败');
      }
    }
  }
};
</script>

<style>
/* keep component styles minimal; global styles will be imported from assets */
[v-cloak] { display: none; }
</style>