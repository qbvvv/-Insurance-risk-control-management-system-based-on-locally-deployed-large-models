<template>
  <div class="page">
    <h1 class="page-title">代理人 / 团队管理</h1>
    <p class="page-subtitle">
      管理销售团队组织架构与业绩信息，数据来自后端接口（若未启动则展示示例数据）。
    </p>

    <div class="grid grid-2">
      <div class="card">
        <h2>团队组织架构（示意）</h2>
        <el-table class="module-table" :data="teams" border size="small" style="width: 100%;">
          <el-table-column prop="name" label="姓名" width="100"></el-table-column>
          <el-table-column prop="title" label="职级" width="100"></el-table-column>
          <el-table-column prop="parent" label="上级"></el-table-column>
        </el-table>
      </div>

      <div class="card">
        <h2>个人 / 团队业绩（示意）</h2>
        <el-table class="module-table" :data="performances" border size="small" style="width: 100%;">
          <el-table-column prop="name" label="对象"></el-table-column>
          <el-table-column prop="premium" label="保费（万元）" width="120"></el-table-column>
          <el-table-column prop="rate" label="KPI 达成率" width="120"></el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script>
import { getAgentPerformanceSummary, getAgentTeams } from "@/api";

export default {
  name: "AgentTeamView",
  data() {
    return {
      teams: [
        { name: "王总监团队", title: "营销总监", parent: "-" },
        { name: "李经理团队", title: "营业部经理", parent: "王总监团队" },
        { name: "张主管", title: "营业部主管", parent: "李经理团队" },
      ],
      performances: [
        { name: "王总监团队", premium: 580, rate: "112%" },
        { name: "李经理团队", premium: 320, rate: "96%" },
        { name: "张主管", premium: 120, rate: "88%" },
      ],
    };
  },
  created() {
    this.fetchAgentTeams();
    this.fetchPerformanceSummary();
  },
  methods: {
    fetchAgentTeams() {
      getAgentTeams()
        .then((res) => {
          this.teams = Array.isArray(res.data) ? res.data : this.teams;
        })
        .catch(() => {
          // 保留示例数据：通常是后端未启动或接口路径不通
        });
    },
    fetchPerformanceSummary() {
      getAgentPerformanceSummary()
        .then((res) => {
          this.performances = Array.isArray(res.data) ? res.data : this.performances;
        })
        .catch(() => {
          // 保留示例数据
        });
    },
  },
};
</script>
