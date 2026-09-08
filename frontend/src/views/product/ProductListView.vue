<template>
  <div>
    <p class="page-hint">
      产品编号由后端按日自动生成；每个标准目录产品（险种 + 名称）仅可建档一次；参考保费与保额上限由目录带出。产品说明可由目录预填，支持在编辑时修改。
    </p>

    <div class="card" style="margin-bottom: 16px;">
      <h2>新增 / 编辑产品</h2>
      <el-form
        ref="productForm"
        :model="form"
        :rules="rules"
        label-width="108px"
        size="small"
        @submit.native.prevent="handleSubmit"
      >
        <div class="form-grid">
          <el-form-item v-if="editingId" label="产品编号">
            <el-input :value="form.productNo" disabled placeholder="保存后由系统生成" />
          </el-form-item>
          <el-form-item label="险种类别" prop="category">
            <el-select
              v-model="form.category"
              placeholder="请选择险种类别"
              clearable
              style="width: 100%;"
              @change="onCategoryChange"
            >
              <el-option v-for="c in categoryOptions" :key="c" :label="c" :value="c" />
            </el-select>
          </el-form-item>
          <el-form-item label="产品名称" prop="productName">
            <el-select
              v-model="form.productName"
              placeholder="请先选险种，再选产品"
              filterable
              style="width: 100%;"
              :disabled="!form.category"
              @change="onProductNameChange"
            >
              <el-option
                v-for="row in nameOptionsFiltered"
                :key="row.productName"
                :label="row.productName"
                :value="row.productName"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="参考保费">
            <div class="readonly-field">{{ form.premiumGuide || "—" }}</div>
          </el-form-item>
          <el-form-item label="保额上限">
            <div class="readonly-field">{{ form.coverageCap || "—" }}</div>
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" placeholder="请选择" style="width: 100%;">
              <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="产品说明" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            maxlength="500"
            show-word-limit
            placeholder="选择目录产品后将自动带出说明，可按需修改"
          />
        </el-form-item>
        <el-form-item class="form-actions-row">
          <el-button type="primary" native-type="submit" :loading="submitting">
            {{ editingId ? "保存修改" : "新增产品" }}
          </el-button>
          <el-button v-if="editingId" @click="resetForm">取消编辑</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="card">
      <h2>产品列表</h2>
      <el-table class="module-table" :data="products" border size="small" style="width: 100%;">
        <el-table-column prop="productNo" label="产品编号" width="150" />
        <el-table-column prop="productName" label="产品名称" min-width="140" />
        <el-table-column prop="category" label="险种类别" width="100" />
        <el-table-column prop="premiumGuide" label="参考保费" width="130" />
        <el-table-column prop="coverageCap" label="保额上限" width="100" />
        <el-table-column prop="description" label="产品说明" min-width="180" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" />
        <el-table-column label="操作" width="232" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="module-table-ops">
              <el-button type="primary" size="mini" @click="goProductDetail(scope.row)">详情</el-button>
              <el-button type="primary" size="mini" @click="editProduct(scope.row)">编辑</el-button>
              <el-button type="danger" size="mini" @click="removeProduct(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <p v-if="error" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { createProduct, deleteProduct, getProductCatalog, getProducts, updateProduct } from "@/api";

export default {
  name: "ProductListView",
  data() {
    return {
      products: [],
      catalog: [],
      error: "",
      catalogError: "",
      editingId: null,
      submitting: false,
      statusOptions: ["在售", "停售"],
      form: {
        productNo: "",
        productName: "",
        category: "",
        description: "",
        premiumGuide: "",
        coverageCap: "0",
        status: "在售",
      },
      rules: {
        category: [{ required: true, message: "请选择险种类别", trigger: "change" }],
        productName: [{ required: true, message: "请选择产品名称", trigger: "change" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
    };
  },
  computed: {
    effectiveCatalog() {
      const base = this.catalog.slice();
      if (
        this.editingId &&
        this.form.productName &&
        !base.some((r) => r.productName === this.form.productName)
      ) {
        base.push({
          productName: this.form.productName,
          category: this.form.category || "其他",
          premiumGuide: this.form.premiumGuide || "",
          coverageCap: this.form.coverageCap || "",
          description: this.form.description || "",
        });
      }
      return base;
    },
    categoryOptions() {
      const s = new Set();
      const order = [];
      this.effectiveCatalog.forEach((row) => {
        if (row.category && !s.has(row.category)) {
          s.add(row.category);
          order.push(row.category);
        }
      });
      return order;
    },
    nameOptionsFiltered() {
      if (!this.form.category) return [];
      let rows = this.effectiveCatalog.filter((r) => r.category === this.form.category);
      if (!this.editingId) {
        rows = rows.filter((r) => !this.isCatalogRowOnboarded(r));
      }
      return rows;
    },
  },
  created() {
    this.fetchCatalog();
    this.fetchProducts();
  },
  methods: {
    goProductDetail(row) {
      this.$router.push(`/product/detail/${row.id}`);
    },
    fetchCatalog() {
      getProductCatalog()
        .then((res) => {
          this.catalog = Array.isArray(res.data) ? res.data : [];
          this.catalogError = "";
        })
        .catch(() => {
          this.catalogError = "加载产品目录失败";
        });
    },
    fetchProducts() {
      this.error = "";
      getProducts()
        .then((res) => {
          this.products = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取产品列表失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        });
    },
    applyCatalogByProductName(name) {
      const row = this.effectiveCatalog.find((r) => r.productName === name);
      if (!row) return;
      this.form.category = row.category;
      this.form.premiumGuide = row.premiumGuide;
      this.form.coverageCap = row.coverageCap;
      this.form.description = row.description || "";
    },
    isCatalogRowOnboarded(row) {
      return this.products.some(
        (p) => p.productName === row.productName && p.category === row.category
      );
    },
    onCategoryChange() {
      this.form.productName = "";
      this.form.premiumGuide = "";
      this.form.coverageCap = "0";
      this.form.description = "";
    },
    onProductNameChange(name) {
      if (name) this.applyCatalogByProductName(name);
    },
    resetForm() {
      this.editingId = null;
      this.form = {
        productNo: "",
        productName: "",
        category: "",
        description: "",
        premiumGuide: "",
        coverageCap: "0",
        status: "在售",
      };
      this.$nextTick(() => {
        if (this.$refs.productForm) this.$refs.productForm.clearValidate();
      });
    },
    handleSubmit() {
      this.$refs.productForm.validate((valid) => {
        if (!valid) return;
        this.submitting = true;
        const done = () => {
          this.submitting = false;
        };
        if (this.editingId) {
          updateProduct(this.editingId, {
            productName: this.form.productName,
            status: this.form.status,
            description: this.form.description,
          })
            .then(() => {
              this.$message.success("保存成功");
              this.fetchProducts();
              this.resetForm();
            })
            .catch((err) => {
              const d = err.response?.data?.detail;
              const msg = typeof d === "string" ? d : err.message;
              this.$message.error(err.response?.status === 409 ? msg : "更新失败：" + msg);
            })
            .finally(done);
        } else {
          createProduct({
            productName: this.form.productName,
            status: this.form.status,
            description: (this.form.description || "").trim() || undefined,
          })
            .then(() => {
              this.$message.success("新增成功");
              this.fetchProducts();
              this.resetForm();
            })
            .catch((err) => {
              const d = err.response?.data?.detail;
              const msg = typeof d === "string" ? d : err.message;
              this.$message.error(err.response?.status === 409 ? msg : "新增失败：" + msg);
            })
            .finally(done);
        }
      });
    },
    editProduct(p) {
      this.editingId = p.id;
      this.form = {
        productNo: p.productNo || "",
        productName: p.productName || "",
        category: p.category || "",
        description: p.description || "",
        premiumGuide: p.premiumGuide || "",
        coverageCap: p.coverageCap || "0",
        status: p.status || "在售",
      };
      if (this.form.productName && !this.form.premiumGuide) {
        this.applyCatalogByProductName(this.form.productName);
      }
      this.$nextTick(() => {
        if (this.$refs.productForm) this.$refs.productForm.clearValidate();
      });
    },
    removeProduct(p) {
      this.$confirm(`确定删除产品：${p.productName}（${p.productNo}）？`, "提示", { type: "warning" })
        .then(() => deleteProduct(p.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchProducts();
        })
        .catch((err) => {
          if (err === "cancel" || err === "close") return;
          this.$message.error("删除失败：" + (err.response?.data?.detail || err.message));
        });
    },
  },
};
</script>

<style scoped>
.page-hint {
  margin: 0 0 16px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.55;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0 16px;
}
.form-actions-row {
  margin-bottom: 0;
}
.form-actions-row :deep(.el-form-item__content) {
  margin-left: 108px !important;
}
.readonly-field {
  font-size: 13px;
  color: #606266;
  line-height: 32px;
  padding: 0 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  min-height: 32px;
  box-sizing: border-box;
}
</style>
