import environment from "@/environment";
import Block from "@/models/Block";
import Study from "@/models/Study";
import axios from "axios";
import Plotly from "plotly.js";

const API_URL = environment.backendUrl;

class DataService {
  async downloadIndicatorsData() {
    const response = await axios.get(API_URL + "/downloadIndicatorsData", {
      responseType: "blob",
    });
    return response.data;
  }
  async getIndicatorConfig() {
    const response = await axios.get(API_URL + "/indicatorsConfig");
    return response.data;
  }
  async getConfig(fileConfig: string): Promise<Study> {
    const response = await axios.get(API_URL + "/get-config", {
      params: { file: fileConfig },
    });

    const study: Study = response.data;

    // for old config files, add main system and id
    study.indicators.forEach((indic) => {
      if (indic.system == null) {
        indic.system = study.system_model;
      }

      if (indic.id == null) {
        indic.id = this.generateId();
      }
    });

    return study;
  }

  public generateId(): string {
    return Math.floor(Math.random() * Date.now()).toString();
  }

  async deleteConfig(file: string): Promise<string> {
    const response = await axios.get(API_URL + "/delete-config", {
      params: { file: file },
    });
    return response.data;
  }

  async copyConfig(file: string): Promise<string> {
    const response = await axios.get(API_URL + "/copy-config", {
      params: { file: file },
    });
    return response.data;
  }

  async saveConfig(filename: string, study: Study): Promise<void> {
    await axios.post(API_URL + "/save-config/" + filename, study);
  }

  async canSaveConfig(file: string): Promise<boolean> {
    const response = await axios.get(API_URL + "/can-save-config", {
      params: { file: file },
    });
    return response.data;
  }

  async renameConfig(oldName: string, newName: string) {
    const response = await axios.get(API_URL + "/rename-config", {
      params: { file: oldName, new_name: newName },
    });
    return response.data;
  }

  async uploadFiles(fileToUpload: File): Promise<Array<string>> {
    const formData = new FormData();
    formData.append("files", fileToUpload);
    const response = await axios.post(API_URL + "/upload_files", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }

  async getVersion(): Promise<string> {
    const response = await axios.get(API_URL + "/version");
    return response.data.version;
  }

  async getStudyType(): Promise<string> {
    const response = await axios.get(API_URL + "/studyType");
    return response.data.study_type;
  }

  async getTabData(tab_name: string): Promise<Array<any>> {
    const response = await axios.get(API_URL + "/getData", {
      params: { tab_name: tab_name },
    });
    return response.data;
  }

  async getTabs(): Promise<Array<string>> {
    const response = await axios.get(API_URL + "/getTabs");
    return response.data;
  }

  async getGraphData(
    indicatorId: string
  ): Promise<{ data: Array<Plotly.Data>; layout: Plotly.Layout }> {
    const response = await axios.get(API_URL + "/getGraph", {
      params: { indicatorId: indicatorId },
    });
    return response.data;
  }

  async getMultiGraphData(
    indicatorIds: Array<string>
  ): Promise<{ data: Array<Plotly.Data>; layout: Plotly.Layout }> {
    const response = await axios.get(API_URL + "/getGraphMulti", {
      params: { indicatorIds: indicatorIds.join(",") },
    });
    return response.data;
  }

  async getLogs(): Promise<Array<string>> {
    const response = await axios.get(API_URL + "/getSimuLogs");
    return response.data;
  }

  async runSimu(configFileName: string): Promise<number> {
    const response = await axios.get(API_URL + "/runSimu", {
      params: { file: configFileName },
    });
    return response.data;
  }

  async loadResult(configFileName: string): Promise<number> {
    const response = await axios.get(API_URL + "/loadFile", {
      params: { file: configFileName },
    });
    return response.data;
  }

  async hasResult(configFileName: string): Promise<boolean> {
    const response = await axios.get(API_URL + "/hasResult", {
      params: { file: configFileName },
    });
    return response.data;
  }

  async stopSimu(): Promise<Array<string>> {
    const response = await axios.get(API_URL + "/stopSimu");
    return response.data;
  }

  async getAvailableConfigs(): Promise<Array<any>> {
    const response = await axios.get(API_URL + "/config-files");
    return response.data;
  }

  async getAvailableBlocks(): Promise<Array<Block>> {
    const response = await axios.get(API_URL + "/getBlocks");
    return response.data;
  }
}

export default new DataService();
