<template>
  <div>
    <div class="card" style="margin-bottom: 16px;">
      <h2>自然语言转规则</h2>
      <p style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">
        输入业务描述（如「同一用户3个月内理赔超过3次则标记为高风险」），解析为结构化规则并可加入规则库。
      </p>
      <el-input
        v-model="nlRuleText"
        type="textarea"
        :rows="2"
        placeholder="例如：同一用户3个月内理赔超过3次则标记为高风险"
        style="margin-bottom: 8px;"
      ></el-input>
      <el-button type="primary" size="small" :loading="parseLoading" @click="doParseRule">
        解析为结构化规则
      </el-button>
      <el-button
        size="small"
        type="success"
        :disabled="!parsedRule"
        :loading="saveRuleLoading"
        style="margin-left: 8px;"
        @click="doSaveParsedRule"
      >
        加入规则库
      </el-button>
      <div v-if="parsedRule" class="parsed-result">
        <p style="font-size: 12px; color: #6b7280; margin: 10px 0 4px;">解析结果：</p>
        <pre class="parsed-json">{{ parsedRuleStr }}</pre>
      </div>
    </div>

    <p class="section-hint">
      可执行规则清单来自 <code>api/preset_rules</code> 全量预设（与备注稿 20 条等一致）+ MySQL 表 <code>risk_rules</code> 中启用的行；服务启动时会将代码预设同步/更新到库（不覆盖
      <code>nl_parsed</code>）。未配数据库时为代码预设 + 本次运行内解析入库的规则。执行测试不填规则描述时，对记录跑当前可执行规则全集。
    </p>
    <div class="card">
      <h2>规则列表</h2>
      <p style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">
        规则 ID、描述、动作与来源（界面显示为「预设」「解析」，接口字段仍为 <code>preset</code> / <code>nl_parsed</code>）；数据来自 <code>GET /rules</code>。
      </p>
      <el-table
        class="module-table"
        :data="presetRules"
        border
        size="small"
        max-height="420"
        style="width: 100%;"
      >
        <el-table-column prop="rule_id" label="规则ID" width="200"></el-table-column>
        <el-table-column prop="description_cn" label="规则描述"></el-table-column>
        <el-table-column
          prop="action"
          label="动作"
          width="120"
          :formatter="formatActionZh"
        ></el-table-column>
        <el-table-column prop="source" label="来源" width="88" :formatter="formatSourceZh"></el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              :disabled="scope.row.source === 'preset'"
              @click="openEditRule(scope.row)"
            >
              编辑
            </el-button>
            <el-button
              size="mini"
              type="danger"
              :disabled="scope.row.source === 'preset'"
              @click="removeRule(scope.row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <p v-if="presetRulesError" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ presetRulesError }}</p>
    </div>

    <el-dialog title="编辑规则" :visible.sync="editDialogVisible" width="680px" destroy-on-close>
      <el-form :model="editForm" label-width="110px" size="small">
        <el-form-item label="规则ID">
          <el-input v-model="editForm.rule_id" disabled />
        </el-form-item>
        <el-form-item label="规则描述">
          <el-input v-model="editForm.description_cn" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="动作">
          <el-select v-model="editForm.action" style="width: 100%;">
            <el-option label="标记高风险" value="tag_high_risk" />
            <el-option label="人工审核" value="manual_review" />
            <el-option label="拒保/拒赔" value="reject" />
            <el-option label="预警" value="alert" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="editForm.priority" :min="0" :max="9999" style="width: 220px;" />
          <span style="font-size: 12px; color: #94a3b8; margin-left: 10px;">数值越小优先级越高</span>
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editForm.enabledBool" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="saveEditRule">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getRules, parseRule, addParsedRule, getRuleDetail, updateRule, deleteRule } from "@/api";

export default {
  name: "RiskPresetRulesView",
  data() {
    return {
      nlRuleText: "同一用户3个月内理赔超过3次则标记为高风险",
      parseLoading: false,
      parsedRule: null,
      saveRuleLoading: false,
      presetRules: [],
      presetRulesError: "",
      editDialogVisible: false,
      editSaving: false,
      editForm: {
        rule_id: "",
        description_cn: "",
        action: "manual_review",
        priority: 100,
        enabledBool: true,
      },
    };
  },
  computed: {
    parsedRuleStr() {
      if (!this.parsedRule) return "";
      return JSON.stringify(this.parsedRule, null, 2);
    },
  },
  mounted() {
    this.fetchPresetRules();
  },
  methods: {
    /** 与后端 RuleAction 枚举一致 */
    formatActionZh(_row, _column, cellValue) {
      const map = {
        tag_high_risk: "标记高风险",
        manual_review: "人工审核",
        reject: "拒保",
        alert: "预警",
        custom: "自定义",
      };
      const key = cellValue == null ? "" : String(cellValue);
      return map[key] || key;
    },
    /** 与后端规则来源字段一致，列表展示中文 */
    formatSourceZh(_row, _column, cellValue) {
      const map = { preset: "预设", nl_parsed: "解析" };
      const key = cellValue == null ? "" : String(cellValue);
      return map[key] || key || "—";
    },
    fetchPresetRules() {
      getRules()
        .then((res) => {
          this.presetRules = Array.isArray(res.data) ? res.data : [];
          this.presetRulesError = "";
        })
        .catch(() => {
          this.presetRulesError = "获取规则列表失败，请确认后端已启动。";
        });
    },
    doParseRule() {
      const text = (this.nlRuleText || "").trim();
      if (!text) {
        this.$message.warning("请输入自然语言规则描述");
        return;
      }
      this.parseLoading = true;
      this.parsedRule = null;
      parseRule(text)
        .then((res) => {
          const d = res.data || {};
          this.parsedRule = d.parsed_rule != null ? d.parsed_rule : d;
          this.$message.success("解析成功，请确认后加入规则库");
        })
        .catch((err) => {
          this.$message.error("解析失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.parseLoading = false;
        });
    },
    doSaveParsedRule() {
      if (!this.parsedRule) {
        this.$message.warning("请先解析规则");
        return;
      }
      this.saveRuleLoading = true;
      addParsedRule(this.parsedRule)
        .then((res) => {
          const d = res.data || {};
          const ruleId = d.rule_id ? `（${d.rule_id}）` : "";
          this.$message.success((d.message || "规则库更新成功") + ruleId);
          this.fetchPresetRules();
        })
        .catch((err) => {
          this.$message.error("加入规则库失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.saveRuleLoading = false;
        });
    },
    openEditRule(row) {
      const rid = row?.rule_id;
      if (!rid) return;
      getRuleDetail(rid)
        .then((res) => {
          const d = res.data || {};
          this.editForm = {
            rule_id: d.rule_id || rid,
            description_cn: d.description_cn || "",
            action: d.action || "manual_review",
            priority: typeof d.priority === "number" ? d.priority : 100,
            enabledBool: String(d.enabled) === "1" || d.enabled === 1 || d.enabled === true,
          };
          this.editDialogVisible = true;
        })
        .catch((err) => {
          this.$message.error("读取规则详情失败：" + (err.response?.data?.detail || err.message));
        });
    },
    saveEditRule() {
      if (!this.editForm.rule_id) return;
      this.editSaving = true;
      const body = {
        description_cn: this.editForm.description_cn,
        action: this.editForm.action,
        priority: this.editForm.priority,
        enabled: this.editForm.enabledBool ? 1 : 0,
      };
      updateRule(this.editForm.rule_id, body)
        .then(() => {
          this.$message.success("保存成功");
          this.editDialogVisible = false;
          this.fetchPresetRules();
        })
        .catch((err) => {
          this.$message.error("保存失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.editSaving = false;
        });
    },
    removeRule(row) {
      const rid = row?.rule_id;
      if (!rid) return;
      this.$confirm(`确定删除规则：${rid}？（仅「解析」来源可删）`, "提示", { type: "warning" })
        .then(() => deleteRule(rid))
        .then(() => {
          this.$message.success("已删除");
          this.fetchPresetRules();
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
.section-hint {
  margin: 0 0 14px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.55;
}
code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.parsed-json {
  font-size: 12px;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 6px;
  overflow: auto;
  max-height: 220px;
}

.parsed-result {
  margin-top: 12px;
}
</style>
