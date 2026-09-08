<template>
  <div class="page">
    <h1 class="page-title">风控与风险评估中心</h1>
    <p class="page-subtitle">
      汇总投保、理赔全过程风险信息，支持对客户、保单、渠道进行多维度风险评分。
    </p>

    <div class="grid grid-2">
      <div class="card">
        <h2>风险雷达（概念示意）</h2>
        <ul class="feature-list">
          <li>承保风险：70 分（偏高）</li>
          <li>道德风险：45 分（中等）</li>
          <li>操作风险：30 分（较低）</li>
          <li>合规风险：55 分（中等）</li>
          <li>集中度风险：65 分（偏高）</li>
        </ul>
        <p class="kpi-footnote">
          * 实际系统中可通过图表组件展示雷达图，本页面为静态原型示意。
        </p>
      </div>

      <div class="card">
        <h2>高风险预警列表（示意数据）</h2>
        <table class="module-native-table">
          <thead>
            <tr>
              <th>预警编号</th>
              <th>对象类型</th>
              <th>对象名称</th>
              <th>风险等级</th>
              <th>预警原因</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>AL2026030601</td>
              <td>客户</td>
              <td>张某某</td>
              <td><span class="tag tag-danger">高</span></td>
              <td>短期内多次投保高保额重疾险</td>
            </tr>
            <tr>
              <td>AL2026030602</td>
              <td>渠道</td>
              <td>XX中介公司</td>
              <td><span class="tag tag-warning">中</span></td>
              <td>退保率显著高于同业平均水平</td>
            </tr>
            <tr>
              <td>AL2026030603</td>
              <td>地区</td>
              <td>某地市</td>
              <td><span class="tag tag-warning">中</span></td>
              <td>特定病种理赔件数异常集中</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RiskView",
};
</script>
