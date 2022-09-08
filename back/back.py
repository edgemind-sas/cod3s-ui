from http import HTTPStatus
import io
from flask import Flask, request, render_template, Response
from flask_cors import CORS, cross_origin
import json
import os
import pkg_resources
import yaml
import sys
import glob
import argparse
import logging
import pathlib
from app_models import AR3App
from pyar3 import STOStudy, STOStudyResults
import subprocess
import time
from datetime import datetime
import shutil
import tempfile

installed_pkg = {pkg.key for pkg in pkg_resources.working_set}
if 'ipdb' in installed_pkg:
    import ipdb  # noqa: 401


# Utility functions
# -----------------
def find_directory(dirname=None, of_file=None, root='.'):
    for path, dirs, files in os.walk(root):
        if not(dirname is None) and (dirname in dirs):
            return os.path.join(path, dirname)
        elif not(of_file is None) and (of_file in files):
            return path

    return None


app_config = {}
app_config["app_name_short"] = "ar3-study-results"
app_config["app_name_long"] = "AR3 study results API"

app_config["author"] = "Developed by EdgeMind (www.edgemind.net) 2021"
app_config["version"] = "0.0.4"

app_config["config_filename"] = os.path.join(os.path.dirname(__file__),
                                             "config.yaml")

app_config["local_config_filename"] = os.path.join(str(pathlib.Path.home()),
                                                   ".ar3simu.conf")

app_config["temp_dir"] = tempfile.gettempdir()


# CLI parameters management
# -------------------------
APP_ARG_PARSER = argparse.ArgumentParser(
    description=app_config["app_name_short"] + " " + app_config["version"])

# APP_ARG_PARSER.add_argument(
#     type=str,
#     dest='project_directory',
#     help='Project Directory.')

APP_ARG_PARSER.add_argument(
    '-w', '--project-folder',
    dest='project_folder',
    action='store',
    default=".",
    help='Project folder (default .)')

APP_ARG_PARSER.add_argument(
    '-f', '--config-study_filename',
    dest='config_filename',
    action='store',
    default=app_config["config_filename"],
    help='Configuration study_filename.')

APP_ARG_PARSER.add_argument(
    '-r', '--reset-app-data',
    dest='reset_app_data',
    action='store_true',
    default=False,
    help='Remove app data to have a fresh restart.')

APP_ARG_PARSER.add_argument(
    '-p', '--progress',
    dest='progress_mode',
    action='store_true',
    default=False,
    help='Show progress bar in the console.')

APP_ARG_PARSER.add_argument(
    '-v', '--verbose',
    dest='verbose_mode',
    action='store_true',
    default=False,
    help='Display log information on stardard output.')

APP_ARG_PARSER.add_argument(
    '-d', '--debug',
    dest='debug_mode',
    action='store_true',
    default=False,
    help='Display debug on stardard output.')


APP_INPUT_ARGS = APP_ARG_PARSER.parse_args()

app_config.update(vars(APP_ARG_PARSER.parse_args()))


currentProcess = None


# app_config["configFolder"] = join(app_config['project_directory'], "studies")
# if not os.path.exists(app_config["configFolder"]):
#     os.mkdir(app_config["configFolder"])

# Logging configuration
if app_config["verbose_mode"]:
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO)
if app_config["debug_mode"]:
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG)


# -------------------------------------


# TODO : Make this more modular
# Loading Local AR3 study configuration
local_config_filename = app_config["local_config_filename"]
local_config_file = pathlib.Path(local_config_filename)

if not(local_config_file.is_file()):
    ar3simu_bin_dir = \
        find_directory(of_file="gtsstocmp.sh",
                       root=str(pathlib.Path.home()))

    if not(ar3simu_bin_dir is None):
        logging.info(f"AR3 simulator binary found at {ar3simu_bin_dir}")
        logging.info(
            f"Configuration saved in file {local_config_filename}")

        with open(local_config_filename, 'w', encoding="utf-8") \
                as yaml_file:
            try:
                ar3_config = yaml.dump(
                    {"ar3bin_folder": ar3simu_bin_dir},
                    yaml_file)

            except yaml.YAMLError as exc:
                print(exc)
                logging.error(exc)
    else:
        logging.error(
            f"Configuration file {local_config_filename} not found, "
            f"please create it specifying the ar3config_folder attribute")

        sys.exit(1)

with open(app_config["local_config_filename"], 'r', encoding="utf-8") as yaml_file:
    try:
        ar3_local_config = yaml.load(yaml_file,
                                     Loader=yaml.FullLoader)

    except yaml.YAMLError as exc:
        print(exc)
        logging.error(exc)


# -------------------------------------
# Loading study configuration
with open(app_config["config_filename"], 'r', encoding="utf-8") as yaml_file:
    try:
        ar3_config = yaml.load(yaml_file,
                               Loader=yaml.FullLoader)

        ar3_config.update(ar3_local_config)

        # Add project_folder in config
        ar3_config.update({"project_folder": app_config["project_folder"]})

    except yaml.YAMLError as exc:
        print(exc)
        logging.error(exc)



app_bknd = AR3App(**ar3_config)

# load blocks at startup
app_bknd.parse_blocks()

# app_bknd.update_data_sel()

# API Flask
# ---------

app = Flask(__name__, static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route("/")
@app.route("/dashboard/<path:text>")
@app.route("/dashboard")
def index():
    return render_template("index.html")


@app.route("/version")
def getVersion():
    return Response(json.dumps({"version": app_config["version"]}),
                    mimetype='application/json')

@app.route("/upload_files", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    # It must be only one study_filename
    study_file = files[0]
    study_filename = os.path.join(
        app_config["temp_dir"], study_file.filename)
    os.makedirs(os.path.dirname(study_filename), exist_ok=True)
    study_file.save(study_filename)

    app_bknd.study_res = STOStudyResults.from_result_csv(study_filename)
    # for study_filename in files:
    #     # study_filename.save(os.path.join(app_bknd.etl.data_raw_dir, study_filename.study_filename))
    #     logging.info(f'Receive study_filename {study_filename.study_filename}')

    # xl = pd.ExcelFile('fake.xlsx')

    return Response(json.dumps(list(app_bknd.study_res.indicators.keys())),
                    mimetype='application/json')


@app.route("/loadFile", methods=["GET"])
def loadFile():
    study_filename = request.args.get('file', default='', type=str)
    study_pathname = os.path.join(app_bknd.get_studies_folder(),
                                  study_filename)

    app_bknd.study = STOStudy.from_yaml(study_pathname)

    app_bknd.study_res = \
        STOStudyResults.from_result_csv(os.path.join(
            app_bknd.get_studies_folder(),
            study_filename.replace(".yaml", ".csv")))

    return Response()


@app.route("/getTabs", methods=["GET"])
def get_tabs():

    tabs = list(app_bknd.study_res.indicators.keys()
                ) if app_bknd.study_res is not None else []

    return Response(json.dumps(tabs),
                    mimetype='application/json')


@app.route("/getData")
def getData():

    indic_name = request.args.get('tab_name')
    indic_df = app_bknd.study_res.indicators[indic_name].data
    return Response(indic_df.to_json(orient="records"),
                    mimetype='application/json')


@app.route("/getGraph")
def getGraph():

    indic_id = request.args.get('indicatorId')

    if not(indic_id in app_bknd.study_res.indicators):
        return Response(None,
                        mimetype='application/json')
    else:
        fig = app_bknd.create_indic_fig(indic_id)

        return Response(fig.to_json(),
                        mimetype='application/json')


@app.route("/getGraphMulti")
def getGraphMulti():

    indic_ids = request.args.get('indicatorIds').split(",")

    fig = app_bknd.create_multi_indic_fig(indic_ids)

    return Response(fig.to_json(),
                    mimetype='application/json')


@app.route("/runSimu")
def run_simu():

    study_filename = request.args.get('file', default='', type=str)
    study_pathname = os.path.join(app_bknd.get_studies_folder(),
                                  study_filename)

    app_bknd.study = STOStudy.from_yaml(study_pathname)
    study_idf_filename = os.path.join(app_bknd.get_studies_folder(),
                                      study_filename.replace(".yaml", ".idf"))
    app_bknd.study.to_idf(study_idf_filename)

    study_mdf_filename = os.path.join(app_bknd.get_studies_folder(),
                                      study_filename.replace(".yaml", ".mdf"))
    study_result_filename = os.path.join(app_bknd.get_studies_folder_name(),
                                         study_filename.replace(".yaml", ".csv"))
    app_bknd.study.to_mdf(study_mdf_filename,
                          result_filename=study_result_filename)

    study_alt_filename = app_bknd.blocks[app_bknd.study.main_block]\
                                 .filename\
                                 .replace(app_bknd.project_folder, "")\
                                 .strip(os.path.sep)

    # Simulator file paths relative to workdir
    study_idf_filename = \
        os.path.join(app_bknd.get_studies_folder_name(),
                     study_filename.replace(".yaml", ".idf"))
    study_mdf_filename = os.path.join(app_bknd.get_studies_folder_name(),
                                      study_filename.replace(".yaml", ".mdf"))

    args = ['ar3simu',
            '-v',
            '-p',
            '-a', app_bknd.ar3bin_folder,
            '-s', app_bknd.study.main_block,
            '-l', study_alt_filename,
            '-i', study_idf_filename,
            '-m', study_mdf_filename,
            #            "-o", csvFilePath,
            "-r"]

    print(" ".join(args))
    with open("stdout.txt", "w") as out:
        currentProcess = subprocess.Popen(args, cwd=app_bknd.project_folder,
                                          stdout=out, stderr=out)

        returnCode = currentProcess.poll()
        while returnCode is None:
            time.sleep(2)
            returnCode = currentProcess.poll()
            continue

        returnCode = currentProcess.poll()

        if returnCode == 0:
            app_bknd.study_res = \
                STOStudyResults.from_result_csv(os.path.join(
                    app_bknd.get_studies_folder(),
                    study_filename.replace(".yaml", ".csv")))

            # out.write(app_bknd.study_res)
            out.write("Simulation completed")

        else:
            # TODO : Deleting results here is maybe a bit hard
            # returnCode != 0 can happen when problems on the simulation process occur
            out.write("Remove current results")
            app_bknd.study_res = None

    return Response(f"{returnCode}", mimetype='application/json')


@app.route("/stopSimu")
def stop_simu():
    if not currentProcess == None:
        currentProcess.kill()
    if os.path.exists("stdout.txt"):
        os.remove("stdout.txt")
    return Response()


@app.route("/getSimuLogs")
def logs():

    output = ""

    if os.path.exists("stdout.txt"):
        with open("stdout.txt", "r") as out:
            output = [line.rstrip() for line in out]

    return Response(json.dumps(output),  mimetype='application/json')


@app.route("/getBlocks")
def get_blocks():

    app_bknd.parse_blocks()
    jsonBlock = []
    for block_name, block in app_bknd.blocks.items():
        jsonBlock.append(block.dict())

    return Response(json.dumps(jsonBlock),  mimetype='application/json')


@app.route("/indicatorsConfig")
def get_indicatorsConfig():
    return Response(json.dumps(app_bknd.simu_config),  mimetype='application/json')


#######################################################
###
# CONFIG FILES API
###
#######################################################


@app.route("/config-files")
def get_config_files():

    configFolder = app_bknd.get_studies_folder()
    # configFiles = [f for f in listdir(
    #     configFolder) if isfile(join(configFolder, f))]
    configFiles = glob.glob(os.path.join(configFolder, "*.yaml"))

    configsMeta = []
    for configFile in configFiles:

        fileMeta = {}
        fileMeta["file_name"] = pathlib.Path(configFile).name

        with open(configFile, 'r', encoding="utf-8") as yaml_file:
            study_specs = yaml.load(yaml_file,
                                    Loader=yaml.FullLoader)

            fileMeta["study_name"] = study_specs['name']

        fileMeta["last_modified"] = \
            datetime.fromtimestamp(
                os.stat(configFile).st_mtime).strftime('%Y-%m-%d-%H:%M')

        fileMeta["has_csv"] = os.path.exists(os.path.join(
            configFolder, fileMeta['file_name'].replace("yaml", "csv")))

        configsMeta.append(fileMeta)

    return Response(json.dumps(configsMeta),  mimetype='application/json')


@app.route("/hasResult")
def hasResult():
    study_filename = request.args.get('file', default='', type=str)

    has_csv = os.path.exists(os.path.join(
        app_bknd.get_studies_folder(), study_filename.replace("yaml", "csv")))
    return Response(json.dumps(has_csv),  mimetype='application/json')


@app.route("/get-config")
def get_config():

    configFolder = app_bknd.get_studies_folder()
    study_filename = request.args.get('file', default='', type=str)
    print(study_filename)

    study_filename = os.path.join(configFolder, study_filename)
    print(study_filename)

    if not(os.path.isfile(study_filename)):
        return Response(status=HTTPStatus.NO_CONTENT)

    with open(study_filename, 'r',
              encoding="utf-8") as yaml_file:
        try:
            study_specs = yaml.load(yaml_file,
                                    Loader=yaml.FullLoader)
            return Response(json.dumps(study_specs),  mimetype='application/json')
        except yaml.YAMLErrorstr as exc:
            logging.error(exc)
            return Response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


@app.route("/delete-config")
def delete_config():

    configFolder = app_bknd.get_studies_folder()
    study_filename = request.args.get('file', default='', type=str)
    os.remove(os.path.join(configFolder, study_filename))
    return Response()


@app.route("/can-save-config")
def can_save_config():
    configFolder = app_bknd.get_studies_folder()
    study_filename = request.args.get('file', default='', type=str)
    canSave = not os.path.isfile(os.path.join(configFolder, study_filename))
    return Response(json.dumps(canSave),  mimetype='application/json')


@app.route("/rename-config")
def rename_config():

    configFolder = app_bknd.get_studies_folder()
    study_filename = request.args.get('file', default='', type=str)
    new_name = request.args.get('new_name', default='', type=str)
    os.rename(os.path.join(configFolder, study_filename),
              os.path.join(configFolder, new_name))
    return Response()


@app.route("/save-config/<config_file>", methods=['POST'])
def saveconfig(config_file):

    configFolder = app_bknd.get_studies_folder()
    study_filename = os.path.join(configFolder, config_file)

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


@app.route("/copy-config")
def copy_config():

    configFolder = app_bknd.get_studies_folder()
    study_filename = request.args.get('file', default='', type=str)
    shutil.copyfile(
        os.path.join(configFolder, study_filename),
        os.path.join(configFolder, study_filename.replace(".yaml", "_copy.yaml")))

    return Response()


@app.route("/downloadIndicatorsData")
def download_indicators_data():
    bio = io.BytesIO()
    app_bknd.study_res.to_excel(bio)
    bio.seek(0)
    response = Response(
        bio, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return response  # returned from a view here


# ipdb.set_trace()
# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=app_config["debug_mode"], host="0.0.0.0", port=5000)
