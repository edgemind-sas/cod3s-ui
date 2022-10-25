import pydantic
from workspace import Workspace


class AR3Workspace(Workspace):

    ar3_install_folder: str = pydantic.Field(
        ".", description="ar3 install folder")
