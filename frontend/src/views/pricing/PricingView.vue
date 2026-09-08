<template>
  <div class="page">
    <h1 class="page-title">费率定价与场景模拟</h1>
    <p class="page-subtitle">
      结合历史赔付经验、费用水平和目标利润率，对不同人群与渠道进行差异化定价模拟。
    </p>

    <div class="grid grid-2">
      <div class="card">
        <h2>定价参数输入（静态示意）</h2>
        <form class="form">
          <div class="form-row">
            <label>基础赔付率假设</label>
            <div class="form-inline">
              <input type="number" value="60" />
              <span class="form-unit">%</span>
            </div>
          </div>

          <div class="form-row">
            <label>费用率假设</label>
            <div class="form-inline">
              <input type="number" value="20" />
              <span class="form-unit">%</span>
            </div>
          </div>

          <div class="form-row">
            <label>目标利润率</label>
            <div class="form-inline">
              <input type="number" value="5" />
              <span class="form-unit">%</span>
            </div>
          </div>

          <div class="form-row">
            <label>风险加载因子</label>
            <select>
              <option>低风险客户（0%）</option>
              <option selected>标准客户（+5%）</option>
              <option>高风险客户（+15%）</option>
            </select>
          </div>

          <button type="button" class="btn-primary">计算建议费率（示意）</button>
        </form>
      </div>

      <div class="card">
        <h2>建议费率区间（示例结果）</h2>
        <table class="module-native-table">
          <thead>
            <tr>
              <th>客户风险等级</th>
              <th>建议费率区间</th>
              <th>说明</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>低风险</td>
              <td>0.8% ~ 1.0%</td>
              <td>健康状况良好、职业风险低、无不良记录。</td>
            </tr>
            <tr>
              <td>标准</td>
              <td>1.0% ~ 1.2%</td>
              <td>各项指标接近公司整体水平。</td>
            </tr>
            <tr>
              <td>高风险</td>
              <td>1.5% ~ 1.8%</td>
              <td>存在既往病史或投保行为异常，需要风险加载。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PricingView",
};
</script>
