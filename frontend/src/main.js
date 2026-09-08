import Vue from "vue";
import ElementUI from "element-ui";
import "element-ui/lib/theme-chalk/index.css";
import App from "./App.vue";
import router from "./router";
import "./assets/base.css";
import "./assets/module-table.css";

Vue.use(ElementUI);

new Vue({
  router,
  render: function (h) {
    return h(App);
  },
}).$mount("#app");
