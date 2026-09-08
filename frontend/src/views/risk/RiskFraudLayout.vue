<template>
  <div class="risk-fraud-layout page">
    <h1 class="page-title">风控与规则管理</h1>
    <p class="page-subtitle">
      规则工作台支持自然语言解析与试算；预设规则库维护可执行策略；黑名单（含下方风控预警流水）用于承保、理赔环节拦截与复核。
    </p>
    <nav class="risk-fraud-subnav">
      <router-link
        v-for="l in nav"
        :key="l.to"
        :to="l.to"
        class="risk-fraud-subnav-link"
        :class="{ 'risk-fraud-subnav-link--active': isNavActive(l) }"
      >
        {{ l.label }}
      </router-link>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  name: "RiskFraudLayout",
  data() {
    return {
      nav: [
        { to: "/risk-fraud/overview", label: "规则工作台", match: "exact" },
        { to: "/risk-fraud/preset-rules", label: "预设规则库", match: "exact" },
        { to: "/risk-fraud/blacklist", label: "黑名单", match: "exact" },
      ],
    };
  },
  methods: {
    isNavActive(l) {
      return this.$route.path === l.to;
    },
  },
};
</script>

<style scoped>
.risk-fraud-subnav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 0 12px;
  margin-bottom: 16px;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}
.risk-fraud-subnav-link {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  color: #64748b;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.risk-fraud-subnav-link:hover {
  color: #334155;
  background: rgba(148, 163, 184, 0.15);
}
.risk-fraud-subnav-link--active {
  background: var(--primary-soft, rgba(59, 130, 246, 0.14));
  color: var(--primary-color, #3b82f6);
  font-weight: 600;
}
</style>
