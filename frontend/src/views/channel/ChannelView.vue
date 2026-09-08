<template>
  <div class="page">
    <h1 class="page-title">渠道管理</h1>
    <p class="page-subtitle">
      维护代理人、银行、网销等销售渠道主数据；编码可自定义，留空则由后端按 CH+日期+序号 生成。右栏业绩与考核为演示数据。
    </p>

    <div class="card" style="margin-bottom: 16px;">
      <h2>新增 / 编辑渠道</h2>
      <el-form
        ref="chForm"
        :model="form"
        :rules="rules"
        label-width="108px"
        size="small"
        @submit.native.prevent="handleSubmit"
      >
        <el-form-item label="渠道编码">
          <el-input
            v-model="form.channelCode"
            :disabled="!!editingId"
            placeholder="留空则保存时自动生成"
            clearable
          />
        </el-form-item>
        <div class="form-grid">
          <el-form-item label="渠道名称" prop="channelName">
            <el-input v-model="form.channelName" clearable />
          </el-form-item>
          <el-form-item label="渠道类型" prop="channelType">
            <el-select v-model="form.channelType" placeholder="请选择" clearable style="width: 100%;">
              <el-option v-for="t in typeOptions" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="负责人" prop="manager">
            <el-input v-model="form.manager" clearable />
          </el-form-item>
          <el-form-item label="联系电话" prop="contactPhone">
            <el-input v-model="form.contactPhone" clearable />
          </el-form-item>
          <el-form-item label="合作状态" prop="status">
            <el-select v-model="form.status" style="width: 100%;">
              <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="佣金/手续费" prop="commissionRule">
          <el-input v-model="form.commissionRule" type="textarea" :rows="2" placeholder="如 首年 25%，续期 5%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item class="form-actions-row">
          <el-button type="primary" native-type="submit" :loading="submitting">
            {{ editingId ? "保存修改" : "新增渠道" }}
          </el-button>
          <el-button v-if="editingId" @click="resetForm">取消编辑</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="channel-bottom">
      <div class="card">
        <h2>渠道信息与合作协议</h2>
        <el-table
          class="module-table"
          :data="channels"
          border
          size="small"
          style="width: 100%;"
          v-loading="loading"
        >
          <el-table-column prop="channelCode" label="渠道编码" width="100" />
          <el-table-column prop="channelName" label="渠道名称" min-width="120" />
          <el-table-column prop="channelType" label="渠道类型" width="90" />
          <el-table-column prop="manager" label="负责人" width="90" />
          <el-table-column prop="commissionRule" label="佣金协议" min-width="120" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="80" />
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

      <div class="card perf-card">
        <h2>渠道业绩与考核（示例）</h2>
        <el-table class="module-table" :data="channelPerf" border size="small" style="width: 100%;">
          <el-table-column prop="name" label="渠道" />
          <el-table-column prop="premium" label="保费收入（万元）" width="140" />
          <el-table-column prop="cases" label="件数" width="80" />
          <el-table-column prop="kpi" label="KPI 达成率" width="120" />
          <el-table-column label="考核结果" width="100">
            <template slot-scope="scope">
              <el-tag :type="scope.row.result === '达标' ? 'success' : 'warning'" size="small">
                {{ scope.row.result }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { createChannel, deleteChannel, getChannels, updateChannel } from "@/api";

export default {
  name: "ChannelView",
  data() {
    return {
      channels: [],
      loading: false,
      error: "",
      editingId: null,
      submitting: false,
      typeOptions: ["代理人", "银行", "网销", "经纪公司", "经代", "其他"],
      statusOptions: ["合作中", "暂停", "终止"],
      channelPerf: [
        { name: "个人代理渠道", premium: 320, cases: 820, kpi: "108%", result: "达标" },
        { name: "银行渠道", premium: 260, cases: 430, kpi: "92%", result: "待提升" },
      ],
      form: {
        channelCode: "",
        channelName: "",
        channelType: "",
        manager: "",
        commissionRule: "",
        contactPhone: "",
        status: "合作中",
        remark: "",
      },
      rules: {
        channelName: [{ required: true, message: "请输入渠道名称", trigger: "blur" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
    };
  },
  created() {
    this.fetchChannels();
  },
  methods: {
    fetchChannels() {
      this.error = "";
      this.loading = true;
      getChannels()
        .then((res) => {
          this.channels = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取渠道列表失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    resetForm() {
      this.editingId = null;
      this.form = {
        channelCode: "",
        channelName: "",
        channelType: "",
        manager: "",
        commissionRule: "",
        contactPhone: "",
        status: "合作中",
        remark: "",
      };
      this.$nextTick(() => {
        if (this.$refs.chForm) this.$refs.chForm.clearValidate();
      });
    },
    payloadForApi() {
      const body = { ...this.form };
      if (!this.editingId && !String(body.channelCode || "").trim()) {
        delete body.channelCode;
      }
      return body;
    },
    handleSubmit() {
      this.$refs.chForm.validate((valid) => {
        if (!valid) return;
        this.submitting = true;
        const done = () => {
          this.submitting = false;
        };
        if (this.editingId) {
          const { channelCode, ...patch } = this.form;
          updateChannel(this.editingId, patch)
            .then(() => {
              this.$message.success("保存成功");
              this.fetchChannels();
              this.resetForm();
            })
            .catch((err) => {
              this.$message.error("更新失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        } else {
          createChannel(this.payloadForApi())
            .then(() => {
              this.$message.success("新增成功");
              this.fetchChannels();
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
        channelCode: row.channelCode || "",
        channelName: row.channelName || "",
        channelType: row.channelType || "",
        manager: row.manager || "",
        commissionRule: row.commissionRule || "",
        contactPhone: row.contactPhone || "",
        status: row.status || "合作中",
        remark: row.remark || "",
      };
      this.$nextTick(() => {
        if (this.$refs.chForm) this.$refs.chForm.clearValidate();
      });
    },
    removeRow(row) {
      this.$confirm(`确定删除渠道：${row.channelName}（${row.channelCode}）？`, "提示", { type: "warning" })
        .then(() => deleteChannel(row.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchChannels();
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
.channel-bottom {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
.perf-card {
  width: 100%;
}
</style>
