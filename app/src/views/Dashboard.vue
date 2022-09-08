<template>
  <v-row align="center" justify="center">
    <v-col cols="10">
      <v-card class="mt-4">
        <v-card-text v-if="loaded">
          <v-tabs v-model="tab" background-color="primary" dark>
            <v-tab v-if="study">
              Synthesis
            </v-tab>
            <v-tab>
              All indicators
            </v-tab>
          </v-tabs>

          <v-tabs-items v-model="tab">
            <v-tab-item class="pa-3" v-if="study">
              <v-select
                label="Selected Indicators"
                :items="indicators"
                item-value="id"
                :item-text="itemText"
                multiple
                v-model="selectedIndicators"
                @change="drawSynthesisPlot()"
              ></v-select>

              <div
                ref="plotSynthesis"
                id="plotSynthesis"
                style="max-height:500px"
              ></div>
              <div>
                <v-btn color="primary" @click="downloadIndicatorsData">
                  <v-icon left>mdi-download</v-icon>
                  Download indicators data
                </v-btn>
              </div>
            </v-tab-item>
            <v-tab-item class="pa-3" eager>
              <v-row>
                <v-col cols="3">
                  <v-text-field
                    dense
                    label="Filter"
                    prepend-inner-icon="mdi-filter"
                    v-model="filterIndicator"
                    clearable
                    type="text"
                    outlined
                    rounded
                    class="mb-5 ml-5 mr-5"
                    hide-details="auto"
                  ></v-text-field>
                  <div
                    style="max-height: 700px"
                    class="overflow-y-auto overflow-x-auto"
                  >
                    <v-tabs
                      @change="showTab"
                      show-arrows
                      v-model="selectedIndicatorTab"
                      color="red accent-4"
                      vertical
                    >
                      <v-tab
                        class="left-justify-tab"
                        v-for="tab in filteredtabs"
                        :key="tab"
                        ><v-icon left>mdi-google-spreadsheet</v-icon
                        >{{ labelForId(tab) }}</v-tab
                      >
                    </v-tabs>
                  </div>
                </v-col>
                <v-col cols="9" class="justify-center">
                  <h2 class="text-center primary--text">
                    <v-icon left>mdi-google-spreadsheet</v-icon
                    >{{ labelForId(tabs[selectedIndicatorTab]) }}
                  </h2>

                  <h3>Graph</h3>
                  <div ref="plot" id="plot" style="max-height:380px"></div>

                  <h3 v-if="study">Configuration</h3>
                  <v-row class="mt-2 mb-1" v-if="study">
                    <v-col cols="4">
                      <b>Measure :</b>
                      {{ indicatorForId(tabs[selectedIndicatorTab]).measure }}
                    </v-col>
                    <v-col cols="4">
                      <b>Stats :</b>
                      {{
                        indicatorForId(tabs[selectedIndicatorTab]).stats.join(
                          ", "
                        )
                      }}
                    </v-col>
                    <v-col cols="4">
                      <span
                        v-if="
                          indicatorForId(tabs[selectedIndicatorTab]).type ===
                            'Boolean'
                        "
                      >
                        <b>Value :</b>
                        {{ indicatorForId(tabs[selectedIndicatorTab]).value }}
                      </span>
                    </v-col>
                  </v-row>

                  <h3>Data</h3>
                  <v-data-table
                    dense
                    :items="data"
                    :headers="headers"
                  ></v-data-table>
                </v-col>
              </v-row>
            </v-tab-item>
          </v-tabs-items>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import DataService from "@/services/DataService";
import { Component, Vue } from "vue-property-decorator";
import Plotly from "plotly.js";
import Study from "@/models/Study";
import Indicator from "@/models/Indicator";

@Component({
  components: {},
})
export default class Dashboard extends Vue {
  public tabs: Array<string> = [];
  public data: Array<any> = [];
  public headers: Array<any> = [];
  public selectedIndicatorTab = 0;

  private tab = 0;

  private study: Study | null = null;
  private studyFile = "";

  private filterIndicator = "";

  private selectedIndicators: Array<string> = [];

  private loaded = false;

  created(): void {
    this.getAsyncData();
  }

  async getAsyncData(): Promise<void> {
    if (this.$route.params.studyFile != undefined) {
      this.studyFile = this.$route.params.studyFile;
      // load study
      this.study = await DataService.getConfig(this.studyFile);
    }

    let alltabs = await DataService.getTabs();

    this.tabs = alltabs.filter((id) => {
      if (this.study) {
        let indic = this.study.indicators.find((i) => i.id === id);
        if (indic) {
          return indic.block === this.study.main_block;
        }
      } else {
        return true;
      }
    });

    if (this.tabs.length > 0) {
      this.showTab(0);
    }

    if (this.study) {
      this.selectedIndicators = this.study.selected_indicators;
    } else {
      this.selectedIndicators = this.tabs;
    }

    this.drawSynthesisPlot();

    this.loaded = true;
  }

  async drawSynthesisPlot(): Promise<void> {
    if (this.study) {
      const graph = await DataService.getMultiGraphData(
        this.selectedIndicators
      );
      Plotly.newPlot(
        this.$refs.plotSynthesis as Plotly.Root,
        graph.data,
        graph.layout,
        { displaylogo: false }
      );
    }
  }

  get filteredtabs(): Array<string> {
    return this.tabs.filter((id) => {
      if (
        this.filterIndicator != null &&
        !this.labelForId(id)
          .toLowerCase()
          .includes(this.filterIndicator.toLowerCase())
      ) {
        return false;
      }

      return true;
    });
  }

  get indicators(): Array<Indicator | string> {
    if (this.study) {
      return this.study.indicators.filter(
        (i) => i.block === this.study?.main_block
      );
    } else {
      return this.tabs;
    }
  }

  async showTab(tabIdx: number): Promise<void> {
    this.data = await DataService.getTabData(this.tabs[tabIdx]);

    this.headers.splice(0, this.headers.length);
    let headers: Array<any> = [];
    Object.keys(this.data[0]).forEach((k) => {
      headers.push({ value: k, text: k });
    });
    console.log(headers);

    this.headers.push(...headers);

    const graph = await DataService.getGraphData(this.tabs[tabIdx]);
    Plotly.newPlot(this.$refs.plot as Plotly.Root, graph.data, graph.layout, {
      displaylogo: false,
    });
  }

  public itemText(item: Indicator): string {
    return `${this.labelForId(item.id)} (${item.observer})`;
  }

  back(): void {
    this.$router.push("/");
  }

  labelForId(id: string): string {
    if (this.study) {
      let indicator = this.study.indicators.find((i) => i.id === id);
      return indicator && indicator.name
        ? indicator.name
        : `${indicator?.observer}_${indicator?.measure}_${
            indicator?.value ? indicator.value : ""
          }`;
    } else {
      return id;
    }
  }

  indicatorForId(id: string): Indicator | undefined {
    if (this.study) {
      let indicator = this.study.indicators.find((i) => i.id === id);
      return indicator;
    }
  }

  async downloadIndicatorsData(): Promise<void> {
    const data = await DataService.downloadIndicatorsData();
    var fileLink = document.createElement("a");
    fileLink.href = window.URL.createObjectURL(new Blob([data]));
    fileLink.setAttribute("download", "indicators_data.xlsx");
    fileLink.click();
  }
}
</script>
<style scoped>
.left-justify-tab {
  justify-content: flex-start;

  text-transform: none !important;
}
</style>
