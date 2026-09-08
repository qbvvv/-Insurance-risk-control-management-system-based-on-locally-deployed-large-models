<template>
  <div v-if="isAuthRoute" class="auth-route-root">
    <router-view />
  </div>
  <div v-else class="app-shell" :class="[themeClass, boxClass]" :style="themeVars">
    <header class="app-header">
      <div class="logo">
        <span class="logo-mark">INS</span>
        <span class="logo-text">{{ i18nText.systemName }}</span>
      </div>
      <div class="header-left">
        <button
          v-if="uiFlags.showReloadBtn"
          class="header-icon-btn header-refresh-btn"
          @click="refreshPage"
          title="刷新"
          aria-label="刷新"
        >
          ⟳
        </button>
        <div v-if="uiFlags.showGlobalBreadcrumb" class="header-breadcrumb" :title="$route.path">
          <span class="breadcrumb-icon">⟡</span>
          <span class="breadcrumb-text">{{ breadcrumbText }}</span>
        </div>
      </div>
      <div class="header-actions">
        <div class="header-search">
          <input class="top-search" type="text" :placeholder="i18nText.searchPlaceholder" />
          <button class="search-btn" @click="confirmSearch" title="确认搜索" aria-label="确认搜索">
            <span
              class="search-icon"
              :style="{
                maskImage: `url(${searchIconUrl})`,
                WebkitMaskImage: `url(${searchIconUrl})`,
              }"
              aria-label="搜索"
            ></span>
          </button>
        </div>
        <select class="select">
          <option>{{ i18nText.branchHead }}</option>
          <option>{{ i18nText.branchEast }}</option>
          <option>{{ i18nText.branchSouth }}</option>
          <option>{{ i18nText.branchWest }}</option>
        </select>
        <select v-if="uiFlags.showI18n" class="select select--mini" v-model="lang">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
        <button class="header-icon-btn" @click="stylePanelOpen = true" title="设置（样式修改在这里）" aria-label="设置">
          ⚙
        </button>
        <div class="user">
          <div class="avatar">A</div>
          <div class="user-info">
            <div class="name">{{ headerUserName }}</div>
            <div class="role">{{ headerUserRole }}</div>
          </div>
          <button class="logout-btn" @click="handleLogout">退出</button>
        </div>
      </div>
    </header>

    <main class="app-main">
      <aside class="sidebar" :class="{ 'sidebar--collapsed': sidebarCollapsed }">
        <div class="sidebar-head">
          <div class="sidebar-brand"></div>
        </div>

        <div class="sidebar-new-wrap">
          <router-link to="/" class="sidebar-new-btn">
            <span
              class="sidebar-new-icon"
              :style="{
                maskImage: `url(${workbenchIconUrl})`,
                WebkitMaskImage: `url(${workbenchIconUrl})`,
              }"
              aria-label="工作台"
            ></span>
            <span class="sidebar-new-text">{{ i18nText.workbench }}</span>
          </router-link>
        </div>

        <div class="sidebar-list-wrap">
          <ul class="sidebar-list">
            <li
              v-for="item in localizedMenus"
              :key="item.path + (item.children ? '-g' : '')"
              class="sidebar-item"
              :class="{ 'sidebar-item--group': item.children && item.children.length }"
            >
              <div v-if="item.children && item.children.length" class="sidebar-group">
                <button
                  type="button"
                  class="sidebar-group-head"
                  :class="{
                    'sidebar-group-head--open': groupOpen[item.path],
                    'sidebar-group-head--active': isGroupActive(item),
                  }"
                  :title="item.name"
                  @click="onGroupHeadClick(item)"
                >
                  <span class="sidebar-item-icon-wrap">
                    <span
                      class="sidebar-item-icon"
                      :style="{
                        maskImage: `url(${item.icon})`,
                        WebkitMaskImage: `url(${item.icon})`,
                      }"
                      :aria-label="item.name"
                    ></span>
                  </span>
                  <span class="sidebar-item-text">{{ item.name }}</span>
                  <span v-if="!sidebarCollapsed" class="sidebar-group-chevron">{{ groupOpen[item.path] ? "⌄" : "›" }}</span>
                </button>
                <ul v-show="!sidebarCollapsed && groupOpen[item.path]" class="sidebar-sublist">
                  <li v-for="child in item.children" :key="child.path" class="sidebar-subitem">
                    <router-link :to="child.path" class="sidebar-sublink" active-class="sidebar-sublink--active">
                      {{ child.name }}
                    </router-link>
                  </li>
                </ul>
              </div>
              <router-link
                v-else
                :to="item.path"
                class="sidebar-item-link"
                active-class="sidebar-item-link--active"
              >
                <span class="sidebar-item-icon-wrap">
                  <span
                    class="sidebar-item-icon"
                    :style="{
                      maskImage: `url(${item.icon})`,
                      WebkitMaskImage: `url(${item.icon})`,
                    }"
                    :aria-label="item.name"
                  ></span>
                </span>
                <span class="sidebar-item-text">{{ item.name }}</span>
                <span class="sidebar-item-more">›</span>
              </router-link>
            </li>
          </ul>
        </div>

        <div v-if="uiFlags.showCollapseBtn" class="sidebar-toggle-wrap">
          <button type="button" class="sidebar-toggle-btn" :title="sidebarCollapsed ? '展开侧栏' : '收起侧栏'" aria-label="收起" @click="sidebarCollapsed = !sidebarCollapsed">
            <span class="sidebar-toggle-icon">{{ sidebarCollapsed ? '▶' : '◀' }}</span>
          </button>
        </div>
      </aside>

      <section class="content">
        <!-- 多标签页放到菜单右边（内容区顶部） -->
        <div v-if="uiFlags.openTabs" class="tabs-bar">
          <button
            v-for="t in tabs"
            :key="t.path"
            class="tab-chip"
            :class="{ active: t.path === $route.path }"
            @click="goTab(t.path)"
            :title="t.title"
          >
            <span class="tab-title">{{ t.title }}</span>
            <span v-if="t.closable" class="tab-close" @click.stop="closeTab(t.path)">×</span>
          </button>
        </div>
        <router-view />
      </section>
    </main>

    <!-- 样式修改侧边栏 -->
    <div v-if="stylePanelOpen" class="style-mask" @click="stylePanelOpen = false"></div>
    <aside class="style-panel" :class="{ 'style-panel--open': stylePanelOpen }">
      <div class="style-panel-head">
        <h3>设置</h3>
        <button class="panel-close" @click="stylePanelOpen = false">✕</button>
      </div>

      <div class="style-block">
        <p class="style-block-title">{{ i18nText.baseConfig }}</p>
        <label class="switch-row" v-for="item in switchItems" :key="item.key">
          <span>{{ item.label }}</span>
          <input type="checkbox" v-model="uiFlags[item.key]" />
        </label>
      </div>
    </aside>
  </div>
</template>

<script>
import { clearAuthSession, getAuthMenus, getAuthUser, logout } from "@/api";

export default {
  name: "App",
  data() {
    return {
      sidebarCollapsed: false,
      /** 侧栏分组展开：如 /risk-fraud */
      groupOpen: {
        "/risk-fraud": true,
        "/customer": true,
        "/product": true,
        "/system": true,
      },
      stylePanelOpen: false,
      themeMode: "light",
      primaryColor: "#3b82f6",
      boxStyle: "shadow",
      lang: "zh",
      tabs: [{ path: "/", title: "工作台", closable: false }],
      uiFlags: {
        // 你要求：剩余设置项默认都为勾选
        showCollapseBtn: true,
        showReloadBtn: true,
        showGlobalBreadcrumb: true,
        openTabs: true,
        showI18n: true,
      },
      authUser: null,
      authMenus: [],
      themeColors: ["#3b82f6", "#4f46e5", "#8b5cf6", "#22c55e", "#06b6d4", "#f43f5e", "#ec4899"],
      sidebarMenus: [
        // Feather Icons（线条型 SVG），通过 CSS mask 进行统一着色
        {
          path: "/customer",
          menuKey: "customer",
          name: "保险客户管理",
          icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/users.svg",
          children: [
            { path: "/customer/list", menuKey: "customerList", name: "客户列表" },
            { path: "/customer/stats", menuKey: "customerStats", name: "客户统计" },
            { path: "/customer/detail", menuKey: "customerDetail", name: "客户详情", matchPrefix: "/customer/detail" },
          ],
        },
        {
          path: "/product",
          menuKey: "product",
          name: "产品管理",
          icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/package.svg",
          children: [
            { path: "/product/list", menuKey: "productList", name: "产品列表" },
            { path: "/product/detail", menuKey: "productDetail", name: "产品详情", matchPrefix: "/product/detail" },
          ],
        },
        { path: "/underwriting", name: "承保管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/file-text.svg" },
        { path: "/policy", name: "保单管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/file.svg" },
        { path: "/claim", name: "理赔管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/credit-card.svg" },
        { path: "/service", name: "售后与投诉管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/headphones.svg" },
        { path: "/channel", name: "渠道管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/share-2.svg" },
        { path: "/finance", name: "财务管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/pie-chart.svg" },
        { path: "/reinsurance", name: "再保管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/shield.svg" },
        {
          path: "/risk-fraud",
          menuKey: "risk-fraud",
          name: "风控与规则管理",
          icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/alert-triangle.svg",
          children: [
            { path: "/risk-fraud/overview", menuKey: "riskFraudOverview", name: "规则工作台" },
            { path: "/risk-fraud/preset-rules", menuKey: "riskFraudPresets", name: "预设规则库" },
            { path: "/risk-fraud/blacklist", menuKey: "riskFraudBlacklist", name: "黑名单" },
          ],
        },
        { path: "/agent-team", name: "代理人/团队管理", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/users.svg" },
        { path: "/report", name: "运营报表与监管报送", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/file-text.svg" },
        { path: "/analytics", name: "报表与分析", icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/bar-chart-2.svg" },
        {
          path: "/system",
          menuKey: "system",
          name: "系统管理",
          icon: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/settings.svg",
          children: [
            { path: "/system/users", menuKey: "systemUsers", name: "用户与角色权限" },
            { path: "/system/params", menuKey: "systemParams", name: "系统参数" },
            { path: "/system/logs", menuKey: "systemLogs", name: "系统日志" },
          ],
        },
      ],
      // Feather 线条图标（用于 mask 着色为单色）
      workbenchIconUrl: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/book-open.svg",
      searchIconUrl: "https://cdn.jsdelivr.net/npm/feather-icons@4.29.2/dist/icons/search.svg",
      i18n: {
        zh: {
          systemName: "保险风控系统",
          workbench: "工作台",
          searchPlaceholder: "搜索模块、规则、客户...",
          branchHead: "总部",
          branchEast: "华东分公司",
          branchSouth: "华南分公司",
          branchWest: "西北分公司",
          adminName: "系统管理员",
          adminRole: "风控中台",
          baseConfig: "基础配置",
          menus: {
            customer: "保险客户管理",
            customerList: "客户列表",
            customerStats: "客户统计",
            customerDetail: "客户详情",
            product: "产品管理",
            productList: "产品列表",
            productDetail: "产品详情",
            underwriting: "承保管理",
            policy: "保单管理",
            claim: "理赔管理",
            service: "售后与投诉管理",
            channel: "渠道管理",
            finance: "财务管理",
            reinsurance: "再保管理",
            "risk-fraud": "风控与规则管理",
            riskFraudOverview: "规则工作台",
            riskFraudPresets: "预设规则库",
            riskFraudBlacklist: "黑名单",
            "agent-team": "代理人/团队管理",
            report: "运营报表与监管报送",
            analytics: "报表与分析",
            system: "系统管理",
            systemUsers: "用户与角色权限",
            systemParams: "系统参数",
            systemLogs: "系统日志",
          },
          settingItems: {
            showCollapseBtn: "显示折叠侧边栏按钮",
            showReloadBtn: "显示重载页面按钮",
            showGlobalBreadcrumb: "显示全局面包屑导航",
            openTabs: "开启多标签页",
            showI18n: "显示多语言选择",
          },
        },
        en: {
          systemName: "Insurance Risk Control System",
          workbench: "Workbench",
          searchPlaceholder: "Search modules, rules, customers...",
          branchHead: "Headquarters",
          branchEast: "East Branch",
          branchSouth: "South Branch",
          branchWest: "Northwest Branch",
          adminName: "Administrator",
          adminRole: "Risk Control Platform",
          baseConfig: "Basic Config",
          menus: {
            customer: "Customer Management",
            customerList: "Customer List",
            customerStats: "Customer Statistics",
            customerDetail: "Customer Profile",
            product: "Product Management",
            productList: "Product List",
            productDetail: "Product Detail",
            underwriting: "Underwriting",
            policy: "Policy Management",
            claim: "Claim Management",
            service: "After-sales & Complaint",
            channel: "Channel Management",
            finance: "Finance Management",
            reinsurance: "Reinsurance Management",
            "risk-fraud": "Risk & Anti-Fraud",
            riskFraudOverview: "Rules Workbench",
            riskFraudPresets: "Preset Rules",
            riskFraudBlacklist: "Blacklist",
            "agent-team": "Agent/Team",
            report: "Operations & Regulatory Reports",
            analytics: "Reports & Analytics",
            system: "System Settings",
            systemUsers: "Users & Roles",
            systemParams: "System Parameters",
            systemLogs: "System Logs",
          },
          settingItems: {
            showCollapseBtn: "Show Sidebar Toggle",
            showReloadBtn: "Show Reload Button",
            showGlobalBreadcrumb: "Show Global Breadcrumb",
            openTabs: "Enable Multi-tabs",
            showI18n: "Show Language Switch",
          },
        },
      },
    };
  },
  computed: {
    isAuthRoute() {
      return this.$route.path === "/login";
    },
    i18nText() {
      return this.i18n[this.lang] || this.i18n.zh;
    },
    headerUserName() {
      if (this.authUser && this.authUser.username) {
        return this.authUser.username;
      }
      return this.i18nText.adminName;
    },
    headerUserRole() {
      if (this.authUser && this.authUser.role) {
        return this.authUser.role;
      }
      return this.i18nText.adminRole;
    },
    localizedMenus() {
      const menus = this.i18nText.menus || {};
      const localized = this.sidebarMenus.map((m) => {
        if (m.children && m.children.length) {
          const pk = m.menuKey || m.path.replace(/^\//, "");
          return {
            ...m,
            name: menus[m.menuKey] || menus[pk] || m.name,
            children: m.children.map((c) => ({
              ...c,
              name: menus[c.menuKey] || c.name,
            })),
          };
        }
        const key = m.path.replace("/", "");
        return { ...m, name: menus[key] || m.name };
      });
      if (!this.authMenus || !this.authMenus.length || this.authMenus.includes("*")) {
        return localized;
      }
      return localized
        .map((m) => {
          if (m.children && m.children.length) {
            const children = m.children.filter((c) => this.authMenus.includes(c.path) || this.authMenus.includes(m.path));
            if (!children.length && !this.authMenus.includes(m.path)) return null;
            return { ...m, children };
          }
          if (this.authMenus.includes(m.path)) return m;
          return null;
        })
        .filter(Boolean);
    },
    breadcrumbText() {
      const path = this.$route.path;
      if (path === "/") return this.i18nText.workbench;
      for (const m of this.localizedMenus) {
        if (m.children && m.children.length) {
          const child = m.children.find((c) => {
            if (c.path === path) return true;
            if (c.matchPrefix && path.startsWith(String(c.matchPrefix))) return true;
            return false;
          });
          if (child) return `${this.i18nText.workbench} / ${m.name} / ${child.name}`;
          if (path === m.path) return `${this.i18nText.workbench} / ${m.name}`;
        } else if (m.path === path) {
          return `${this.i18nText.workbench} / ${m.name}`;
        }
      }
      return `${this.i18nText.workbench} / ${path}`;
    },
    themeClass() {
      if (this.themeMode === "system") {
        return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "theme-dark"
          : "theme-light";
      }
      return this.themeMode === "dark" ? "theme-dark" : "theme-light";
    },
    boxClass() {
      return this.boxStyle === "border" ? "box-border" : "box-shadow";
    },
    themeVars() {
      return {
        "--primary-color": this.primaryColor,
        "--primary-soft": this.hexToRgba(this.primaryColor, 0.14),
      };
    },
    switchItems() {
      const labels = (this.i18nText && this.i18nText.settingItems) || {};
      return [
        { key: "showCollapseBtn", label: labels.showCollapseBtn || "显示折叠侧边栏按钮" },
        { key: "showReloadBtn", label: labels.showReloadBtn || "显示重载页面按钮" },
        { key: "showGlobalBreadcrumb", label: labels.showGlobalBreadcrumb || "显示全局面包屑导航" },
        { key: "openTabs", label: labels.openTabs || "开启多标签页" },
        { key: "showI18n", label: labels.showI18n || "显示多语言选择" },
      ];
    },
  },
  watch: {
    uiFlags: {
      deep: true,
      handler(v) {
        localStorage.setItem("ins-ui-flags", JSON.stringify(v));
      },
    },
    themeMode(v) {
      localStorage.setItem("ins-theme-mode", v);
    },
    primaryColor(v) {
      localStorage.setItem("ins-primary-color", v);
    },
    boxStyle(v) {
      localStorage.setItem("ins-box-style", v);
    },
    lang(v) {
      localStorage.setItem("ins-lang", v);
    },
    $route: {
      handler() {
        this.syncRiskGroupOpen();
      },
      immediate: true,
    },
  },
  created() {
    const savedFlags = localStorage.getItem("ins-ui-flags");
    const savedTheme = localStorage.getItem("ins-theme-mode");
    const savedColor = localStorage.getItem("ins-primary-color");
    const savedBox = localStorage.getItem("ins-box-style");
    const savedLang = localStorage.getItem("ins-lang");
    if (savedFlags) this.uiFlags = { ...this.uiFlags, ...JSON.parse(savedFlags) };
    if (savedTheme) this.themeMode = savedTheme;
    if (savedColor) this.primaryColor = savedColor;
    if (savedBox) this.boxStyle = savedBox;
    if (savedLang) this.lang = savedLang;
    this.authUser = getAuthUser();
    this.authMenus = getAuthMenus();
  },
  mounted() {
    // 安装一次路由 hook，用于：
    // - 顶部进度条
    // - 多标签页收集
    if (this._hooksInstalled) return;
    this._hooksInstalled = true;
    if (this.$router) {
      this.$router.beforeEach((to, from, next) => {
        if (this.uiFlags.openTabs) this.addTab(to);
        next();
      });
    }
  },
  methods: {
    refreshPage() {
      // 对于当前毕设级别项目：直接刷新页面最稳
      window.location.reload();
    },
    async handleLogout() {
      try {
        await logout();
      } catch (e) {
        // 即使后端会话已失效，也继续本地登出。
      } finally {
        clearAuthSession();
        this.authUser = null;
        this.authMenus = [];
        this.$router.push("/login");
      }
    },
    confirmSearch() {
      // 目前前端只是样式/交互占位：你后面接入搜索接口时再替换这里的逻辑
      if (this.$message && this.$message.info) {
        this.$message.info("搜索功能尚未接入（仅确认按钮占位）。");
      }
    },
    addTab(route) {
      const path = route.path;
      if (this.tabs.some((t) => t.path === path)) return;
      const title = this.resolveTabTitle(path);
      this.tabs.push({ path, title, closable: path !== "/" });
    },
    resolveTabTitle(path) {
      if (path.startsWith("/customer/detail")) return this.i18nText.menus?.customerDetail || "客户详情";
      if (path.startsWith("/product/detail")) return this.i18nText.menus?.productDetail || "产品详情";
      for (const m of this.localizedMenus) {
        if (m.children && m.children.length) {
          const child = m.children.find((c) => {
            if (c.path === path) return true;
            if (c.matchPrefix && path.startsWith(String(c.matchPrefix))) return true;
            return false;
          });
          if (child) return child.name;
        }
        if (m.path === path) return m.name;
      }
      return path;
    },
    syncRiskGroupOpen() {
      const p = this.$route.path;
      if (p.startsWith("/risk-fraud")) {
        this.$set(this.groupOpen, "/risk-fraud", true);
      }
      if (p.startsWith("/customer")) {
        this.$set(this.groupOpen, "/customer", true);
      }
      if (p.startsWith("/product")) {
        this.$set(this.groupOpen, "/product", true);
      }
      if (p.startsWith("/system")) {
        this.$set(this.groupOpen, "/system", true);
      }
    },
    onGroupHeadClick(item) {
      if (!item.children || !item.children.length) return;
      if (this.sidebarCollapsed) {
        this.$router.push(item.children[0].path).catch(() => {});
        return;
      }
      this.$set(this.groupOpen, item.path, !this.groupOpen[item.path]);
    },
    isGroupActive(item) {
      const p = this.$route.path;
      if (!item.children || !item.children.length) return false;
      return item.children.some((c) => {
        if (c.path === p) return true;
        if (c.matchPrefix && p.startsWith(String(c.matchPrefix))) return true;
        return false;
      });
    },
    goTab(path) {
      if (this.$route.path === path) return;
      this.$router.push(path);
    },
    closeTab(path) {
      const idx = this.tabs.findIndex((t) => t.path === path);
      if (idx <= 0) return;
      const isActive = this.$route.path === path;
      this.tabs.splice(idx, 1);
      if (isActive) {
        const fallback = this.tabs[Math.max(0, idx - 1)];
        this.$router.push(fallback.path);
      }
    },
    setTheme(mode) {
      this.themeMode = mode;
      this.stylePanelOpen = this.stylePanelOpen;
    },
    setPrimaryColor(color) {
      this.primaryColor = color;
      this.stylePanelOpen = this.stylePanelOpen;
    },
    setBoxStyle(style) {
      this.boxStyle = style;
    },
    hexToRgba(hex, alpha) {
      const m = hex.replace("#", "");
      const full = m.length === 3 ? m.split("").map((x) => x + x).join("") : m;
      const num = parseInt(full, 16);
      const r = (num >> 16) & 255;
      const g = (num >> 8) & 255;
      const b = num & 255;
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    },
  },
};
</script>

<style scoped>
.auth-route-root {
  min-height: 100vh;
  min-height: 100dvh;
}

.cb-mode {
  filter: saturate(0.92) contrast(1.06);
}

.top-progress {
  position: sticky;
  top: 64px;
  z-index: 12;
  height: 2px;
  background: transparent;
}
.top-progress-bar {
  height: 2px;
  background: var(--primary-color);
  transition: width 0.18s ease;
}

.tabs-bar {
  position: sticky;
  top: 64px;
  z-index: 11;
  display: flex;
  gap: 8px;
  padding: 10px 24px;
  /* 抵消 .content 的顶部/左右内边距，让标签贴近菜单右侧顶边 */
  margin: -20px -24px 12px;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-card);
  overflow-x: auto;
}
.tab-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 30px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-card-soft);
  color: var(--text-main);
  cursor: pointer;
  white-space: nowrap;
}
.tab-chip.active {
  /* 当前页标签不再蓝色高亮，保持与普通标签同一风格 */
  border-color: var(--border-subtle);
  box-shadow: none;
  background: var(--bg-card-soft);
  color: var(--text-main);
}
.tab-title {
  font-size: 12px;
}
.tab-close {
  font-size: 14px;
  opacity: 0.7;
}
.tab-chip:hover .tab-close {
  opacity: 1;
}
.header-center {
  flex: 1;
  padding: 0 24px;
}
.top-search {
  width: min(520px, 100%);
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  color: var(--text-main);
  padding: 0 12px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 180px;
}
.header-refresh-btn {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  padding: 0;
}
.header-breadcrumb {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: 1px solid var(--border-subtle);
  border-radius: 999px;
  background: var(--bg-card);
  color: var(--text-soft);
  font-size: 12px;
  white-space: nowrap;
}
.breadcrumb-icon {
  color: var(--primary-color);
}
.breadcrumb-text {
  color: var(--text-main);
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-search {
  display: flex;
  align-items: center;
  width: 280px;
  height: 36px;
}
.header-search .top-search {
  width: 100%;
  height: 36px;
  border-radius: 8px 0 0 8px;
  border-right: none;
}
.search-btn {
  width: 42px;
  height: 36px;
  border-radius: 0 8px 8px 0;
  border: 1px solid var(--border-subtle);
  border-left: none;
  background: var(--bg-card);
  color: var(--text-soft);
  cursor: pointer;
}
.search-btn:hover {
  background: var(--bg-card-soft);
  color: var(--primary-color);
  border-color: var(--primary-soft);
}

.search-icon {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-color: var(--text-soft);
  mask-size: contain;
  mask-repeat: no-repeat;
  mask-position: center;
  -webkit-mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  -webkit-mask-position: center;
  transition: background-color 0.18s ease;
}

.search-btn:hover .search-icon {
  background-color: var(--primary-color);
}
.style-entry-btn {
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  color: var(--text-main);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 12px;
  cursor: pointer;
}
.style-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.25);
  z-index: 80;
}
.style-panel {
  position: fixed;
  right: -360px;
  top: 0;
  width: 340px;
  height: 100vh;
  background: var(--bg-card);
  border-left: 1px solid var(--border-subtle);
  z-index: 90;
  transition: right 0.24s ease;
  padding: 14px 14px 24px;
  overflow-y: auto;
}
.style-panel--open {
  right: 0;
}
.style-panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.style-panel-head h3 {
  margin: 0;
  font-size: 18px;
}
.panel-close {
  border: none;
  background: transparent;
  color: var(--text-soft);
  cursor: pointer;
  font-size: 14px;
}
.style-block {
  border-top: 1px solid var(--border-subtle);
  padding: 14px 0;
}
.style-block-title {
  margin: 0 0 10px;
  font-size: 14px;
  color: var(--text-main);
}
.option-row {
  display: flex;
  gap: 8px;
}
.theme-chip {
  border: 1px solid var(--border-subtle);
  background: var(--bg-card);
  color: var(--text-main);
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
}
.theme-chip.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-soft);
}
.color-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.color-dot {
  width: 24px;
  height: 24px;
  border-radius: 999px;
  border: 2px solid transparent;
  cursor: pointer;
}
.color-dot.active {
  border-color: #fff;
  box-shadow: 0 0 0 2px var(--primary-color);
}
.switch-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 13px;
}
.switch-row input {
  width: 38px;
  height: 20px;
}
@media (max-width: 900px) {
  .header-left {
    display: none;
  }
  .style-panel {
    width: min(92vw, 340px);
  }
}

.logout-btn {
  margin-left: 10px;
  height: 30px;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  background: var(--bg-card);
  color: var(--text-main);
  padding: 0 10px;
  cursor: pointer;
}

.logout-btn:hover {
  color: var(--primary-color);
  border-color: var(--primary-soft);
}
</style>
