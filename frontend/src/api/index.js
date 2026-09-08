/**
 * 风控与规则管理等后端接口封装。
 * 后端默认地址：http://localhost:8000（启动 uvicorn api.server:app）
 */

import axios from "axios";

const baseURL =
  typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE
    ? import.meta.env.VITE_API_BASE
    : "http://localhost:8000";

const request = axios.create({
  baseURL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

const AUTH_TOKEN_KEY = "ins-auth-token";
const AUTH_USER_KEY = "ins-auth-user";
const AUTH_PERMISSION_KEY = "ins-auth-permissions";
const AUTH_MENUS_KEY = "ins-auth-menus";

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY) || "";
}

export function setAuthSession(token, user, authz = {}) {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }
  if (user) {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(AUTH_USER_KEY);
  }
  const permissions = Array.isArray(authz.permissions) ? authz.permissions : [];
  const menus = Array.isArray(authz.menus) ? authz.menus : [];
  localStorage.setItem(AUTH_PERMISSION_KEY, JSON.stringify(permissions));
  localStorage.setItem(AUTH_MENUS_KEY, JSON.stringify(menus));
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
  localStorage.removeItem(AUTH_PERMISSION_KEY);
  localStorage.removeItem(AUTH_MENUS_KEY);
}

export function getAuthUser() {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

export function getAuthPermissions() {
  const raw = localStorage.getItem(AUTH_PERMISSION_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

export function getAuthMenus() {
  const raw = localStorage.getItem(AUTH_MENUS_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

export function hasPermission(permission) {
  const perms = getAuthPermissions();
  if (perms.includes("*:*")) return true;
  return perms.includes(permission);
}

request.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      clearAuthSession();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export function login(username, password) {
  return request.post("/auth/login", { username, password });
}

export function register(username, password) {
  return request.post("/auth/register", { username, password });
}

export function fetchCurrentUser() {
  return request.get("/auth/me");
}

export function logout() {
  return request.post("/auth/logout");
}

export function resetUserPassword(username, newPassword) {
  return request.post("/auth/reset_password", { username, newPassword });
}

export function forceLogoutUser(username) {
  return request.post("/auth/force_logout", { username });
}

export function getAuthSessions() {
  return request.get("/auth/sessions");
}

/** 自然语言 → 结构化规则 */
export function parseRule(ruleText, promptVariant = "json_only") {
  return request.post("/parse_rule", {
    rule_text: ruleText,
    prompt_variant: promptVariant,
  });
}

/** 对单条记录执行规则（可带 rule_text 或使用全部预设规则） */
export function evaluateRule(record, ruleText = null) {
  return request.post("/evaluate_rule", {
    record,
    rule_text: ruleText || undefined,
  });
}

/** 自然语言业务描述 -> 测试记录 JSON */
export function parseTestRecord(text) {
  return request.post("/parse_test_record", { text });
}

/** 将已解析规则加入规则库 */
export function addParsedRule(parsedRule) {
  return request.post("/rules/add_parsed", {
    parsed_rule: parsedRule,
  });
}

/** 查询命中该规则的客户列表 */
export function queryRuleMatchedCustomers({ ruleText = null, parsedRule = null } = {}) {
  return request.post("/rules/query_matched_customers", {
    rule_text: ruleText || undefined,
    parsed_rule: parsedRule || undefined,
  });
}

/** 对命中客户执行规则动作 */
export function applyRuleActions({ ruleText = null, parsedRule = null, customerIds = null } = {}) {
  return request.post("/rules/apply_actions", {
    rule_text: ruleText || undefined,
    parsed_rule: parsedRule || undefined,
    customer_ids: customerIds || undefined,
  });
}

/** 规则库列表（预设 + NL 入库，见 risk_rules 表） */
export function getRules() {
  return request.get("/rules");
}

/** 规则详情 */
export function getRuleDetail(ruleId) {
  return request.get(`/rules/${encodeURIComponent(ruleId)}`);
}

/** 更新规则（描述/动作/启停/优先级） */
export function updateRule(ruleId, patch) {
  return request.put(`/rules/${encodeURIComponent(ruleId)}`, patch || {});
}

/** 删除规则（仅 nl_parsed） */
export function deleteRule(ruleId) {
  return request.delete(`/rules/${encodeURIComponent(ruleId)}`);
}

/** 黑名单页：黑名单列表 */
export function getBlacklist() {
  return request.get("/blacklist");
}

/** 黑名单页：新增黑名单项 */
export function addBlacklistItem(item) {
  return request.post("/blacklist", item);
}

/** 黑名单页：更新黑名单项 */
export function updateBlacklistItem(id, item) {
  return request.put(`/blacklist/${id}`, item);
}

/** 黑名单页：删除黑名单项 */
export function deleteBlacklistItem(id) {
  return request.delete(`/blacklist/${id}`);
}

/** 黑名单页：风控预警列表 */
export function getRiskAlerts() {
  return request.get("/risk_alerts");
}

/** 黑名单页：新增风控预警 */
export function addRiskAlert(item) {
  return request.post("/risk_alerts", item);
}

/** 保险客户管理 */
export function getCustomers() {
  return request.get("/customers");
}

export function getCustomer(id) {
  return request.get(`/customers/${id}`);
}

export function createCustomer(data) {
  return request.post("/customers", data);
}

export function updateCustomer(id, data) {
  return request.put(`/customers/${id}`, data);
}

export function deleteCustomer(id) {
  return request.delete(`/customers/${id}`);
}

/** 客户照片本地上传（multipart，字段名 file） */
export function uploadCustomerPhoto(file) {
  const fd = new FormData();
  fd.append("file", file);
  return request.post("/customers/upload_photo", fd, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  });
}

/** 保单管理 */
export function getPolicies() {
  return request.get("/policies");
}

export function createPolicy(data) {
  return request.post("/policies", data);
}

export function updatePolicy(id, data) {
  return request.put(`/policies/${id}`, data);
}

export function deletePolicy(id) {
  return request.delete(`/policies/${id}`);
}

/** 保险产品管理 */
export function getProducts() {
  return request.get("/products");
}

export function getProduct(id) {
  return request.get(`/products/${id}`);
}

/** 标准产品目录（下拉：名称 / 险种 / 参考保费等） */
export function getProductCatalog() {
  return request.get("/products/catalog");
}

export function getProductCategories() {
  return request.get("/products/categories");
}

export function createProduct(data) {
  return request.post("/products", data);
}

export function updateProduct(id, data) {
  return request.put(`/products/${id}`, data);
}

export function deleteProduct(id) {
  return request.delete(`/products/${id}`);
}

/** 承保案件 */
export function getUnderwritingCases() {
  return request.get("/underwriting_cases");
}

export function createUnderwritingCase(data) {
  return request.post("/underwriting_cases", data);
}

export function updateUnderwritingCase(id, data) {
  return request.put(`/underwriting_cases/${id}`, data);
}

export function deleteUnderwritingCase(id) {
  return request.delete(`/underwriting_cases/${id}`);
}

/** 理赔案件 */
export function getClaims() {
  return request.get("/claims");
}

export function createClaim(data) {
  return request.post("/claims", data);
}

export function updateClaim(id, data) {
  return request.put(`/claims/${id}`, data);
}

export function deleteClaim(id) {
  return request.delete(`/claims/${id}`);
}

/** 售后与投诉工单 */
export function getServiceTickets() {
  return request.get("/service_tickets");
}

export function createServiceTicket(data) {
  return request.post("/service_tickets", data);
}

export function updateServiceTicket(id, data) {
  return request.put(`/service_tickets/${id}`, data);
}

export function deleteServiceTicket(id) {
  return request.delete(`/service_tickets/${id}`);
}

/** 销售渠道 */
export function getChannels() {
  return request.get("/channels");
}

export function createChannel(data) {
  return request.post("/channels", data);
}

export function updateChannel(id, data) {
  return request.put(`/channels/${id}`, data);
}

export function deleteChannel(id) {
  return request.delete(`/channels/${id}`);
}

/** 财务管理 — 保费收付流水 */
export function getPremiumFlows() {
  return request.get("/premium_flows");
}

export function createPremiumFlow(data) {
  return request.post("/premium_flows", data);
}

export function updatePremiumFlow(id, data) {
  return request.put(`/premium_flows/${id}`, data);
}

export function deletePremiumFlow(id) {
  return request.delete(`/premium_flows/${id}`);
}

/** 财务管理 — 佣金结算与对账 */
export function getCommissionSettlements() {
  return request.get("/commission_settlements");
}

export function createCommissionSettlement(data) {
  return request.post("/commission_settlements", data);
}

export function updateCommissionSettlement(id, data) {
  return request.put(`/commission_settlements/${id}`, data);
}

export function deleteCommissionSettlement(id) {
  return request.delete(`/commission_settlements/${id}`);
}

/** 再保管理 — 再保合同 */
export function getReinsuranceContracts() {
  return request.get("/reinsurance_contracts");
}

export function createReinsuranceContract(data) {
  return request.post("/reinsurance_contracts", data);
}

export function updateReinsuranceContract(id, data) {
  return request.put(`/reinsurance_contracts/${id}`, data);
}

export function deleteReinsuranceContract(id) {
  return request.delete(`/reinsurance_contracts/${id}`);
}

/** 再保管理 — 分出/分入账单 */
export function getReinsuranceBills() {
  return request.get("/reinsurance_bills");
}

export function createReinsuranceBill(data) {
  return request.post("/reinsurance_bills", data);
}

export function updateReinsuranceBill(id, data) {
  return request.put(`/reinsurance_bills/${id}`, data);
}

export function deleteReinsuranceBill(id) {
  return request.delete(`/reinsurance_bills/${id}`);
}

/** 代理人/团队管理 — 团队 */
export function getAgentTeams() {
  return request.get("/agent_teams");
}

export function createAgentTeam(data) {
  return request.post("/agent_teams", data);
}

export function updateAgentTeam(id, data) {
  return request.put(`/agent_teams/${id}`, data);
}

export function deleteAgentTeam(id) {
  return request.delete(`/agent_teams/${id}`);
}

/** 代理人/团队管理 — 代理人 */
export function getAgents() {
  return request.get("/agents");
}

export function createAgent(data) {
  return request.post("/agents", data);
}

export function updateAgent(id, data) {
  return request.put(`/agents/${id}`, data);
}

export function deleteAgent(id) {
  return request.delete(`/agents/${id}`);
}

/** 代理人/团队管理 — 业绩汇总 */
export function getAgentPerformanceSummary(period = "") {
  return request.get("/agent_performance_summary", { params: period ? { period } : {} });
}

/** 报表与分析 — 运营报表摘要 */
export function getAnalyticsSummary() {
  return request.get("/analytics/summary");
}

/** 系统管理 — 用户 */
export function getSystemUsers() {
  return request.get("/system_users");
}

export function createSystemUser(data) {
  return request.post("/system_users", data);
}

export function updateSystemUser(id, data) {
  return request.put(`/system_users/${id}`, data);
}

export function deleteSystemUser(id) {
  return request.delete(`/system_users/${id}`);
}

/** 系统管理 — 参数 */
export function getSystemParams() {
  return request.get("/system_params");
}

export function createSystemParam(data) {
  return request.post("/system_params", data);
}

export function updateSystemParam(id, data) {
  return request.put(`/system_params/${id}`, data);
}

export function deleteSystemParam(id) {
  return request.delete(`/system_params/${id}`);
}

/** 系统管理 — 日志 */
export function getSystemLogs({ limit = 100, module = "", actor = "", keyword = "" } = {}) {
  return request.get("/system_logs", { params: { limit, module, actor, keyword } });
}

export function getAuditPolicies() {
  return request.get("/system/audit_policies");
}

export function getSystemRoadmap() {
  return request.get("/system/roadmap");
}

export default request;
