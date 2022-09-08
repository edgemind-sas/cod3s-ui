import Vue from "vue";
import VueRouter, { RouteConfig } from "vue-router";
import Dashboard from "../views/Dashboard.vue";
import WorkspaceManager from "../views/WorkspaceManager.vue";
import DataManager from "../views/DataManager.vue";
import EditStudy from "../views/EditStudy.vue";
import DataService from "../services/DataService";
import StudyType from "@/models/StudyType";

Vue.use(VueRouter);

const routes: Array<RouteConfig> = [
  {
    path: "/",
    name: "Workspace Manager",
    component: WorkspaceManager,
  },
  {
    path: "/studyManager/:workspace?",
    name: "Study Manager",
    component: DataManager,
  },
  {
    path: "/dashboard/:studyFile?",
    name: "Dashboard",
    component: Dashboard,
  },
  {
    path: "/editStudy/:studyFile?",
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
