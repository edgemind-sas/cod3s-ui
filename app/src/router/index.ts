import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import WorkspaceManager from "../views/WorkspaceManager.vue";
import WorkspaceView from "../views/WorkspaceView.vue";
import EditStudy from "../views/EditStudy.vue";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Workspace Manager",
    component: WorkspaceManager,
  },
  {
    path: "/workspace/:workspaceId?",
    name: "Workspace",
    component: WorkspaceView,
  },
  {
    path: "/dashboard/:workspaceId?/:studyFile?",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: "/editStudy/:workspaceId?/:studyFile?",
    name: "Edit Study",
    component: EditStudy,
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
