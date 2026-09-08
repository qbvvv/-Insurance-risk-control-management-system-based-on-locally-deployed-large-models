<template>
  <div class="login-page">
    <div
      class="login-shell"
      :class="loginFormExpanded ? 'login-shell--expanded' : 'login-shell--collapsed'"
    >
      <section class="brand-panel">
        <div class="brand-logo">RG</div>
        <div class="brand-pill">RULE GENERATION &amp; MANAGEMENT</div>
        <h1>登录到保险风控规则生成与管理系统</h1>
        <p class="brand-desc">
          聚焦自然语言规则解析、规则库治理与规则引擎执行，贯通承保与理赔风控审查；联动黑名单与风控预警流水，并配套系统审计留痕。默认管理员账户为
          <strong>admin / admin123</strong>。
        </p>
        <div
          class="module-carousel"
          @mouseenter="pauseCarousel"
          @mouseleave="resumeCarousel"
        >
          <div class="carousel-viewport">
            <div
              class="carousel-track"
              :style="{ transform: `translateX(-${carouselIndex * 100}%)` }"
            >
              <article
                v-for="(card, idx) in moduleCards"
                :key="idx"
                class="carousel-card"
              >
                <h3 class="card-title">{{ card.title }}</h3>
                <p class="card-desc">{{ card.desc }}</p>
              </article>
            </div>
          </div>
          <div class="carousel-footer">
            <button type="button" class="carousel-nav" aria-label="上一张" @click="prevCard">
              ‹
            </button>
            <div class="carousel-dots" role="tablist">
              <button
                v-for="(_, i) in moduleCards"
                :key="'dot-' + i"
                type="button"
                class="carousel-dot"
                :class="{ active: i === carouselIndex }"
                :aria-label="'切换到第' + (i + 1) + '张'"
                :aria-selected="i === carouselIndex"
                @click="goToCard(i)"
              />
            </div>
            <button type="button" class="carousel-nav" aria-label="下一张" @click="nextCard">
              ›
            </button>
          </div>
        </div>
        <p v-if="!loginFormExpanded" class="brand-expand-hint">
          点击右侧手柄展开登录区，即可输入账号密码。
        </p>
      </section>

      <button
        type="button"
        class="form-edge-handle"
        :aria-expanded="loginFormExpanded"
        :aria-label="loginFormExpanded ? '收起登录区' : '展开登录区'"
        :title="loginFormExpanded ? '收起' : '展开以输入账号密码'"
        @click="toggleLoginFormExpanded"
      >
        <span class="form-edge-handle-icon" aria-hidden="true" />
      </button>

      <section v-show="loginFormExpanded" class="form-panel">
        <div class="form-panel-head">
          <div class="form-pill">SECURE ACCESS</div>
          <h2>{{ isRegisterMode ? "创建账号" : "欢迎回来" }}</h2>
          <p class="form-desc">
            {{ isRegisterMode ? "注册普通用户后可直接登录进入系统。" : "请使用账号密码登录，进入你的风控工作台。" }}
          </p>
        </div>

        <div class="form-panel-body form-panel-body--open">
          <form class="login-form" @submit.prevent="isRegisterMode ? onRegister() : onLogin()">
            <div class="form-row">
              <label>用户名</label>
              <input v-model="form.username" type="text" placeholder="请输入用户名" :tabindex="loginFormExpanded ? 0 : -1" />
            </div>
            <div class="form-row">
              <label>密码</label>
              <input v-model="form.password" type="password" placeholder="请输入密码" :tabindex="loginFormExpanded ? 0 : -1" />
            </div>
            <div v-if="isRegisterMode" class="form-row">
              <label>确认密码</label>
              <input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" :tabindex="loginFormExpanded ? 0 : -1" />
            </div>
            <div class="form-actions">
              <button type="submit" class="btn-primary" :disabled="loading || !loginFormExpanded">
                {{ loading ? (isRegisterMode ? "注册中..." : "登录中...") : (isRegisterMode ? "注册并登录" : "登录") }}
              </button>
              <button type="button" class="btn-ghost" :disabled="!loginFormExpanded" @click="toggleMode">
                {{ isRegisterMode ? "返回登录" : "注册普通用户" }}
              </button>
            </div>
            <p class="form-tip">管理员默认账号：admin / admin123</p>
          </form>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { getAuthToken, login, register, setAuthSession } from "@/api";

export default {
  name: "LoginView",
  data() {
    return {
      loading: false,
      /** 右侧登录区是否展开；折叠时不可输入账号密码 */
      loginFormExpanded: false,
      isRegisterMode: false,
      carouselIndex: 0,
      carouselTimer: null,
      carouselPaused: false,
      moduleCards: [
        {
          title: "规则工作台与规则库",
          desc:
            "支持自然语言描述一键解析为结构化规则，补充阈值与时间窗后与预设规则统一入库；可编辑启停、优先级，并对业务描述生成测试记录执行命中试算，快速验证策略效果。",
        },
        {
          title: "业务数据与客户风控",
          desc:
            "维护客户、产品与保单、理赔等核心业务数据，为规则引擎提供统一字段口径；结合命中客户检索，便于从投保到赔付全链路定位高风险主体与关联案件。",
        },
        {
          title: "黑名单",
          desc:
            "维护证件号、手机号、设备、收款账户等黑名单对象，与规则执行联动；对高频命中、渠道异常等情形汇聚预警信息，支撑承保与理赔环节的拦截与复核。",
        },
        {
          title: "系统管理与审计",
          desc:
            "用户与角色、系统参数及操作日志集中管理，配合登录鉴权与菜单权限；关键配置与规则变更可追溯，满足内部风控运营的基本治理与留痕需求。",
        },
      ],
      form: {
        username: "admin",
        password: "admin123",
        confirmPassword: "",
      },
    };
  },
  created() {
    if (getAuthToken()) {
      this.$router.replace("/dashboard");
    }
  },
  mounted() {
    this.startCarousel();
  },
  beforeDestroy() {
    this.stopCarousel();
  },
  methods: {
    startCarousel() {
      this.stopCarousel();
      this.carouselTimer = setInterval(() => {
        if (!this.carouselPaused) {
          this.nextCard();
        }
      }, 5200);
    },
    stopCarousel() {
      if (this.carouselTimer) {
        clearInterval(this.carouselTimer);
        this.carouselTimer = null;
      }
    },
    pauseCarousel() {
      this.carouselPaused = true;
    },
    resumeCarousel() {
      this.carouselPaused = false;
    },
    nextCard() {
      const n = this.moduleCards.length;
      this.carouselIndex = n ? (this.carouselIndex + 1) % n : 0;
    },
    prevCard() {
      const n = this.moduleCards.length;
      if (!n) return;
      this.carouselIndex = (this.carouselIndex - 1 + n) % n;
    },
    goToCard(i) {
      if (i >= 0 && i < this.moduleCards.length) {
        this.carouselIndex = i;
      }
    },
    toggleLoginFormExpanded() {
      this.loginFormExpanded = !this.loginFormExpanded;
    },
    async onLogin() {
      if (!this.loginFormExpanded) {
        this.$message.warning("请先点击品牌卡片右侧手柄展开登录区，再输入账号密码");
        return;
      }
      const username = (this.form.username || "").trim();
      const password = this.form.password || "";
      if (!username || !password) {
        this.$message.warning("请输入用户名和密码");
        return;
      }
      this.loading = true;
      try {
        const resp = await login(username, password);
        const payload = resp && resp.data ? resp.data : {};
        setAuthSession(payload.token, payload.user || null, {
          permissions: payload.permissions || [],
          menus: payload.menus || [],
        });
        this.$message.success("登录成功");
        this.$router.push("/dashboard");
      } catch (err) {
        const msg = err?.response?.data?.detail || "登录失败，请检查账号密码";
        this.$message.error(msg);
      } finally {
        this.loading = false;
      }
    },
    async onRegister() {
      if (!this.loginFormExpanded) {
        this.$message.warning("请先点击品牌卡片右侧手柄展开登录区，再填写注册信息");
        return;
      }
      const username = (this.form.username || "").trim();
      const password = this.form.password || "";
      const confirmPassword = this.form.confirmPassword || "";
      if (!username || !password || !confirmPassword) {
        this.$message.warning("请完整填写注册信息");
        return;
      }
      if (password !== confirmPassword) {
        this.$message.warning("两次输入的密码不一致");
        return;
      }
      this.loading = true;
      try {
        const resp = await register(username, password);
        const payload = resp && resp.data ? resp.data : {};
        setAuthSession(payload.token, payload.user || null, {
          permissions: payload.permissions || [],
          menus: payload.menus || [],
        });
        this.$message.success("注册成功，已自动登录");
        this.$router.push("/dashboard");
      } catch (err) {
        const msg = err?.response?.data?.detail || "注册失败，请稍后重试";
        this.$message.error(msg);
      } finally {
        this.loading = false;
      }
    },
    toggleMode() {
      this.isRegisterMode = !this.isRegisterMode;
      if (this.isRegisterMode) {
        this.loginFormExpanded = true;
        this.form.username = "";
        this.form.password = "";
        this.form.confirmPassword = "";
      } else {
        this.form.username = "admin";
        this.form.password = "admin123";
        this.form.confirmPassword = "";
      }
    },
  },
};
</script>

<style scoped>
.login-page {
  position: relative;
  /* 登录路由无顶栏，若仍用 100vh-110px 会在底部露出 body 底色形成“白条” */
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: #eef3ef;
  background-image: url("/images/login-elegant-bg.svg");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.login-page::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.55) 0%,
    rgba(245, 248, 245, 0.35) 45%,
    rgba(236, 241, 237, 0.5) 100%
  );
}

.login-shell {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 0;
  overflow: visible;
  border-radius: 24px;
  box-shadow: 0 22px 50px rgba(52, 68, 60, 0.22);
}

.login-shell--collapsed {
  width: min(680px, 100%);
  grid-template-columns: 1fr;
  grid-template-rows: auto;
}

.login-shell--collapsed .brand-panel {
  grid-column: 1;
  grid-row: 1;
  border-radius: 24px;
}

.login-shell--collapsed .form-edge-handle {
  grid-column: 1;
  grid-row: 1;
  justify-self: end;
  align-self: center;
  margin-right: -13px;
  z-index: 4;
}

.login-shell--expanded {
  width: min(1120px, 100%);
  grid-template-columns: 1.15fr 1fr;
  overflow: hidden;
}

.login-shell--expanded .brand-panel {
  grid-column: 1;
  grid-row: 1;
  border-radius: 24px 0 0 24px;
}

.login-shell--expanded .form-panel {
  grid-column: 2;
  grid-row: 1;
}

.login-shell--expanded .form-edge-handle {
  grid-column: 1 / -1;
  grid-row: 1;
  justify-self: start;
  align-self: center;
  width: 26px;
  margin-left: calc(100% * 1.15 / 2.15 - 13px);
  z-index: 4;
}

.brand-panel {
  position: relative;
  border-radius: 24px 0 0 24px;
  padding: 34px 30px;
  color: #faf8f4;
  background: linear-gradient(152deg, #4d5c54 0%, #5f7369 38%, #7d9388 72%, #9eb5aa 100%);
  overflow: hidden;
}

.brand-panel::after {
  content: "";
  position: absolute;
  right: -100px;
  bottom: -120px;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.09);
}

.brand-logo {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  margin-bottom: 14px;
}

.brand-pill,
.form-pill {
  display: inline-flex;
  align-items: center;
  height: 28px;
  border-radius: 999px;
  padding: 0 12px;
  font-size: 12px;
  letter-spacing: 1px;
  font-weight: 700;
}

.brand-pill {
  color: rgba(250, 248, 244, 0.92);
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.12);
  margin-bottom: 14px;
}

.brand-panel h1 {
  margin: 0 0 10px;
  font-size: 44px;
  line-height: 1.2;
}

.brand-desc {
  margin: 0 0 18px;
  line-height: 1.75;
  font-size: 17px;
  color: rgba(250, 248, 244, 0.92);
}

.brand-desc strong {
  color: #fff;
  font-weight: 700;
}

.module-carousel {
  position: relative;
  z-index: 1;
  margin-top: 4px;
}

.carousel-viewport {
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  min-height: 148px;
}

.carousel-track {
  display: flex;
  transition: transform 0.48s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

.carousel-card {
  flex: 0 0 100%;
  box-sizing: border-box;
  padding: 18px 20px 16px;
  color: rgba(250, 248, 244, 0.96);
}

.card-title {
  margin: 0 0 10px;
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #fff;
}

.card-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.72;
  color: rgba(250, 248, 244, 0.88);
}

.carousel-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-top: 12px;
}

.carousel-nav {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0 2px;
  transition: background 0.2s, border-color 0.2s;
}

.carousel-nav:hover {
  background: rgba(255, 255, 255, 0.22);
  border-color: rgba(255, 255, 255, 0.45);
}

.carousel-dots {
  display: flex;
  gap: 8px;
  align-items: center;
}

.carousel-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  padding: 0;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.35);
  transition: transform 0.2s, background 0.2s;
}

.carousel-dot.active {
  background: #fff;
  transform: scale(1.25);
}

.brand-expand-hint {
  position: relative;
  z-index: 1;
  margin: 16px 0 0;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.65;
  color: rgba(250, 248, 244, 0.88);
  background: rgba(0, 0, 0, 0.12);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
}

.form-panel {
  position: relative;
  border-radius: 0 24px 24px 0;
  padding: 30px 28px 30px 36px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 224, 0.95);
  border-left: none;
  box-shadow: inset 1px 0 0 rgba(200, 210, 200, 0.45);
  backdrop-filter: blur(10px);
}

.form-edge-handle {
  position: relative;
  width: 26px;
  height: 72px;
  padding: 0;
  margin: 0;
  border: 1px solid rgba(199, 214, 206, 0.95);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, box-shadow 0.2s, border-color 0.2s;
  box-sizing: border-box;
}

.login-shell--collapsed .form-edge-handle {
  border-left: none;
  border-radius: 0 14px 14px 0;
  background: linear-gradient(180deg, rgba(236, 248, 255, 0.98), rgba(224, 238, 248, 0.96));
  box-shadow: 3px 2px 12px rgba(40, 60, 50, 0.12);
}

.login-shell--expanded .form-edge-handle {
  border-right: none;
  border-radius: 14px 0 0 14px;
  background: linear-gradient(180deg, rgba(236, 248, 255, 0.98), rgba(224, 238, 248, 0.96));
  box-shadow: -3px 2px 12px rgba(40, 60, 50, 0.12);
}

.form-edge-handle:hover {
  background: linear-gradient(180deg, #fff, rgba(232, 244, 252, 0.98));
}

.login-shell--expanded .form-edge-handle:hover {
  box-shadow: -4px 3px 16px rgba(40, 60, 50, 0.16);
}

.login-shell--collapsed .form-edge-handle:hover {
  box-shadow: 4px 3px 16px rgba(40, 60, 50, 0.16);
}

.form-edge-handle:focus-visible {
  outline: 2px solid #6b9080;
  outline-offset: 2px;
}

.form-edge-handle-icon {
  display: block;
  width: 0;
  height: 0;
  margin-left: 3px;
  border-style: solid;
  border-width: 7px 0 7px 10px;
  border-color: transparent transparent transparent #1e3a5f;
  transition: transform 0.25s ease, border-color 0.2s;
}

@media (min-width: 1081px) {
  .login-shell--expanded .form-edge-handle-icon {
    margin-left: 0;
    margin-right: 2px;
    border-width: 7px 10px 7px 0;
    border-color: transparent #1e3a5f transparent transparent;
  }
}

.form-panel-head {
  position: relative;
  z-index: 1;
}

.form-panel-body {
  margin-top: 8px;
  pointer-events: auto;
}

.form-pill {
  color: #4f6d62;
  background: rgba(232, 241, 236, 0.95);
  border: 1px solid rgba(189, 206, 196, 0.5);
}

.form-panel h2 {
  margin: 14px 0 8px;
  font-size: 40px;
  color: #0f172a;
}

.form-desc {
  margin: 0 0 14px;
  color: #475569;
  font-size: 16px;
}

.login-form {
  display: grid;
  gap: 14px;
}

.form-row label {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.form-row input {
  width: 100%;
  height: 52px;
  border-radius: 14px;
  border: 1px solid #d1d5db;
  background: #fff;
  padding: 0 14px;
  font-size: 18px;
  color: #111827;
  outline: none;
}

.form-row input:focus {
  border-color: #6b9080;
  box-shadow: 0 0 0 3px rgba(107, 144, 128, 0.18);
}

.form-actions {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-top: 4px;
}

/* 覆盖全局 base.css 里 .btn-primary 的 margin-top / align-self，否则 Edge 下主按钮会下移错位 */
.form-actions .btn-primary,
.form-actions .btn-ghost {
  margin: 0;
  align-self: stretch;
}

.form-tip {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.btn-primary,
.btn-ghost {
  box-sizing: border-box;
  appearance: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  min-height: 48px;
  height: 48px;
  padding: 0 18px;
  font-size: 18px;
  font-weight: 600;
  font-family: inherit;
  line-height: 1.2;
  cursor: pointer;
}

.btn-primary {
  color: #fff;
  background: linear-gradient(135deg, #4f6d62, #6b9080);
  border: 1px solid transparent;
}

.btn-primary:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.btn-ghost {
  color: #4f6d62;
  background: rgba(237, 244, 240, 0.95);
  border: 1px solid rgba(183, 202, 193, 0.65);
}

@media (max-width: 1080px) {
  .login-shell--expanded {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
    border-radius: 18px;
    overflow: hidden;
  }
  .login-shell--expanded .brand-panel {
    grid-column: 1;
    grid-row: 1;
    border-radius: 18px 18px 0 0;
  }
  .login-shell--expanded .form-panel {
    grid-column: 1;
    grid-row: 2;
    border-radius: 0 0 18px 18px;
    border-left: 1px solid rgba(226, 232, 224, 0.95);
    box-shadow: none;
    padding: 28px 22px 26px 22px;
  }
  .login-shell--expanded .form-edge-handle {
    grid-column: 1;
    grid-row: 2;
    justify-self: center;
    align-self: start;
    width: 72px;
    height: 26px;
    margin-left: 0;
    margin-top: -13px;
    border: 1px solid rgba(199, 214, 206, 0.95);
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    border-right: 1px solid rgba(199, 214, 206, 0.95);
    box-shadow: 0 -2px 12px rgba(40, 60, 50, 0.1);
  }
  .login-shell--collapsed {
    border-radius: 18px;
  }
  .login-shell--collapsed .brand-panel {
    border-radius: 18px;
  }
  .login-shell--collapsed .form-edge-handle {
    justify-self: center;
    align-self: end;
    width: 72px;
    height: 26px;
    margin-right: 0;
    margin-bottom: -13px;
    border: 1px solid rgba(199, 214, 206, 0.95);
    border-top: none;
    border-radius: 0 0 14px 14px;
    border-left: 1px solid rgba(199, 214, 206, 0.95);
    box-shadow: 0 3px 12px rgba(40, 60, 50, 0.12);
  }
  /* 窄屏：手柄在分区边缘，收起=向下展开，展开=向上收起 */
  .login-shell--collapsed .form-edge-handle-icon {
    margin-left: 0;
    margin-top: 0;
    margin-bottom: 3px;
    border-width: 0 7px 10px 7px;
    border-color: transparent transparent #1e3a5f transparent;
  }
  .login-shell--expanded .form-edge-handle-icon {
    margin-left: 0;
    margin-top: 3px;
    margin-bottom: 0;
    border-width: 10px 7px 0 7px;
    border-color: #1e3a5f transparent transparent transparent;
  }
  .brand-panel h1,
  .form-panel h2 {
    font-size: 34px;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 12px;
  }
  .login-shell--expanded .brand-panel {
    border-radius: 18px 18px 0 0;
    padding: 20px 16px;
  }
  .login-shell--collapsed .brand-panel {
    padding: 20px 16px;
  }
  .form-panel {
    padding: 24px 16px 20px;
  }
  .form-actions {
    flex-direction: column;
  }
}
</style>
