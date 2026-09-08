<template>
  <div class="page">
    <h1 class="page-title">报表与分析</h1>
    <p class="page-subtitle">
      提供多维度数据分析视图，展示经营驾驶舱与分析清单。
    </p>

    <div class="kpi-row">
      <div class="kpi-card">
        <p class="kpi-label">保费收入（万元）</p>
        <p class="kpi-value">{{ summary.premiumTotalWan }}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">赔付金额（万元）</p>
        <p class="kpi-value">{{ summary.claimTotalWan }}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">综合赔付率（%）</p>
        <p class="kpi-value">{{ summary.claimRatioPercent }}</p>
      </div>
      <div class="kpi-card">
        <p class="kpi-label">风控预警 / 黑名单</p>
        <p class="kpi-value">{{ summary.riskAlertCount || 0 }} / {{ summary.blacklistCount || 0 }}</p>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h2>经营结构概览</h2>
        <div ref="mainChart" class="chart"></div>
      </div>

      <div class="card insight-card">
        <h2>分析报表清单</h2>
        <div class="insight-headline">
          <span class="insight-chip">分析维度</span>
          <span class="insight-chip insight-chip--sub">产品 / 渠道</span>
          <span class="insight-chip insight-chip--sub">客户 / 时间</span>
        </div>
        <p class="section-explain">
          下列为经营分析中常见的<strong>报表类型与统计维度</strong>说明；实现上需在明细数据（保单、理赔、客户行为等）之上做汇总与切片（本页为能力清单示意）。
        </p>
        <ul class="feature-list explain-list">
          <li>
            <strong><span class="bullet-tag">01</span>保费分析报表（按产品 / 渠道 / 区域 / 时间）</strong>
            <span class="item-desc">从不同业务切片观察保费规模、增速与结构，用于考核渠道、区域经营与产品组合策略。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">02</span>理赔分析报表（赔付率、案均赔款、时效）</strong>
            <span class="item-desc">赔付率＝赔款/保费等口径下的成本水平；案均赔款反映单案严重程度；时效衡量立案至结案快慢，支撑理赔运营优化。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">03</span>客户分析报表（流失率、留存率、转化率）</strong>
            <span class="item-desc">流失/留存刻画客户是否持续在保或复购；转化率常指从询价、投保到出单等环节的转化，用于销售与客户运营。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">04</span>续期分析报表（续期率、失效率）</strong>
            <span class="item-desc">针对长期险续期收费：续期率衡量按时续交比例；失效率（或断保率）衡量未续导致保单终止的情况，影响继续率与现金流。</span>
          </li>
          <li>
            <strong><span class="bullet-tag">05</span>监管报表与自定义报表配置</strong>
            <span class="item-desc">前者对接固定监管模板；后者允许业务配置维度与指标，生成专题分析表（与「运营报表与监管报送」模块相互衔接）。</span>
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
  name: "AnalyticsView",
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
      if (!this.$refs.mainChart) return;
      this.chart = echarts.init(this.$refs.mainChart);
      this.renderChart();
    },
    handleResize() {
      if (this.chart) this.chart.resize();
    },
    renderChart() {
      if (!this.chart) return;
      const premium = Number(this.summary.premiumTotalWan || 0);
      const claim = Number(this.summary.claimTotalWan || 0);
      this.chart.setOption({
        tooltip: { trigger: "item" },
        legend: { bottom: 0 },
        series: [
          {
            type: "pie",
            radius: ["45%", "70%"],
            itemStyle: { borderRadius: 8, borderColor: "#fff", borderWidth: 2 },
            data: [
              { value: premium, name: "保费收入" },
              { value: claim, name: "赔付金额" },
            ],
          },
        ],
      });
    },
    fetchSummary() {
      getAnalyticsSummary()
        .then((res) => {
          this.summary = Object.assign(this.summary, res.data || {});
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
  background: linear-gradient(90deg, #3b82f6, #0ea5e9);
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
  color: #1d4ed8;
  background: #e0e7ff;
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
  color: #1d4ed8;
  background: #dbeafe;
}
</style>
