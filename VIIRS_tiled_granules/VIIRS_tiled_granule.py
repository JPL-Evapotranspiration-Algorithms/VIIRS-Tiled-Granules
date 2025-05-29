from typing import Union, List
import logging
from datetime import datetime
from glob import glob
from os import makedirs
from os.path import exists, join, abspath, expanduser, basename, splitext
import json
import h5py
import numpy as np
import pandas as pd
from dateutil import parser
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import Point, Polygon
from skimage.transform import resize

import colored_logging
import rasters
import rasters as rt
from modland import parsehv, generate_modland_grid

from rasters import Raster, RasterGrid, RasterGeometry

from .granule_ID import *

# Define colormaps for NDVI and Albedo
NDVI_COLORMAP = LinearSegmentedColormap.from_list(
    name="NDVI",
    colors=[
        "#0000ff",
        "#000000",
        "#745d1a",
        "#e1dea2",
        "#45ff01",
        "#325e32"
    ]
)

ALBEDO_COLORMAP = "gray"

DEFAULT_WORKING_DIRECTORY = "."

logger = logging.getLogger(__name__)

class VIIRSTiledGranule:
    """
    Class representing a VIIRS Granule.
    """

    def __init__(self, filename: str):
        """
        Initialize the VIIRSGranule object.

        :param filename: Path to the VIIRS granule file.
        """
        self._filename = filename
        self._cloud_mask = None

    def __repr__(self):
        """
        Return a string representation of the VIIRSGranule object.
        """
        display_dict = {
            "filename": self.filename
        }
        display_string = json.dumps(display_dict, indent=2)
        return display_string

    @property
    def filename(self) -> str:
        """
        Return the filename of the granule.
        """
        return self._filename
    
    @property
    def filename_absolute(self) -> str:
        """
        Return the absolute path of the filename.
        """
        return abspath(expanduser(self.filename))

    @property
    def filename_base(self) -> str:
        """
        Return the base name of the filename.
        """
        return basename(self.filename)

    @property
    def filename_stem(self) -> str:
        """
        Return the stem of the filename.
        """
        return splitext(self.filename_base)[0]

    @property
    def tile(self) -> str:
        """
        Return the tile information from the filename.
        """
        return parse_VIIRS_tile(self.filename)

    @property
    def hv(self) -> tuple:
        """
        Return the horizontal and vertical tile indices.
        """
        return parsehv(self.tile)

    @property
    def h(self) -> int:
        """
        Return the horizontal tile index.
        """
        return self.hv[0]

    @property
    def v(self) -> int:
        """
        Return the vertical tile index.
        """
        return self.hv[1]

    @property
    def date_UTC(self) -> datetime:
        """
        Return the date in UTC from the filename.
        """
        return datetime.strptime(self.filename_base.split(".")[1][1:], "%Y%j")

    @property
    def grids(self) -> List[str]:
        """
        Return the list of grids in the HDF5 file.
        """
        with h5py.File(self.filename_absolute, "r") as file:
            return list(file["HDFEOS/GRIDS/"].keys())

    def variables(self, grid: str) -> List[str]:
        """
        Return the list of variables in a specific grid.

        :param grid: The grid name.
        """
        with h5py.File(self.filename_absolute, "r") as file:
            return list(file[f"HDFEOS/GRIDS/{grid}/Data Fields/"].keys())
    
    def variable(self, variable: str) -> Raster:
        if hasattr(self, variable):
            return getattr(self, variable)
        else:
            raise AttributeError(f"Variable '{variable}' not found in VIIRSTiledGranule.")
