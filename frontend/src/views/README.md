# views 目录说明

所有页面级 Vue 组件按**业务模块**放在对应子文件夹下，便于查找和扩展。

## 当前结构

```
views/
├── README.md           # 本说明
├── auth/               # 登录、鉴权
│   └── LoginView.vue
├── dashboard/          # 首页 / 数据大屏
│   └── DashboardView.vue
├── customer/           # 客户相关
│   ├── CustomerLayout.vue
│   ├── CustomerListView.vue
│   ├── CustomerDetailView.vue
│   └── CustomerStatsView.vue
├── product/            # 产品相关
│   └── ProductView.vue
├── underwriting/       # 承保
│   └── UnderwritingView.vue
├── policy/             # 保单
│   └── PolicyView.vue
├── claim/              # 理赔
│   └── ClaimView.vue
├── service/            # 售后与投诉
│   └── ServiceView.vue
├── channel/            # 渠道
│   └── ChannelView.vue
├── finance/            # 财务
│   └── FinanceView.vue
├── reinsurance/        # 再保
│   └── ReinsuranceView.vue
├── risk/               # 风控与规则管理（嵌套路由 + 多页）
│   ├── RiskView.vue
│   ├── RiskFraudLayout.vue      # /risk-fraud 父级布局
│   ├── RiskFraudOverview.vue    # /risk-fraud/overview 规则工作台
│   ├── RiskPresetRulesView.vue  # /risk-fraud/preset-rules 预设规则库
│   └── RiskBlacklistView.vue    # /risk-fraud/blacklist 黑名单
├── agent/              # 代理人/团队
│   └── AgentTeamView.vue
├── pricing/            # 定价
│   └── PricingView.vue
├── analytics/          # 报表与分析（可放多个）
│   ├── ReportView.vue
│   └── AnalyticsView.vue
├── rule/               # 规则引擎
│   └── RuleView.vue
└── system/             # 系统管理
    └── SystemView.vue
```

## 以后如何新增页面

### 1. 属于已有模块

- 在对应子文件夹里新建 `xxxView.vue`（或你习惯的命名）。
- 在 `src/router/index.js` 里：
  - 顶部增加：`import XxxView from "@/views/模块名/XxxView.vue";`
  - `routes` 里增加：`{ path: "/xxx", name: "xxx", component: XxxView },`
- 如需在侧栏展示，在 `App.vue` 的 `sidebarMenus` 里加一项：`{ path: "/xxx", name: "显示名称" }`。
- 若需要**可展开子菜单**：为该菜单项增加 `children` 数组（示例见「风控与规则管理」），并在 `router/index.js` 中配置父级 `component` + `children` 子路由。

### 2. 全新业务模块

1. 在 `views/` 下新建文件夹，例如 `views/compliance/`（合规）。
2. 在该文件夹下新建页面，如 `ComplianceView.vue`。
3. 在 `router/index.js` 里用 `@/views/compliance/ComplianceView.vue` 引入并配置路由。
4. 若要在左侧菜单显示，在 `App.vue` 的 `sidebarMenus` 中增加对应项。

### 3. 引用公共组件

- 一律用 **`@/components/xxx`**，不要用 `../components/xxx`，这样页面放在任意层级子目录下都能正确解析。
- 示例：`import BaseCard from "@/components/BaseCard.vue";`

### 4. 命名建议

- 页面组件：以 `View` 结尾，如 `CustomerListView.vue`、`ReportView.vue`。
- 同一模块下多个页面：可加前缀，如 `RiskView.vue`、`RiskFraudView.vue`。
