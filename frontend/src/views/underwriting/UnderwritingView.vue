<template>
  <div class="page">
    <h1 class="page-title">承保管理</h1>
    <p class="page-subtitle">
      投保申请受理与核保记录；投保单号由后端生成。新建时须选择已建档客户，姓名与证件号来自客户主数据；关联保单号仅在「已通过 / 自动通过」状态下可填。编辑时不可修改客户、产品与申请金额等建档信息。
    </p>

    <div class="card">
      <div class="list-head">
        <h2>承保案件列表</h2>
        <el-button type="primary" size="small" @click="openAddDialog">新增案件</el-button>
      </div>

      <el-table
        class="module-table"
        :data="cases"
        border
        size="small"
        style="width: 100%;"
        v-loading="loading"
      >
        <el-table-column prop="caseNo" label="投保单号" width="130" />
        <el-table-column prop="applicantName" label="投保人" width="90" />
        <el-table-column prop="customerNo" label="客户编号" width="110" />
        <el-table-column prop="productName" label="投保产品" min-width="120" />
        <el-table-column prop="premium" label="保费" width="80" />
        <el-table-column prop="status" label="状态" width="110" />
        <el-table-column prop="riskScore" label="风险" width="60" />
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
      :title="dialogMode === 'add' ? '新增承保案件' : '编辑承保案件'"
      :visible.sync="dialogVisible"
      width="720px"
      destroy-on-close
      @closed="onDialogClosed"
    >
      <el-form ref="uwForm" :model="form" :rules="activeRules" label-width="120px" size="small" class="dialog-form">
        <el-form-item v-if="dialogMode === 'edit'" label="投保单号">
          <el-input :value="form.caseNo" disabled />
        </el-form-item>

        <el-form-item label="客户编号" prop="customerNo">
          <el-select
            v-if="isAdd"
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
          <el-input v-else :value="form.customerNo" disabled />
        </el-form-item>

        <el-form-item label="投保人">
          <el-input :value="form.applicantName || '—'" disabled placeholder="选择客户后自动带出" />
        </el-form-item>

        <el-form-item label="证件号">
          <el-input :value="form.idNo || '—'" disabled placeholder="来自客户档案" />
        </el-form-item>

        <el-form-item label="投保产品" prop="productName">
          <el-select
            v-if="isAdd"
            v-model="form.productName"
            filterable
            clearable
            allow-create
            default-first-option
            placeholder="请选择或输入产品名称"
            style="width: 100%;"
            :loading="productsLoading"
          >
            <el-option v-for="name in productNameOptions" :key="name" :label="name" :value="name" />
          </el-select>
          <el-input v-else :value="form.productName" disabled />
        </el-form-item>

        <el-form-item label="申请保费" prop="premium">
          <el-input-number
            v-if="isAdd"
            v-model="form.premium"
            :min="0"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 100%;"
          />
          <el-input v-else :value="String(form.premium)" disabled />
        </el-form-item>

        <el-form-item label="申请保额" prop="coverageAmount">
          <el-input-number
            v-if="isAdd"
            v-model="form.coverageAmount"
            :min="0"
            :precision="2"
            :step="1000"
            controls-position="right"
            style="width: 100%;"
          />
          <el-input v-else :value="String(form.coverageAmount)" disabled />
        </el-form-item>

        <el-form-item label="渠道" prop="channel">
          <el-input v-model="form.channel" placeholder="如 线上直销" clearable />
        </el-form-item>

        <el-form-item v-if="isAdd" label="案件状态">
          <el-input value="待受理" disabled />
          <p class="field-hint">新单受理后固定为「待受理」，后续在编辑中推进核保状态。</p>
        </el-form-item>
        <el-form-item v-else label="案件状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择" style="width: 100%;">
            <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>

        <el-form-item label="风险分" prop="riskScore">
          <el-input
            v-model="form.riskScore"
            :disabled="isAdd"
            placeholder="如 低 / 中 / 高"
            clearable
          />
          <p v-if="isAdd" class="field-hint">受理阶段不评定；立案后由核保在编辑中填写。</p>
        </el-form-item>

        <el-form-item label="关联保单号" prop="policyNo">
          <el-input
            v-model="form.policyNo"
            :disabled="!policyNoEditable"
            :placeholder="policyNoPlaceholder"
            clearable
          />
          <p v-if="!policyNoEditable && !isAdd" class="field-hint">
            仅当状态为「已通过」或「自动通过」时可填写已签发保单号。
          </p>
          <p v-if="isAdd" class="field-hint">通过后方可关联保单，受理时不可填。</p>
        </el-form-item>

        <el-form-item :label="remarkLabel" prop="decisionNote">
          <el-input
            v-model="form.decisionNote"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            :placeholder="remarkPlaceholder"
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
  createUnderwritingCase,
  deleteUnderwritingCase,
  getCustomers,
  getProducts,
  getUnderwritingCases,
  updateUnderwritingCase,
} from "@/api";

const POLICY_ALLOWED_STATUSES = ["已通过", "自动通过"];

export default {
  name: "UnderwritingView",
  data() {
    return {
      cases: [],
      customers: [],
      products: [],
      loading: false,
      customersLoading: false,
      productsLoading: false,
      error: "",
      dialogVisible: false,
      dialogMode: "add",
      editingId: null,
      submitting: false,
      statusOptions: [
        "待受理",
        "核保中",
        "自动通过",
        "待人工核保",
        "已通过",
        "已拒保",
        "待补充材料",
      ],
      form: {
        caseNo: "",
        customerNo: "",
        applicantName: "",
        idNo: "",
        productName: "",
        premium: 0,
        coverageAmount: 0,
        channel: "",
        status: "待受理",
        riskScore: "",
        decisionNote: "",
        policyNo: "",
      },
      addRules: {
        customerNo: [{ required: true, message: "请选择客户", trigger: "change" }],
        productName: [{ required: true, message: "请选择投保产品", trigger: "change" }],
      },
      editRules: {
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
    };
  },
  computed: {
    isAdd() {
      return this.dialogMode === "add";
    },
    activeRules() {
      return this.isAdd ? this.addRules : this.editRules;
    },
    productNameOptions() {
      const set = new Set();
      this.products.forEach((p) => {
        if (p.productName) set.add(p.productName);
      });
      return Array.from(set).sort();
    },
    policyNoEditable() {
      if (this.isAdd) return false;
      return POLICY_ALLOWED_STATUSES.includes(this.form.status);
    },
    policyNoPlaceholder() {
      if (this.isAdd) return "受理阶段不可填写";
      if (this.policyNoEditable) return "填写已签发保单号";
      return "请先将状态调整为「已通过」或「自动通过」";
    },
    remarkLabel() {
      return this.isAdd ? "受理备注" : "核保备注";
    },
    remarkPlaceholder() {
      return this.isAdd ? "受理说明（可选）" : "核保结论与说明";
    },
  },
  created() {
    this.fetchCases();
    this.fetchCustomers();
    this.fetchProducts();
  },
  methods: {
    fetchCustomers() {
      this.customersLoading = true;
      getCustomers()
        .then((res) => {
          this.customers = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.$message.warning("加载客户列表失败，将无法选择客户建档信息");
        })
        .finally(() => {
          this.customersLoading = false;
        });
    },
    fetchProducts() {
      this.productsLoading = true;
      getProducts()
        .then((res) => {
          this.products = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.$message.warning("加载产品列表失败");
        })
        .finally(() => {
          this.productsLoading = false;
        });
    },
    fetchCases() {
      this.error = "";
      this.loading = true;
      getUnderwritingCases()
        .then((res) => {
          this.cases = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取承保案件失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    parseNum(v) {
      const n = Number(v);
      return Number.isFinite(n) ? n : 0;
    },
    emptyForm() {
      return {
        caseNo: "",
        customerNo: "",
        applicantName: "",
        idNo: "",
        productName: "",
        premium: 0,
        coverageAmount: 0,
        channel: "",
        status: "待受理",
        riskScore: "",
        decisionNote: "",
        policyNo: "",
      };
    },
    resetForm() {
      this.editingId = null;
      this.form = this.emptyForm();
      this.$nextTick(() => {
        if (this.$refs.uwForm) this.$refs.uwForm.clearValidate();
      });
    },
    onDialogClosed() {
      this.resetForm();
    },
    applyCustomerByNo(customerNo) {
      const c = this.customers.find((x) => x.customerNo === customerNo);
      if (c) {
        this.form.applicantName = c.name || "";
        this.form.idNo = c.idNo || "";
      } else {
        this.form.applicantName = "";
        this.form.idNo = "";
      }
    },
    onCustomerChange(val) {
      this.applyCustomerByNo(val);
    },
    openAddDialog() {
      if (!this.customers.length && !this.customersLoading) this.fetchCustomers();
      if (!this.products.length && !this.productsLoading) this.fetchProducts();
      this.dialogMode = "add";
      this.editingId = null;
      this.form = this.emptyForm();
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.uwForm) this.$refs.uwForm.clearValidate();
      });
    },
    openEditDialog(row) {
      this.dialogMode = "edit";
      this.editingId = row.id;
      this.form = {
        caseNo: row.caseNo || "",
        customerNo: row.customerNo || "",
        applicantName: row.applicantName || "",
        idNo: row.idNo || "",
        productName: row.productName || "",
        premium: this.parseNum(row.premium),
        coverageAmount: this.parseNum(row.coverageAmount),
        channel: row.channel || "",
        status: row.status || "待受理",
        riskScore: row.riskScore || "",
        decisionNote: row.decisionNote || "",
        policyNo: row.policyNo || "",
      };
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.uwForm) this.$refs.uwForm.clearValidate();
      });
    },
    payloadForCreate() {
      return {
        customerNo: this.form.customerNo,
        productName: this.form.productName,
        premium: String(this.form.premium ?? 0),
        coverageAmount: String(this.form.coverageAmount ?? 0),
        channel: this.form.channel || "",
        decisionNote: this.form.decisionNote || "",
      };
    },
    payloadForUpdate() {
      return {
        channel: this.form.channel || "",
        status: this.form.status,
        riskScore: this.form.riskScore || "",
        decisionNote: this.form.decisionNote || "",
        policyNo: this.form.policyNo || "",
      };
    },
    submitDialog() {
      this.$refs.uwForm.validate((valid) => {
        if (!valid) return;
        this.submitting = true;
        const done = () => {
          this.submitting = false;
        };
        if (this.editingId) {
          updateUnderwritingCase(this.editingId, this.payloadForUpdate())
            .then(() => {
              this.$message.success("保存成功");
              this.dialogVisible = false;
              this.fetchCases();
            })
            .catch((err) => {
              this.$message.error("更新失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        } else {
          createUnderwritingCase(this.payloadForCreate())
            .then(() => {
              this.$message.success("新增成功");
              this.dialogVisible = false;
              this.fetchCases();
            })
            .catch((err) => {
              this.$message.error("新增失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        }
      });
    },
    removeRow(row) {
      this.$confirm(`确定删除案件：${row.caseNo}？`, "提示", { type: "warning" })
        .then(() => deleteUnderwritingCase(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchCases();
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
.field-hint {
  margin: 6px 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.45;
}
</style>
