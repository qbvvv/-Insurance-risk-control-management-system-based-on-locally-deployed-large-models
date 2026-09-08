<template>
  <div class="page">
    <h1 class="page-title">系统管理</h1>
    <p class="page-subtitle">
      维护系统用户与角色、可配置参数及操作日志查询；用户与参数支持新增、编辑、删除（日志为只读审计记录）。
    </p>
    <nav class="system-subnav">
      <router-link
        v-for="l in nav"
        :key="l.to"
        :to="l.to"
        class="system-subnav-link"
        :class="{ 'system-subnav-link--active': isNavActive(l) }"
      >
        {{ l.label }}
      </router-link>
    </nav>

    <div class="system-stack">
      <div v-if="currentSection === 'users'" class="card">
        <h2>用户与角色权限</h2>
        <el-form
          ref="userForm"
          :model="userForm"
          :rules="userRules"
          label-width="88px"
          size="small"
          class="mini-form"
          @submit.native.prevent="submitUser"
        >
          <el-form-item v-if="userEditingId" label="用户 ID">
            <el-input :value="userEditingId" disabled />
          </el-form-item>
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="userForm.username"
              :disabled="!!userEditingId"
              clearable
              placeholder="3-32位字母数字下划线"
              maxlength="32"
              show-word-limit
              @blur="prefillDisplayName"
            />
          </el-form-item>
          <el-form-item label="姓名" prop="fullName">
            <el-input v-model="userForm.fullName" clearable placeholder="如 张三" maxlength="32" show-word-limit />
          </el-form-item>
          <el-form-item label="工号" prop="employeeNo">
            <el-input v-model="userForm.employeeNo" clearable placeholder="如 EMP0001" maxlength="32" />
          </el-form-item>
          <el-form-item label="机构编码" prop="orgCode">
            <el-input
              v-model="userForm.orgCode"
              clearable
              placeholder="如 HQ、SH01"
              maxlength="32"
              @blur="normalizeOrgCode"
            />
          </el-form-item>
          <el-form-item label="部门" prop="department">
            <el-input v-model="userForm.department" clearable maxlength="64" show-word-limit />
          </el-form-item>
          <el-form-item label="岗位" prop="post">
            <el-input v-model="userForm.post" clearable maxlength="64" show-word-limit />
          </el-form-item>
          <el-form-item label="角色" prop="role">
            <el-select
              v-model="userForm.role"
              filterable
              placeholder="请选择岗位角色"
              style="width: 100%;"
              :disabled="isBuiltinAdminEdit"
              @change="onUserRoleChange"
            >
              <el-option v-for="r in roleOptionsForForm" :key="r" :label="r" :value="r" />
            </el-select>
          </el-form-item>
          <el-form-item label="数据权限" prop="dataScope">
            <el-select v-model="userForm.dataScope" style="width: 100%;" :disabled="isBuiltinAdminEdit">
              <el-option
                v-for="scope in dataScopeOptions"
                :key="scope"
                :label="scope"
                :value="scope"
                :disabled="scope === '全部数据' && userForm.role !== '系统管理员'"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="userForm.status" style="width: 100%;" :disabled="isBuiltinAdminEdit">
              <el-option label="启用" value="启用" />
              <el-option label="停用" value="停用" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="userSubmitting">
              {{ userEditingId ? "保存" : "新增用户" }}
            </el-button>
            <el-button v-if="userEditingId" @click="resetUserForm">取消</el-button>
          </el-form-item>
        </el-form>
        <el-table
          class="module-table"
          :data="users"
          border
          size="small"
          style="width: 100%;"
          v-loading="usersLoading"
        >
          <el-table-column prop="username" label="用户名" min-width="100" />
          <el-table-column prop="fullName" label="姓名" min-width="90" show-overflow-tooltip />
          <el-table-column prop="orgCode" label="机构" min-width="90" show-overflow-tooltip />
          <el-table-column prop="department" label="部门" min-width="90" show-overflow-tooltip />
          <el-table-column prop="role" label="角色" min-width="100" />
          <el-table-column prop="dataScope" label="数据权限" min-width="90" />
          <el-table-column prop="status" label="状态" width="72" />
          <el-table-column prop="updatedAt" label="更新日期" width="108" />
          <el-table-column label="操作" width="360" align="left" fixed="right">
            <template slot-scope="scope">
              <div class="module-table-ops module-table-ops--nowrap">
                <el-button type="primary" size="mini" @click="editUser(scope.row)">编辑</el-button>
                <el-button size="mini" @click="resetPassword(scope.row)">重置密码</el-button>
                <el-button size="mini" @click="forceOffline(scope.row)">强制下线</el-button>
                <el-button
                  type="danger"
                  size="mini"
                  :disabled="scope.row.username === 'admin'"
                  @click="removeUser(scope.row)"
                >
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="currentSection === 'params'" class="card">
        <h2>系统参数</h2>
        <el-form
          ref="paramForm"
          :model="paramForm"
          :rules="paramRulesActive"
          label-width="88px"
          size="small"
          class="mini-form"
          @submit.native.prevent="submitParam"
        >
          <el-form-item v-if="paramEditingId" label="参数键">
            <el-input :value="paramForm.paramKey" disabled />
          </el-form-item>
          <el-form-item v-else label="参数键" prop="paramKey">
            <el-input v-model="paramForm.paramKey" clearable placeholder="唯一标识，如 nl_prompt_variant" />
          </el-form-item>
          <el-form-item label="参数值" prop="paramValue">
            <el-input v-model="paramForm.paramValue" clearable />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input v-model="paramForm.description" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="paramSubmitting">
              {{ paramEditingId ? "保存" : "新增参数" }}
            </el-button>
            <el-button v-if="paramEditingId" @click="resetParamForm">取消</el-button>
          </el-form-item>
        </el-form>
        <el-table
          class="module-table"
          :data="params"
          border
          size="small"
          style="width: 100%;"
          v-loading="paramsLoading"
        >
          <el-table-column prop="paramKey" label="参数键" min-width="120" />
          <el-table-column prop="paramValue" label="参数值" min-width="100" />
          <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip />
          <el-table-column label="操作" width="168" align="center" fixed="right">
            <template slot-scope="scope">
              <div class="module-table-ops">
                <el-button type="primary" size="mini" @click="editParam(scope.row)">编辑</el-button>
                <el-button type="danger" size="mini" @click="removeParam(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

      </div>

      <div v-if="currentSection === 'logs'" class="card">
        <h2>系统日志</h2>
        <div class="logs-toolbar">
          <el-input v-model="logQuery.actor" size="mini" clearable placeholder="按操作者筛选" class="log-filter" />
          <el-input v-model="logQuery.module" size="mini" clearable placeholder="按模块筛选" class="log-filter" />
          <el-input v-model="logQuery.keyword" size="mini" clearable placeholder="关键词" class="log-filter log-filter-wide" />
          <el-button size="mini" @click="resetLogQuery">重置</el-button>
          <el-button size="mini" :loading="logsLoading" @click="fetchSystemLogs">刷新</el-button>
        </div>
        <el-table class="module-table" :data="logs" border size="small" style="width: 100%;" v-loading="logsLoading">
          <el-table-column prop="logType" label="类型" width="80" />
          <el-table-column prop="actor" label="操作者" width="100" />
          <el-table-column prop="module" label="模块" width="90" />
          <el-table-column prop="result" label="结果" width="90" />
          <el-table-column prop="action" label="操作内容" min-width="180" show-overflow-tooltip />
          <el-table-column prop="ip" label="IP" width="130" show-overflow-tooltip />
          <el-table-column prop="createdAt" label="时间" width="120" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import {
  createSystemParam,
  createSystemUser,
  deleteSystemParam,
  deleteSystemUser,
  forceLogoutUser,
  getSystemLogs,
  getSystemParams,
  getSystemUsers,
  resetUserPassword,
  updateSystemParam,
  updateSystemUser,
} from "@/api";

export default {
  name: "SystemView",
  data() {
    return {
      users: [],
      usersLoading: false,
      userEditingId: "",
      userSubmitting: false,
      userForm: {
        username: "",
        fullName: "",
        employeeNo: "",
        orgCode: "",
        department: "",
        post: "",
        role: "",
        dataScope: "本人",
        status: "启用",
      },
      roleOptions: ["系统管理员", "承保岗", "理赔岗", "反欺诈岗", "财务岗", "再保岗", "审计岗", "普通用户"],
      dataScopeOptions: ["全部数据", "本机构数据", "本人"],
      userRules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
          {
            pattern: /^[a-zA-Z0-9_]{3,32}$/,
            message: "用户名为 3-32 位字母、数字或下划线",
            trigger: "blur",
          },
        ],
        fullName: [{ max: 32, message: "姓名不超过 32 字", trigger: "blur" }],
        employeeNo: [
          { max: 32, message: "工号不超过 32 位", trigger: "blur" },
          { pattern: /^[A-Za-z0-9_-]*$/, message: "工号仅允许字母数字、下划线与短横线", trigger: "blur" },
        ],
        orgCode: [
          { max: 32, message: "机构编码不超过 32 位", trigger: "blur" },
          { pattern: /^[A-Za-z0-9/_-]*$/, message: "机构编码仅允许字母数字、斜杠与短横线", trigger: "blur" },
        ],
        department: [{ max: 64, message: "部门不超过 64 字", trigger: "blur" }],
        post: [{ max: 64, message: "岗位不超过 64 字", trigger: "blur" }],
        role: [{ required: true, message: "请选择角色", trigger: "change" }],
        dataScope: [{ required: true, message: "请选择数据权限", trigger: "change" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
      params: [],
      paramsLoading: false,
      paramEditingId: "",
      paramSubmitting: false,
      paramForm: {
        paramKey: "",
        paramValue: "",
        description: "",
      },
      paramRules: {
        paramKey: [{ required: true, message: "请输入参数键", trigger: "blur" }],
      },
      logs: [],
      logsLoading: false,
      nav: [
        { to: "/system/users", label: "用户与角色权限", match: "exact" },
        { to: "/system/params", label: "系统参数", match: "exact" },
        { to: "/system/logs", label: "系统日志", match: "exact" },
      ],
      logQuery: {
        actor: "",
        module: "",
        keyword: "",
      },
    };
  },
  created() {
    this.fetchSystemUsers();
    this.fetchSystemParams();
    this.fetchSystemLogs();
  },
  computed: {
    currentSection() {
      const path = this.$route.path || "";
      if (path.startsWith("/system/params")) return "params";
      if (path.startsWith("/system/logs")) return "logs";
      return "users";
    },
    paramRulesActive() {
      if (this.paramEditingId) {
        return {};
      }
      return this.paramRules;
    },
    /** 编辑内置 admin 时锁定角色、数据权限与状态，避免误操作导致无法登录 */
    isBuiltinAdminEdit() {
      return !!this.userEditingId && this.userForm.username === "admin";
    },
    /** 新建用户不允许选「系统管理员」；仅内置 admin 可保留该角色 */
    roleOptionsForForm() {
      if (this.isBuiltinAdminEdit) return ["系统管理员"];
      return this.roleOptions.filter((r) => r !== "系统管理员");
    },
  },
  methods: {
    isNavActive(l) {
      const p = this.$route.path;
      if (l.match === "prefix") return p === l.to || p.startsWith(`${l.to}/`);
      return p === l.to;
    },
    fetchSystemUsers() {
      this.usersLoading = true;
      getSystemUsers()
        .then((res) => {
          this.users = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.users = [];
        })
        .finally(() => {
          this.usersLoading = false;
        });
    },
    resetUserForm() {
      this.userEditingId = "";
      this.userForm = {
        username: "",
        fullName: "",
        employeeNo: "",
        orgCode: "",
        department: "",
        post: "",
        role: "",
        dataScope: "本人",
        status: "启用",
      };
      this.$nextTick(() => this.$refs.userForm && this.$refs.userForm.clearValidate());
    },
    editUser(row) {
      this.userEditingId = row.id;
      const isAdmin = (row.username || "").trim() === "admin";
      this.userForm = {
        username: row.username || "",
        fullName: row.fullName || "",
        employeeNo: row.employeeNo || "",
        orgCode: row.orgCode || "",
        department: row.department || "",
        post: row.post || "",
        role: row.role || "",
        dataScope: isAdmin ? "全部数据" : row.dataScope || "本人",
        status: row.status || "启用",
      };
      this.$nextTick(() => this.$refs.userForm && this.$refs.userForm.clearValidate());
    },
    onUserRoleChange(role) {
      if (role === "系统管理员") {
        this.userForm.dataScope = "全部数据";
      } else if (["承保岗", "理赔岗", "反欺诈岗", "财务岗", "再保岗"].includes(role)) {
        this.userForm.dataScope = "本机构数据";
      } else {
        this.userForm.dataScope = "本人";
      }
    },
    prefillDisplayName() {
      if (this.userEditingId) return;
      const u = (this.userForm.username || "").trim();
      if (!u || (this.userForm.fullName || "").trim()) return;
      this.userForm.fullName = u;
    },
    normalizeOrgCode() {
      this.userForm.orgCode = (this.userForm.orgCode || "").trim().toUpperCase();
    },
    submitUser() {
      this.$refs.userForm.validate((ok) => {
        if (!ok) return;
        const done = () => {
          this.userSubmitting = false;
        };
        this.userSubmitting = true;
        if (this.userEditingId) {
          updateSystemUser(this.userEditingId, {
            fullName: this.userForm.fullName,
            employeeNo: this.userForm.employeeNo,
            orgCode: this.userForm.orgCode,
            department: this.userForm.department,
            post: this.userForm.post,
            role: this.userForm.role,
            dataScope: this.userForm.dataScope,
            status: this.userForm.status,
          })
            .then(() => {
              this.$message.success("已保存");
              this.fetchSystemUsers();
              this.resetUserForm();
            })
            .catch((e) => {
              this.$message.error(this.errDetail(e));
            })
            .finally(done);
        } else {
          createSystemUser({
            username: this.userForm.username,
            fullName: this.userForm.fullName,
            employeeNo: this.userForm.employeeNo,
            orgCode: this.userForm.orgCode,
            department: this.userForm.department,
            post: this.userForm.post,
            role: this.userForm.role,
            dataScope: this.userForm.dataScope,
            status: this.userForm.status,
          })
            .then(() => {
              this.$message.success("已新增用户");
              this.fetchSystemUsers();
              this.resetUserForm();
            })
            .catch((e) => {
              this.$message.error(this.errDetail(e));
            })
            .finally(done);
        }
      });
    },
    removeUser(row) {
      this.$confirm(`确定删除用户「${row.username}」？`, "提示", { type: "warning" })
        .then(() => deleteSystemUser(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchSystemUsers();
          if (this.userEditingId === row.id) this.resetUserForm();
        })
        .catch((e) => {
          if (e === "cancel" || e === "close") return;
          this.$message.error(this.errDetail(e));
        });
    },
    fetchSystemParams() {
      this.paramsLoading = true;
      getSystemParams()
        .then((res) => {
          this.params = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.params = [];
        })
        .finally(() => {
          this.paramsLoading = false;
        });
    },
    resetParamForm() {
      this.paramEditingId = "";
      this.paramForm = { paramKey: "", paramValue: "", description: "" };
      this.$nextTick(() => this.$refs.paramForm && this.$refs.paramForm.clearValidate());
    },
    editParam(row) {
      this.paramEditingId = row.id;
      this.paramForm = {
        paramKey: row.paramKey || "",
        paramValue: row.paramValue || "",
        description: row.description || "",
      };
      this.$nextTick(() => this.$refs.paramForm && this.$refs.paramForm.clearValidate());
    },
    submitParam() {
      this.$refs.paramForm.validate((ok) => {
        if (!ok) return;
        const done = () => {
          this.paramSubmitting = false;
        };
        this.paramSubmitting = true;
        if (this.paramEditingId) {
          updateSystemParam(this.paramEditingId, {
            paramValue: this.paramForm.paramValue,
            description: this.paramForm.description,
          })
            .then(() => {
              this.$message.success("已保存");
              this.fetchSystemParams();
              this.resetParamForm();
            })
            .catch((e) => {
              this.$message.error(this.errDetail(e));
            })
            .finally(done);
        } else {
          createSystemParam({
            paramKey: this.paramForm.paramKey,
            paramValue: this.paramForm.paramValue,
            description: this.paramForm.description,
          })
            .then(() => {
              this.$message.success("已新增参数");
              this.fetchSystemParams();
              this.resetParamForm();
            })
            .catch((e) => {
              this.$message.error(this.errDetail(e));
            })
            .finally(done);
        }
      });
    },
    removeParam(row) {
      this.$confirm(`确定删除参数「${row.paramKey}」？`, "提示", { type: "warning" })
        .then(() => deleteSystemParam(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchSystemParams();
          if (this.paramEditingId === row.id) this.resetParamForm();
        })
        .catch((e) => {
          if (e === "cancel" || e === "close") return;
          this.$message.error(this.errDetail(e));
        });
    },
    fetchSystemLogs() {
      this.logsLoading = true;
      getSystemLogs({
        limit: 50,
        module: this.logQuery.module,
        actor: this.logQuery.actor,
        keyword: this.logQuery.keyword,
      })
        .then((res) => {
          this.logs = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.logs = [];
        })
        .finally(() => {
          this.logsLoading = false;
        });
    },
    resetLogQuery() {
      this.logQuery = { actor: "", module: "", keyword: "" };
      this.fetchSystemLogs();
    },
    async resetPassword(row) {
      try {
        const ret = await this.$prompt(`请输入用户 ${row.username} 的新密码（至少6位）`, "重置密码", {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          inputType: "password",
          inputPattern: /^.{6,}$/,
          inputErrorMessage: "密码长度至少 6 位",
        });
        await resetUserPassword(row.username, ret.value);
        this.$message.success("密码已重置");
      } catch (e) {
        if (e === "cancel" || e === "close") return;
        this.$message.error(this.errDetail(e));
      }
    },
    async forceOffline(row) {
      try {
        await this.$confirm(`确定强制下线用户「${row.username}」？`, "提示", { type: "warning" });
        const resp = await forceLogoutUser(row.username);
        const count = resp?.data?.count ?? 0;
        this.$message.success(`已下线 ${count} 个会话`);
      } catch (e) {
        if (e === "cancel" || e === "close") return;
        this.$message.error(this.errDetail(e));
      }
    },
    errDetail(e) {
      const d = e && e.response && e.response.data && e.response.data.detail;
      if (typeof d === "string") return d;
      if (Array.isArray(d) && d.length && d[0].msg) return d.map((x) => x.msg).join("；");
      return (e && e.message) || "请求失败";
    },
  },
};
</script>

<style scoped>
.system-stack {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.system-subnav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 0 12px;
  margin-bottom: 16px;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}
.system-subnav-link {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  color: #64748b;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.system-subnav-link:hover {
  color: #334155;
  background: rgba(148, 163, 184, 0.15);
}
.system-subnav-link--active {
  background: var(--primary-soft, rgba(59, 130, 246, 0.14));
  color: var(--primary-color, #3b82f6);
  font-weight: 600;
}
.mini-form {
  margin-bottom: 12px;
}
.logs-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.log-filter {
  width: 140px;
}
.log-filter-wide {
  width: 220px;
}
</style>
