<template>
  <v-overlay class="text-center" :value="show">
    <v-card min-width="900" light>
      <v-card-title
        >Building dashboard
        <v-btn @click="killDashboard" outlined class="ml-5" color="accent"
          ><v-icon left> mdi-stop </v-icon> Cancel</v-btn
        >
        <v-btn
          @click="showDashboard"
          :disabled="!complete"
          outlined
          class="ml-5"
          color="primary"
          ><v-icon left> mdi-chart-line </v-icon> Show results</v-btn
        >
      </v-card-title>
      <v-card-text>
        <log-viewer :log="logs" :loading="isLoading" />
      </v-card-text>
      <v-card-actions> </v-card-actions>
    </v-card>
  </v-overlay>
</template>

<script lang="ts">
import { Component, Vue, Prop } from "vue-property-decorator";

import LogViewer from "@femessage/log-viewer";
import DataService from "@/services/DataService";
import WorkspaceService from "@/services/WorkspaceService";
import Workspace from "@/models/Workspace";

@Component({ components: { LogViewer } })
export default class ProcessRunner extends Vue {
  public show = false;
  public isLoading = true;
  public logs = "";
  private updateTimer: any = null;
  public complete = false;
  public configFileName!: string;

  async refresh(): Promise<void> {
    let logARray = await DataService.getLogs();
    this.logs = logARray.join("\n");
  }

  private workspaceId: number | null = null;

  async run(workspaceId: number, configFileName: string): Promise<void> {
    this.workspaceId = workspaceId;
    this.configFileName = configFileName;
    this.show = true;
    this.logs = "";
    this.isLoading = true;
    this.updateTimer = setInterval(() => {
      this.refresh();
    }, 1000);
    let returncode = await WorkspaceService.runStudy(
      workspaceId,
      configFileName
    );

    clearInterval(this.updateTimer);
    this.refresh();
    this.isLoading = false;
    this.complete = returncode == 0;
    //    this.show = false;
  }

  async killDashboard(): Promise<void> {
    if (this.workspaceId) {
      await WorkspaceService.stopStudy(this.workspaceId, this.configFileName);
    }
    clearInterval(this.updateTimer);
    this.show = false;
    this.complete = false;
  }

  async showDashboard(): Promise<void> {
    this.complete = false;
    let routeData = this.$router.resolve({
      path: `/dashboard/${this.workspaceId}/${this.configFileName}`,
    });
    window.open(routeData.href, "_blank");
    this.show = false;
  }
}
</script>

<style></style>
