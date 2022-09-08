<template>
  <v-container pa-10>
    <v-row align="center" justify="center">
      <v-col cols="8">
        <v-card outlined style="border: 0.15em solid black" v-if="isAr3()">
          <v-card-title class="justify-center primary--text">
            <h2>Load a result file</h2>
          </v-card-title>
          <v-card-text>
            <v-row align="center" justify="center">
              <v-col cols="5">
                <v-file-input
                  accept=".csv"
                  label="Result file"
                  v-model="fileToUpload"
                  :loading="uploading"
                  :disabled="uploading"
                ></v-file-input>
              </v-col>
              <v-col cols="2">
                <v-btn
                  color="accent"
                  :disabled="uploading || fileToUpload == null"
                  @click="uploadFile()"
                  ><v-icon left>mdi-upload</v-icon>
                  Upload files
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <v-card class="mt-4" outlined style="border: 0.15em solid black">
          <v-card-title class="justify-center primary--text">
            <h2>List of studies</h2>
            <v-btn outlined color="primary" class="ml-5" to="/editStudy/"
              ><v-icon left dark> mdi-plus </v-icon>New study</v-btn
            >
          </v-card-title>
          <v-text-field
            label="Search study"
            prepend-inner-icon="mdi-magnify"
            v-model="filterStudy"
            clearable
            type="text"
            outlined
            rounded
            class="ml-10 mr-10"
            hide-details="auto"
          ></v-text-field>
          <v-list class="pa-3">
            <template v-for="(item, i) in filteredConfigList">
              <v-list-item :key="item.file_name">
                <v-list-item-content>
                  <v-list-item-title class="mb-2" style="font-size: x-large">{{
                    item.study_name
                  }}</v-list-item-title>
                  <v-list-item-subtitle>
                    <v-icon small left>mdi-file</v-icon>

                    <span>{{ item.file_name }}</span>

                    <v-btn
                      @click="renameFile(item)"
                      class="ma-2"
                      text
                      icon
                      x-small
                    >
                      <v-icon>mdi-pen</v-icon>
                    </v-btn>
                  </v-list-item-subtitle>
                  <v-list-item-subtitle>
                    <v-icon small left>mdi-clock-outline</v-icon>
                    <span>{{ item.last_modified }}</span></v-list-item-subtitle
                  >
                </v-list-item-content>
                <v-list-item-action>
                  <v-row
                    ><v-btn
                      small
                      outlined
                      color="primary"
                      class="mr-1"
                      @click="copyConfig(item.file_name)"
                      ><v-icon left> mdi-content-copy </v-icon>
                      Copy
                    </v-btn>
                    <v-btn
                      :to="'/editStudy/' + item.file_name"
                      small
                      outlined
                      color="primary"
                      class="mr-1"
                      style="cursor: pointer"
                      ><v-icon left> mdi-pen </v-icon> Edit </v-btn
                    ><v-btn
                      small
                      outlined
                      color="primary"
                      class="mr-1"
                      @click="deleteConfig(item.file_name)"
                      ><v-icon left> mdi-delete </v-icon>
                      Delete
                    </v-btn>
                    <v-btn
                      small
                      outlined
                      color="accent"
                      class="mr-1"
                      @click="run(item.file_name)"
                      ><v-icon left> mdi-cog </v-icon>
                      Simulate
                    </v-btn>
                    <v-btn
                      small
                      @click="showDashboard(item.file_name)"
                      :disabled="!item.has_csv"
                      outlined
                      color="primary"
                      ><v-icon left> mdi-chart-line </v-icon> Show
                      results</v-btn
                    >
                  </v-row>
                </v-list-item-action>
              </v-list-item>
              <v-divider v-if="i < configList.length - 1" :key="i"></v-divider>
            </template>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <process-runner ref="processRunner"></process-runner>
  </v-container>
</template>

<script lang="ts">
import DataService from "@/services/DataService";
import { Component, Inject, Vue } from "vue-property-decorator";
import ProcessRunner from "@/components/ProcessRunner.vue";
import StudyType from "@/models/StudyType";
import AppService from "@/services/AppService";

@Component({
  components: {
    ProcessRunner,
  },
})
export default class DataManager extends Vue {
  public studyType: StudyType = AppService.getStudyType();

  public uploading = false;
  public fileToUpload: File | null = null;
  public configList: Array<any> = [];
  public filterStudy = "";

  mounted(): void {
    this.getAsyncData();
  }

  async getAsyncData(): Promise<void> {
    let availableConfigs = await DataService.getAvailableConfigs();
    this.configList = availableConfigs;
  }

  get filteredConfigList(): Array<any> {
    return this.configList.filter(
      (t) =>
        this.filterStudy == null ||
        t.study_name.toLowerCase().includes(this.filterStudy.toLowerCase())
    );
  }

  public async uploadFile(): Promise<void> {
    this.uploading = true;

    let tabs: Array<string> = [];
    if (this.fileToUpload instanceof File) {
      tabs = await DataService.uploadFiles(this.fileToUpload);
    }

    this.uploading = false;
    this.fileToUpload = null;

    this.$root.$emit("DATA_FILE_LOADED", tabs);
    this.$router.push("/dashboard");
  }

  public async run(configFileName: string): Promise<void> {
    await (this.$refs.processRunner as ProcessRunner).run(configFileName);
    await this.getAsyncData();
  }

  async renameFile(item: any): Promise<void> {
    let newName = prompt('Rename "' + item.file_name + '":', item.file_name);

    if (newName && newName !== item.file_name) {
      let valid = true;
      // check that file doesn't exist
      this.configList.forEach((element) => {
        if (element.file_name === newName) {
          alert("A config file " + newName + " already exists");
          valid = false;
        }
      });

      if (valid) {
        await DataService.renameConfig(item.file_name, newName);
        await this.getAsyncData();
      }
    }
  }

  async deleteConfig(item: string): Promise<void> {
    if (confirm("Do you really want to delete " + item + "?")) {
      await DataService.deleteConfig(item);
      await this.getAsyncData();
    }
  }

  async copyConfig(item: string): Promise<void> {
    await DataService.copyConfig(item);
    await this.getAsyncData();
  }

  async showDashboard(item: string): Promise<void> {
    await DataService.loadResult(item);

    let routeData = this.$router.resolve({
      path: `/dashboard/${item}`,
    });
    window.open(routeData.href, "_blank");
  }

  isAr3(): boolean {
    return this.studyType === StudyType.AR3;
  }
}
</script>
