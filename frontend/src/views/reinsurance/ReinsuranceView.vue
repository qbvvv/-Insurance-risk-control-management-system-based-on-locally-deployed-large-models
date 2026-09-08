<template>
  <div class="page">
    <h1 class="page-title">再保管理</h1>
    <p class="page-subtitle">
      再保合同与分出/分入账单；合同号、账单号可由后端生成（RC/RB + 日期 + 序号），也可在新增时手工指定唯一编号。金额单位为万元。
    </p>

    <div class="grid grid-2 reinsurance-grid">
      <div class="card">
        <h2>再保合同</h2>
        <el-form
          ref="rcForm"
          :model="rcForm"
          :rules="rcRules"
          label-width="100px"
          size="small"
          class="mini-form"
          @submit.native.prevent="submitContract"
        >
          <el-form-item v-if="rcEditingId" label="合同编号">
            <el-input :value="rcForm.contractNo" disabled />
          </el-form-item>
          <el-form-item label="再保类型" prop="contractType">
            <el-select v-model="rcForm.contractType" style="width: 100%;" filterable allow-create default-first-option>
              <el-option v-for="t in contractTypeOptions" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="原保险人" prop="cedent">
            <el-input v-model="rcForm.cedent" clearable />
          </el-form-item>
          <el-form-item label="再保险人" prop="reinsurer">
            <el-input v-model="rcForm.reinsurer" clearable />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="rcForm.status" style="width: 100%;">
              <el-option v-for="s in contractStatusOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="备注" prop="remark">
            <el-input v-model="rcForm.remark" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="rcSubmitting">
              {{ rcEditingId ? "保存" : "新增合同" }}
            </el-button>
            <el-button v-if="rcEditingId" @click="resetRcForm">取消</el-button>
          </el-form-item>
        </el-form>
        <el-table
          class="module-table"
          :data="contractRows"
          border
          size="small"
          style="width: 100%;"
          v-loading="rcLoading"
        >
          <el-table-column prop="contractNo" label="合同编号" min-width="130" show-overflow-tooltip />
          <el-table-column prop="contractType" label="再保类型" min-width="120" show-overflow-tooltip />
          <el-table-column prop="cedent" label="原保险人" min-width="120" show-overflow-tooltip />
          <el-table-column prop="reinsurer" label="再保险人" min-width="140" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" min-width="90" show-overflow-tooltip />
          <el-table-column label="操作" width="168" align="center">
            <template slot-scope="scope">
              <div class="module-table-ops">
                <el-button type="primary" size="mini" @click="editRc(scope.row)">编辑</el-button>
                <el-button type="danger" size="mini" @click="removeRc(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <p v-if="rcError" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ rcError }}</p>
      </div>

      <div class="card">
        <h2>分出 / 分入与再保账单</h2>
        <el-form
          ref="rbForm"
          :model="rbForm"
          :rules="rbRules"
          label-width="120px"
          size="small"
          class="mini-form"
          @submit.native.prevent="submitBill"
        >
          <el-form-item v-if="rbEditingId" label="账单号">
            <el-input :value="rbForm.billNo" disabled />
          </el-form-item>
          <el-form-item label="业务类型" prop="kind">
            <el-select v-model="rbForm.kind" style="width: 100%;">
              <el-option v-for="k in billKindOptions" :key="k" :label="k" :value="k" />
            </el-select>
          </el-form-item>
          <el-form-item label="账期" prop="period">
            <el-input v-model="rbForm.period" placeholder="如 2026Q1" clearable />
          </el-form-item>
          <el-form-item label="保费（万元）" prop="premium">
            <el-input v-model="rbForm.premium" clearable />
          </el-form-item>
          <el-form-item label="摊回赔款（万元）" prop="claimRecover">
            <el-input v-model="rbForm.claimRecover" clearable />
          </el-form-item>
          <el-form-item label="备注" prop="remark">
            <el-input v-model="rbForm.remark" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" native-type="submit" :loading="rbSubmitting">
              {{ rbEditingId ? "保存" : "新增账单" }}
            </el-button>
            <el-button v-if="rbEditingId" @click="resetRbForm">取消</el-button>
          </el-form-item>
        </el-form>
        <el-table
          class="module-table"
          :data="billRows"
          border
          size="small"
          style="width: 100%;"
          v-loading="rbLoading"
        >
          <el-table-column prop="kind" label="业务类型" min-width="100" show-overflow-tooltip />
          <el-table-column prop="period" label="账期" min-width="120" show-overflow-tooltip />
          <el-table-column prop="premium" label="保费（万元）" min-width="130" show-overflow-tooltip />
          <el-table-column prop="claimRecover" label="摊回赔款（万元）" min-width="150" show-overflow-tooltip />
          <el-table-column label="操作" width="168" align="center">
            <template slot-scope="scope">
              <div class="module-table-ops">
                <el-button type="primary" size="mini" @click="editRb(scope.row)">编辑</el-button>
                <el-button type="danger" size="mini" @click="removeRb(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <p v-if="rbError" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ rbError }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import {
  createReinsuranceBill,
  createReinsuranceContract,
  deleteReinsuranceBill,
  deleteReinsuranceContract,
  getReinsuranceBills,
  getReinsuranceContracts,
  updateReinsuranceBill,
  updateReinsuranceContract,
} from "@/api";

export default {
  name: "ReinsuranceView",
  data() {
    return {
      contractRows: [],
      billRows: [],
      rcLoading: false,
      rbLoading: false,
      rcError: "",
      rbError: "",
      rcEditingId: null,
      rbEditingId: null,
      rcSubmitting: false,
      rbSubmitting: false,
      contractTypeOptions: ["比例再保", "溢额再保", "超赔再保", "临时分保", "其他"],
      contractStatusOptions: ["生效", "待生效", "已终止"],
      billKindOptions: ["分出", "分入"],
      rcForm: {
        contractNo: "",
        contractType: "比例再保",
        cedent: "本公司",
        reinsurer: "",
        status: "生效",
        remark: "",
      },
      rbForm: {
        billNo: "",
        kind: "分出",
        period: "",
        premium: "0",
        claimRecover: "0",
        remark: "",
      },
      rcRules: {
        contractType: [{ required: true, message: "请选择或填写再保类型", trigger: "change" }],
        cedent: [{ required: true, message: "请输入原保险人", trigger: "blur" }],
        reinsurer: [{ required: true, message: "请输入再保险人", trigger: "blur" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
      rbRules: {
        kind: [{ required: true, message: "请选择业务类型", trigger: "change" }],
        period: [{ required: true, message: "请输入账期", trigger: "blur" }],
        premium: [{ required: true, message: "请输入保费", trigger: "blur" }],
        claimRecover: [{ required: true, message: "请输入摊回赔款", trigger: "blur" }],
      },
    };
  },
  created() {
    this.fetchContracts();
    this.fetchBills();
  },
  methods: {
    fetchContracts() {
      this.rcError = "";
      this.rcLoading = true;
      getReinsuranceContracts()
        .then((res) => {
          this.contractRows = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.rcError = "加载再保合同失败，请确认后端已启动（uvicorn api.server:app --reload）。";
        })
        .finally(() => {
          this.rcLoading = false;
        });
    },
    fetchBills() {
      this.rbError = "";
      this.rbLoading = true;
      getReinsuranceBills()
        .then((res) => {
          this.billRows = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.rbError = "加载再保账单失败，请确认后端已启动（uvicorn api.server:app --reload）。";
        })
        .finally(() => {
          this.rbLoading = false;
        });
    },
    resetRcForm() {
      this.rcEditingId = null;
      this.rcForm = {
        contractNo: "",
        contractType: "比例再保",
        cedent: "本公司",
        reinsurer: "",
        status: "生效",
        remark: "",
      };
      this.$nextTick(() => {
        if (this.$refs.rcForm) this.$refs.rcForm.clearValidate();
      });
    },
    resetRbForm() {
      this.rbEditingId = null;
      this.rbForm = {
        billNo: "",
        kind: "分出",
        period: "",
        premium: "0",
        claimRecover: "0",
        remark: "",
      };
      this.$nextTick(() => {
        if (this.$refs.rbForm) this.$refs.rbForm.clearValidate();
      });
    },
    submitContract() {
      this.$refs.rcForm.validate((valid) => {
        if (!valid) return;
        this.rcSubmitting = true;
        const done = () => {
          this.rcSubmitting = false;
        };
        if (this.rcEditingId) {
          const { contractNo, ...patch } = this.rcForm;
          updateReinsuranceContract(this.rcEditingId, patch)
            .then(() => {
              this.$message.success("已保存");
              this.fetchContracts();
              this.resetRcForm();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        } else {
          const body = { ...this.rcForm };
          delete body.contractNo;
          createReinsuranceContract(body)
            .then(() => {
              this.$message.success("已新增");
              this.fetchContracts();
              this.resetRcForm();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        }
      });
    },
    submitBill() {
      this.$refs.rbForm.validate((valid) => {
        if (!valid) return;
        this.rbSubmitting = true;
        const done = () => {
          this.rbSubmitting = false;
        };
        if (this.rbEditingId) {
          const { billNo, ...patch } = this.rbForm;
          updateReinsuranceBill(this.rbEditingId, patch)
            .then(() => {
              this.$message.success("已保存");
              this.fetchBills();
              this.resetRbForm();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        } else {
          const body = { ...this.rbForm };
          delete body.billNo;
          createReinsuranceBill(body)
            .then(() => {
              this.$message.success("已新增");
              this.fetchBills();
              this.resetRbForm();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        }
      });
    },
    editRc(row) {
      this.rcEditingId = row.id;
      this.rcForm = {
        contractNo: row.contractNo || "",
        contractType: row.contractType || "比例再保",
        cedent: row.cedent || "",
        reinsurer: row.reinsurer || "",
        status: row.status || "生效",
        remark: row.remark || "",
      };
      this.$nextTick(() => this.$refs.rcForm && this.$refs.rcForm.clearValidate());
    },
    removeRc(row) {
      this.$confirm(`删除合同 ${row.contractNo}？`, "提示", { type: "warning" })
        .then(() => deleteReinsuranceContract(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchContracts();
        })
        .catch((e) => {
          if (e === "cancel" || e === "close") return;
          this.$message.error(e.response?.data?.detail || e.message);
        });
    },
    editRb(row) {
      this.rbEditingId = row.id;
      this.rbForm = {
        billNo: row.billNo || "",
        kind: row.kind || "分出",
        period: row.period || "",
        premium: row.premium != null ? String(row.premium) : "0",
        claimRecover: row.claimRecover != null ? String(row.claimRecover) : "0",
        remark: row.remark || "",
      };
      this.$nextTick(() => this.$refs.rbForm && this.$refs.rbForm.clearValidate());
    },
    removeRb(row) {
      this.$confirm(`删除账单 ${row.billNo}？`, "提示", { type: "warning" })
        .then(() => deleteReinsuranceBill(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchBills();
        })
        .catch((e) => {
          if (e === "cancel" || e === "close") return;
          this.$message.error(e.response?.data?.detail || e.message);
        });
    },
  },
};
</script>

<style scoped>
.reinsurance-grid {
  grid-template-columns: 1fr !important;
  gap: 16px;
  align-items: start;
}
.mini-form {
  margin-bottom: 12px;
}
</style>
