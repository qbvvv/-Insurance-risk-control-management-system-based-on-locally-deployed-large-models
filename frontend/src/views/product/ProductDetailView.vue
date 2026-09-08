<template>
  <div class="card detail-card">
    <div class="detail-toolbar">
      <h2>产品详情</h2>
      <div v-if="!routeId" class="picker-row">
        <span class="picker-label">选择产品</span>
        <el-select
          v-model="pickedId"
          filterable
          placeholder="从列表选择"
          style="width: 320px;"
          size="small"
          @change="goPicked"
        >
          <el-option
            v-for="p in pickList"
            :key="p.id"
            :label="`${p.productName}（${p.productNo}）`"
            :value="p.id"
          />
        </el-select>
      </div>
      <el-button v-else type="text" size="small" @click="$router.push('/product/list')">返回列表</el-button>
    </div>

    <div v-loading="loading" class="detail-body">
      <template v-if="routeId && product">
        <div class="detail-grid">
          <div class="cell"><span class="k">产品编号</span><span class="v">{{ product.productNo }}</span></div>
          <div class="cell"><span class="k">产品名称</span><span class="v">{{ product.productName }}</span></div>
          <div class="cell"><span class="k">险种类别</span><span class="v">{{ product.category || "—" }}</span></div>
          <div class="cell"><span class="k">状态</span><span class="v">{{ product.status }}</span></div>
          <div class="cell"><span class="k">参考保费</span><span class="v">{{ product.premiumGuide || "—" }}</span></div>
          <div class="cell"><span class="k">保额上限</span><span class="v">{{ product.coverageCap || "—" }}</span></div>
          <div class="cell"><span class="k">建档日期</span><span class="v">{{ product.createdAt || "—" }}</span></div>
        </div>
        <div class="desc-block">
          <h3 class="desc-title">产品说明</h3>
          <p class="desc-body">{{ product.description && product.description.trim() ? product.description : "暂无说明，可在「产品列表」中编辑该产品补充。" }}</p>
        </div>
      </template>
      <p v-else-if="routeId && !loading && loadError" class="err">{{ loadError }}</p>
      <p v-else-if="!routeId" class="hint muted">请从上方下拉选择产品，或在「产品列表」中点击「详情」进入。</p>
    </div>
  </div>
</template>

<script>
import { getProduct, getProducts } from "@/api";

export default {
  name: "ProductDetailView",
  data() {
    return {
      product: null,
      loading: false,
      loadError: "",
      pickList: [],
      pickedId: "",
    };
  },
  computed: {
    routeId() {
      return (this.$route.params.id || "").trim();
    },
  },
  watch: {
    $route: {
      handler() {
        this.load();
      },
      immediate: true,
    },
  },
  created() {
    getProducts()
      .then((res) => {
        this.pickList = Array.isArray(res.data) ? res.data : [];
        if (!this.routeId && this.pickList.length === 1) {
          this.$router.replace(`/product/detail/${this.pickList[0].id}`).catch(() => {});
        }
      })
      .catch(() => {});
  },
  methods: {
    goPicked(id) {
      if (!id) return;
      this.$router.push(`/product/detail/${id}`).catch(() => {});
    },
    load() {
      this.product = null;
      this.loadError = "";
      if (!this.routeId) {
        this.pickedId = "";
        return;
      }
      this.pickedId = this.routeId;
      this.loading = true;
      getProduct(this.routeId)
        .then((res) => {
          this.product = res.data || null;
        })
        .catch((e) => {
          this.loadError =
            (e.response && e.response.data && e.response.data.detail) || e.message || "加载失败";
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>

<style scoped>
.detail-card {
  padding: 16px 20px 24px;
}
.detail-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-toolbar h2 {
  margin: 0;
  font-size: 18px;
}
.picker-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.picker-label {
  font-size: 13px;
  color: #64748b;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 20px;
}
.detail-grid .cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.detail-grid .k {
  font-size: 12px;
  color: #64748b;
}
.detail-grid .v {
  font-size: 14px;
  color: #0f172a;
  word-break: break-all;
}
.desc-block {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}
.desc-title {
  margin: 0 0 10px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}
.desc-body {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: #334155;
  white-space: pre-wrap;
}
.hint {
  margin-top: 8px;
  font-size: 13px;
  color: #475569;
}
.hint.muted {
  color: #94a3b8;
}
.err {
  color: #ef4444;
  font-size: 14px;
}
@media (max-width: 720px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
