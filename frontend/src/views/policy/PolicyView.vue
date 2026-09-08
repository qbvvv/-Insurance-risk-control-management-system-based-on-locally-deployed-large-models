<template>
  <div class="page">
    <h1 class="page-title">保单管理</h1>
    <p class="page-subtitle">维护保单基础信息；新增时保单号由后端自动生成，客户与产品从主数据下拉选择。</p>

    <div class="card">
      <div class="list-head">
        <h2>保单列表</h2>
        <el-button type="primary" size="small" @click="openAddDialog">新增保单</el-button>
      </div>

      <el-table
        class="module-table"
        :data="policies"
        border
        size="small"
        style="width: 100%;"
        v-loading="loading"
      >
        <el-table-column prop="policyNo" label="保单号" width="140" />
        <el-table-column prop="customerNo" label="客户编号" width="120" />
        <el-table-column prop="productName" label="产品名称" />
        <el-table-column prop="premium" label="保费" width="100" />
        <el-table-column prop="coverageAmount" label="保额" width="120" />
        <el-table-column prop="startDate" label="起保日期" width="110" />
        <el-table-column prop="endDate" label="止保日期" width="110" />
        <el-table-column prop="status" label="状态" width="90" />
        <el-table-column label="操作" width="168" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="module-table-ops">
              <el-button type="primary" size="mini" @click="openEditDialog(scope.row)">编辑</el-button>
              <el-button type="danger" size="mini" @click="removePolicy(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <p v-if="error" class="table-error">{{ error }}</p>
    </div>

    <el-dialog
      :title="dialogMode === 'add' ? '新增保单' : '编辑保单'"
      :visible.sync="dialogVisible"
      width="720px"
      destroy-on-close
      @closed="onDialogClosed"
    >
      <el-form ref="policyForm" :model="form" :rules="dialogRules" label-width="100px" size="small" class="dialog-form">
        <el-form-item v-if="dialogMode === 'add'" label="保单号">
          <el-input disabled placeholder="保存后由系统自动生成" />
        </el-form-item>
        <el-form-item v-else label="保单号" prop="policyNo">
          <el-input v-model="form.policyNo" disabled />
        </el-form-item>
        <el-form-item label="客户编号" prop="customerNo">
          <el-select
            v-model="form.customerNo"
            filterable
            clearable
            placeholder="请选择客户"
            style="width: 100%;"
          >
            <el-option
              v-for="opt in customerOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="产品名称" prop="productName">
          <el-select
            v-model="form.productName"
            filterable
            clearable
            placeholder="请选择产品"
            style="width: 100%;"
          >
            <el-option
              v-for="opt in productNameOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="保费" prop="premium">
          <el-input-number
            v-model="premiumNumber"
            :min="0"
            :max="1e12"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="保额" prop="coverageAmount">
          <el-input-number
            v-model="coverageNumber"
            :min="0"
            :max="1e13"
            :precision="2"
            :step="10000"
            controls-position="right"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="起保日期" prop="startDate">
          <el-date-picker
            v-model="form.startDate"
            type="date"
            placeholder="选择起保日期"
            value-format="yyyy-MM-dd"
            style="width: 100%;"
            clearable
            @change="onStartDateChange"
          />
        </el-form-item>
        <el-form-item label="止保日期" prop="endDate">
          <el-date-picker
            v-model="form.endDate"
            type="date"
            placeholder="选择止保日期"
            value-format="yyyy-MM-dd"
            style="width: 100%;"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
            <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
          </el-select>
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
import { createPolicy, deletePolicy, getPolicies, updatePolicy, getCustomers, getProducts } from "@/api";

export default {
  name: "PolicyView",
  data() {
    return {
      policies: [],
      customerList: [],
      productList: [],
      loading: false,
      error: "",
      dialogVisible: false,
      dialogMode: "add",
      editingId: null,
      submitting: false,
      premiumNumber: 0,
      coverageNumber: 0,
      statusOptions: ["生效中", "待生效", "已失效", "已退保"],
      form: {
        policyNo: "",
        customerNo: "",
        productName: "",
        premium: "0",
        coverageAmount: "0",
        startDate: "",
        endDate: "",
        status: "生效中",
      },
    };
  },
  computed: {
    customerOptions() {
      return (this.customerList || []).map((c) => ({
        value: c.customerNo,
        label: `${c.customerNo || ""} ${c.name || ""}`.trim(),
      }));
    },
    productNameOptions() {
      const seen = new Set();
      const out = [];
      for (const p of this.productList || []) {
        const n = (p.productName || "").trim();
        if (!n || seen.has(n)) continue;
        seen.add(n);
        out.push({ label: n, value: n });
      }
      return out;
    },
    dialogRules() {
      const r = {
        customerNo: [{ required: true, message: "请选择客户编号", trigger: "change" }],
        productName: [{ required: true, message: "请选择产品名称", trigger: "change" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
        endDate: [{ validator: this.checkEndAfterStart, trigger: "change" }],
      };
      if (this.dialogMode === "edit") {
        r.policyNo = [{ required: true, message: "保单号缺失", trigger: "blur" }];
      }
      return r;
    },
  },
  created() {
    this.fetchPolicies();
    this.loadRefs();
  },
  methods: {
    checkEndAfterStart(rule, value, callback) {
      const start = this.form.startDate;
      if (!value || !start) {
        callback();
        return;
      }
      if (String(value) < String(start)) {
        callback(new Error("止保日期不能早于起保日期"));
        return;
      }
      callback();
    },
    onStartDateChange() {
      this.$nextTick(() => {
        if (this.$refs.policyForm && this.form.endDate) {
          this.$refs.policyForm.validateField("endDate");
        }
      });
    },
    loadRefs() {
      getCustomers()
        .then((res) => {
          this.customerList = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {});
      getProducts()
        .then((res) => {
          this.productList = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {});
    },
    syncNumbersFromForm() {
      const p = parseFloat(String(this.form.premium || "0").replace(/,/g, ""));
      const c = parseFloat(String(this.form.coverageAmount || "0").replace(/,/g, ""));
      this.premiumNumber = Number.isFinite(p) && p >= 0 ? p : 0;
      this.coverageNumber = Number.isFinite(c) && c >= 0 ? c : 0;
    },
    syncFormMoneyFromNumbers() {
      const fmt = (n) => {
        if (n === null || n === undefined || Number.isNaN(n)) return "0";
        return String(Math.round(n * 100) / 100);
      };
      this.form.premium = fmt(this.premiumNumber);
      this.form.coverageAmount = fmt(this.coverageNumber);
    },
    fetchPolicies() {
      this.error = "";
      this.loading = true;
      getPolicies()
        .then((res) => {
          this.policies = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取保单列表失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    emptyForm() {
      return {
        policyNo: "",
        customerNo: "",
        productName: "",
        premium: "0",
        coverageAmount: "0",
        startDate: "",
        endDate: "",
        status: "生效中",
      };
    },
    resetForm() {
      this.editingId = null;
      this.form = this.emptyForm();
      this.premiumNumber = 0;
      this.coverageNumber = 0;
      this.$nextTick(() => {
        if (this.$refs.policyForm) this.$refs.policyForm.clearValidate();
      });
    },
    onDialogClosed() {
      this.resetForm();
    },
    openAddDialog() {
      this.loadRefs();
      this.dialogMode = "add";
      this.editingId = null;
      this.form = this.emptyForm();
      this.premiumNumber = 0;
      this.coverageNumber = 0;
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.policyForm) this.$refs.policyForm.clearValidate();
      });
    },
    openEditDialog(p) {
      this.loadRefs();
      this.dialogMode = "edit";
      this.editingId = p.id;
      this.form = {
        policyNo: p.policyNo || "",
        customerNo: p.customerNo || "",
        productName: p.productName || "",
        premium: p.premium || "0",
        coverageAmount: p.coverageAmount || "0",
        startDate: p.startDate || "",
        endDate: p.endDate || "",
        status: p.status || "生效中",
      };
      this.syncNumbersFromForm();
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.policyForm) this.$refs.policyForm.clearValidate();
      });
    },
    submitDialog() {
      this.syncFormMoneyFromNumbers();
      this.$refs.policyForm.validate((valid) => {
        if (!valid) return;
        this.submitting = true;
        const done = () => {
          this.submitting = false;
        };
        const payload = { ...this.form };
        if (this.dialogMode === "add") {
          delete payload.policyNo;
        }
        if (this.editingId) {
          updatePolicy(this.editingId, payload)
            .then(() => {
              this.$message.success("保存成功");
              this.dialogVisible = false;
              this.fetchPolicies();
            })
            .catch((err) => {
              this.$message.error("更新失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        } else {
          createPolicy(payload)
            .then(() => {
              this.$message.success("新增成功");
              this.dialogVisible = false;
              this.fetchPolicies();
            })
            .catch((err) => {
              this.$message.error("新增失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        }
      });
    },
    removePolicy(p) {
      this.$confirm(`确定删除保单：${p.policyNo}？`, "提示", { type: "warning" })
        .then(() => deletePolicy(p.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchPolicies();
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
</style>
