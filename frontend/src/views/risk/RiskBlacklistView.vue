<template>
  <div>
    <p class="section-hint">
      本页上方为黑名单维护（高风险客户或证件对象），下方为风控预警流水；可与规则命中结果联合用于承保、理赔环节拦截或人工复核。
    </p>
    <div class="card" style="margin-bottom: 16px;">
      <h2>黑名单</h2>
      <el-form
        ref="blacklistFormRef"
        :model="blacklistForm"
        :rules="blacklistRules"
        label-width="88px"
        size="small"
        class="mini-form"
        @submit.native.prevent="submitBlacklist"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="blacklistForm.name" clearable />
        </el-form-item>
        <el-form-item label="证件号" prop="idNo">
          <el-input v-model="blacklistForm.idNo" clearable />
        </el-form-item>
        <el-form-item label="列入原因" prop="reason">
          <el-input v-model="blacklistForm.reason" clearable />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="blacklistForm.status" style="width: 100%;">
            <el-option label="启用" value="启用" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="blacklistSubmitting">
            {{ blacklistEditingId ? "保存" : "新增黑名单" }}
          </el-button>
          <el-button v-if="blacklistEditingId" @click="resetBlacklistForm">取消</el-button>
          <el-button @click="fetchBlacklist">刷新</el-button>
        </el-form-item>
      </el-form>

      <el-table class="module-table" :data="blacklist" border size="small" style="width: 100%;" v-loading="blacklistLoading">
        <el-table-column prop="name" label="姓名" width="90"></el-table-column>
        <el-table-column prop="idNo" label="证件号"></el-table-column>
        <el-table-column prop="reason" label="列入原因"></el-table-column>
        <el-table-column prop="status" label="状态" width="80"></el-table-column>
        <el-table-column label="操作" width="168" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="module-table-ops">
              <el-button type="primary" size="mini" @click="editBlacklist(scope.row)">编辑</el-button>
              <el-button type="danger" size="mini" @click="removeBlacklist(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <p v-if="blacklistError" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ blacklistError }}</p>
    </div>

    <div class="card">
      <h2>风控预警</h2>
      <p style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">
        风控预警流水（数据来自后端接口），与上方名单联动展示。
      </p>
      <el-table
        class="module-table"
        :data="alerts"
        border
        size="small"
        style="width: 100%;"
        v-loading="alertsLoading"
        :max-height="420"
      >
        <el-table-column prop="code" label="预警编号" width="128" show-overflow-tooltip />
        <el-table-column prop="type" label="预警类型" width="112" show-overflow-tooltip />
        <el-table-column prop="desc" label="预警说明" min-width="200" show-overflow-tooltip />
        <el-table-column prop="level" label="风险等级" width="96" align="center" />
      </el-table>
      <p v-if="alertsError" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ alertsError }}</p>
    </div>
  </div>
</template>

<script>
import { addBlacklistItem, deleteBlacklistItem, getBlacklist, getRiskAlerts, updateBlacklistItem } from "@/api";

export default {
  name: "RiskBlacklistView",
  data() {
    return {
      blacklist: [],
      blacklistLoading: false,
      blacklistSubmitting: false,
      blacklistEditingId: "",
      blacklistForm: {
        name: "",
        idNo: "",
        reason: "",
        status: "启用",
      },
      blacklistRules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        idNo: [{ required: true, message: "请输入证件号", trigger: "blur" }],
        reason: [{ required: true, message: "请输入列入原因", trigger: "blur" }],
      },
      alerts: [],
      alertsLoading: false,
      fallbackAlerts: [
        {
          code: "AL2026030601",
          type: "集中投保",
          desc: "短期内同一地址多笔高保额投保",
          level: "高",
        },
      ],
      blacklistError: "",
      alertsError: "",
    };
  },
  mounted() {
    this.fetchBlacklist();
    this.fetchAlerts();
  },
  methods: {
    resetBlacklistForm() {
      this.blacklistEditingId = "";
      this.blacklistForm = { name: "", idNo: "", reason: "", status: "启用" };
      this.$nextTick(() => this.$refs.blacklistFormRef && this.$refs.blacklistFormRef.clearValidate());
    },
    editBlacklist(row) {
      this.blacklistEditingId = row.id;
      this.blacklistForm = {
        name: row.name || "",
        idNo: row.idNo || "",
        reason: row.reason || "",
        status: row.status || "启用",
      };
      this.$nextTick(() => this.$refs.blacklistFormRef && this.$refs.blacklistFormRef.clearValidate());
    },
    submitBlacklist() {
      this.$refs.blacklistFormRef.validate((ok) => {
        if (!ok) return;
        this.blacklistSubmitting = true;
        const payload = {
          name: this.blacklistForm.name,
          idNo: this.blacklistForm.idNo,
          reason: this.blacklistForm.reason,
          status: this.blacklistForm.status || "启用",
        };
        const req = this.blacklistEditingId
          ? updateBlacklistItem(this.blacklistEditingId, payload)
          : addBlacklistItem(payload);
        req
          .then(() => {
            this.$message.success(this.blacklistEditingId ? "黑名单已更新" : "黑名单已新增");
            this.fetchBlacklist();
            this.resetBlacklistForm();
          })
          .catch((err) => {
            this.$message.error("操作失败：" + (err.response?.data?.detail || err.message));
          })
          .finally(() => {
            this.blacklistSubmitting = false;
          });
      });
    },
    removeBlacklist(row) {
      this.$confirm(`确定删除黑名单「${row.name}」？`, "提示", { type: "warning" })
        .then(() => deleteBlacklistItem(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchBlacklist();
          if (this.blacklistEditingId === row.id) this.resetBlacklistForm();
        })
        .catch((err) => {
          if (err === "cancel" || err === "close") return;
          this.$message.error("删除失败：" + (err.response?.data?.detail || err.message));
        });
    },
    fetchBlacklist() {
      this.blacklistLoading = true;
      getBlacklist()
        .then((res) => {
          this.blacklist = Array.isArray(res.data) ? res.data : [];
          this.blacklistError = "";
        })
        .catch(() => {
          this.blacklist = [];
          this.blacklistError = "接口请求失败，请确认后端已启动。";
        })
        .finally(() => {
          this.blacklistLoading = false;
        });
    },
    fetchAlerts() {
      this.alertsLoading = true;
      getRiskAlerts()
        .then((res) => {
          this.alerts = Array.isArray(res.data) ? res.data : [];
          this.alertsError = "";
        })
        .catch(() => {
          this.alerts = this.fallbackAlerts;
          this.alertsError =
            "接口请求失败，显示示例数据。请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.alertsLoading = false;
        });
    },
  },
};
</script>

<style scoped>
.section-hint {
  margin: 0 0 14px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.55;
}

.mini-form {
  margin-bottom: 12px;
}
</style>
