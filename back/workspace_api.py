import json
import logging
import os
import pydantic
import yaml
from ar3_workspace import AR3Workspace
from flask import Response, abort, request
from pyc_workspace import PycatshooWorkspace


class WorkspaceDescriptor(pydantic.BaseModel):
    id: int = pydantic.Field(None, description="Workspace id")
    name: str = pydantic.Field(None, description="Workspace name")
    path: str = pydantic.Field(None, description="Workspace path")
    type: str = pydantic.Field(None, description="Workspace type")


class WorkspaceApi:

    # need to get / store them from a workspace.yaml file
    available_workspaces = []

    open_workspace = None

    def __init__(self, app):
        self.app = app

        # load workspaces from workspaces.yaml
        with open("workspaces.yaml", 'r', encoding="utf-8") as yaml_file:
            try:
                workspaces_config = yaml.load(yaml_file,
                                              Loader=yaml.FullLoader)

                for workspace_config in workspaces_config["workspaces"]:
                    self.available_workspaces.append(
                        WorkspaceDescriptor(**workspace_config))
            except yaml.YAMLError as exc:
                print(exc)
                logging.error(exc)

        app.add_url_rule("/workspace/open/<int:workspace_id>",
                         view_func=self.open, methods=["GET"])

        app.add_url_rule("/workspace/delete/<int:workspace_id>",
                         view_func=self.delete_workspace, methods=["GET"])

        app.add_url_rule("/workspace/new",
                         view_func=self.create_workspace, methods=["POST"])

        app.add_url_rule("/workspace/<int:workspace_id>/listStudies",
                         view_func=self.list_studies, methods=["GET"])
        app.add_url_rule("/workspace/<int:workspace_id>/loadStudy/<study_name>",
                         view_func=self.load_study, methods=["GET"])
        app.add_url_rule("/workspace/<int:workspace_id>/runStudy/<study_name>",
                         view_func=self.run_study, methods=["GET"])
        app.add_url_rule("/workspace/<int:workspace_id>/stopStudy/<study_name>",
                         view_func=self.stopStudy, methods=["GET"])
        app.add_url_rule("/workspace/<int:workspace_id>/hasResults/<study_name>",
                         view_func=self.hasResult, methods=["GET"])
        app.add_url_rule("/workspace/<int:workspace_id>/saveStudy/<study_name>",
                         view_func=self.save_study, methods=["POST"])

        app.add_url_rule("/workspace/<int:workspace_id>/newStudy/<study_name>",
                         view_func=self.new_study, methods=["POST"])

        app.add_url_rule("/workspace/<int:workspace_id>/data/<study_name>",
                         view_func=self.get_data, methods=["GET"])

        app.add_url_rule("/workspace/<int:workspace_id>/graphdata/<study_name>",
                         view_func=self.get_graph_data, methods=["GET"])

        app.add_url_rule("/workspace/<int:workspace_id>/systeminfos/<study_name>",
                         view_func=self.get_system_info, methods=["GET"])

        app.add_url_rule("/workspace/list",
                         view_func=self.list, methods=["GET"])

        app.add_url_rule("/workspace/<int:workspace_id>/getSystems",
                         view_func=self.get_systems, methods=["GET"])

    def save_workspaces(self):
        with open("workspaces.yaml", 'w', encoding="utf-8") as yaml_file:
            try:
                workspaces = [x.dict() for x in self.available_workspaces]
                yaml.dump({"workspaces": workspaces}, yaml_file)

            except yaml.YAMLError as exc:
                print(exc)
                logging.error(exc)

    def list(self):
        workspacesDescriptorSerializable = [
            x.dict() for x in self.available_workspaces]
        return Response(json.dumps(workspacesDescriptorSerializable),  mimetype='application/json')

    def open(self, workspace_id):
        logging.info(f'Try to open workspace with id {workspace_id}')
        workspace = self.get_workspace(workspace_id)
        return Response(workspace.json(include={'id', 'name', 'type'}),  mimetype='application/json')

    def delete_workspace(self, workspace_id):
        logging.info(f'Try to delete workspace with id {workspace_id}')

        workspace = next(
            (x for x in self.available_workspaces if x.id == workspace_id), None)

        if workspace is not None:
            self.available_workspaces.remove(workspace)
            self.save_workspaces()

        return Response()

    def create_workspace(self):
        logging.info('Try to create workspace')

        workspace_config = json.loads(request.data)

        # search new id

        id = -1
        id_free = False
        while (not id_free):
            id += 1
            workspace_description = next(
                (x for x in self.available_workspaces if x.id == id), None)
            id_free = workspace_description is None

        workspace_config.update({"id": id})

        logging.info(workspace_config)
        self.available_workspaces.append(
            WorkspaceDescriptor(**workspace_config))

        self.save_workspaces()

        return Response()

    def get_workspace(self, workspace_id):

        if self.open_workspace and self.open_workspace.id == workspace_id:
            return self.open_workspace

        if self.open_workspace is not None:
            self.open_workspace.close()

        workspace_description = next(
            (x for x in self.available_workspaces if x.id == workspace_id), None)

        if workspace_description is None:
            logging.error(f'Can\'t find Workspace with id {workspace_id}')
            abort(404)

        logging.info(f'Open workspace {workspace_description.name}')

        workspace_instance = None
        if workspace_description.type == "ar3":
            workspace_instance = AR3Workspace(**workspace_description.dict())
        elif workspace_description.type == "pycatshoo":
            workspace_instance = PycatshooWorkspace(
                **workspace_description.dict())
        else:
            logging.error(
                f'Can\'t instanciate Workspace {workspace_id} with type {workspace_description.type}')
            abort(404)

        self.open_workspace = workspace_instance

        return workspace_instance

    def list_studies(self, workspace_id):

        workspace = self.get_workspace(workspace_id)
        configsMeta = workspace.get_study_files()

        return Response(json.dumps(configsMeta),  mimetype='application/json')

    def load_study(self, workspace_id, study_name):

        workspace = self.get_workspace(workspace_id)
        study = workspace.get_study(study_name)
        return Response(json.dumps(study),  mimetype='application/json')

    def run_study(self, workspace_id, study_name):

        workspace = self.get_workspace(workspace_id)

        return_code = workspace.run_study(study_name)

        return Response(json.dumps(return_code),  mimetype='application/json')

    def stopStudy(self, workspace_id, study_name):

        workspace = self.get_workspace(workspace_id)

        workspace.stop_study()

        return Response()

    def get_systems(self, workspace_id):
        workspace = self.get_workspace(workspace_id)
        return Response(json.dumps(workspace.get_systems()),  mimetype='application/json')

    def new_study(self, workspace_id, study_name):

        workspace = self.get_workspace(workspace_id)

        workspace.new_study(study_name)

        return Response()

    def save_study(self, workspace_id, study_name):

        workspace = self.get_workspace(workspace_id)

        study_filename = workspace.get_study_path(study_name)

        fileExist = os.path.isfile(study_filename)

        with open(study_filename, 'w+',
                  encoding="utf-8") as yaml_file:
            try:
                yaml.dump(request.json,
                          yaml_file)

                # if we just have created the study_filename, chmod it to avoid docker study_filename creation impossible to write
                if not fileExist:
                    os.chmod(study_filename, 0o666)
            except yaml.YAMLErrorstr as exc:
                logging.error(exc)

        return Response()

    def hasResult(self, workspace_id, study_name):

        return Response(json.dumps(True), mimetype='application/json')
        workspace = self.get_workspace(workspace_id)
        return Response(json.dumps(workspace.has_result(study_name)), mimetype='application/json')

    def get_data(self, workspace_id, study_name):

        indic_name = request.args.get('tab_name')
        workspace = self.get_workspace(workspace_id)
        indic_df = workspace.get_data(study_name, indic_name)
        return Response(indic_df.to_json(orient="records"),
                        mimetype='application/json')

    def get_system_info(self, workspace_id, study_name):

        workspace = self.get_workspace(workspace_id)
        infos = workspace.get_system_info(study_name)
        return Response(json.dumps(infos),
                        mimetype='application/json')

    def get_graph_data(self, workspace_id, study_name):

        indic_name = request.args.get('indicatorId')
        workspace = self.get_workspace(workspace_id)
        fig = workspace.get_graph_data(study_name, indic_name)
        return Response(fig.to_json(),
                        mimetype='application/json')
