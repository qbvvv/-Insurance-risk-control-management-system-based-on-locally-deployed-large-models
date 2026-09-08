import Vue from "vue";
import VueRouter from "vue-router";
import { getAuthMenus, getAuthToken } from "@/api";

// 按业务模块从 views 子目录引入，便于维护
import DashboardView from "@/views/dashboard/DashboardView.vue";
import LoginView from "@/views/auth/LoginView.vue";
import CustomerLayout from "@/views/customer/CustomerLayout.vue";
import CustomerListView from "@/views/customer/CustomerListView.vue";
import CustomerDetailView from "@/views/customer/CustomerDetailView.vue";
import CustomerStatsView from "@/views/customer/CustomerStatsView.vue";
import ProductLayout from "@/views/product/ProductLayout.vue";
import ProductListView from "@/views/product/ProductListView.vue";
import ProductDetailView from "@/views/product/ProductDetailView.vue";
import UnderwritingView from "@/views/underwriting/UnderwritingView.vue";
import PolicyView from "@/views/policy/PolicyView.vue";
import ClaimView from "@/views/claim/ClaimView.vue";
import ServiceView from "@/views/service/ServiceView.vue";
import ChannelView from "@/views/channel/ChannelView.vue";
import FinanceView from "@/views/finance/FinanceView.vue";
import ReinsuranceView from "@/views/reinsurance/ReinsuranceView.vue";
import RiskView from "@/views/risk/RiskView.vue";
import RiskFraudLayout from "@/views/risk/RiskFraudLayout.vue";
import RiskFraudOverview from "@/views/risk/RiskFraudOverview.vue";
import RiskPresetRulesView from "@/views/risk/RiskPresetRulesView.vue";
import RiskBlacklistView from "@/views/risk/RiskBlacklistView.vue";
import AgentTeamView from "@/views/agent/AgentTeamView.vue";
import PricingView from "@/views/pricing/PricingView.vue";
import ReportView from "@/views/analytics/ReportView.vue";
import AnalyticsView from "@/views/analytics/AnalyticsView.vue";
import RuleView from "@/views/rule/RuleView.vue";
import SystemView from "@/views/system/SystemView.vue";

Vue.use(VueRouter);

const routes = [
  { path: "/login", name: "login", component: LoginView },
  { path: "/", redirect: "/login" },
  { path: "/dashboard", name: "dashboard", component: DashboardView },
  {
    path: "/customer",
    component: CustomerLayout,
    redirect: "/customer/list",
    children: [
      { path: "list", name: "customer-list", component: CustomerListView },
      { path: "stats", name: "customer-stats", component: CustomerStatsView },
      { path: "detail/:id?", name: "customer-detail", component: CustomerDetailView },
    ],
  },
  {
    path: "/product",
    component: ProductLayout,
    redirect: "/product/list",
    children: [
      { path: "list", name: "product-list", component: ProductListView },
      { path: "detail/:id?", name: "product-detail", component: ProductDetailView },
    ],
  },
  { path: "/underwriting", name: "underwriting", component: UnderwritingView },
  { path: "/policy", name: "policy", component: PolicyView },
  { path: "/claim", name: "claim", component: ClaimView },
  { path: "/service", name: "service", component: ServiceView },
  { path: "/channel", name: "channel", component: ChannelView },
  { path: "/finance", name: "finance", component: FinanceView },
  { path: "/reinsurance", name: "reinsurance", component: ReinsuranceView },
  { path: "/risk", name: "risk", component: RiskView },
  {
    path: "/risk-fraud",
    component: RiskFraudLayout,
    redirect: "/risk-fraud/overview",
    children: [
      { path: "overview", name: "risk-fraud-overview", component: RiskFraudOverview },
      { path: "preset-rules", name: "risk-fraud-presets", component: RiskPresetRulesView },
      { path: "blacklist", name: "risk-fraud-blacklist", component: RiskBlacklistView },
    ],
  },
  { path: "/agent-team", name: "agent-team", component: AgentTeamView },
  { path: "/pricing", name: "pricing", component: PricingView },
  { path: "/report", name: "report", component: ReportView },
  { path: "/analytics", name: "analytics", component: AnalyticsView },
  { path: "/rule", name: "rule", component: RuleView },
  {
    path: "/system",
    component: SystemView,
    redirect: "/system/users",
    children: [
      { path: "users", name: "system-users", component: SystemView },
      { path: "params", name: "system-params", component: SystemView },
      { path: "logs", name: "system-logs", component: SystemView },
    ],
  },
];

const router = new VueRouter({
  mode: "history",
  base: "/",
  routes,
});

const routeMenuMap = {
  "/dashboard": "/dashboard",
  "/customer": "/customer",
  "/product": "/product",
  "/underwriting": "/underwriting",
  "/policy": "/policy",
  "/claim": "/claim",
  "/service": "/service",
  "/channel": "/channel",
  "/finance": "/finance",
  "/reinsurance": "/reinsurance",
  "/risk": "/risk",
  "/risk-fraud": "/risk-fraud",
  "/agent-team": "/agent-team",
  "/report": "/report",
  "/analytics": "/analytics",
  "/rule": "/rule",
  "/system": "/system",
};

function resolveRequiredMenu(path) {
  for (const key of Object.keys(routeMenuMap)) {
    if (path === key || path.startsWith(`${key}/`)) {
      return routeMenuMap[key];
    }
  }
  return "";
}

router.beforeEach((to, from, next) => {
  if (to.path === "/login") {
    next();
    return;
  }
  const token = getAuthToken();
  if (!token) {
    next("/login");
    return;
  }
  const requiredMenu = resolveRequiredMenu(to.path);
  if (!requiredMenu) {
    next();
    return;
  }
  const menus = getAuthMenus();
  if (!menus.length || menus.includes("*") || menus.includes(requiredMenu)) {
    next();
    return;
  }
  next("/dashboard");
  return;
});

export default router;
