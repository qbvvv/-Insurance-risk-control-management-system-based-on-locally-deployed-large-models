<template>
  <div class="page">
    <h1 class="page-title">规则引擎与策略配置</h1>
    <p class="page-subtitle">
      统一管理承保、理赔、反欺诈等业务规则，实现业务人员可视化配置与快速上线。
    </p>

    <div class="grid grid-2">
      <div class="card">
        <h2>规则列表（示例）</h2>
        <table class="module-native-table">
          <thead>
            <tr>
              <th>规则编号</th>
              <th>规则名称</th>
              <th>规则类型</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>UW_RISK_001</td>
              <td>BMI 超标人工核保</td>
              <td>承保规则</td>
              <td><span class="tag tag-success">启用</span></td>
            </tr>
            <tr>
              <td>CL_FRAUD_003</td>
              <td>短期内多次出险预警</td>
              <td>理赔规则</td>
              <td><span class="tag tag-success">启用</span></td>
            </tr>
            <tr>
              <td>CHN_QUAL_002</td>
              <td>渠道退保率超阈值预警</td>
              <td>渠道规则</td>
              <td><span class="tag tag-warning">草稿</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <h2>规则配置表单（静态示意）</h2>
        <form class="form">
          <div class="form-row">
            <label>规则名称</label>
            <input type="text" placeholder="如：BMI 超标人工核保" />
          </div>

          <div class="form-row">
            <label>规则适用环节</label>
            <select>
              <option>承保</option>
              <option>理赔</option>
              <option>续保</option>
              <option>反欺诈</option>
            </select>
          </div>

          <div class="form-row">
            <label>规则表达式（示意）</label>
            <textarea
              rows="4"
              placeholder="例如：if BMI &gt; 30 and 年龄 &gt; 45 then 核保结论 = '人工核保'"
            ></textarea>
          </div>

          <button type="button" class="btn-primary">模拟保存规则（静态）</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RuleView",
};
</script>
