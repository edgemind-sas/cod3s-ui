# -*- coding: utf-8 -*-
import pkg_resources
from pyar3 import STOStudy, STOStudyResults
import typing
import glob
import pandas as pd
import pydantic
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
import os
from pathlib import Path

installed_pkg = {pkg.key for pkg in pkg_resources.working_set}
if 'ipdb' in installed_pkg:
    import ipdb  # noqa: 401

PandasDataFrame = typing.TypeVar('pd.core.dataframe')
PandasSeries = typing.TypeVar('pd.core.series')

pio.templates.default = "plotly_white"


class AR3Observer(pydantic.BaseModel):
    name: str = pydantic.Field(
        None, description="Observer name")
    type: str = pydantic.Field(
        None, description="Observer type")


class AR3Block(pydantic.BaseModel):

    name: str = pydantic.Field(
        None, description="Block name")
    observers: typing.List[AR3Observer] = pydantic.Field(
        [], description="Models block")
    filename: str = pydantic.Field(
        None, description="Block filename")


class AR3App(pydantic.BaseModel):

    blocks: typing.Dict[str, AR3Block] = pydantic.Field(
        {}, description="Project blocks")

    study: STOStudy = pydantic.Field(
        None, description="Stochastic simulation study")

    study_res: STOStudyResults = pydantic.Field(
        None, description="Stochastic simulator results")

    ar3bin_folder: str = pydantic.Field(
        ".", description="AR3 binary folder")

    simu_config: dict = pydantic.Field(
        {}, description="Simulator config")

    project_folder: str = pydantic.Field(
        ".", description="Project folder")

    simu_process_id: typing.Any = pydantic.Field(
        None, description="Simulation process")

    layout: dict = pydantic.Field(
        {}, description="Application layout config")

    def get_studies_folder_name(self):
        return "studies"

    def get_studies_folder(self):

        studies_folder = os.path.join(self.project_folder,
                                      self.get_studies_folder_name())

        Path(studies_folder).mkdir(parents=True, exist_ok=True)

        return studies_folder

    def parse_blocks(self, path=None, filter_no_observers=True):

        if path is None:
            path = self.project_folder

        self.blocks = {}

        for root, dirs, files in os.walk(path):
            for file in files:
                if not(file.startswith(".")) and file.endswith(".alt"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding='latin-1') as altfile:
                        currentAR3Blocks = []  # store currents AR3Block, can be imbricated
                        insideComment = False
                        for line in altfile:
                            line = line.strip()
                            if(line.startswith("/*")):
                                insideComment = True
                                continue
                            if(line.endswith("*/")):
                                insideComment = False
                                continue
                            if(insideComment or line.startswith("//")):
                                continue
                            if line.startswith("block"):
                                block = AR3Block()
                                block.filename = path
                                block.name = line.split(
                                    " ")[1].replace("\n", "")
                                currentAR3Blocks.append(block)
                            elif line.startswith("end"):
                                if currentAR3Blocks:  # check list is not empty
                                    block = currentAR3Blocks.pop()
                                    if not filter_no_observers or (filter_no_observers and block.observers):
                                        self.blocks[block.name] = block
                            elif line.startswith("observer"):
                                if currentAR3Blocks:  # check we can associate observer to a block
                                    obs = AR3Observer()
                                    lineTokens = line.split(" ")
                                    obs.type = lineTokens[1]
                                    obs.name = lineTokens[2]
                                    currentAR3Blocks[-1].observers.append(obs)

    def create_indic_fig(self, indic_id, fig=None, line_color="#4C78A8", fig_layout="auto"):

        indic_df = self.study_res.indicators[indic_id].data

        indic_name = indic_id
        indic_description = indic_id
        if self.study:
            indic = self.study.get_indicator_from_id(indic_id)
            indic_name = indic.name
            indic_description = indic.description

        if fig is None:
            fig = go.Figure()

        fig.add_scatter(
            x=indic_df["date"].to_list(),
            y=indic_df["mean"].to_list(),
            mode='lines+markers',
            name="mean",
            legendgroup=indic_name,
            legendgrouptitle_text=indic_name,
            # showlegend=True,
            line_width=1,
            line_color=line_color
        )

        print(indic)
        if "confidence-range" in indic_df.columns:

            ci_min = indic_df["mean"] - indic_df["confidence-range"]
            ci_max = indic_df["mean"] + indic_df["confidence-range"]

            fig.add_scatter(
                x=indic_df["date"].to_list(),
                y=ci_min.to_list(),
                mode='lines',
                name="mean",
                legendgroup=indic.name,
                # legendgrouptitle_text=indic.name,
                showlegend=False,
                line_width=0,
                line_color=line_color
            )

            fig.add_scatter(
                x=indic_df["date"].to_list(),
                y=ci_max.to_list(),
                mode='lines',
                name="mean",
                legendgroup=indic.name,
                # legendgrouptitle_text=indic.name,
                showlegend=False,
                line_width=0,
                fill='tonexty',
                line_color=line_color
            )

        if fig_layout == "auto":
            fig_layout = self.layout.get("indic_fig", {})\
                                    .get("layout", {})

            xaxis_title = f"{self.study.simu_params.schedule_name}"
            if not(self.study.simu_params.schedule_unit is None):
                xaxis_title += f" ({self.study.simu_params.schedule_unit})"

            fig.update_layout(title=indic_description,
                              xaxis_title=xaxis_title)

            fig.update_layout(**fig_layout)

        return fig

    def create_multi_indic_fig(self, indic_ids=[], fig=None):

        color_map = self.layout.get("color_map",
                                    px.colors.qualitative.T10)

        if fig is None:
            fig = go.Figure()

        fig_layout = self.layout.get("indic_fig", {})\
                                .get("layout", {})

        for i, indic_id in enumerate(indic_ids):

            if not(indic_id in self.study_res.indicators):
                continue

            line_color = color_map[i % len(color_map)]

            fig = self.create_indic_fig(indic_id=indic_id,
                                        line_color=line_color,
                                        fig=fig)

        xaxis_title = f"{self.study.simu_params.schedule_name}"
        if not(self.study.simu_params.schedule_unit is None):
            xaxis_title += f" ({self.study.simu_params.schedule_unit})"

        fig.update_layout(xaxis_title=xaxis_title)

        fig.update_layout(**fig_layout)
        return fig

    # def create_criticity_dist_fig(self):

    #     colors = self.layout.get("criticity_colors")
    #     criticity_labels = self.criticity_dist.index.to_list()
    #     criticity_counts = self.criticity_dist.to_list()
    #     marker_color = [colors.get(lab, "RoyalBlue")
    #                     for lab in criticity_labels]

    #     fig = make_subplots(specs=[[{"secondary_y": True}]])

    #     fig.add_bar(
    #         x=criticity_labels,
    #         y=criticity_counts,
    #         marker_color=marker_color,
    #         showlegend=False
    #     )

    #     color_cumul = self.layout.get("color_theme", {}).get("blue", "blue")
    #     count_sum = self.criticity_dist.sum()
    #     fig.add_scatter(
    #         x=criticity_labels,
    #         y=(self.criticity_dist.cumsum()/count_sum).to_list(),
    #         marker_color=color_cumul,
    #         secondary_y=True,
    #         name="% cumulated"
    #     )

    #     fig.update_yaxes(title_text="Counts",
    #                      secondary_y=False)
    #     fig.update_yaxes(title_text="Cumulated counts",
    #                      tickformat=',.0%',
    #                      range=[0, 1.1],
    #                      secondary_y=True)

    #     fig_layout = self.layout.get("criticity_fig", {})\
    #                             .get("layout", {})

    #     fig.update_layout(**fig_layout)

    #     # fig.update_layout(legend=dict(
    #     #     orientation="h",
    #     #     yanchor="bottom",
    #     #     y=1.02,
    #     #     xanchor="right",
    #     #     x=1
    #     # ))

    #     return fig
