<template>
  <div>
    <base-card>
      <div class="list-head">
        <h2>客户列表</h2>
        <el-button type="primary" size="small" @click="openAddDialog">新增客户</el-button>
      </div>

      <div class="search-bar card-inner">
        <span class="search-title">客户查找</span>
        <el-input v-model="filters.name" placeholder="姓名" clearable size="small" class="search-field" />
        <el-input v-model="filters.phone" placeholder="手机号" clearable size="small" class="search-field" />
        <el-input v-model="filters.idNo" placeholder="证件号" clearable size="small" class="search-field" />
        <el-button size="small" @click="resetFilters">重置</el-button>
      </div>

      <el-table
        class="module-table"
        :data="filteredCustomers"
        border
        size="small"
        style="width: 100%;"
        v-loading="loading"
      >
        <el-table-column prop="customerNo" label="客户编号" width="120" />
        <el-table-column prop="name" label="姓名" width="96" />
        <el-table-column label="性别" width="56">
          <template slot-scope="scope">{{ scope.row.gender || "—" }}</template>
        </el-table-column>
        <el-table-column prop="idType" label="证件类型" width="120" show-overflow-tooltip />
        <el-table-column prop="idNo" label="证件号" min-width="140" show-overflow-tooltip />
        <el-table-column prop="phone" label="联系方式" width="120" />
        <el-table-column prop="occupation" label="职业" min-width="120" show-overflow-tooltip />
        <el-table-column prop="level" label="等级" width="72" />
        <el-table-column prop="status" label="状态" width="80" />
        <el-table-column label="操作" width="232" align="center" fixed="right">
          <template slot-scope="scope">
            <div class="module-table-ops">
              <el-button type="primary" size="mini" @click="goCustomerDetail(scope.row)">详情</el-button>
              <el-button type="primary" size="mini" @click="openEditDialog(scope.row)">编辑</el-button>
              <el-button type="danger" size="mini" @click="removeCustomer(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
        <template slot="empty">
          <span v-if="!customers.length">暂无客户数据</span>
          <span v-else>无匹配结果，请调整查找条件</span>
        </template>
      </el-table>
      <p v-if="error" style="font-size: 12px; color: #f56c6c; margin-top: 8px;">{{ error }}</p>
    </base-card>

    <el-dialog
      :title="dialogMode === 'add' ? '新增客户' : '编辑客户'"
      :visible.sync="dialogVisible"
      width="720px"
      destroy-on-close
      @closed="onDialogClosed"
    >
      <el-form ref="customerForm" :model="form" :rules="rules" label-width="100px" size="small" class="dialog-form">
        <el-form-item label="照片" prop="photo">
          <el-upload
            ref="photoUpload"
            class="photo-upload"
            action=""
            :auto-upload="false"
            :limit="1"
            accept="image/*"
            :on-change="onPhotoChange"
            :on-remove="onPhotoRemove"
            list-type="text"
          >
            <el-button size="small" type="default" :loading="uploadingPhoto">选择本地图片并上传</el-button>
            <span slot="tip" class="el-upload__tip">从本机选择图片上传至档案（可选）；详情页展示照片，列表不展示头像。</span>
          </el-upload>
          <p v-if="form.photo" class="photo-saved">已存档，可在客户详情查看</p>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" maxlength="30" show-word-limit clearable />
        </el-form-item>
        <el-form-item label="证件类型" prop="idType">
          <el-select v-model="form.idType" style="width: 100%;" @change="onIdTypeChange">
            <el-option v-for="t in idTypeOptions" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="证件号码" prop="idNo">
          <el-input v-model="form.idNo" clearable />
        </el-form-item>
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="form.phone" maxlength="11" clearable />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" style="width: 100%;">
            <el-option v-for="g in genderOptions" :key="g" :label="g" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="职业" prop="occupation">
          <el-select v-model="form.occupation" filterable allow-create style="width: 100%;">
            <el-option v-for="o in occupationOptions" :key="o" :label="o" :value="o" />
          </el-select>
        </el-form-item>
        <el-form-item label="客户等级" prop="level">
          <el-select v-model="form.level" style="width: 100%;">
            <el-option v-for="l in levelOptions" :key="l" :label="l" :value="l" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" style="width: 100%;">
            <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系地址" prop="address">
          <el-input v-model="form.address" clearable />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="2" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitDialog">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import BaseCard from "@/components/BaseCard.vue";
import {
  getCustomers,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  uploadCustomerPhoto,
} from "@/api";

function isValidChineseId18(id) {
  if (!id || typeof id !== "string") return false;
  const s = id.trim().toUpperCase();
  if (s.length !== 18) return false;
  const re = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$/;
  if (!re.test(s)) return false;
  const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2];
  const checkCodes = "10X98765432";
  let sum = 0;
  for (let i = 0; i < 17; i++) sum += parseInt(s[i], 10) * weights[i];
  return checkCodes[sum % 11] === s[17];
}

function isValidChineseId15(id) {
  if (!id || typeof id !== "string") return false;
  const s = id.trim();
  if (s.length !== 15) return false;
  return /^[1-9]\d{7}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}$/.test(s);
}

export default {
  name: "CustomerListView",
  components: { BaseCard },
  data() {
    const validateName = (rule, value, callback) => {
      const v = (value || "").trim();
      if (!v) {
        callback(new Error("请输入姓名"));
        return;
      }
      if (v.length < 2 || v.length > 30) {
        callback(new Error("姓名长度为 2～30 个字符"));
        return;
      }
      if (/^\d+$/.test(v)) {
        callback(new Error("姓名不能为纯数字"));
        return;
      }
      if (!/^[\u4e00-\u9fa5a-zA-Z·．.\s]{2,30}$/.test(v)) {
        callback(new Error("姓名仅支持中文、字母、间隔号或空格"));
        return;
      }
      callback();
    };

    const validatePhone = (rule, value, callback) => {
      const v = (value || "").trim();
      if (!v) {
        callback(new Error("请输入手机号"));
        return;
      }
      if (!/^1[3-9]\d{9}$/.test(v)) {
        callback(new Error("请输入有效的 11 位中国大陆手机号"));
        return;
      }
      callback();
    };

    return {
      customers: [],
      loading: false,
      error: "",
      filters: {
        name: "",
        phone: "",
        idNo: "",
      },
      dialogVisible: false,
      dialogMode: "add",
      editingId: null,
      submitting: false,
      uploadingPhoto: false,
      idTypeOptions: ["身份证", "护照", "港澳居民来往内地通行证", "台湾居民来往大陆通行证", "其他"],
      genderOptions: ["未知", "男", "女"],
      occupationOptions: [
        "国家机关负责人",
        "专业技术人员",
        "办事人员",
        "商业服务业人员",
        "农林牧渔水利业",
        "生产运输工人",
        "军人",
        "退休",
        "学生",
        "无业",
        "不便分类",
      ],
      levelOptions: ["普通", "VIP", "白金", "钻石"],
      statusOptions: ["在保", "失效", "待续保"],
      form: {
        customerNo: "",
        name: "",
        idType: "身份证",
        idNo: "",
        phone: "",
        gender: "未知",
        occupation: "",
        level: "普通",
        status: "在保",
        photo: "",
        address: "",
        remark: "",
      },
      rules: {
        name: [{ required: true, validator: validateName, trigger: "blur" }],
        idType: [{ required: true, message: "请选择证件类型", trigger: "change" }],
        phone: [{ required: true, validator: validatePhone, trigger: "blur" }],
        occupation: [{ required: true, message: "请选择或填写职业", trigger: "change" }],
        level: [{ required: true, message: "请选择客户等级", trigger: "change" }],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
      },
    };
  },
  computed: {
    filteredCustomers() {
      let list = this.customers;
      const n = (this.filters.name || "").trim();
      const p = (this.filters.phone || "").trim();
      const id = (this.filters.idNo || "").trim();
      if (n) list = list.filter((c) => (c.name || "").includes(n));
      if (p) list = list.filter((c) => (c.phone || "").includes(p));
      if (id) list = list.filter((c) => (c.idNo || "").includes(id));
      return list;
    },
  },
  created() {
    this.$set(this.rules, "idNo", [{ required: true, validator: this.validateIdNoRule, trigger: "blur" }]);
    this.fetchCustomers();
  },
  methods: {
    goCustomerDetail(row) {
      this.$router.push(`/customer/detail/${row.id}`);
    },
    resetFilters() {
      this.filters = { name: "", phone: "", idNo: "" };
    },
    validateIdNoRule(rule, value, callback) {
      const v = (value || "").trim();
      if (!v) {
        callback(new Error("请输入证件号码"));
        return;
      }
      const t = this.form.idType;
      if (t === "身份证") {
        if (v.length === 18) {
          if (!isValidChineseId18(v)) {
            callback(new Error("身份证号格式或校验位不正确，请核对 18 位号码"));
            return;
          }
        } else if (v.length === 15) {
          if (!isValidChineseId15(v)) {
            callback(new Error("15 位身份证格式不正确"));
            return;
          }
        } else {
          callback(new Error("身份证须为 15 位或 18 位"));
          return;
        }
        callback();
        return;
      }
      if (t === "护照" && (v.length < 5 || v.length > 20)) {
        callback(new Error("护照号码长度一般为 5～20 位"));
        return;
      }
      if (v.length < 4 || v.length > 30) {
        callback(new Error("证件号码长度为 4～30 位"));
        return;
      }
      callback();
    },
    onIdTypeChange() {
      this.$nextTick(() => {
        if (this.$refs.customerForm) this.$refs.customerForm.validateField("idNo");
      });
    },
    clearPhotoUpload() {
      this.$nextTick(() => {
        if (this.$refs.photoUpload) this.$refs.photoUpload.clearFiles();
      });
    },
    onPhotoChange(file) {
      const raw = file.raw;
      if (!raw) return;
      if (!raw.type || !raw.type.startsWith("image/")) {
        this.$message.warning("请选择图片文件");
        this.clearPhotoUpload();
        return;
      }
      this.uploadingPhoto = true;
      uploadCustomerPhoto(raw)
        .then((res) => {
          const url = res.data && res.data.photoUrl;
          if (url) {
            this.form.photo = url;
            this.$message.success("照片已上传并存档");
          }
        })
        .catch((e) => {
          this.$message.error((e.response && e.response.data && e.response.data.detail) || e.message || "上传失败");
          this.clearPhotoUpload();
        })
        .finally(() => {
          this.uploadingPhoto = false;
        });
    },
    onPhotoRemove() {
      this.form.photo = "";
    },
    openAddDialog() {
      this.dialogMode = "add";
      this.editingId = null;
      this.resetFormModel();
      this.clearPhotoUpload();
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.customerForm) this.$refs.customerForm.clearValidate();
      });
    },
    openEditDialog(c) {
      this.dialogMode = "edit";
      this.editingId = c.id;
      this.form = {
        customerNo: c.customerNo || "",
        name: c.name || "",
        idType: c.idType || "身份证",
        idNo: c.idNo || "",
        phone: c.phone || "",
        gender: c.gender || "未知",
        occupation: c.occupation || "",
        level: c.level || "普通",
        status: c.status || "在保",
        photo: c.photo || "",
        address: c.address || "",
        remark: c.remark || "",
      };
      if (!this.occupationOptions.includes(this.form.occupation) && this.form.occupation) {
        this.occupationOptions = [...this.occupationOptions, this.form.occupation];
      }
      this.clearPhotoUpload();
      this.dialogVisible = true;
      this.$nextTick(() => {
        if (this.$refs.customerForm) this.$refs.customerForm.clearValidate();
      });
    },
    onDialogClosed() {
      this.editingId = null;
      this.resetFormModel();
      this.clearPhotoUpload();
    },
    resetFormModel() {
      this.form = {
        customerNo: "",
        name: "",
        idType: "身份证",
        idNo: "",
        phone: "",
        gender: "未知",
        occupation: "",
        level: "普通",
        status: "在保",
        photo: "",
        address: "",
        remark: "",
      };
    },
    submitDialog() {
      this.$refs.customerForm.validate((valid) => {
        if (!valid) return;
        this.submitting = true;
        const body = { ...this.form };
        delete body.customerNo;
        const done = () => {
          this.submitting = false;
        };
        if (this.dialogMode === "edit" && this.editingId) {
          updateCustomer(this.editingId, body)
            .then(() => {
              this.$message.success("保存成功");
              this.dialogVisible = false;
              this.fetchCustomers();
            })
            .catch((err) => {
              this.$message.error("更新失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        } else {
          createCustomer(body)
            .then(() => {
              this.$message.success("新增成功");
              this.dialogVisible = false;
              this.fetchCustomers();
            })
            .catch((err) => {
              this.$message.error("新增失败：" + (err.response?.data?.detail || err.message));
            })
            .finally(done);
        }
      });
    },
    fetchCustomers() {
      this.loading = true;
      this.error = "";
      getCustomers()
        .then((res) => {
          this.customers = Array.isArray(res.data) ? res.data : [];
        })
        .catch(() => {
          this.error =
            "获取客户列表失败，请确认后端已启动：先在后端目录激活虚拟环境（PowerShell：.\\.venv\\Scripts\\Activate.ps1），再启动 uvicorn api.server:app --reload";
        })
        .finally(() => {
          this.loading = false;
        });
    },
    removeCustomer(c) {
      this.$confirm(`确定删除客户：${c.name}？`, "提示", { type: "warning" })
        .then(() => deleteCustomer(c.id))
        .then(() => {
          this.$message.success("已删除");
          this.fetchCustomers();
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
.list-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.list-head h2 {
  margin: 0;
  font-size: 18px;
}
.search-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding: 12px 14px;
  background: #f8fafc;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}
.search-title {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-right: 4px;
}
.search-field {
  width: 160px;
}
.card-inner {
  margin-left: 0;
  margin-right: 0;
}
.dialog-form :deep(.el-form-item) {
  margin-bottom: 14px;
}
.photo-upload :deep(.el-upload__tip) {
  margin-top: 6px;
  color: #94a3b8;
  font-size: 12px;
  line-height: 1.4;
  display: block;
}
.photo-saved {
  margin: 6px 0 0;
  font-size: 12px;
  color: #64748b;
  word-break: break-all;
}
@media (max-width: 640px) {
  .search-field {
    width: 100%;
  }
}
</style>
