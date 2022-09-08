<template>
  <v-row justify="center">
    <v-col cols="11">
      <v-form ref="form">
        <template v-if="asyncDataLoaded">
          <v-card class="mt-4">
            <v-card-title>
              <v-btn to="/" outlined color="primary" class="ml-5"
                ><v-icon left dark> mdi-chevron-left </v-icon>Back</v-btn
              >
              <v-btn
                @click="save"
                outlined
                color="accent"
                class="ml-5"
                :disabled="!formIsValid() || dirtyStudy"
                ><v-icon left dark> mdi-floppy </v-icon>Save</v-btn
              >
              <v-btn
                @click="runSimulation"
                outlined
                color="accent"
                class="ml-5"
                :disabled="!formIsValid()"
                ><v-icon left dark> mdi-cog </v-icon>Save & Simulate</v-btn
              >

              <v-btn
                @click="showResults"
                outlined
                color="primary"
                class="ml-5"
                :disabled="!formIsValid() || !hasResult || dirtyStudy"
                ><v-icon left dark>mdi-chart-line</v-icon>Save & Show
                Results</v-btn
              >
            </v-card-title>
            <v-card-text>
              <v-tabs v-model="tab" background-color="primary" dark>
                <v-tab>
                  General
                </v-tab>
                <v-tab>
                  Indicators
                </v-tab>
                <v-tab>
                  Dashboard
                </v-tab>
              </v-tabs>

              <v-tabs-items v-model="tab">
                <v-tab-item class="pa-3">
                  <div class="mt-3">
                    <v-text-field
                      outlined
                      v-model="study.name"
                      label="Study name"
                      :rules="requiredRules"
                      @input="studyNameChange"
                    ></v-text-field>
                    <v-text-field
                      outlined
                      v-model="study.description"
                      label="Study description"
                    ></v-text-field>
                    <v-text-field
                      outlined
                      v-model="studyFile"
                      label="Config file"
                      :rules="requiredRules"
                      disabled
                    ></v-text-field>
                    <v-select
                      outlined
                      :items="availableBlocks"
                      item-text="name"
                      item-value="name"
                      label="Block"
                      v-model="study.main_block"
                      :rules="requiredRules"
                      @change="dirtyStudy = true"
                    ></v-select>
                    <h2 class="mb-5">Simulation parameters</h2>
                    <v-row>
                      <v-col cols="6">
                        <v-text-field
                          outlined
                          :value="study.simu_params.nb_runs"
                          @input="study.simu_params.nb_runs = Number($event)"
                          label="Runs count"
                          type="number"
                          :hide-details="true"
                          @change="dirtyStudy = true"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="6">
                        <v-text-field
                          outlined
                          :value="study.simu_params.seed"
                          @input="study.simu_params.seed = Number($event)"
                          label="Seed"
                          type="number"
                          :hide-details="true"
                          @change="dirtyStudy = true"
                        ></v-text-field>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="6">
                        <v-text-field
                          outlined
                          label="Epoch label"
                          v-model="study.simu_params.schedule_name"
                          :hide-details="true"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="6">
                        <v-text-field
                          outlined
                          label="Epoch unit"
                          v-model="study.simu_params.schedule_unit"
                          :hide-details="true"
                        ></v-text-field>
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="4">
                        <v-text-field
                          outlined
                          label="From"
                          :value="study.simu_params.schedule_from"
                          @input="
                            study.simu_params.schedule_from = Number($event)
                          "
                          type="number"
                          :hide-details="true"
                          @change="dirtyStudy = true"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="4">
                        <v-text-field
                          outlined
                          :value="study.simu_params.schedule_to"
                          @input="
                            study.simu_params.schedule_to = Number($event)
                          "
                          label="To"
                          :rules="requiredRules"
                          type="number"
                          :hide-details="true"
                          @change="dirtyStudy = true"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="4">
                        <v-text-field
                          outlined
                          :value="study.simu_params.schedule_step"
                          @input="
                            study.simu_params.schedule_step = Number($event)
                          "
                          label="Step"
                          :rules="requiredRules"
                          type="number"
                          :hide-details="true"
                        ></v-text-field>
                      </v-col>
                    </v-row>
                  </div>
                </v-tab-item>
                <v-tab-item class="pa-3">
                  <indicators-configurator
                    :block="currentBlock"
                    :indicators="study.indicators"
                    v-on:dirty-config="dirtyStudy = true"
                  ></indicators-configurator
                ></v-tab-item>

                <v-tab-item class="pa-3">
                  <v-select
                    label="Selected Indicators"
                    :items="study.indicators"
                    item-value="id"
                    :item-text="itemText"
                    multiple
                    v-model="study.selected_indicators"
                  ></v-select>
                </v-tab-item>
              </v-tabs-items>
            </v-card-text>
          </v-card>
        </template>
      </v-form>
    </v-col>

    <process-runner ref="processRunner"></process-runner>
  </v-row>
</template>

<script lang="ts">
/* eslint-disable */
import { Component, Vue, Watch } from "vue-property-decorator";

import ProcessRunner from "@/components/ProcessRunner.vue";
import IndicatorsConfigurator from "@/components/IndicatorsConfigurator.vue";
import DataService from "@/services/DataService";
import Block from "@/models/Block";
import Study from "@/models/Study";
import Indicator from "@/models/Indicator";

@Component({
  components: {
    ProcessRunner,
    IndicatorsConfigurator,
  },
})
export default class EditStudy extends Vue {
  public studyFile = "";
  public study: Study | any = {};
  public asyncDataLoaded = false;
  private isStudyAsFile = true;
  private tab: number = 0;

  private hasResult = false;

  private dirtyStudy = false;

  get currentBlock(): Block | undefined {
    return this.availableBlocks.find((b) => b.name == this.study.main_block);
  }

  public itemText(item: Indicator) {
    return `${item.name} (${item.observer})`;
  }

  public availableBlocks: Array<Block> = [];

  public formIsValid() {
    if (this.$refs.form != undefined) {
      let valid = (this.$refs.form as Vue & {
        validate: () => boolean;
      }).validate();
      return valid;
    }
    return false;
  }

  created(): void {
    this.studyFile = this.$route.params.studyFile;
    this.isStudyAsFile = this.$route.params.studyFile != undefined;
    this.getAsyncData();
  }

  studyNameChange() {
    if (!this.isStudyAsFile) {
      this.studyFile = this.study.name.replaceAll(" ", "_") + ".yaml";
      this.study.simu_params.result_filename = this.studyFile.replace(
        ".yaml",
        ".csv"
      );
    }
  }

  async getAsyncData(): Promise<void> {
    this.asyncDataLoaded = false;

    this.availableBlocks = await DataService.getAvailableBlocks();
    if (this.isStudyAsFile) {
      this.study = await DataService.getConfig(this.studyFile);
      this.hasResult = await DataService.hasResult(this.studyFile);
      this.study.simu_params.result_filename = this.studyFile.replace(
        ".yaml",
        ".csv"
      );
    } else {
      this.study = {
        name: "New Study",
        description: "",
        main_block: "",
        indicators: [],
        simu_params: {
          nb_runs: 1000,
          seed: 1234,
          schedule_from: 10,
          schedule_to: 1000,
          schedule_step: 10,
        },
      };

      this.studyNameChange();
    }
    this.asyncDataLoaded = true;
  }

  async save(): Promise<boolean> {
    let canSave = true;

    if (!this.isStudyAsFile) {
      canSave = await DataService.canSaveConfig(this.studyFile);
    }

    if (canSave) {
      this.cleanupStudy();

      await DataService.saveConfig(this.studyFile, this.study);
      this.isStudyAsFile = true;
    } else {
      alert(
        "Can't save config : a file with " +
          this.studyFile +
          " name already exist"
      );
    }

    return canSave;
  }

  private cleanupStudy() {
    console.info("Clean indicators");
    this.study.indicators.forEach((indicator: Indicator) => {
      let block = indicator.block;

      console.info(`Indicator ${indicator.id} has block : ${block}`);

      let b = this.availableBlocks.find((b) => b.name === block);

      if (b == undefined) {
        console.info("Block " + block + " no longer exists, clean indicator");
        this.$delete(
          this.study.indicators,
          this.study.indicators.indexOf(indicator)
        );
        return;
      }

      let observer = indicator.observer;

      console.info(`Indicator ${indicator.id} has observer : ${observer}`);
      let o = b.observers.find((o) => o.name == observer);

      if (o == undefined) {
        console.info(
          "Observer " + observer + " no longer exists, clean indicator"
        );
        this.$delete(
          this.study.indicators,
          this.study.indicators.indexOf(indicator)
        );
        return;
      }
    });
  }

  async runSimulation(): Promise<void> {
    let saved = await this.save();
    if (saved) {
      await (this.$refs.processRunner as ProcessRunner).run(this.studyFile);

      this.hasResult = await DataService.hasResult(this.studyFile);
    }
  }

  async showResults(): Promise<void> {
    let saved = await this.save();
    if (saved) {
      await DataService.loadResult(this.studyFile);

      let routeData = this.$router.resolve({
        path: `/dashboard/${this.studyFile}`,
      });
      window.open(routeData.href, "_blank");
    }
  }

  public requiredRules = [(v: any) => !!v || "Value is required"];
}
</script>
