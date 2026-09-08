<template>
  <div class="page dash-root">
    <div class="dash-bg" aria-hidden="true" />

    <header class="dash-head">
      <div>
        <h1 class="dash-title">运营数据大屏</h1>
        <p class="dash-sub">实时汇总承保、理赔、风险与渠道数据 · 接口驱动 · 下方可进入运营报表与报表分析模块</p>
      </div>
      <div class="dash-head-actions">
        <span v-if="lastFetchedAt" class="dash-updated">更新于 {{ lastFetchedAt }}</span>
        <el-button type="primary" size="small" plain :loading="loading" @click="fetchAll">刷新数据</el-button>
      </div>
    </header>

    <div v-loading="loading" class="dash-body" element-loading-text="加载运营数据…" element-loading-background="rgba(255, 255, 255, 0.9)">
      <el-row :gutter="16" class="kpi-row">
        <el-col :xs="24" :sm="24" :md="8">
          <div class="glass kpi-card kpi-a">
            <div class="kpi-icon" aria-hidden="true" />
            <h3>承保与业务</h3>
            <div class="kpi-grid">
              <div>
                <p class="kpi-label">投保 / 核保案件</p>
                <p class="kpi-value">{{ fmtInt(kpi.uwCount) }}</p>
              </div>
              <div>
                <p class="kpi-label">自动 / 高效核保占比</p>
                <p class="kpi-value accent">{{ kpi.uwPassRate }}</p>
              </div>
            </div>
            <p class="kpi-foot">在册保单 {{ fmtInt(kpi.policyCount) }} · 客户 {{ fmtInt(kpi.customerCount) }}</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <div class="glass kpi-card kpi-b">
            <div class="kpi-icon" aria-hidden="true" />
            <h3>风险与合规</h3>
            <div class="kpi-grid">
              <div>
                <p class="kpi-label">风险预警</p>
                <p class="kpi-value warn">{{ fmtInt(kpi.riskAlertCount) }}</p>
              </div>
              <div>
                <p class="kpi-label">黑名单条目</p>
                <p class="kpi-value danger">{{ fmtInt(kpi.blacklistCount) }}</p>
              </div>
            </div>
            <p class="kpi-foot">保费收入 {{ kpi.premiumTotalWan }} 万元 · 赔付 {{ kpi.claimTotalWan }} 万元</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="24" :md="8">
          <div class="glass kpi-card kpi-c">
            <div class="kpi-icon" aria-hidden="true" />
            <h3>理赔与效率</h3>
            <div class="kpi-grid">
              <div>
                <p class="kpi-label">理赔案件数</p>
                <p class="kpi-value">{{ fmtInt(kpi.claimCount) }}</p>
              </div>
              <div>
                <p class="kpi-label">综合赔付率</p>
                <p class="kpi-value accent-soft">{{ kpi.claimRatioPercent }}%</p>
              </div>
            </div>
            <p class="kpi-foot">数据来自全库汇总 · 与报表分析模块一致</p>
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16" class="module-links-row">
        <el-col :xs="24" :sm="12">
          <router-link to="/report" class="module-link-card glass">
            <div class="module-link-icon module-link-icon--doc" aria-hidden="true">
              <i class="el-icon-document" />
            </div>
            <div class="module-link-text">
              <h3 class="module-link-title">运营报表与监管报送</h3>
              <p class="module-link-desc">监管指标口径、报送清单与运营报表导出</p>
            </div>
            <i class="el-icon-arrow-right module-link-chevron" aria-hidden="true" />
          </router-link>
        </el-col>
        <el-col :xs="24" :sm="12">
          <router-link to="/analytics" class="module-link-card glass">
            <div class="module-link-icon module-link-icon--chart" aria-hidden="true">
              <i class="el-icon-s-data" />
            </div>
            <div class="module-link-text">
              <h3 class="module-link-title">报表与分析</h3>
              <p class="module-link-desc">多维汇总、趋势与可视化分析</p>
            </div>
            <i class="el-icon-arrow-right module-link-chevron" aria-hidden="true" />
          </router-link>
        </el-col>
      </el-row>

      <el-row :gutter="16" class="chart-row">
        <el-col :xs="24" :lg="14">
          <div class="glass chart-wrap">
            <div class="chart-head">
              <h3>近七日保费流水（万元）</h3>
              <span class="chart-hint">基于保费收付流水按日聚合</span>
            </div>
            <div ref="lineRef" class="chart-box" />
          </div>
        </el-col>
        <el-col :xs="24" :lg="10">
          <div class="glass chart-wrap">
            <div class="chart-head">
              <h3>险种结构（按保单保费）</h3>
              <span class="chart-hint">产品类别占比</span>
            </div>
            <div ref="pieRef" class="chart-box" />
          </div>
        </el-col>
      </el-row>

      <el-row :gutter="16" class="chart-row">
        <el-col :span="24">
          <div class="glass chart-wrap chart-wrap-wide">
            <div class="chart-head">
              <h3>渠道业绩（佣金结算 / 万元）</h3>
              <span class="chart-hint">无结算数据时按核保渠道保费估算</span>
            </div>
            <div ref="barRef" class="chart-box chart-tall" />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";
import {
  getAnalyticsSummary,
  getPolicies,
  getProducts,
  getPremiumFlows,
  getCommissionSettlements,
  getUnderwritingCases,
} from "@/api";

const CHART_TEXT = "#475569";
const CHART_LINE = "rgba(148, 163, 184, 0.45)";
const ACCENT = "#14b8a6";
const ACCENT2 = "#0284c7";
const MUTED = "#64748b";
const TOOLTIP_BG = "rgba(255, 255, 255, 0.96)";
const TOOLTIP_TEXT = "#1e293b";

export default {
  name: "DashboardView",
  data() {
    return {
      loading: false,
      lastFetchedAt: "",
      kpi: {
        uwCount: 0,
        uwPassRate: "—",
        policyCount: 0,
        customerCount: 0,
        riskAlertCount: 0,
        blacklistCount: 0,
        claimCount: 0,
        claimRatioPercent: "0",
        premiumTotalWan: "0",
        claimTotalWan: "0",
      },
      lineChart: null,
      pieChart: null,
      barChart: null,
    };
  },
  mounted() {
    this.$nextTick(() => {
      this.ensureCharts();
      window.addEventListener("resize", this.handleResize);
    });
    this.fetchAll();
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    this.disposeCharts();
  },
  methods: {
    fmtInt(n) {
      if (n == null || Number.isNaN(n)) return "0";
      return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    disposeCharts() {
      if (this.lineChart) {
        this.lineChart.dispose();
        this.lineChart = null;
      }
      if (this.pieChart) {
        this.pieChart.dispose();
        this.pieChart = null;
      }
      if (this.barChart) {
        this.barChart.dispose();
        this.barChart = null;
      }
    },
    ensureCharts() {
      const common = { renderer: "canvas" };
      if (this.$refs.lineRef && !this.lineChart) {
        this.lineChart = echarts.init(this.$refs.lineRef, null, common);
      }
      if (this.$refs.pieRef && !this.pieChart) {
        this.pieChart = echarts.init(this.$refs.pieRef, null, common);
      }
      if (this.$refs.barRef && !this.barChart) {
        this.barChart = echarts.init(this.$refs.barRef, null, common);
      }
    },
    handleResize() {
      this.lineChart && this.lineChart.resize();
      this.pieChart && this.pieChart.resize();
      this.barChart && this.barChart.resize();
    },
    last7DateKeys() {
      const keys = [];
      const labels = [];
      const now = new Date();
      for (let i = 6; i >= 0; i -= 1) {
        const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, "0");
        const day = String(d.getDate()).padStart(2, "0");
        keys.push(`${y}-${m}-${day}`);
        labels.push(`${m}-${day}`);
      }
      return { keys, labels };
    },
    buildPremiumSeries(flows) {
      const { keys, labels } = this.last7DateKeys();
      const sums = Object.fromEntries(keys.map((k) => [k, 0]));
      (flows || []).forEach((f) => {
        if ((f.flowType || "") === "理赔赔款") return;
        const raw = (f.createdAt || "").trim();
        const day = raw.slice(0, 10);
        if (Object.prototype.hasOwnProperty.call(sums, day)) {
          sums[day] += parseFloat(f.amount) || 0;
        }
      });
      const values = keys.map((k) => Math.round((sums[k] / 10000) * 100) / 100);
      return { labels, values };
    },
    aggregateCategoryPie(policies, products) {
      const nameToCat = {};
      (products || []).forEach((p) => {
        nameToCat[p.productName] = (p.category || "未分类").trim() || "未分类";
      });
      const catSum = {};
      (policies || []).forEach((pol) => {
        const cat = nameToCat[pol.productName] || (pol.productName || "其他").trim() || "其他";
        catSum[cat] = (catSum[cat] || 0) + (parseFloat(pol.premium) || 0);
      });
      const entries = Object.entries(catSum)
        .map(([name, v]) => ({ name, value: Math.max(Math.round((v / 10000) * 100) / 100, 0) }))
        .filter((x) => x.value > 0)
        .sort((a, b) => b.value - a.value);
      if (!entries.length) {
        return [{ name: "暂无保单数据", value: 1 }];
      }
      return entries;
    },
    aggregateChannelBar(settlements, uwCases) {
      const fromComm = {};
      (settlements || []).forEach((s) => {
        const k = (s.channelName || "未命名").trim() || "未命名";
        fromComm[k] = (fromComm[k] || 0) + (parseFloat(s.commissionAmount) || 0);
      });
      const keys = Object.keys(fromComm);
      if (keys.length) {
        return keys
          .map((name) => ({ name, value: Math.round((fromComm[name] / 10000) * 100) / 100 }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 12);
      }
      const fromUw = {};
      (uwCases || []).forEach((c) => {
        const k = (c.channel || "").trim() || "未指定渠道";
        fromUw[k] = (fromUw[k] || 0) + (parseFloat(c.premium) || 0);
      });
      const k2 = Object.keys(fromUw);
      if (!k2.length) return [];
      return k2
        .map((name) => ({ name, value: Math.round((fromUw[name] / 10000) * 100) / 100 }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 12);
    },
    uwPassRateText(cases) {
      if (!cases || !cases.length) return "—";
      const ok = cases.filter((c) => {
        const s = (c.status || "").trim();
        return /通过|承保|标体|同意|已出单|生效/i.test(s);
      }).length;
      return `${((ok / cases.length) * 100).toFixed(1)}%`;
    },
    baseChartOpts() {
      return {
        backgroundColor: "transparent",
        textStyle: { color: CHART_TEXT, fontFamily: "system-ui, sans-serif" },
      };
    },
    applyLine(labels, values) {
      if (!this.lineChart) return;
      this.lineChart.setOption(
        {
          ...this.baseChartOpts(),
          tooltip: {
            trigger: "axis",
            backgroundColor: TOOLTIP_BG,
            borderColor: "rgba(148, 163, 184, 0.5)",
            textStyle: { color: TOOLTIP_TEXT },
          },
          grid: { left: 48, right: 24, top: 28, bottom: 28 },
          xAxis: {
            type: "category",
            data: labels,
            axisLine: { lineStyle: { color: CHART_LINE } },
            axisLabel: { color: CHART_TEXT },
          },
          yAxis: {
            type: "value",
            name: "万元",
            nameTextStyle: { color: MUTED, fontSize: 11 },
            splitLine: { lineStyle: { color: CHART_LINE, type: "dashed" } },
            axisLabel: { color: CHART_TEXT },
          },
          series: [
            {
              type: "line",
              smooth: 0.35,
              symbol: "circle",
              symbolSize: 8,
              showSymbol: true,
              lineStyle: { width: 3, color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: ACCENT2 },
                { offset: 1, color: ACCENT },
              ]) },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: "rgba(2, 132, 199, 0.22)" },
                  { offset: 1, color: "rgba(255, 255, 255, 0.02)" },
                ]),
              },
              data: values,
            },
          ],
        },
        { notMerge: true }
      );
    },
    applyPie(data) {
      if (!this.pieChart) return;
      const isPlaceholder = data.length === 1 && data[0].name === "暂无保单数据";
      this.pieChart.setOption(
        {
          ...this.baseChartOpts(),
          tooltip: {
            trigger: "item",
            backgroundColor: TOOLTIP_BG,
            borderColor: "rgba(148, 163, 184, 0.5)",
            textStyle: { color: TOOLTIP_TEXT },
            formatter: isPlaceholder ? "{b}" : "{b}<br/>{c} 万元 ({d}%)",
          },
          legend: { bottom: 4, textStyle: { color: CHART_TEXT, fontSize: 11 } },
          series: [
            {
              type: "pie",
              radius: ["42%", "72%"],
              center: ["50%", "46%"],
              avoidLabelOverlap: true,
              itemStyle: {
                borderRadius: 8,
                borderColor: "#fff",
                borderWidth: 2,
              },
              label: { color: CHART_TEXT, formatter: isPlaceholder ? "{b}" : "{b}\n{d}%" },
              data: data.map((d, i) => ({
                ...d,
                itemStyle: isPlaceholder
                  ? { color: MUTED }
                  : {
                      color: ["#22d3ee", "#38bdf8", "#818cf8", "#c084fc", "#fb7185", "#fbbf24", "#34d399"][i % 7],
                    },
              })),
            },
          ],
        },
        { notMerge: true }
      );
    },
    applyBar(rows) {
      if (!this.barChart) return;
      const names = rows.map((r) => r.name);
      const vals = rows.map((r) => r.value);
      if (!names.length) {
        names.push("暂无");
        vals.push(0);
      }
      this.barChart.setOption(
        {
          ...this.baseChartOpts(),
          tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            backgroundColor: TOOLTIP_BG,
            borderColor: "rgba(148, 163, 184, 0.5)",
            textStyle: { color: TOOLTIP_TEXT },
          },
          grid: { left: 72, right: 24, top: 20, bottom: 48 },
          xAxis: {
            type: "category",
            data: names,
            axisLabel: { color: CHART_TEXT, rotate: names.length > 6 ? 28 : 0, interval: 0 },
            axisLine: { lineStyle: { color: CHART_LINE } },
          },
          yAxis: {
            type: "value",
            name: "万元",
            nameTextStyle: { color: MUTED, fontSize: 11 },
            splitLine: { lineStyle: { color: CHART_LINE, type: "dashed" } },
            axisLabel: { color: CHART_TEXT },
          },
          series: [
            {
              type: "bar",
              data: vals,
              barMaxWidth: 36,
              itemStyle: {
                borderRadius: [6, 6, 0, 0],
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: "#67e8f9" },
                  { offset: 0.45, color: "#38bdf8" },
                  { offset: 1, color: "#1d4ed8" },
                ]),
              },
            },
          ],
        },
        { notMerge: true }
      );
    },
    async fetchAll() {
      this.loading = true;
      try {
        const [sumRes, polRes, prodRes, flowRes, commRes, uwRes] = await Promise.all([
          getAnalyticsSummary(),
          getPolicies(),
          getProducts(),
          getPremiumFlows(),
          getCommissionSettlements(),
          getUnderwritingCases(),
        ]);
        const s = sumRes.data || {};
        const policies = Array.isArray(polRes.data) ? polRes.data : [];
        const products = Array.isArray(prodRes.data) ? prodRes.data : [];
        const flows = Array.isArray(flowRes.data) ? flowRes.data : [];
        const settlements = Array.isArray(commRes.data) ? commRes.data : [];
        const uwCases = Array.isArray(uwRes.data) ? uwRes.data : [];

        this.kpi = {
          uwCount: uwCases.length,
          uwPassRate: this.uwPassRateText(uwCases),
          policyCount: s.policyCount ?? policies.length,
          customerCount: s.customerCount ?? 0,
          riskAlertCount: s.riskAlertCount ?? 0,
          blacklistCount: s.blacklistCount ?? 0,
          claimCount: s.claimCount ?? 0,
          claimRatioPercent: String(s.claimRatioPercent ?? "0"),
          premiumTotalWan: String(s.premiumTotalWan ?? "0"),
          claimTotalWan: String(s.claimTotalWan ?? "0"),
        };

        const { labels, values } = this.buildPremiumSeries(flows);
        const pieData = this.aggregateCategoryPie(policies, products);
        const barData = this.aggregateChannelBar(settlements, uwCases);

        this.lastFetchedAt = new Date().toLocaleString("zh-CN", { hour12: false });

        await this.$nextTick();
        this.ensureCharts();
        this.applyLine(labels, values);
        this.applyPie(pieData);
        this.applyBar(barData);

        // 渠道名过长时预留底部空间
        this.handleResize();
      } catch (e) {
        this.$message.error((e && e.response && e.response.data && e.response.data.detail) || e.message || "加载失败");
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.dash-root {
  position: relative;
  max-width: 1320px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
  padding: 8px 4px 32px;
  color: #1e293b;
}

.dash-bg {
  position: absolute;
  inset: 0;
  background: #fff;
  border-radius: 16px;
  pointer-events: none;
  z-index: 0;
}

.dash-head,
.dash-body {
  position: relative;
  z-index: 1;
}

.dash-head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
  padding: 4px 8px 0;
}

.dash-title {
  margin: 0;
  font-size: 1.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #0f172a;
}

.dash-sub {
  margin: 8px 0 0;
  font-size: 13px;
  color: #64748b;
}

.dash-head-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dash-updated {
  font-size: 12px;
  color: #94a3b8;
}

.glass {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
}

.kpi-row {
  margin-bottom: 8px !important;
}

.module-links-row {
  margin-bottom: 8px !important;
}

.module-link-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  margin-bottom: 16px;
  text-decoration: none;
  color: inherit;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.15s ease;
}

.module-link-card:hover {
  border-color: #bae6fd;
  box-shadow: 0 8px 28px rgba(2, 132, 199, 0.12);
  transform: translateY(-1px);
}

.module-link-card:active {
  transform: translateY(0);
}

.module-link-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.module-link-icon--doc {
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.14), rgba(148, 163, 184, 0.1));
  color: #0369a1;
}

.module-link-icon--chart {
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.16), rgba(56, 189, 248, 0.1));
  color: #0d9488;
}

.module-link-text {
  flex: 1;
  min-width: 0;
}

.module-link-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: 0.02em;
}

.module-link-desc {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.45;
}

.module-link-chevron {
  flex-shrink: 0;
  font-size: 14px;
  color: #94a3b8;
}

.module-link-card:hover .module-link-chevron {
  color: #0284c7;
}

.kpi-card {
  position: relative;
  overflow: hidden;
  padding: 18px 20px 16px;
  margin-bottom: 16px;
  min-height: 168px;
}

.kpi-card::after {
  content: "";
  position: absolute;
  top: -40%;
  right: -20%;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  opacity: 0.08;
  pointer-events: none;
}

.kpi-a::after {
  background: #38bdf8;
}
.kpi-b::after {
  background: #f472b6;
}
.kpi-c::after {
  background: #34d399;
}

.kpi-icon {
  position: absolute;
  top: 14px;
  right: 16px;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  opacity: 0.5;
  background: linear-gradient(135deg, rgba(2, 132, 199, 0.12), rgba(148, 163, 184, 0.08));
}

.kpi-card h3 {
  margin: 0 0 14px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.06em;
}

.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.kpi-label {
  margin: 0 0 4px;
  font-size: 12px;
  color: #94a3b8;
}

.kpi-value {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #0f172a;
  line-height: 1.15;
}

.kpi-value.accent {
  color: #0d9488;
}
.kpi-value.accent-soft {
  color: #0369a1;
}
.kpi-value.warn {
  color: #ca8a04;
}
.kpi-value.danger {
  color: #ea580c;
}

.kpi-foot {
  margin: 14px 0 0;
  font-size: 11px;
  color: #64748b;
  line-height: 1.4;
}

.chart-row {
  margin-top: 4px !important;
}

.chart-wrap {
  padding: 14px 16px 10px;
  margin-bottom: 16px;
}

.chart-wrap-wide {
  margin-bottom: 8px;
}

.chart-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.chart-head h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.chart-hint {
  font-size: 11px;
  color: #64748b;
}

.chart-box {
  height: 260px;
  width: 100%;
}

.chart-tall {
  height: 280px;
}

@media (max-width: 768px) {
  .dash-title {
    font-size: 1.35rem;
  }
  .kpi-value {
    font-size: 22px;
  }
}
</style>
