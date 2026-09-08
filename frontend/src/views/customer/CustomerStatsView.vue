<template>
  <div>
    <div class="card" style="margin-bottom: 16px;">
      <h2>客户统计</h2>
      <p class="muted">基于当前客户列表的等级、状态分布（数据来自接口，与列表一致）。</p>
    </div>
    <el-row :gutter="16">
      <el-col :xs="24" :md="8">
        <div class="stat-card">
          <p class="stat-label">客户总数</p>
          <p class="stat-num">{{ total }}</p>
        </div>
      </el-col>
      <el-col :xs="24" :md="8">
        <div class="stat-card">
          <p class="stat-label">在保客户</p>
          <p class="stat-num accent">{{ inForce }}</p>
        </div>
      </el-col>
      <el-col :xs="24" :md="8">
        <div class="stat-card">
          <p class="stat-label">已存档照片（条数）</p>
          <p class="stat-num">{{ withPhoto }}</p>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="16" style="margin-top: 16px;">
      <el-col :xs="24" :md="12">
        <div class="card">
          <h3>按客户等级</h3>
          <ul class="bar-list">
            <li v-for="r in byLevel" :key="r.name">
              <span class="name">{{ r.name }}</span>
              <div class="bar-wrap">
                <div class="bar" :style="{ width: r.pct + '%' }" />
              </div>
              <span class="cnt">{{ r.count }}</span>
            </li>
          </ul>
        </div>
      </el-col>
      <el-col :xs="24" :md="12">
        <div class="card">
          <h3>按客户状态</h3>
          <ul class="bar-list">
            <li v-for="r in byStatus" :key="r.name">
              <span class="name">{{ r.name }}</span>
              <div class="bar-wrap">
                <div class="bar bar-alt" :style="{ width: r.pct + '%' }" />
              </div>
              <span class="cnt">{{ r.count }}</span>
            </li>
          </ul>
        </div>
      </el-col>
    </el-row>
    <p v-if="error" class="err">{{ error }}</p>
  </div>
</template>

<script>
import { getCustomers } from "@/api";

export default {
  name: "CustomerStatsView",
  data() {
    return {
      rows: [],
      error: "",
    };
  },
  computed: {
    total() {
      return this.rows.length;
    },
    inForce() {
      return this.rows.filter((c) => (c.status || "") === "在保").length;
    },
    withPhoto() {
      return this.rows.filter((c) => (c.photo || "").trim()).length;
    },
    byLevel() {
      return this.aggregate("level");
    },
    byStatus() {
      return this.aggregate("status");
    },
  },
  created() {
    getCustomers()
      .then((res) => {
        this.rows = Array.isArray(res.data) ? res.data : [];
      })
      .catch(() => {
        this.error = "加载客户数据失败";
      });
  },
  methods: {
    aggregate(field) {
      const m = {};
      this.rows.forEach((c) => {
        const k = (c[field] || "未填").trim() || "未填";
        m[k] = (m[k] || 0) + 1;
      });
      const max = Math.max(1, ...Object.values(m));
      return Object.entries(m)
        .map(([name, count]) => ({ name, count, pct: Math.round((count / max) * 100) }))
        .sort((a, b) => b.count - a.count);
    },
  },
};
</script>

<style scoped>
.muted {
  margin: 0 0 8px;
  font-size: 13px;
  color: #64748b;
}
.stat-card {
  background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 18px;
  margin-bottom: 16px;
}
.stat-label {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}
.stat-num {
  margin: 6px 0 0;
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
}
.stat-num.accent {
  color: #059669;
}
.card h3 {
  margin: 0 0 12px;
  font-size: 15px;
}
.bar-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.bar-list li {
  display: grid;
  grid-template-columns: 72px 1fr 36px;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 13px;
}
.bar-list .name {
  color: #475569;
}
.bar-wrap {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}
.bar {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  min-width: 2px;
  transition: width 0.3s ease;
}
.bar-alt {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}
.cnt {
  text-align: right;
  color: #0f172a;
  font-variant-numeric: tabular-nums;
}
.err {
  color: #ef4444;
  font-size: 13px;
  margin-top: 12px;
}
</style>
