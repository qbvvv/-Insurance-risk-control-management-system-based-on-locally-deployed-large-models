<template>
  <div class="card detail-card">
    <div class="detail-toolbar">
      <h2>客户详情</h2>
      <div v-if="!routeId" class="picker-row">
        <span class="picker-label">选择客户</span>
        <el-select
          v-model="pickedId"
          filterable
          placeholder="从列表选择或输入 id"
          style="width: 260px;"
          size="small"
          @change="goPicked"
        >
          <el-option v-for="c in pickList" :key="c.id" :label="`${c.name}（${c.customerNo}）`" :value="c.id" />
        </el-select>
      </div>
      <el-button v-else type="text" size="small" @click="$router.push('/customer/list')">返回列表</el-button>
    </div>

    <div v-loading="loading" class="detail-body">
      <template v-if="routeId && customer">
        <div class="detail-main">
          <div class="detail-with-photo">
            <div class="detail-avatar-block">
              <img
                class="detail-avatar"
                :src="resolvedPhotoSrc"
                alt="客户照片"
                @error="onPhotoError"
              />
            </div>
            <div class="detail-grid">
            <div class="cell"><span class="k">客户编号</span><span class="v">{{ customer.customerNo }}</span></div>
            <div class="cell"><span class="k">姓名</span><span class="v">{{ customer.name }}</span></div>
            <div class="cell"><span class="k">性别</span><span class="v">{{ customer.gender || "—" }}</span></div>
            <div class="cell"><span class="k">证件类型</span><span class="v">{{ customer.idType }}</span></div>
            <div class="cell"><span class="k">证件号</span><span class="v">{{ customer.idNo }}</span></div>
            <div class="cell"><span class="k">手机</span><span class="v">{{ customer.phone }}</span></div>
            <div class="cell"><span class="k">职业</span><span class="v">{{ customer.occupation || "—" }}</span></div>
            <div class="cell"><span class="k">等级</span><span class="v">{{ customer.level }}</span></div>
            <div class="cell"><span class="k">状态</span><span class="v">{{ customer.status }}</span></div>
            <div class="cell span2"><span class="k">联系地址</span><span class="v">{{ customer.address || "—" }}</span></div>
            <div class="cell span2"><span class="k">备注</span><span class="v">{{ customer.remark || "—" }}</span></div>
            <div class="cell"><span class="k">建档日期</span><span class="v">{{ customer.createdAt || "—" }}</span></div>
            </div>
          </div>
        </div>

        <div class="policies-block">
          <h3 class="policies-title">关联保单</h3>
          <p v-if="policiesError" class="policies-err">{{ policiesError }}</p>
          <div v-else v-loading="policiesLoading" class="policies-body">
            <div v-if="customerPolicies.length" class="policies-table-wrap">
            <table class="module-native-table">
              <thead>
                <tr>
                  <th>保单号</th>
                  <th>产品名称</th>
                  <th>保费</th>
                  <th>保额</th>
                  <th>起止日期</th>
                  <th>状态</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in customerPolicies" :key="p.id">
                  <td>{{ p.policyNo }}</td>
                  <td>{{ p.productName }}</td>
                  <td>{{ p.premium }}</td>
                  <td>{{ p.coverageAmount }}</td>
                  <td>{{ p.startDate }} ~ {{ p.endDate }}</td>
                  <td>{{ p.status }}</td>
                </tr>
              </tbody>
            </table>
            </div>
            <p v-else class="policies-empty">该客户暂无保单记录（保单以客户编号关联，可在「保单管理」中维护）。</p>
          </div>
        </div>
      </template>
      <p v-else-if="routeId && !loading && loadError" class="err">{{ loadError }}</p>
      <p v-else-if="!routeId" class="hint muted">请从上方下拉选择客户，或在「客户列表」中点击「详情」进入。</p>
    </div>
  </div>
</template>

<script>
import { getCustomer, getCustomers, getPolicies } from "@/api";

const DEFAULT_AVATAR_SVG = encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" width="160" height="160" viewBox="0 0 160 160">
    <rect fill="#e8eef5" width="160" height="160"/>
    <circle cx="80" cy="58" r="24" fill="#94a3b8"/>
    <ellipse cx="80" cy="118" rx="44" ry="28" fill="#94a3b8"/>
  </svg>`
);

export default {
  name: "CustomerDetailView",
  data() {
    return {
      customer: null,
      loading: false,
      loadError: "",
      pickList: [],
      pickedId: "",
      photoLoadFailed: false,
      defaultAvatarSrc: `data:image/svg+xml,${DEFAULT_AVATAR_SVG}`,
      customerPolicies: [],
      policiesLoading: false,
      policiesError: "",
    };
  },
  computed: {
    routeId() {
      return (this.$route.params.id || "").trim();
    },
    resolvedPhotoSrc() {
      const raw = (this.customer && this.customer.photo) || "";
      const p = String(raw).trim();
      if (this.photoLoadFailed || !p) return this.defaultAvatarSrc;
      return p;
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
    getCustomers()
      .then((res) => {
        this.pickList = Array.isArray(res.data) ? res.data : [];
        if (!this.routeId && this.pickList.length === 1) {
          this.$router.replace(`/customer/detail/${this.pickList[0].id}`).catch(() => {});
        }
      })
      .catch(() => {});
  },
  methods: {
    goPicked(id) {
      if (!id) return;
      this.$router.push(`/customer/detail/${id}`).catch(() => {});
    },
    onPhotoError() {
      this.photoLoadFailed = true;
    },
    loadRelatedPolicies(customerNo) {
      this.customerPolicies = [];
      this.policiesError = "";
      if (!customerNo) return;
      this.policiesLoading = true;
      getPolicies()
        .then((res) => {
          const all = Array.isArray(res.data) ? res.data : [];
          const no = String(customerNo).trim();
          this.customerPolicies = all.filter((p) => (p.customerNo || "").trim() === no);
        })
        .catch(() => {
          this.policiesError = "加载关联保单失败，请确认后端已启动。";
        })
        .finally(() => {
          this.policiesLoading = false;
        });
    },
    load() {
      this.photoLoadFailed = false;
      this.customer = null;
      this.loadError = "";
      this.customerPolicies = [];
      this.policiesError = "";
      if (!this.routeId) {
        this.pickedId = "";
        return;
      }
      this.pickedId = this.routeId;
      this.loading = true;
      getCustomer(this.routeId)
        .then((res) => {
          this.customer = res.data || null;
          if (this.customer && this.customer.customerNo) {
            this.loadRelatedPolicies(this.customer.customerNo);
          }
        })
        .catch((e) => {
          this.loadError = (e.response && e.response.data && e.response.data.detail) || e.message || "加载失败";
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
.detail-main {
  display: block;
}
.detail-with-photo {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 24px;
}
.detail-avatar-block {
  flex-shrink: 0;
}
.detail-avatar {
  display: block;
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f1f5f9;
}
.detail-grid {
  flex: 1;
  min-width: 240px;
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 20px;
}
.detail-grid .cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.detail-grid .span2 {
  grid-column: span 2;
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
.policies-block {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}
.policies-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}
.policies-err {
  margin: 0;
  font-size: 13px;
  color: #ef4444;
}
.policies-empty {
  margin: 0;
  font-size: 13px;
  color: #94a3b8;
}
.policies-table-wrap {
  overflow-x: auto;
}
.hint {
  margin-top: 20px;
  font-size: 13px;
  color: #475569;
}
.hint.muted {
  color: #94a3b8;
}
.hint .link {
  color: #2563eb;
  margin-right: 6px;
}
.err {
  color: #ef4444;
  font-size: 14px;
}
@media (max-width: 720px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .detail-grid .span2 {
    grid-column: span 1;
  }
  .policies-table-wrap {
    margin: 0 -4px;
  }
}
</style>
