<template>
  <v-row v-if="dataLoaded">
    <v-col cols="3">
      <v-text-field
        dense
        label="Filter"
        prepend-inner-icon="mdi-filter"
        v-model="filterObserver"
        clearable
        type="text"
        outlined
        rounded
        class="mb-5"
        hide-details="auto"
      ></v-text-field>
      <v-switch label="Hide empty components" v-model="hideEmptyComponents">
      </v-switch>
      <v-tabs v-model="indicatorTab" vertical>
        <v-tab
          class="left-justify-tab"
          v-for="component in filteredComponentsList"
          :key="component.name"
          ><v-chip class="mr-2" small color="secondary">{{
            indicFor(component.name).length
          }}</v-chip>
          {{ component.name }}
        </v-tab>
      </v-tabs>
    </v-col>
    <v-col cols="9">
      <v-tabs-items v-model="indicatorTab" vertical>
        <v-tab-item
          v-for="component in filteredComponentsList"
          :key="component.name"
        >
          <v-btn class="ml-5" color="accent" @click="addIndic(component.name)"
            ><v-icon>mdi-plus</v-icon>Add indicator</v-btn
          >

          <v-data-table
            :items="indicFor(component.name)"
            :headers="headersFor(null)"
          >
            <template v-slot:[`item.var`]="indicators">
              <v-select
                :items="availableVarList(component.name)"
                v-model="indicators.item.var"
                hide-details="true"
                @change="dirtyConfig()"
              ></v-select>
            </template>

            <template v-slot:[`item.description`]="indicators">
              <v-text-field
                v-model="indicators.item.description"
                label="Description"
                single-line
                hide-details="true"
                @change="dirtyConfig()"
              ></v-text-field>
            </template>

            <template v-slot:[`item.unit`]="indicators">
              <v-text-field
                v-model="indicators.item.unit"
                label="Unit"
                single-line
                hide-details="true"
                @change="dirtyConfig()"
              ></v-text-field>
            </template>
            <!--
            <template v-slot:[`item.measure`]="indicators">
              <v-select
                :items="indicatorConfig[component.type].measure_list"
                v-model="indicators.item.measure"
                hide-details="true"
                @change="dirtyConfig()"
              ></v-select>
            </template>
-->
            <template v-slot:[`item.stats`]="indicators">
              <v-select
                :items="stats_list"
                v-model="indicators.item.stats"
                multiple
                hide-details="true"
                @change="dirtyConfig()"
              ></v-select>
            </template>
            <!--
            <template v-slot:[`item.value`]="indicators">
              <v-switch
                dense
                v-if="component.type === 'Boolean'"
                v-model="indicators.item.value"
                :label="`${indicators.item.value.toString()}`"
                @change="dirtyConfig()"
              ></v-switch>
            </template>
-->
            <template v-slot:[`item.delete`]="indicators">
              <v-btn
                small
                outlined
                color="primary"
                @click="deleteIndic(indicators.item)"
                ><v-icon>mdi-delete</v-icon></v-btn
              >
            </template>
          </v-data-table>
        </v-tab-item>
      </v-tabs-items>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import System from "@/models/System";
import Indicator from "@/models/Indicator";
import Observer from "@/models/Observer";
import DataService from "@/services/DataService";
import { Component, Vue, Prop } from "vue-property-decorator";
import WorkspaceService from "@/services/WorkspaceService";

@Component({})
export default class PycIndicatorsConfigurator extends Vue {
  @Prop() indicators!: Array<any>;
  @Prop() system!: System;
  @Prop() workspaceId!: number;
  @Prop() studyName!: string;

  private indicatorTab = 0;
  private indicatorConfig: any = {};
  private dataLoaded = false;
  private filterObserver = "";
  private hideEmptyComponents = false;

  private system_info = {};

  indicFor(componentName: string): Array<any> {
    return this.indicators.filter((indic) => indic.component === componentName);
  }

  private stats_list = ["mean", "stddev"];

  availableVarList(name: string): Array<string> {
    return this.system_info[name];
  }

  get filteredComponentsList(): Array<any> {
    let components = Object.keys(this.system_info).map((n) => ({ name: n }));

    if (this.hideEmptyComponents) {
      return components.filter((c) => this.indicFor(c.name).length != 0);
    }
    return components;
  }

  addIndic(component: string): void {
    let first_value = this.availableVarList(component)[0];
    this.indicators.push({
      var: first_value,
      stats: ["mean", "stddev"],
      component: component,
    });
  }

  headersFor(type: string): any {
    let headers = [
      {
        text: "Name",
        value: "var",
      },
      {
        text: "Description",
        value: "description",
      },
      {
        text: "Unit",
        value: "unit",
      },
      // {
      //   text: "Measure",
      //   value: "measure",
      // },
      {
        text: "Stats",
        value: "stats",
      },
    ];

    // if (type === "Boolean") {
    //   headers.push({
    //     text: "Value",
    //     value: "value",
    //   });
    // }

    headers.push({
      text: "Delete",
      value: "delete",
    });

    return headers;
  }

  public dirtyConfig(): void {
    this.$emit("dirty-config");
  }

  created(): void {
    this.getIndicatorConfig();
  }

  deleteIndic(indic: Indicator): void {
    this.$delete(this.indicators, this.indicators.indexOf(indic));
    this.dirtyConfig();
  }

  async getIndicatorConfig(): Promise<void> {
    this.system_info = await WorkspaceService.getSystemInfo(
      this.workspaceId,
      this.studyName
    );

    this.dataLoaded = true;
  }
}
</script>
<style scoped>
.left-justify-tab {
  justify-content: flex-start;
  text-transform: none !important;
}
</style>
