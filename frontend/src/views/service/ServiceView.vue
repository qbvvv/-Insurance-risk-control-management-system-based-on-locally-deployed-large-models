<template>
  <div class="page">
    <h1 class="page-title">售后与投诉管理</h1>
    <p class="page-subtitle">
      统一记录售后服务与投诉工单；工单号由后端生成（CS + 日期 + 序号）。建档后类型、客户与诉求正文等不可修改，仅可在弹窗中更新状态、处理人与处理说明。
    </p>

    <div class="card">
      <div class="list-head">
        <h2>工单列表</h2>
        <el-button type="primary" size="small" @click="openAddDialog">新增工单</el-button>
      </div>

      <el-table
        class="module-table"
        :data="tickets"
        border
        size="small"
        style="width: 100%;"
        v-loading="loading"
      >
        <el-table-column prop="ticketNo" label="工单号" width="130" />
        <el-table-column prop="ticketType" label="类型" width="72" />
        <el-table-column prop="contactName" label="联系人" width="90" />
        <el-table-column prop="policyNo" label="保单号" width="120" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="startDate" label="计划开始" width="100" />
        <el-table-column prop="endDate" label="计划结束" width="100" />
        <el-table-column prop="subject" label="主题" min-width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="90" />
        <el-table-column prop="handler" label="处理人" width="100" />
        <el-table-column label="操作" width="168" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="module-table-ops">
              <el-button type="primary" size="mini" @click="openEditDialog(scope.row)">编辑</el-button>
              <el-button type="danger" size="mini" @click="removeRow(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <p v-if="error" class="table-error">{{ error }}</p>
    </div>

    <el-dialog
      :title="dialogMode === 'add' ? '新增工单' : '处理工单'"
      :visible.sync="dialogVisible"
      width="760px"
      destroy-on-close
      @closed="onDialogClosed"
    >
      <p v-if="dialogMode === 'edit'" class="dialog-hint">
        灰色字段为建档信息，不可修改；请在本单内更新进度与处理说明。
      </p>
      <el-form ref="ticketForm" :model="form" :rules="activeRules" label-width="108px" size="small" class="dialog-form">
        <el-form-item v-if="dialogMode === 'edit'" label="工单编号">
          <el-input :value="form.ticketNo" disabled />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="类型" prop="ticketType">
            <el-select v-model="form.ticketType" style="width: 100%;" :disabled="isLocked">
              <el-option label="售后" value="售后" />
              <el-option label="投诉" value="投诉" />
            </el-select>
          </el-form-item>
          <el-form-item label="客户" prop="customerNo">
            <el-select
              v-if="!isLocked"
              v-model="form.customerNo"
              filterable
              clearable
              placeholder="请选择已建档客户"
              style="width: 100%;"
              :loading="customersLoading"
              @change="onCustomerChange"
            >
              <el-option
                v-for="c in customers"
                :key="c.id"
                :label="`${c.customerNo}　${c.name}`"
                :value="c.customerNo"
              />
            </el-select>
            <el-input v-else :value="customerDisplay" disabled />
          </el-form-item>
          <el-form-item label="联系人" prop="contactName">
            <el-input v-model="form.contactName" clearable maxlength="64" show-word-limit :disabled="isLocked" />
          </el-form-item>
          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="form.phone" clearable maxlength="20" placeholder="选客户后自动带出，可改" :disabled="isLocked" />
          </el-form-item>
          <el-form-item label="关联保单" prop="policyNo">
            <el-select
              v-if="!isLocked"
              v-model="form.policyNo"
              filterable
              clearable
              allow-create
              default-first-option
              placeholder="先选客户；可选已有保单或手输单号"
              style="width: 100%;"
              :loading="policiesLoading"
              :disabled="!form.customerNo"
            >
              <el-option
                v-for="p in policiesForCustomer"
                :key="p.id"
                :label="`${p.policyNo}　${p.productName || ''}`"
                :value="p.policyNo"
              />
            </el-select>
            <el-input v-else :value="form.policyNo || '—'" disabled />
          </el-form-item>
          <el-form-item label="分类" prop="category">
            <el-select
              v-if="!isLocked"
              v-model="form.category"
              filterable
              clearable
              allow-create
              default-first-option
              placeholder="选择或输入分类"
              style="width: 100%;"
            >
              <el-option v-for="cat in categoryOptions" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-input v-else :value="form.category || '—'" disabled />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" style="width: 100%;">
              <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="处理人" prop="handler">
            <el-select
              v-model="form.handler"
              filterable
              clearable
              allow-create
              default-first-option
              placeholder="选择或输入处理人"
              style="width: 100%;"
            >
              <el-option v-for="h in handlerSelectOptions" :key="h" :label="h" :value="h" />
            </el-select>
          </el-form-item>
          <el-form-item label="计划开始" prop="startDate">
            <el-date-picker
              v-if="!isLocked"
              v-model="form.startDate"
              type="date"
              placeholder="选择开始日期"
              value-format="yyyy-MM-dd"
              style="width: 100%;"
              clearable
              @change="onPlanStartChange"
            />
            <el-input v-else :value="form.startDate || '—'" disabled />
          </el-form-item>
          <el-form-item label="计划结束" prop="endDate">
            <el-date-picker
              v-if="!isLocked"
              v-model="form.endDate"
              type="date"
              placeholder="选择结束日期"
              value-format="yyyy-MM-dd"
              style="width: 100%;"
              clearable
              :picker-options="endDatePickerOptions"
              @change="onPlanEndChange"
            />
            <el-input v-else :value="form.endDate || '—'" disabled />
          </el-form-item>
        </div>
        <p v-if="!isLocked" class="field-hint">计划起止须同时填写或同时留空；结束日期不能早于开始日期。</p>
        <el-form-item label="主题" prop="subject">
          <el-input v-model="form.subject" clearable maxlength="256" show-word-limit :disabled="isLocked" />
        </el-form-item>
        <el-form-item label="详细内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="3"
            maxlength="4000"
            show-word-limit
            :disabled="isLocked"
          />
        </el-form-item>
        <el-form-item label="处理说明" prop="resolutionNote">
          <el-input
            v-model="form.resolutionNote"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="结案或跟进时填写"
          />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitDialog">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  createServiceTicket,
  deleteServiceTicket,
  getCustomers,
  getPolicies,
  getServiceTickets,
  updateServiceTicket,
} from "@/api";

function normalizePhoneInput(v) {
  return String(v || "")
    .trim()
    .replace(/\s+/g, "");
}

export default {
  name: "ServiceView",
  data() {
    return {
      tickets: [],
      customers: [],
      policies: [],
      loading: false,
      customersLoading: false,
      policiesLoading: false,
      error: "",
      dialogVisible: false,
      dialogMode: "add",
      editingId: null,
      submitting: false,
      statusOptions: ["待受理", "处理中", "已回复", "已结案"],
      categoryOptions: [
        "理赔时效",
        "保全变更",
        "销售误导",
        "保单变更",
        "续保咨询",
        "退保咨询",
        "核保时效",
        "增值服务",
        "发票与凭证",
        "渠道纠纷",
        "其他",
      ],
      handlerPresets: ["客服值班", "合规专员", "理赔专员", "运营专员", "财务专员"],
      form: {
        ticketNo: "",
        ticketType: "投诉",
        customerNo: "",
        contactName: "",
        phone: "",
        policyNo: "",
        category: "",
        subject: "",
        content: "",
        status: "待受理",
        handler: "",
        resolutionNote: "",
        startDate: "",
        endDate: "",
      },
      editRules: {
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
    };
  },
  computed: {
    isLocked() {
      return this.dialogMode === "edit";
    },
    activeRules() {
      if (this.dialogMode === "edit") return this.editRules;
      return {
        ticketType: [{ required: true, message: "请选择类型", trigger: "change" }],
        customerNo: [{ required: true, message: "请选择客户", trigger: "change" }],
        contactName: [
          { required: true, message: "请输入联系人", trigger: "blur" },
          { min: 2, max: 64, message: "联系人长度为 2–64 个字符", trigger: "blur" },
        ],
        phone: [{ validator: this.validatePhoneRule, trigger: "blur" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
        startDate: [{ validator: this.validatePlanRangeRule, trigger: "change" }],
        endDate: [{ validator: this.validatePlanRangeRule, trigger: "change" }],
      };
    },
    policiesForCustomer() {
      const no = (this.form.customerNo || "").trim();
      if (!no) return [];
      const list = Array.isArray(this.policies) ? this.policies : [];
      return list.filter((p) => (p.customerNo || "").trim() === no);
    },
    handlerSelectOptions() {
      const fromTickets = [
        ...new Set(
          (this.tickets || [])
            .map((t) => (t.handler || "").trim())
            .filter(Boolean)
        ),
      ];
      return [...new Set([...this.handlerPresets, ...fromTickets])];
    },
    customerDisplay() {
      const no = this.form.customerNo || "";
      const c = this.customers.find((x) => x.customerNo === no);
      if (c) return `${no}　${c.name}`;
      return no || "—";
    },
    endDatePickerOptions() {
      return {
        disabledDate: (time) => {
          const s = (this.form.startDate || "").trim();
          if (!s) return false;
          const parts = s.split("-").map((x) => parseInt(x, 10));
          if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return false;
          const start = new Date(parts[0], parts[1] - 1, parts[2]);
          start.setHours(0, 0, 0, 0);
          const t = new Date(time);
          t.setHours(0, 0, 0, 0);
          return t.getTime() < start.getTime();
        },
      };
    },
  },
  created() {
    this.fetchTickets();
    this.loadMasters();
  },
  methods: {
    validatePhoneRule(rule, value, callback) {
      const raw = normalizePhoneInput(value);
      if (!raw) return callback();
      const digits = raw.replace(/[^\d]/g, "");
      if (/^1[3-9]\d{9}$/.test(digits)) return callback();
      if (digits.length >= 7 && digits.length <= 12 && /^\d+$/.test(digits)) return callback();
      callback(new Error("请输入合法手机号（11 位）或 7–12 位数字固话"));
    },
    validatePlanRangeRule(rule, value, callback) {
      const s = (this.form.startDate || "").trim();
      const e = (this.form.endDate || "").trim();
      if (!s && !e) return callback();
      if (s && !e) return callback(new Error("请选择计划结束日期"));
      if (!s && e) return callback(new Error("请选择计划开始日期"));
      if (s && e && e < s) return callback(new Error("结束日期不能早于开始日期"));
      callback();
    },
    loadMasters() {
      this.customersLoading = true;
      getCustomers()
        .then((res) => {
          this.customers = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.customers = [];
        })
        .finally(() => {
          this.customersLoading = false;
        });
      this.policiesLoading = true;
      getPolicies()
        .then((res) => {
          this.policies = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.policies = [];
        })
        .finally(() => {
          this.policiesLoading = false;
        });
    },
    fetchTickets() {
      this.error = "";
      this.loading = true;
      getServiceTickets()
        .then((res) => {
          this.tickets = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取工单列表失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    onCustomerChange() {
      if (this.isLocked) return;
      const no = (this.form.customerNo || "").trim();
      this.form.policyNo = "";
      const c = this.customers.find((x) => x.customerNo === no);
      if (c) {
        this.form.contactName = c.name || "";
        this.form.phone = c.phone || "";
      } else {
        this.form.contactName = "";
        this.form.phone = "";
      }
      this.$nextTick(() => {
        if (this.$refs.ticketForm) {
          this.$refs.ticketForm.validateField("customerNo");
        }
      });
    },
    onPlanStartChange() {
      const s = (this.form.startDate || "").trim();
      const e = (this.form.endDate || "").trim();
      if (s && e && e < s) this.form.endDate = "";
      this.$nextTick(() => {
        if (this.$refs.ticketForm) {
          this.$refs.ticketForm.validateField("startDate");
          this.$refs.ticketForm.validateField("endDate");
        }
      });
    },
    onPlanEndChange() {
      this.$nextTick(() => {
        if (this.$refs.ticketForm) {
          this.$refs.ticketForm.validateField("startDate");
          this.$refs.ticketForm.validateField("endDate");
        }
      });
    },
    emptyForm() {
      return {
        ticketNo: "",
        ticketType: "投诉",
        customerNo: "",
        contactName: "",
        phone: "",
        policyNo: "",
        category: "",
        subject: "",
        content: "",
        status: "待受理",
        handler: "",
        resolutionNote: "",
        startDate: "",
        endDate: "",
      };
    },
    resetForm() {
      this.editingId = null;
      this.form = this.emptyForm();
      this.$nextTick(() => {
        if (this.$refs.ticketForm) this.$refs.ticketForm.clearValidate();
      });
    },
    onDialogClosed() {
      this.resetForm();
    },
    openAddDialog() {
      this.dialogMode = "add";
      this.editingId = null;
      this.form = this.emptyForm();
      this.loadMasters();
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.ticketForm) this.$refs.ticketForm.clearValidate();
      });
    },
    openEditDialog(row) {
      this.dialogMode = "edit";
      this.editingId = row.id;
      this.form = {
        ticketNo: row.ticketNo || "",
        ticketType: row.ticketType || "投诉",
        customerNo: row.customerNo || "",
        contactName: row.contactName || "",
        phone: row.phone || "",
        policyNo: row.policyNo || "",
        category: row.category || "",
        subject: row.subject || "",
        content: row.content || "",
        status: row.status || "待受理",
        handler: row.handler || "",
        resolutionNote: row.resolutionNote || "",
        startDate: row.startDate || "",
        endDate: row.endDate || "",
      };
      this.loadMasters();
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.ticketForm) this.$refs.ticketForm.clearValidate();
      });
    },
    submitDialog() {
      this.$refs.ticketForm.validate((valid) => {
        if (!valid) return;
        this.submitting = true;
        const done = () => {
          this.submitting = false;
        };
        if (this.editingId) {
          updateServiceTicket(this.editingId, {
            status: this.form.status,
            handler: this.form.handler,
            resolutionNote: this.form.resolutionNote,
          })
            .then(() => {
              this.$message.success("保存成功");
              this.dialogVisible = false;
              this.fetchTickets();
            })
            .catch((err) => {
              this.$message.error("更新失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        } else {
          const { ticketNo, ...body } = this.form;
          createServiceTicket(body)
            .then(() => {
              this.$message.success("新增成功");
              this.dialogVisible = false;
              this.fetchTickets();
            })
            .catch((err) => {
              const d = err.response?.data?.detail;
              const msg = Array.isArray(d)
                ? d.map((x) => x.msg || x).join("；")
                : d || err.message;
              this.$message.error("新增失败：" + msg);
            })
            .finally(done);
        }
      });
    },
    removeRow(row) {
      this.$confirm(`确定删除工单：${row.ticketNo}？`, "提示", { type: "warning" })
        .then(() => deleteServiceTicket(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchTickets();
        })
        .catch((err) => {
          if (err === "cancel" || err === "close") return;
          this.$message.error("删除失败：" + (err.response?.data?.detail || err.message));
        });
    },
  },
};
</script>

<style scoped>
.list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.list-head h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
.table-error {
  font-size: 12px;
  color: #f56c6c;
  margin-top: 8px;
}
.dialog-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0 16px;
}
.field-hint {
  margin: -4px 0 12px;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}
</style>
