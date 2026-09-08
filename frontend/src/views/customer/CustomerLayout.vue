<template>
  <div class="customer-layout page">
    <h1 class="page-title">保险客户管理</h1>
    <nav class="customer-subnav">
      <router-link
        v-for="l in nav"
        :key="l.to"
        :to="l.to"
        class="customer-subnav-link"
        :class="{ 'customer-subnav-link--active': isNavActive(l) }"
      >
        {{ l.label }}
      </router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: "CustomerLayout",
  data() {
    return {
      nav: [
        { to: "/customer/list", label: "客户列表", match: "exact" },
        { to: "/customer/stats", label: "客户统计", match: "exact" },
        { to: "/customer/detail", label: "客户详情", match: "prefix" },
      ],
    };
  },
  methods: {
    isNavActive(l) {
      const p = this.$route.path;
      if (l.match === "prefix") return p === l.to || p.startsWith(`${l.to}/`);
      return p === l.to;
    },
  },
};
</script>

<style scoped>
.customer-subnav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 0 12px;
  margin-bottom: 16px;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}
.customer-subnav-link {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  color: #64748b;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.customer-subnav-link:hover {
  color: #334155;
  background: rgba(148, 163, 184, 0.15);
}
.customer-subnav-link--active {
  background: var(--primary-soft, rgba(59, 130, 246, 0.14));
  color: var(--primary-color, #3b82f6);
  font-weight: 600;
}
</style>
