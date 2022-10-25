<template>
  <v-row justify="center">
    <v-col cols="11">
      <v-form ref="form">
        <template v-if="asyncDataLoaded">
          <v-card class="mt-4">
            <v-card-title>
              <v-btn
                :to="'/workspace/' + workspaceId"
                outlined
                color="primary"
                class="ml-5"
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
                <v-tab> General </v-tab>
                <v-tab> Indicators </v-tab>
                <v-tab> Dashboard </v-tab>
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
                      :items="availableSystems"
                      item-text="name"
                      item-value="path"
                      label="System"
                      v-model="study.system_model"
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
                          :value="study.simu_params.schedule[0].start"
                          @input="
                            study.simu_params.schedule[0].start = Number($event)
                          "
                          type="number"
                          :hide-details="true"
                          @change="dirtyStudy = true"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="4">
                        <v-text-field
                          outlined
                          :value="study.simu_params.schedule[0].end"
                          @input="
                            study.simu_params.schedule[0].end = Number($event)
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
                          :value="study.simu_params.schedule[0].nvalues"
                          @input="
                            study.simu_params.schedule[0].nvalues =
                              Number($event)
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
                  <pyc-indicators-configurator
                    :system="currentSystem"
                    :indicators="study.indicators"
                    :studyName="studyFile"
                    :workspaceId="workspaceId"
                    v-on:dirty-config="dirtyStudy = true"
                  ></pyc-indicators-configurator
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
import PycIndicatorsConfigurator from "@/components/PycIndicatorsConfigurator.vue";
import DataService from "@/services/DataService";
import System from "@/models/System";
import Study from "@/models/Study";
import Indicator from "@/models/Indicator";
import WorkspaceService from "@/services/WorkspaceService";

@Component({
  components: {
    ProcessRunner,
    IndicatorsConfigurator,
    PycIndicatorsConfigurator,
  },
})
export default class EditStudy extends Vue {
  public studyFile = "";
  public workspaceId: number = -1;
  public study: Study | any = {};
  public asyncDataLoaded = false;
  private isStudyAsFile = true;
  private tab: number = 0;

  private hasResult = false;

  private dirtyStudy = false;

  get currentSystem(): System | undefined {
    return this.availableSystems.find((b) => b.path == this.study.system_model);
  }

  public itemText(item: Indicator) {
    return `${item.name} (${item.observer})`;
  }

  public availableSystems: Array<System> = [];

  public formIsValid() {
    if (this.$refs.form != undefined) {
      let valid = (
        this.$refs.form as Vue & {
          validate: () => boolean;
        }
      ).validate();
      return valid;
    }
    return false;
  }

  created(): void {
    this.workspaceId = parseInt(this.$route.params.workspaceId);
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

    this.availableSystems = await WorkspaceService.getAvailableSystems(
      this.workspaceId
    );
    if (this.isStudyAsFile) {
      this.study = await WorkspaceService.loadStudy(
        this.workspaceId,
        this.studyFile
      );
      this.hasResult = false; //await DataService.hasResult(this.studyFile);
      this.study.simu_params.result_filename = this.studyFile.replace(
        ".yaml",
        ".csv"
      );
    } else {
      this.study = {
        name: "New Study",
        description: "",
        system_model: "",
        indicators: [],
        simu_params: {
          nb_runs: 1000,
          seed: 1234,
          schedule: [
            {
              start: 10,
              stop: 1000,
              nvalues: 10,
            },
          ],
        },
      };

      this.studyNameChange();
    }
    this.asyncDataLoaded = true;
  }

  async save(): Promise<boolean> {
    let canSave = true;

    if (!this.isStudyAsFile) {
      canSave = await WorkspaceService.canSaveConfig(
        this.workspaceId,
        this.studyFile
      );
    }

    if (canSave) {
      //this.cleanupStudy();

      await WorkspaceService.saveConfig(
        this.workspaceId,
        this.studyFile,
        this.study
      );
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
      let System = indicator.System;

      console.info(`Indicator ${indicator.id} has System : ${System}`);

      let b = this.availableSystems.find((b) => b.name === System);

      if (b == undefined) {
        console.info("System " + System + " no longer exists, clean indicator");
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
      await (this.$refs.processRunner as ProcessRunner).run(
        this.workspaceId,
        this.studyFile
      );

      this.hasResult = await WorkspaceService.hasResults(
        this.workspaceId,
        this.studyFile
      );
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
