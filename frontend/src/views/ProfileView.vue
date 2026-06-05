<template>
  <div class="profile-page">
    <div class="container" style="max-width: 640px;">
      <div class="page-header">
        <h1>👤 个人中心</h1>
      </div>
      <div class="profile-card">
        <div v-if="user" class="profile-info">
          <el-avatar :size="72">{{ user.username?.charAt(0) }}</el-avatar>
          <h2>{{ user.username }}</h2>
          <p>{{ user.email }}</p>
          <el-tag :type="user.role === 'admin' ? 'danger' : 'info'">{{ user.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
        </div>
        <el-divider />
        <div class="profile-links">
          <el-button text @click="$router.push('/favorites')">⭐ 我的收藏</el-button>
          <el-button text @click="$router.push('/settings')">⚙️ 账号设置</el-button>
          <el-button v-if="user?.role === 'admin'" text type="danger" @click="$router.push('/admin')">🔧 后台管理</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types/api'

const user = ref<UserInfo | null>(null)

onMounted(async () => {
  try {
    const { data } = await authApi.getMe()
    user.value = data
    localStorage.setItem('user_info', JSON.stringify(data))
  } catch { /* handled */ }
})
</script>

<style lang="scss" scoped>
@use '@/assets/styles/variables' as *;

.profile-page { padding: 32px 0 64px; }

.profile-card {
  background: #fff;
  border-radius: $radius-xl;
  padding: 40px 32px;
  box-shadow: $shadow-sm;
}

.profile-info {
  text-align: center;

  h2 { margin-top: 16px; font-size: $font-size-xl; }
  p { color: $color-text-secondary; font-size: $font-size-sm; margin: 4px 0 12px; }
}

.profile-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
</style>
