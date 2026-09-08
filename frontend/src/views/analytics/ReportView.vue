<template>
  <div class="page">
    <h1 class="page-title">运营报表与监管报送</h1>
    <p class="page-subtitle">
      针对公司内部管理与外部监管，提供多维度报表展示与导出能力。
    </p>

    <div class="kpi-row">
      <div class="kpi-card">
        <p class="kpi-label">客户数</p>
        <p class="kpi-value">{{ summary.customerCount }}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">保单数</p>
        <p class="kpi-value">{{ summary.policyCount }}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">理赔案件数</p>
        <p class="kpi-value">{{ summary.claimCount }}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">风控预警 / 黑名单</p>
        <p class="kpi-value">{{ summary.riskAlertCount || 0 }} / {{ summary.blacklistCount || 0 }}</p>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h2>核心经营指标（动态）</h2>
        <div ref="barChart" class="chart"></div>
      </div>

      <div class="card insight-card">
        <h2>监管报送要点</h2>
        <div class="insight-headline">
          <span class="insight-chip">监管口径</span>
          <span class="insight-chip insight-chip--sub">合规归档</span>
          <span class="insight-chip insight-chip--sub">对外报送</span>
        </div>
        <p class="section-explain">
          以下为险企在<strong>对内合规归档</strong>与<strong>对外监管报送</strong>中常见的数据范畴说明（示意）；本页不替代正式监管报表格式，实际报送以监管最新规则为准。
        </p>
        <ul class="feature-list explain-list">
          <li>
            <strong><span class="bullet-tag">01</span>保费与赔付相关监管报表</strong>
            <span class="item-desc">按监管口径汇总的保费收入、赔款支出、未决赔款等，用于偿付能力评估、统计季报/年报等场景的数据基础。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">02</span>偿付能力信息披露指标</strong>
            <span class="item-desc">与「偿二代」等框架相关的实际资本、最低资本、综合偿付能力充足率等需定期披露或报送的指标集合。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">03</span>反洗钱、反欺诈相关报送数据</strong>
            <span class="item-desc">大额与可疑交易、客户身份与受益所有人、异常投保/理赔行为等，满足人民银行反洗钱及行业反欺诈数据协作要求。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">04</span>产品条款备案与变更记录</strong>
            <span class="item-desc">条款费率备案、产品停售与变更轨迹，便于监管核查产品合规性与消费者权益保护。</span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { getAnalyticsSummary } from "@/api";
import * as echarts from "echarts";

export default {
  name: "ReportView",
  data() {
    return {
      summary: {
        premiumTotalWan: "0",
        claimTotalWan: "0",
        claimRatioPercent: "0",
        customerCount: 0,
        policyCount: 0,
        claimCount: 0,
        riskAlertCount: 0,
        blacklistCount: 0,
      },
      chart: null,
    };
  },
  created() {
    this.fetchSummary();
  },
  mounted() {
    this.initChart();
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    if (this.chart) this.chart.dispose();
  },
  methods: {
    initChart() {
      if (!this.$refs.barChart) return;
      this.chart = echarts.init(this.$refs.barChart);
      this.renderChart();
    },
    handleResize() {
      if (this.chart) this.chart.resize();
    },
    renderChart() {
      if (!this.chart) return;
      const premium = Number(this.summary.premiumTotalWan || 0);
      const claim = Number(this.summary.claimTotalWan || 0);
      const ratio = Number(this.summary.claimRatioPercent || 0);
      this.chart.setOption({
        tooltip: {
          trigger: "axis",
          formatter(params) {
            const arr = Array.isArray(params) ? params : [params];
            const idx = arr[0].dataIndex;
            if (idx === 0) return `保费收入<br/>${premium} 万元`;
            if (idx === 1) return `赔付金额<br/>${claim} 万元`;
            return `综合赔付率<br/>${ratio} %`;
          },
        },
        xAxis: {
          type: "category",
          data: ["保费收入", "赔付金额", "赔付率"],
          axisLabel: { color: "#6b7280" },
        },
        yAxis: [
          {
            type: "value",
            name: "万元",
            position: "left",
            axisLabel: { color: "#6b7280" },
            splitLine: { lineStyle: { color: "#eef2f7" } },
          },
          {
            type: "value",
            name: "%",
            position: "right",
            axisLabel: { color: "#6b7280" },
            splitLine: { show: false },
          },
        ],
        series: [
          {
            type: "bar",
            name: "金额（万元）",
            yAxisIndex: 0,
            barWidth: 28,
            barGap: "30%",
            itemStyle: { color: "#3b82f6", borderRadius: [8, 8, 0, 0] },
            data: [
              { value: premium, itemStyle: { opacity: 1 } },
              { value: claim, itemStyle: { opacity: 1 } },
              { value: 0, itemStyle: { opacity: 0 } },
            ],
          },
          {
            type: "bar",
            name: "综合赔付率（%）",
            yAxisIndex: 1,
            barWidth: 28,
            itemStyle: { color: "#0ea5e9", borderRadius: [8, 8, 0, 0] },
            data: [
              { value: 0, itemStyle: { opacity: 0 } },
              { value: 0, itemStyle: { opacity: 0 } },
              { value: ratio, itemStyle: { opacity: 1 } },
            ],
          },
        ],
      });
    },
    fetchSummary() {
      getAnalyticsSummary()
        .then((res) => {
          this.summary = res.data || this.summary;
          this.renderChart();
        })
        .catch(() => {});
    },
  },
};
</script>

<style scoped>
.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.kpi-card {
  background: #fff;
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: 0 2px 12px rgba(17, 24, 39, 0.06);
}
.kpi-label {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}
.kpi-value {
  margin: 8px 0 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}
.chart {
  height: 320px;
}
@media (max-width: 1200px) {
  .kpi-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 768px) {
  .kpi-row {
    grid-template-columns: 1fr;
  }
}

.section-explain {
  margin: 0 0 14px;
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
}
.insight-card {
  position: relative;
  overflow: hidden;
}
.insight-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #0ea5e9, #38bdf8);
}
.insight-headline {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}
.insight-chip {
  display: inline-flex;
  align-items: center;
  height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #0369a1;
  background: #e0f2fe;
}
.insight-chip--sub {
  color: #64748b;
  background: #f1f5f9;
}

.explain-list li {
  margin-bottom: 12px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
}

.explain-list li:last-child {
  margin-bottom: 0;
}

.explain-list .item-desc {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.5;
  color: #6b7280;
  font-weight: normal;
}
.bullet-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 6px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #0369a1;
  background: #dbeafe;
}
</style>
