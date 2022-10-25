
import logging

import plotly.graph_objects as go
import os
import yaml
import cod3slib.pycatshoo
import Pycatshoo as pyc
import shutil
import pandas as pd


from workspace import Workspace


class PycatshooWorkspace(Workspace):

    current_study: cod3slib.StudyModel = None

    def get_study(self, study_name):
        study_filename = self.get_study_path(study_name)
        with open(study_filename, 'r', encoding="utf-8") as yaml_file:
            return yaml.load(yaml_file, Loader=yaml.FullLoader)

    def load_study(self, study_name):
        study_filename = self.get_study_path(study_name)
        if self.current_study and self.current_study.system_model:
            pyc.CSystem.deleteSys(self.current_study.system_model.bkd)
        self.current_study = cod3slib.StudyModel.from_yaml(
            study_filename, self.path, self.get_result_folder(study_name))

    def get_result_folder(self, study_name):
        return os.path.join(self.get_studies_folder_path(),
                            study_name.replace(".yaml", ".results"))

    def prepare_results_folder(self, study_name):
        results_folder = self.get_result_folder(study_name)

        if os.path.exists(results_folder) and os.path.isdir(results_folder):
            shutil.rmtree(results_folder)

        # create a result folder
        os.mkdir(results_folder)

        return results_folder

    def _store_results(self, study_name):
        study = self.current_study

        results_folder = self.get_result_folder(study_name)

        for indicator in study.indicators:
            indicator_desc = indicator.dict(
                exclude={"values", "bkd", "instants"})
            indicator_file_name = os.path.join(
                results_folder, f'{indicator.name}.yaml')
            with open(indicator_file_name, 'w+',
                      encoding="utf-8") as yaml_file:
                try:
                    yaml.dump(indicator_desc, yaml_file)

                except yaml.YAMLErrorstr as exc:
                    logging.error(exc)

            indicator_result_filename = os.path.join(
                results_folder, f'{indicator.name}.csv')
            indicator.values.pivot_table(
                values='value', index="instant", columns='stat', aggfunc='first').to_csv(indicator_result_filename)

    def new_study(self, study_name):
        if self.current_study:
            pyc.CSystem.deleteSys(self.current_study.system_model.bkd)

        simu = {"simu_params": {"nb_runs": 1,
                                "schedule": [{"end": 500, "nvalues": 100, "start": 0}]}}

        self.current_study = cod3slib.StudyModel(**simu)
        study_filename = self.get_study_path(study_name)

        fileExist = os.path.isfile(study_filename)

        with open(study_filename, 'w+',
                  encoding="utf-8") as yaml_file:
            try:

                study = self.current_study.dict()
                study.update({"cls": "PycStudy", "name": "New study"})

                yaml.dump(study,
                          yaml_file)

                # if we just have created the study_filename, chmod it to avoid docker study_filename creation impossible to write
                if not fileExist:
                    os.chmod(study_filename, 0o666)
            except yaml.YAMLErrorstr as exc:
                logging.error(exc)

    def run_study(self, study_name):
        with open("stdout.txt", "w") as out:
            try:
                out.writelines("Start simulation\n")
                self.prepare_results_folder(study_name)
                self.load_study(study_name)

                # self.execute_before_hooks(study_name)

                self.current_study.run_simu()

                # self.execute_after_hooks(study_name)

                # store results
                self._store_results(study_name)

                out.writelines("Simulation complete\n")
            except Exception as e:
                out.write("Error during simulation\n")
                out.write(str(e))
                return -1
        return 0

    def accept_study(self, study_dict):
        return "cls" in study_dict and study_dict["cls"] == "PycStudy"

    def stop_study(self):

        if self.current_study:
            pyc.CSystem.deleteSys(self.current_study.system_model.bkd)
            self.current_study = None
        if os.path.exists("stdout.txt"):
            os.remove("stdout.txt")

    def get_systems(self):

        # search all yaml files with cls: PycSystem attribute
        systemsFiles = []
        for root, dirnames, filenames in os.walk(self.path):
            for filename in filenames:
                if filename.endswith("yaml"):
                    potential_system_file = os.path.join(root, filename)
                    relative_path = os.path.relpath(
                        potential_system_file, self.path)
                    with open(potential_system_file, 'r', encoding="utf-8") as yaml_file:
                        potential_system = yaml.load(yaml_file,
                                                     Loader=yaml.FullLoader)

                        if "cls" in potential_system and potential_system["cls"] == "PycSystem":

                            fileMeta = {
                                "name": potential_system["name"], "path": relative_path, "content": potential_system}
                            systemsFiles.append(fileMeta)
        return systemsFiles

    def get_system_info(self, study_name):

        self.load_study(study_name)
        components = {}
        for component_name, component in self.current_study.system_model.components.items():
            components.update(
                {component_name: [var.name().removeprefix(component_name + ".") for var in component.bkd.getVariables()]})
        return components

    def has_result(self, study_name):
        results_folder = os.path.join(self.get_studies_folder_path(),
                                      study_name.replace(".yaml", ".results"))

        return os.path.exists(results_folder)

    def get_data(self, study_name, indic_name):

        results_folder = os.path.join(self.get_studies_folder_path(),
                                      study_name.replace(".yaml", ".results"))

        return pd.read_csv(os.path.join(results_folder, f'{indic_name}.csv'))

    def get_graph_data(self, study_name, indic_name):

        fig = go.Figure()
        line_color = "#4C78A8"
        fig_layout = "auto"

        results_folder = os.path.join(self.get_studies_folder_path(),
                                      study_name.replace(".yaml", ".results"))

        indic_df = pd.read_csv(os.path.join(
            results_folder, f'{indic_name}.csv'))

        fig.add_scatter(
            x=indic_df["instant"].to_list(),
            y=indic_df["mean"].to_list(),
            mode='lines+markers',
            name="mean",
            legendgroup=indic_name,
            legendgrouptitle_text=indic_name,
            # showlegend=True,
            line_width=1,
            line_color=line_color
        )

        return fig

    def close(self):
        if self.current_study is not None:
            self.stop_study()
