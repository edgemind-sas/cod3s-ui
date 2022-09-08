<template>
  <v-app>
    <v-app-bar app>
      <v-spacer />
      <h1 class="primary--text">
        COD3S Study Manager
        <v-chip color="secondary" outlined>{{ version }}</v-chip>
      </h1>
      <v-spacer />
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import DataService from "./services/DataService";

@Component
export default class App extends Vue {
  public showContent = false;

  public version = "0.0.0";

  created(): void {
    DataService.getVersion().then((v) => this.$set(this, "version", v));
  }
}
</script>
