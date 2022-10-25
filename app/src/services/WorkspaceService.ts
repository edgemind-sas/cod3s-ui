import environment from "@/environment";
import Workspace from "@/models/Workspace";
import axios from "axios";

const API_URL = environment.backendUrl;

class WorkspaceService {
  async getWorkspaces(): Promise<Array<Workspace>> {
    const response = await axios.get(API_URL + "/workspace/list");
    return response.data as Array<Workspace>;
  }

  async openWorkspace(workspaceId: number): Promise<Workspace> {
    const response = await axios.get(
      API_URL + `/workspace/open/${workspaceId}`
    );
    return response.data as Workspace;
  }

  async deleteWorkspace(workspaceId: number): Promise<void> {
    await axios.get(API_URL + `/workspace/delete/${workspaceId}`);
  }

  async createWorkspace(workspace: Workspace): Promise<void> {
    await axios.post(API_URL + `/workspace/new`, workspace);
  }

  async getAvailableStudies(workspaceId: number): Promise<Array<any>> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/listStudies`
    );
    return response.data as Array<any>;
  }

  async getAvailableSystems(workspaceId: number): Promise<Array<any>> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/getSystems`
    );
    return response.data as Array<any>;
  }

  async loadStudy(workspaceId: number, studyName: string): Promise<any> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/loadStudy/${studyName}`
    );

    return response.data;
  }

  async runStudy(workspaceId: number, studyName: string): Promise<number> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/runStudy/${studyName}`
    );

    return response.data;
  }

  async hasResults(workspaceId: number, studyName: string): Promise<boolean> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/hasResults/${studyName}`
    );

    return response.data;
  }

  async stopStudy(workspaceId: number, studyName: string): Promise<void> {
    await axios.get(
      API_URL + `/workspace/${workspaceId}/stopStudy/${studyName}`
    );
  }

  async saveConfig(workspaceId: number, studyFile: string, study: any) {
    await axios.post(
      API_URL + `/workspace/${workspaceId}/saveStudy/${studyFile}`,
      study
    );
  }

  async canSaveConfig(
    workspaceId: number,
    studyFile: string
  ): Promise<boolean> {
    const response = await axios.get(API_URL + "/can-save-config", {
      params: { file: studyFile },
    });
    return response.data;
  }

  async createStudy(workspaceId: number, studyFile: string): Promise<void> {
    await axios.post(
      API_URL + `/workspace/${workspaceId}/newStudy/${studyFile}`
    );
  }

  async getSystemInfo(
    workspaceId: number,
    studyName: string
  ): Promise<boolean> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/systeminfos/${studyName}`
    );

    return response.data;
  }

  async getTabData(
    workspaceId: number,
    studyFile: string,
    tab_name: string
  ): Promise<Array<any>> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/data/${studyFile}`,
      {
        params: { tab_name: tab_name },
      }
    );
    return response.data;
  }

  async getGraphData(
    workspaceId: number,
    studyFile: string,
    indicatorId: string
  ): Promise<{ data: Array<Plotly.Data>; layout: Plotly.Layout }> {
    const response = await axios.get(
      API_URL + `/workspace/${workspaceId}/graphdata/${studyFile}`,
      {
        params: { indicatorId: indicatorId },
      }
    );
    return response.data;
  }
}

export default new WorkspaceService();
