
import os
from datetime import datetime
from pathlib import Path

import pydantic
import yaml


class Workspace(pydantic.BaseModel):

    id: int = pydantic.Field(
        None, description="Workspace name")

    name: str = pydantic.Field(
        None, description="Workspace name")

    path: str = pydantic.Field(
        None, description="Workspace path")

    type: str = pydantic.Field(
        None, description="Workspace type")

    def get_studies_folder_path(self):
        return os.path.join(self.path, "studies")

    def get_study_path(self, study_file_name):
        return os.path.join(self.get_studies_folder_path(), study_file_name)

    def get_study_files(self):

        configFiles = []
        for root, dirnames, filenames in os.walk(self.get_studies_folder_path()):
            for filename in filenames:
                if filename.endswith("yaml"):
                    configFiles.append(os.path.join(root, filename))

        configsMeta = []
        for configFile in configFiles:

            fileMeta = {}
            with open(configFile, 'r', encoding="utf-8") as yaml_file:
                study_specs = yaml.load(yaml_file,
                                        Loader=yaml.FullLoader)

                if not self.accept_study(study_specs):
                    continue

                fileMeta["study_name"] = study_specs['name']

            fileMeta["file_name"] = Path(configFile).name
            fileMeta["last_modified"] = datetime.fromtimestamp(
                os.stat(configFile).st_mtime).strftime('%Y-%m-%d-%H:%M')

            fileMeta["has_result"] = self.has_result(fileMeta["file_name"])
            configsMeta.append(fileMeta)
        return configsMeta

    def get_study(self, study_name):
        raise ("not implemented")

    def run_study(self, study_name):
        raise ("not implemented")

    def new_study(self, study_name):
        raise ("not implemented")

    def accept_study(self, study_dict):
        return True

    def stop_study(self):
        raise ("not implemented")

    def get_systems(self):
        raise ("not implemented")

    def has_result(self, study_name):
        raise ("not implemented")

    def get_data(self, study_name, indic_name):
        raise ("not implemented")

    def get_graph_data(self, study_name, indic_name):
        raise ("not implemented")

    def get_system_info(self):
        raise ("not implemented")

    def close(self):
        raise ("not implemented")
