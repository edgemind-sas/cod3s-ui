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
      ></v-text-field>
      <v-btn color="accent"> <v-icon>mdi-plus</v-icon>New workspace</v-btn>
    </v-row>
    <v-row align="center">
      <v-col v-for="workspace in workspaces" :key="workspace.name" cols="4">
        <v-card class="mt-4" outlined style="border: 0.1em solid grey">
          <v-card-title class="text-h5" v-text="workspace.name"></v-card-title>
          <v-card-subtitle v-text="workspace.type"></v-card-subtitle>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn icon :to="'/studyManager/' + workspace.name">
              <v-icon>mdi-open-in-app</v-icon>
            </v-btn>
            <v-btn icon>
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
import FakeService from "@/services/FakeService";

@Component
export default class WorkspaceManager extends Vue {
  workspaces: Array<Workspace> = [];

  mounted(): void {
    this.workspaces = FakeService.getFakeWorkspaces();
  }
}
</script>
