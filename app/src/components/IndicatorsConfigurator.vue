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
      <v-switch label="Hide empty observers" v-model="hideEmptyObservers">
      </v-switch>
      <v-tabs v-model="indicatorTab" vertical>
        <v-tab
          class="left-justify-tab"
          v-for="observer in filteredObserversList"
          :key="observer.name"
          ><v-chip class="mr-2" small color="secondary">{{
            indicFor(observer.name).length
          }}</v-chip>
          {{ observer.name }}
        </v-tab>
      </v-tabs>
    </v-col>
    <v-col cols="9">
      <v-tabs-items v-model="indicatorTab" vertical>
        <v-tab-item
          v-for="observer in filteredObserversList"
          :key="observer.name"
        >
          <v-btn class="ml-5" color="accent" @click="addIndic(observer)"
            ><v-icon>mdi-plus</v-icon>Add indicator</v-btn
          >

          <v-data-table
            :items="indicFor(observer.name)"
            :headers="headersFor(observer.type)"
          >
            <template v-slot:[`item.name`]="indicators">
              <v-text-field
                v-model="indicators.item.name"
                label="Name"
                single-line
                hide-details="true"
              ></v-text-field>
            </template>
            <template v-slot:[`item.description`]="indicators">
              <v-text-field
                v-model="indicators.item.description"
                label="Description"
                single-line
                hide-details="true"
              ></v-text-field>
            </template>

            <template v-slot:[`item.unit`]="indicators">
              <v-text-field
                v-model="indicators.item.unit"
                label="Unit"
                single-line
                hide-details="true"
              ></v-text-field>
            </template>

            <template v-slot:[`item.measure`]="indicators">
              <v-select
                :items="indicatorConfig[observer.type].measure_list"
                v-model="indicators.item.measure"
                hide-details="true"
                @change="dirtyConfig()"
              ></v-select>
            </template>

            <template v-slot:[`item.stats`]="indicators">
              <v-select
                :items="indicatorConfig[observer.type].stats_list"
                v-model="indicators.item.stats"
                multiple
                hide-details="true"
                @change="dirtyConfig()"
              ></v-select>
            </template>

            <template v-slot:[`item.value`]="indicators">
              <v-switch
                dense
                v-if="observer.type === 'Boolean'"
                v-model="indicators.item.value"
                :label="`${indicators.item.value.toString()}`"
                @change="dirtyConfig()"
              ></v-switch>
            </template>

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
import Block from "@/models/Block";
import Indicator from "@/models/Indicator";
import Observer from "@/models/Observer";
import DataService from "@/services/DataService";
import { Component, Vue, Prop } from "vue-property-decorator";

@Component({})
export default class IndicatorsConfigurator extends Vue {
  @Prop() indicators!: Array<Indicator>;
  @Prop() block!: Block;

  private indicatorTab = 0;
  private indicatorConfig: any = {};
  private dataLoaded = false;
  private filterObserver = "";
  private hideEmptyObservers = false;

  indicFor(observerName: string): Array<Indicator> {
    return this.indicators.filter(
      (indic: Indicator) =>
        indic.observer === observerName && indic.block === this.block.name
    );
  }

  headersFor(type: string): any {
    let headers = [
      {
        text: "Name",
        value: "name",
      },
      {
        text: "Description",
        value: "description",
      },
      {
        text: "Unit",
        value: "unit",
      },
      {
        text: "Measure",
        value: "measure",
      },
      {
        text: "Stats",
        value: "stats",
      },
    ];

    if (type === "Boolean") {
      headers.push({
        text: "Value",
        value: "value",
      });
    }

    headers.push({
      text: "Delete",
      value: "delete",
    });

    return headers;
  }

  get filteredObserversList(): Array<Observer> {
    return this.block.observers.filter((obs) => {
      if (this.hideEmptyObservers && this.indicFor(obs.name).length == 0) {
        return false;
      }

      if (
        this.filterObserver != null &&
        !obs.name.toLowerCase().includes(this.filterObserver.toLowerCase())
      ) {
        return false;
      }

      return true;
    });
  }

  addIndic(observer: Observer): void {
    let newIndic = new Indicator();
    newIndic.id = DataService.generateId();
    newIndic.observer = observer.name;
    newIndic.type = observer.type;
    newIndic.block = this.block.name;
    newIndic.measure = this.indicatorConfig[observer.type].measure_list[0];
    newIndic.stats = ["mean", "standard-deviation", "confidence-range"];
    newIndic.value = observer.type === "Boolean" ? true : "";
    newIndic.name = `Indic on ${observer.name}`;
    newIndic.description = `Indic on ${observer.name}`;

    this.indicators.push(newIndic);
    this.dirtyConfig();
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
    let config = await DataService.getIndicatorConfig();

    this.indicatorConfig = config.observer_config;
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
