<template>
  <div class="page">
    <h1 class="page-title">财务管理</h1>
    <p class="page-subtitle">
      保费收付流水与佣金结算对账；流水号、结算单号由后端生成（PF/CM + 日期 + 序号），也可在新增时手工指定唯一编号。新增与编辑均在弹窗中完成。
    </p>

    <div class="grid grid-2 finance-grid">
      <div class="card">
        <div class="list-head">
          <h2>保费收取与赔款支付</h2>
          <el-button type="primary" size="small" @click="openPfAddDialog">新增流水</el-button>
        </div>
        <el-table
          class="module-table"
          :data="premiumRows"
          border
          size="small"
          style="width: 100%;"
          v-loading="pfLoading"
        >
          <el-table-column prop="flowNo" label="流水号" min-width="140" show-overflow-tooltip />
          <el-table-column prop="flowType" label="类型" min-width="100" show-overflow-tooltip />
          <el-table-column prop="policyNo" label="保单号" min-width="130" show-overflow-tooltip />
          <el-table-column prop="amount" label="金额（元）" min-width="110" show-overflow-tooltip />
          <el-table-column prop="payMethod" label="支付方式" min-width="110" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" min-width="90" show-overflow-tooltip />
          <el-table-column label="操作" width="168" align="center">
            <template slot-scope="scope">
              <div class="module-table-ops">
                <el-button type="primary" size="mini" @click="openPfEditDialog(scope.row)">编辑</el-button>
                <el-button type="danger" size="mini" @click="removePf(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <p v-if="pfError" class="table-error">{{ pfError }}</p>
      </div>

      <div class="card">
        <div class="list-head">
          <h2>佣金结算与对账</h2>
          <el-button type="primary" size="small" @click="openCsAddDialog">新增结算</el-button>
        </div>
        <el-table
          class="module-table"
          :data="commissionRows"
          border
          size="small"
          style="width: 100%;"
          v-loading="csLoading"
        >
          <el-table-column prop="settlementNo" label="结算单号" min-width="140" show-overflow-tooltip />
          <el-table-column prop="channelName" label="渠道 / 代理人" min-width="150" show-overflow-tooltip />
          <el-table-column prop="period" label="结算周期" min-width="110" show-overflow-tooltip />
          <el-table-column prop="commissionAmount" label="佣金（元）" min-width="120" show-overflow-tooltip />
          <el-table-column prop="reconcileStatus" label="对账状态" min-width="110" show-overflow-tooltip />
          <el-table-column label="操作" width="168" align="center">
            <template slot-scope="scope">
              <div class="module-table-ops">
                <el-button type="primary" size="mini" @click="openCsEditDialog(scope.row)">编辑</el-button>
                <el-button type="danger" size="mini" @click="removeCs(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <p v-if="csError" class="table-error">{{ csError }}</p>
      </div>
    </div>

    <el-dialog
      :title="pfEditingId ? '编辑保费流水' : '新增保费流水'"
      :visible.sync="pfDialogVisible"
      width="560px"
      append-to-body
      destroy-on-close
      @closed="onPfDialogClosed"
    >
      <el-form ref="pfForm" :model="pfForm" :rules="pfRules" label-width="100px" size="small" class="dialog-form">
        <el-form-item v-if="pfEditingId" label="流水号">
          <el-input :value="pfForm.flowNo" disabled />
        </el-form-item>
        <el-form-item label="业务类型" prop="flowType">
          <el-select v-model="pfForm.flowType" style="width: 100%;">
            <el-option v-for="t in flowTypeOptions" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="保单号" prop="policyNo">
          <el-input v-model="pfForm.policyNo" clearable placeholder="如 P20260001" />
        </el-form-item>
        <el-form-item label="金额(元)" prop="amount">
          <el-input v-model="pfForm.amount" clearable />
        </el-form-item>
        <el-form-item label="支付方式" prop="payMethod">
          <el-input v-model="pfForm.payMethod" clearable />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-input v-model="pfForm.status" clearable />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="pfForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="pfDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="pfSubmitting" @click="submitPremiumFlow">
          {{ pfEditingId ? "保存" : "确定" }}
        </el-button>
      </span>
    </el-dialog>

    <el-dialog
      :title="csEditingId ? '编辑佣金结算' : '新增佣金结算'"
      :visible.sync="csDialogVisible"
      width="560px"
      append-to-body
      destroy-on-close
      @closed="onCsDialogClosed"
    >
      <el-form ref="csForm" :model="csForm" :rules="csRules" label-width="100px" size="small" class="dialog-form">
        <el-form-item v-if="csEditingId" label="结算单号">
          <el-input :value="csForm.settlementNo" disabled />
        </el-form-item>
        <el-form-item label="渠道/代理人" prop="channelName">
          <el-input v-model="csForm.channelName" clearable />
        </el-form-item>
        <el-form-item label="渠道编码" prop="channelCode">
          <el-input v-model="csForm.channelCode" placeholder="可选" clearable />
        </el-form-item>
        <el-form-item label="结算周期" prop="period">
          <el-input v-model="csForm.period" placeholder="如 2026-02" clearable />
        </el-form-item>
        <el-form-item label="佣金(元)" prop="commissionAmount">
          <el-input v-model="csForm.commissionAmount" clearable />
        </el-form-item>
        <el-form-item label="对账状态" prop="reconcileStatus">
          <el-select v-model="csForm.reconcileStatus" style="width: 100%;">
            <el-option v-for="s in reconcileOptions" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="csForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="csDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="csSubmitting" @click="submitCommission">
          {{ csEditingId ? "保存" : "确定" }}
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  createCommissionSettlement,
  createPremiumFlow,
  deleteCommissionSettlement,
  deletePremiumFlow,
  getCommissionSettlements,
  getPremiumFlows,
  updateCommissionSettlement,
  updatePremiumFlow,
} from "@/api";

export default {
  name: "FinanceView",
  data() {
    return {
      premiumRows: [],
      commissionRows: [],
      pfLoading: false,
      csLoading: false,
      pfError: "",
      csError: "",
      pfDialogVisible: false,
      csDialogVisible: false,
      pfEditingId: null,
      csEditingId: null,
      pfSubmitting: false,
      csSubmitting: false,
      flowTypeOptions: ["首期", "续期", "理赔赔款", "退保退费", "其他"],
      reconcileOptions: ["待对账", "对账中", "已对账", "有差异"],
      pfForm: {
        flowNo: "",
        flowType: "首期",
        policyNo: "",
        amount: "0",
        payMethod: "",
        status: "",
        remark: "",
      },
      csForm: {
        settlementNo: "",
        channelName: "",
        channelCode: "",
        period: "",
        commissionAmount: "0",
        reconcileStatus: "待对账",
        remark: "",
      },
      pfRules: {
        flowType: [{ required: true, message: "请选择类型", trigger: "change" }],
        policyNo: [{ required: true, message: "请输入保单号", trigger: "blur" }],
        amount: [{ required: true, message: "请输入金额", trigger: "blur" }],
      },
      csRules: {
        channelName: [{ required: true, message: "请输入渠道名称", trigger: "blur" }],
        period: [{ required: true, message: "请输入结算周期", trigger: "blur" }],
        commissionAmount: [{ required: true, message: "请输入佣金", trigger: "blur" }],
        reconcileStatus: [{ required: true, message: "请选择对账状态", trigger: "change" }],
      },
    };
  },
  created() {
    this.fetchPremiumFlows();
    this.fetchCommissionRows();
  },
  methods: {
    fetchPremiumFlows() {
      this.pfError = "";
      this.pfLoading = true;
      getPremiumFlows()
        .then((res) => {
          this.premiumRows = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.pfError = "加载保费流水失败，请确认后端已启动（uvicorn api.server:app --reload）。";
        })
        .finally(() => {
          this.pfLoading = false;
        });
    },
    fetchCommissionRows() {
      this.csError = "";
      this.csLoading = true;
      getCommissionSettlements()
        .then((res) => {
          this.commissionRows = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.csError = "加载佣金结算失败，请确认后端已启动（uvicorn api.server:app --reload）。";
        })
        .finally(() => {
          this.csLoading = false;
        });
    },
    emptyPfForm() {
      return {
        flowNo: "",
        flowType: "首期",
        policyNo: "",
        amount: "0",
        payMethod: "",
        status: "",
        remark: "",
      };
    },
    emptyCsForm() {
      return {
        settlementNo: "",
        channelName: "",
        channelCode: "",
        period: "",
        commissionAmount: "0",
        reconcileStatus: "待对账",
        remark: "",
      };
    },
    resetPfForm() {
      this.pfEditingId = null;
      this.pfForm = this.emptyPfForm();
      this.$nextTick(() => {
        if (this.$refs.pfForm) this.$refs.pfForm.clearValidate();
      });
    },
    resetCsForm() {
      this.csEditingId = null;
      this.csForm = this.emptyCsForm();
      this.$nextTick(() => {
        if (this.$refs.csForm) this.$refs.csForm.clearValidate();
      });
    },
    onPfDialogClosed() {
      this.resetPfForm();
    },
    onCsDialogClosed() {
      this.resetCsForm();
    },
    openPfAddDialog() {
      this.pfEditingId = null;
      this.pfForm = this.emptyPfForm();
      this.pfDialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.pfForm) this.$refs.pfForm.clearValidate();
      });
    },
    openPfEditDialog(row) {
      this.pfEditingId = row.id;
      this.pfForm = {
        flowNo: row.flowNo || "",
        flowType: row.flowType || "首期",
        policyNo: row.policyNo || "",
        amount: row.amount || "0",
        payMethod: row.payMethod || "",
        status: row.status || "",
        remark: row.remark || "",
      };
      this.pfDialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.pfForm) this.$refs.pfForm.clearValidate();
      });
    },
    openCsAddDialog() {
      this.csEditingId = null;
      this.csForm = this.emptyCsForm();
      this.csDialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.csForm) this.$refs.csForm.clearValidate();
      });
    },
    openCsEditDialog(row) {
      this.csEditingId = row.id;
      this.csForm = {
        settlementNo: row.settlementNo || "",
        channelName: row.channelName || "",
        channelCode: row.channelCode || "",
        period: row.period || "",
        commissionAmount: row.commissionAmount || "0",
        reconcileStatus: row.reconcileStatus || "待对账",
        remark: row.remark || "",
      };
      this.csDialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.csForm) this.$refs.csForm.clearValidate();
      });
    },
    submitPremiumFlow() {
      this.$refs.pfForm.validate((valid) => {
        if (!valid) return;
        this.pfSubmitting = true;
        const done = () => {
          this.pfSubmitting = false;
        };
        if (this.pfEditingId) {
          const { flowNo, ...patch } = this.pfForm;
          updatePremiumFlow(this.pfEditingId, patch)
            .then(() => {
              this.$message.success("已保存");
              this.pfDialogVisible = false;
              this.fetchPremiumFlows();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        } else {
          const body = { ...this.pfForm };
          delete body.flowNo;
          createPremiumFlow(body)
            .then(() => {
              this.$message.success("已新增");
              this.pfDialogVisible = false;
              this.fetchPremiumFlows();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        }
      });
    },
    submitCommission() {
      this.$refs.csForm.validate((valid) => {
        if (!valid) return;
        this.csSubmitting = true;
        const done = () => {
          this.csSubmitting = false;
        };
        if (this.csEditingId) {
          const { settlementNo, ...patch } = this.csForm;
          updateCommissionSettlement(this.csEditingId, patch)
            .then(() => {
              this.$message.success("已保存");
              this.csDialogVisible = false;
              this.fetchCommissionRows();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        } else {
          const body = { ...this.csForm };
          delete body.settlementNo;
          createCommissionSettlement(body)
            .then(() => {
              this.$message.success("已新增");
              this.csDialogVisible = false;
              this.fetchCommissionRows();
            })
            .catch((e) => {
              this.$message.error(e.response?.data?.detail || e.message);
            })
            .finally(done);
        }
      });
    },
    removePf(row) {
      this.$confirm(`删除流水 ${row.flowNo}？`, "提示", { type: "warning" })
        .then(() => deletePremiumFlow(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchPremiumFlows();
        })
        .catch((e) => {
          if (e === "cancel" || e === "close") return;
          this.$message.error(e.response?.data?.detail || e.message);
        });
    },
    removeCs(row) {
      this.$confirm(`删除结算单 ${row.settlementNo}？`, "提示", { type: "warning" })
        .then(() => deleteCommissionSettlement(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchCommissionRows();
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
.finance-grid {
  grid-template-columns: 1fr !important;
  gap: 16px;
  align-items: start;
}
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
.dialog-form >>> .el-form-item:last-child {
  margin-bottom: 0;
}
</style>
