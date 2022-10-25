<template>
  <v-container pa-10>
    <v-row>
      <v-text-field
        label="Search workspace"
        prepend-inner-icon="mdi-magnify"
        clearable
        type="text"
        outlined
        rounded
        class="ml-10 mr-10"
        hide-details="auto"
        v-model="filterWorkspace"
      ></v-text-field>

      <v-dialog v-model="dialog" persistent max-width="600px">
        <template v-slot:activator="{ on, attrs }">
          <v-btn outlined color="accent" v-bind="attrs" v-on="on"
            ><v-icon left dark> mdi-plus </v-icon>New workspace</v-btn
          >
        </template>
        <v-card>
          <v-card-title>
            <span class="text-h5">New workspace</span>
          </v-card-title>

          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="newmodel.name"
                    label="Name"
                    required
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="12">
                  <v-text-field
                    v-model="newmodel.path"
                    label="Path"
                    required
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-select
                    v-model="newmodel.type"
                    label="Type"
                    :items="['pycatshoo', 'ar3']"
                    required
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="dialog = false">
              Cancel
            </v-btn>
            <v-btn color="blue darken-1" text @click="saveNewWorkspace()">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-row>
    <v-row align="center" v-if="dataLoading">
      <v-progress-circular
        :size="50"
        color="primary"
        indeterminate
      ></v-progress-circular
      >Loading workspaces...
    </v-row>

    <v-row align="center" v-if="!dataLoading">
      <v-col
        v-for="workspace in filteredWorkspaces"
        :key="workspace.name"
        cols="4"
      >
        <v-card class="mt-4" outlined style="border: 0.1em solid grey">
          <v-card-title class="text-h5" v-text="workspace.name"></v-card-title>
          <v-card-subtitle v-text="workspace.type"></v-card-subtitle>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn icon @click="openWorkspace(workspace)">
              <v-icon>mdi-open-in-app</v-icon>
            </v-btn>
            <v-btn icon @click="deleteWorkspace(workspace)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col cols="4"> </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import Workspace from "@/models/Workspace";
import WorkspaceService from "@/services/WorkspaceService";

@Component
export default class WorkspaceManager extends Vue {
  workspaces: Array<Workspace> = [];
  dataLoading = true;
  dialog = false;
  filterWorkspace = "";

  newmodel = new Workspace();

  mounted(): void {
    this.loadWorkspaces();
  }

  get filteredWorkspaces(): Array<Workspace> {
    return this.workspaces.filter(
      (t) =>
        this.filterWorkspace == null ||
        t.name.toLowerCase().includes(this.filterWorkspace.toLowerCase())
    );
  }

  async loadWorkspaces(): Promise<void> {
    this.workspaces = await WorkspaceService.getWorkspaces();

    this.dataLoading = false;
  }

  async openWorkspace(workspace: Workspace): Promise<void> {
    this.$router.push(`/workspace/${workspace.id}`);
  }

  async saveNewWorkspace(): Promise<void> {
    await WorkspaceService.createWorkspace(this.newmodel);
    this.dialog = false;
    this.loadWorkspaces();
  }

  async deleteWorkspace(workspace: Workspace): Promise<void> {
    await WorkspaceService.deleteWorkspace(workspace.id);
    this.loadWorkspaces();
  }
}
</script>
