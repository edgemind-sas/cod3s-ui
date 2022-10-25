import argparse
import json
import logging
import os
import sys
import pkg_resources
from flask import Flask, Response, render_template
from flask_cors import CORS

from workspace_api import WorkspaceApi

installed_pkg = {pkg.key for pkg in pkg_resources.working_set}
if 'ipdb' in installed_pkg:
    import ipdb  # noqa: 401

app_config = {}
app_config["app_name_short"] = "cod3s backend"
app_config["app_name_long"] = "COD3S backend"
app_config["author"] = "Developed by EdgeMind (www.edgemind.net) 2022"
app_config["version"] = "0.0.5"
app_config["config_filename"] = os.path.join(os.path.dirname(__file__),
                                             "config.yaml")

# CLI parameters management
# -------------------------
APP_ARG_PARSER = argparse.ArgumentParser(
    description=app_config["app_name_short"] + " " + app_config["version"])

APP_ARG_PARSER.add_argument(
    '-f', '--config-filename',
    dest='config_filename',
    action='store',
    default=app_config["config_filename"],
    help='Configuration filename.')

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


# Logging configuration
if app_config["verbose_mode"]:
    logging.basicConfig(stream=sys.stdout,
                        level=logging.INFO)
if app_config["debug_mode"]:
    logging.basicConfig(stream=sys.stdout,
                        level=logging.DEBUG)


app = Flask(__name__, static_folder="./dist/static",
            template_folder="./dist")
cors = CORS(app)

# load workspace api
workspace_api = WorkspaceApi(app)


@app.route("/")
@app.route("/dashboard/<path:text>")
@app.route("/dashboard")
def index():
    return render_template("index.html")


@app.route("/version")
def getVersion():
    return Response(json.dumps({"version": app_config["version"]}),
                    mimetype='application/json')


@app.route("/getSimuLogs")
def logs():

    output = ""

    if os.path.exists("stdout.txt"):
        with open("stdout.txt", "r") as out:
            output = [line.rstrip() for line in out]

    return Response(json.dumps(output),  mimetype='application/json')


# ipdb.set_trace()
# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=app_config["debug_mode"], host="0.0.0.0", port=5000)
