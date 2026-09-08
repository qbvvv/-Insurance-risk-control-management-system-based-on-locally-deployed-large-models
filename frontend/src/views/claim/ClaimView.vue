<template>
  <div class="page">
    <h1 class="page-title">理赔管理</h1>
    <p class="page-subtitle">
      理赔报案与核赔处理；理赔案件号由后端按当日序号自动生成（CLM + 日期 + 四位序号）。请先选择保单，客户编号与产品名称将随保单联动。
    </p>

    <div class="card" style="margin-bottom: 16px;">
      <h2>新增 / 编辑理赔案件</h2>
      <el-form
        ref="claimForm"
        :model="form"
        :rules="formRules"
        label-width="108px"
        size="small"
        @submit.native.prevent="handleSubmit"
      >
        <el-form-item v-if="editingId" label="理赔案件号">
          <el-input :value="form.claimNo" disabled />
        </el-form-item>
        <el-form-item v-else label="理赔案件号">
          <el-input :value="nextClaimNoPreview" disabled placeholder="保存后由系统自动生成（与列表同步后预览）" />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="保单号" prop="policyNo">
            <el-select
              v-model="form.policyNo"
              filterable
              clearable
              placeholder="请选择保单"
              style="width: 100%;"
              :loading="metaLoading"
              @change="onPolicyChange"
            >
              <el-option
                v-for="p in policyOptions"
                :key="p.policyNo"
                :label="p.label"
                :value="p.policyNo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="客户编号" prop="customerNo">
            <el-select
              v-model="form.customerNo"
              filterable
              clearable
              placeholder="请选择客户"
              style="width: 100%;"
              :loading="metaLoading"
              @change="onCustomerChange"
            >
              <el-option
                v-for="c in customerOptions"
                :key="c.value"
                :label="c.label"
                :value="c.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="索赔人" prop="claimantName">
            <el-input v-model="form.claimantName" placeholder="默认可随客户带出，可改" clearable maxlength="64" show-word-limit />
          </el-form-item>
          <el-form-item label="产品/险种" prop="productName">
            <el-select
              v-model="form.productName"
              filterable
              clearable
              placeholder="请选择产品"
              style="width: 100%;"
              :loading="metaLoading"
            >
              <el-option
                v-for="p in productOptions"
                :key="p.value"
                :label="p.label"
                :value="p.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="理赔类型" prop="claimType">
            <el-select v-model="form.claimType" clearable placeholder="请选择" style="width: 100%;" allow-create filterable>
              <el-option v-for="t in claimTypeOptions" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="出险原因" prop="incidentReason">
            <el-input v-model="form.incidentReason" clearable maxlength="256" show-word-limit placeholder="简要说明" />
          </el-form-item>
          <el-form-item label="出险日期" prop="incidentDate">
            <el-date-picker
              v-model="form.incidentDate"
              type="date"
              placeholder="选择出险日期"
              value-format="yyyy-MM-dd"
              style="width: 100%;"
              clearable
              @change="onIncidentDateChange"
            />
          </el-form-item>
          <el-form-item label="报案日期" prop="reportDate">
            <el-date-picker
              v-model="form.reportDate"
              type="date"
              placeholder="选择报案日期"
              value-format="yyyy-MM-dd"
              style="width: 100%;"
              clearable
            />
          </el-form-item>
          <el-form-item label="申请金额" prop="claimAmount">
            <el-input v-model="form.claimAmount" placeholder="非负数，最多两位小数" clearable />
          </el-form-item>
          <el-form-item label="核定金额" prop="approvedAmount">
            <el-input v-model="form.approvedAmount" placeholder="核赔后填写，可留空" clearable />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择" style="width: 100%;">
              <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="核赔备注" prop="decisionNote">
          <el-input v-model="form.decisionNote" type="textarea" :rows="2" placeholder="审核结论与说明" maxlength="512" show-word-limit />
        </el-form-item>
        <el-form-item class="form-actions-row">
          <el-button type="primary" native-type="submit" :loading="submitting">
            {{ editingId ? "保存修改" : "新增案件" }}
          </el-button>
          <el-button v-if="editingId" @click="resetForm">取消编辑</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <h2>理赔案件列表</h2>
      <el-table class="module-table" :data="claims" border size="small" style="width: 100%;" v-loading="listLoading">
        <el-table-column prop="claimNo" label="案件号" width="140" />
        <el-table-column prop="policyNo" label="保单号" width="120" />
        <el-table-column prop="claimantName" label="索赔人" width="90" />
        <el-table-column prop="productName" label="产品" min-width="120" />
        <el-table-column prop="claimAmount" label="申请金额" width="90" />
        <el-table-column prop="approvedAmount" label="核定金额" width="90" />
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="168" align="center">
          <template slot-scope="scope">
            <div class="module-table-ops">
              <el-button type="primary" size="mini" @click="editRow(scope.row)">编辑</el-button>
              <el-button type="danger" size="mini" @click="removeRow(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <p v-if="error" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { createClaim, deleteClaim, getClaims, getCustomers, getPolicies, getProducts, updateClaim } from "@/api";

function validateMoney(rule, value, callback) {
  const s = String(value == null ? "" : value).trim();
  if (!s) {
    callback(new Error("请输入金额"));
    return;
  }
  if (!/^\d+(\.\d{1,2})?$/.test(s)) {
    callback(new Error("请输入非负数字，最多两位小数"));
    return;
  }
  const n = Number(s);
  if (n < 0 || n > 1e12) {
    callback(new Error("金额超出合理范围"));
    return;
  }
  callback();
}

function validateOptionalMoney(rule, value, callback) {
  const s = String(value == null ? "" : value).trim();
  if (!s) {
    callback();
    return;
  }
  validateMoney(rule, s, callback);
}

export default {
  name: "ClaimView",
  data() {
    return {
      claims: [],
      policiesRaw: [],
      listLoading: false,
      metaLoading: false,
      error: "",
      editingId: null,
      submitting: false,
      customerOptions: [],
      productOptions: [],
      claimTypeOptions: ["医疗", "财产", "车损", "责任", "意外", "营业中断", "身故", "其他"],
      statusOptions: [
        "待受理",
        "查勘中",
        "审核中",
        "待支付",
        "已支付",
        "已拒赔",
        "已结案",
        "处理中",
        "待调查",
        "待人工核赔",
      ],
      form: {
        claimNo: "",
        policyNo: "",
        customerNo: "",
        claimantName: "",
        productName: "",
        claimType: "",
        incidentReason: "",
        incidentDate: "",
        reportDate: "",
        claimAmount: "0",
        approvedAmount: "",
        status: "待受理",
        decisionNote: "",
      },
      customerByNo: {},
    };
  },
  computed: {
    policyOptions() {
      return (this.policiesRaw || []).map((p) => ({
        policyNo: p.policyNo,
        label: `${p.policyNo} · ${p.customerNo || ""} · ${p.productName || ""}`,
      }));
    },
    nextClaimNoPreview() {
      const d = new Date();
      const pad = (n) => String(n).padStart(2, "0");
      const ds = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
      const prefix = `CLM${ds}`;
      const n = (this.claims || []).filter((c) => String(c.claimNo || "").startsWith(prefix)).length;
      return `${prefix}${String(n + 1).padStart(4, "0")}`;
    },
    formRules() {
      return {
        policyNo: [{ required: true, message: "请选择保单号", trigger: "change" }],
        customerNo: [{ required: true, message: "请选择客户编号", trigger: "change" }],
        claimantName: [{ required: true, message: "请输入索赔人", trigger: "blur" }],
        productName: [{ required: true, message: "请选择产品名称", trigger: "change" }],
        claimAmount: [{ validator: validateMoney, trigger: "blur" }],
        approvedAmount: [{ validator: validateOptionalMoney, trigger: "blur" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
        reportDate: [{ validator: this.validateReportDate, trigger: "change" }],
      };
    },
  },
  created() {
    this.fetchClaims();
    this.loadMetaOptions();
  },
  methods: {
    validateReportDate(rule, value, callback) {
      const rep = value;
      const inc = this.form.incidentDate;
      if (rep && inc && rep < inc) {
        callback(new Error("报案日期不能早于出险日期"));
        return;
      }
      callback();
    },
    onIncidentDateChange() {
      this.$nextTick(() => {
        if (this.$refs.claimForm) this.$refs.claimForm.validateField("reportDate");
      });
    },
    onPolicyChange(policyNo) {
      if (!policyNo) return;
      const p = (this.policiesRaw || []).find((x) => x.policyNo === policyNo);
      if (!p) return;
      this.form.customerNo = p.customerNo || "";
      this.form.productName = p.productName || "";
      const cust = this.customerByNo[this.form.customerNo];
      if (cust && cust.name && !this.form.claimantName) {
        this.form.claimantName = cust.name;
      }
    },
    onCustomerChange(customerNo) {
      const cust = this.customerByNo[customerNo];
      if (cust && cust.name && !this.form.claimantName) {
        this.form.claimantName = cust.name;
      }
    },
    loadMetaOptions() {
      this.metaLoading = true;
      Promise.all([getPolicies(), getCustomers(), getProducts()])
        .then(([pr, cr, prodR]) => {
          this.policiesRaw = Array.isArray(pr.data) ? pr.data : [];
          const customers = Array.isArray(cr.data) ? cr.data : [];
          const products = Array.isArray(prodR.data) ? prodR.data : [];
          this.customerByNo = {};
          this.customerOptions = customers.map((c) => {
            const no = c.customerNo;
            this.customerByNo[no] = c;
            return { value: no, label: `${no} · ${c.name || ""}` };
          });
          const names = new Set();
          this.productOptions = [];
          for (const p of products) {
            const name = (p.productName || "").trim();
            if (!name || names.has(name)) continue;
            names.add(name);
            this.productOptions.push({ value: name, label: name });
          }
        })
        .catch(() => {
          this.$message.warning("保单/客户/产品列表加载失败，下拉可能为空");
        })
        .finally(() => {
          this.metaLoading = false;
        });
    },
    fetchClaims() {
      this.error = "";
      this.listLoading = true;
      getClaims()
        .then((res) => {
          this.claims = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取理赔列表失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.listLoading = false;
        });
    },
    resetForm() {
      this.editingId = null;
      this.form = {
        claimNo: "",
        policyNo: "",
        customerNo: "",
        claimantName: "",
        productName: "",
        claimType: "",
        incidentReason: "",
        incidentDate: "",
        reportDate: "",
        claimAmount: "0",
        approvedAmount: "",
        status: "待受理",
        decisionNote: "",
      };
      this.$nextTick(() => {
        if (this.$refs.claimForm) this.$refs.claimForm.clearValidate();
      });
    },
    handleSubmit() {
      this.$refs.claimForm.validate((valid) => {
        if (!valid) return;
        const pol = (this.policiesRaw || []).find((x) => x.policyNo === this.form.policyNo);
        if (pol) {
          if (pol.customerNo) this.form.customerNo = pol.customerNo;
          if (pol.productName) this.form.productName = pol.productName;
        }
        this.submitting = true;
        const done = () => {
          this.submitting = false;
        };
        if (this.editingId) {
          const { claimNo, ...patch } = this.form;
          updateClaim(this.editingId, patch)
            .then(() => {
              this.$message.success("保存成功");
              this.fetchClaims();
              this.resetForm();
            })
            .catch((err) => {
              this.$message.error("更新失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        } else {
          const { claimNo, ...body } = this.form;
          createClaim(body)
            .then((res) => {
              const no = res.data && res.data.claimNo;
              this.$message.success(no ? `新增成功，案件号：${no}` : "新增成功");
              this.fetchClaims();
              this.loadMetaOptions();
              this.resetForm();
            })
            .catch((err) => {
              this.$message.error("新增失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        }
      });
    },
    editRow(row) {
      this.editingId = row.id;
      this.form = {
        claimNo: row.claimNo || "",
        policyNo: row.policyNo || "",
        customerNo: row.customerNo || "",
        claimantName: row.claimantName || "",
        productName: row.productName || "",
        claimType: row.claimType || "",
        incidentReason: row.incidentReason || "",
        incidentDate: row.incidentDate || "",
        reportDate: row.reportDate || "",
        claimAmount: row.claimAmount || "0",
        approvedAmount: row.approvedAmount || "",
        status: row.status || "待受理",
        decisionNote: row.decisionNote || "",
      };
      this.loadMetaOptions();
      this.$nextTick(() => {
        if (this.$refs.claimForm) this.$refs.claimForm.clearValidate();
      });
    },
    removeRow(row) {
      this.$confirm(`确定删除理赔案件：${row.claimNo}？`, "提示", { type: "warning" })
        .then(() => deleteClaim(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchClaims();
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
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0 16px;
}
.form-actions-row {
  margin-bottom: 0;
}
.form-actions-row :deep(.el-form-item__content) {
  margin-left: 108px !important;
}
</style>
