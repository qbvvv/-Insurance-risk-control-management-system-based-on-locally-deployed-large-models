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

    <div class="card" style="margin-bottom: 16px;">
      <h2>规则执行测试</h2>
      <p style="font-size: 12px; color: #6b7280; margin-bottom: 8px;">
        输入一条业务记录（JSON），不填上方「自然语言规则」时会对该记录执行规则库全部规则。
      </p>
      <div style="margin-bottom: 8px;">
        <span style="font-size: 12px; color: #6b7280;">快捷填充：</span>
        <el-button
          v-for="ex in exampleRecords"
          :key="ex.label"
          size="mini"
          type="text"
          @click="testRecordText = ex.label"
        >
          {{ ex.label }}
        </el-button>
      </div>
      <el-input
        v-model="testRecordText"
        type="textarea"
        :rows="2"
        placeholder="例如：同一用户3个月内理赔超过3次"
        style="margin-bottom: 8px;"
      ></el-input>
      <el-button
        size="small"
        :loading="parseRecordLoading"
        style="margin-bottom: 8px;"
        @click="doParseTestRecord"
      >
        解析业务描述为测试记录
      </el-button>
      <pre class="parsed-json" style="margin-bottom: 8px;">{{ testRecordStr }}</pre>
      <el-button type="primary" size="small" :loading="evalLoading" @click="doEvaluateRule">
        执行规则
      </el-button>
      <el-button
        size="small"
        type="warning"
        :loading="matchedLoading"
        style="margin-left: 8px;"
        @click="doQueryMatchedCustomers"
      >
        查询命中客户
      </el-button>
      <div v-if="evaluateResult !== null" class="evaluate-result">
        <p style="margin: 10px 0 4px;">
          <strong>是否命中：</strong>
          <el-tag :type="evaluateResult.hit ? 'danger' : 'success'" size="small">
            {{ evaluateResult.hit ? "命中" : "未命中" }}
          </el-tag>
        </p>
        <pre v-if="evaluateResult.details && evaluateResult.details.length" class="parsed-json">{{ JSON.stringify(evaluateResult.details, null, 2) }}</pre>
      </div>
      <div v-if="matchedCustomers.length" class="evaluate-result">
        <p style="margin: 10px 0 4px;">
          <strong>命中客户：</strong>
          <el-tag type="danger" size="small">{{ matchedCustomers.length }}</el-tag>
        </p>
        <el-table :data="matchedCustomers" border size="small" max-height="460" class="matched-customers-table">
          <el-table-column prop="customer_no" label="客户编号" width="140"></el-table-column>
          <el-table-column prop="customer_name" label="客户姓名" width="140"></el-table-column>
          <el-table-column label="命中规则详情">
            <template slot-scope="scope">
              <pre class="parsed-json matched-detail-json">{{ JSON.stringify(scope.row.hit_details || [], null, 2) }}</pre>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 8px;">
          <el-button
            size="small"
            type="danger"
            :loading="applyActionLoading"
            @click="doApplyActionsForMatchedCustomers"
          >
            执行动作并更新客户
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  parseRule,
  evaluateRule,
  addParsedRule,
  queryRuleMatchedCustomers,
  applyRuleActions,
  parseTestRecord,
} from "@/api";

const EXAMPLE_RECORDS = [
  { label: "同一用户3个月内理赔超过3次" },
  { label: "同一保单年度内理赔次数超过5次" },
  { label: "投保人年龄超过70岁" },
  { label: "单日同一IP提交超过10次申请" },
  { label: "理赔金额与年度保费比例超过10倍" },
  { label: "新用户投保后7天内申请理赔" },
  { label: "同一银行卡被超过3个不同保单使用" },
  { label: "夜间提交理赔申请" },
  { label: "同一地址对应超过5份高额保单" },
];

export default {
  name: "RiskFraudOverview",
  data() {
    return {
      exampleRecords: EXAMPLE_RECORDS,
      // 默认留空：不填规则文本时，执行规则库全部规则（见 doEvaluateRule 的说明）
      nlRuleText: "",
      parseLoading: false,
      parsedRule: null,
      saveRuleLoading: false,
      testRecordText: "同一用户3个月内理赔超过3次",
      parseRecordLoading: false,
      testRecordStr: '{"user_id":"u1","claim_count_3m":4}',
      evalLoading: false,
      evaluateResult: null,
      matchedLoading: false,
      matchedCustomers: [],
      applyActionLoading: false,
    };
  },
  computed: {
    parsedRuleStr() {
      if (!this.parsedRule) return "";
      return JSON.stringify(this.parsedRule, null, 2);
    },
  },
  methods: {
    getActiveRuleText() {
      // 注意：testRecordText 是“业务描述”，只用于 parse_test_record 生成测试记录；
      // 规则文本必须来自“自然语言规则”输入框，否则会导致只执行一条 demo_rule 而非规则库全量规则。
      return (this.nlRuleText || "").trim() || "";
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
        })
        .catch((err) => {
          this.$message.error("加入规则库失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.saveRuleLoading = false;
        });
    },
    getRulePayloadForBatchActions() {
      const currentText = this.getActiveRuleText();
      return currentText ? { ruleText: currentText } : {};
    },
    doParseTestRecord() {
      const text = (this.testRecordText || "").trim();
      if (!text) {
        this.$message.warning("请输入业务描述");
        return;
      }
      this.parseRecordLoading = true;
      parseTestRecord(text)
        .then((res) => {
          const rec = res.data?.record || {};
          this.testRecordStr = JSON.stringify(rec, null, 2);
          this.$message.success("已解析为测试记录 JSON");
        })
        .catch((err) => {
          this.$message.error("解析失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.parseRecordLoading = false;
        });
    },
    doEvaluateRule() {
      let record = {};
      try {
        record = JSON.parse(this.testRecordStr || "{}");
      } catch (e) {
        this.$message.warning("请输入合法的 JSON");
        return;
      }
      this.evalLoading = true;
      this.evaluateResult = null;
      const ruleText = this.getActiveRuleText() || null;
      evaluateRule(record, ruleText)
        .then((res) => {
          this.evaluateResult = {
            hit: res.data.hit,
            details: res.data.details || [],
          };
          this.$message.success("执行完成");
        })
        .catch((err) => {
          this.$message.error("执行失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.evalLoading = false;
        });
    },
    doQueryMatchedCustomers() {
      const payload = this.getRulePayloadForBatchActions();
      if (!payload.parsedRule && !payload.ruleText) {
        this.$message.warning("请先输入或解析一条规则");
        return;
      }
      this.matchedLoading = true;
      this.matchedCustomers = [];
      queryRuleMatchedCustomers(payload)
        .then((res) => {
          const d = res.data || {};
          this.matchedCustomers = Array.isArray(d.items) ? d.items : [];
          this.$message.success(`检索完成，共命中 ${d.hit_count || 0} 位客户`);
        })
        .catch((err) => {
          this.$message.error("检索失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.matchedLoading = false;
        });
    },
    doApplyActionsForMatchedCustomers() {
      const payload = this.getRulePayloadForBatchActions();
      if (!payload.parsedRule && !payload.ruleText) {
        this.$message.warning("请先输入或解析一条规则");
        return;
      }
      this.applyActionLoading = true;
      applyRuleActions(payload)
        .then((res) => {
          const d = res.data || {};
          this.$message.success(`动作执行完成，已更新 ${d.affected_count || 0} 位客户`);
        })
        .catch((err) => {
          this.$message.error("动作执行失败：" + (err.response?.data?.detail || err.message));
        })
        .finally(() => {
          this.applyActionLoading = false;
        });
    },
  },
};
</script>

<style scoped>
.parsed-json,
.evaluate-result pre {
  font-size: 12px;
  background: #f5f5f5;
  padding: 10px;
  border-radius: 6px;
  overflow: auto;
  max-height: 200px;
}
.parsed-result,
.evaluate-result {
  margin-top: 12px;
}

.matched-customers-table {
  margin-top: 6px;
}

.matched-detail-json {
  margin: 0;
  max-height: 150px;
  white-space: pre-wrap;
}
</style>
