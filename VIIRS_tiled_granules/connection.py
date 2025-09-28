from typing import Union, List
from datetime import date, datetime

import earthaccess

import rasters as rt
from rasters import SpatialGeometry, RasterGeometry, Raster

from modland import generate_modland_grid

from .constants import *
from .search_granules import search_granules
from .retrieve_granule import retrieve_granule
from .VIIRS_tiled_granule import VIIRSTiledGranule

class VIIRSTiledProductConnection:
    GranuleClass = VIIRSTiledGranule

    def __init__(
            self,
            concept_ID: str,
            download_directory: str = DOWNLOAD_DIRECTORY):
        self.concept_ID = concept_ID
        self.download_directory = download_directory
    
    def search(
            self,
            date_UTC: Union[date, datetime, str] = None,
            start_date_UTC: Union[date, datetime, str] = None,
            end_date_UTC: Union[date, datetime, str] = None,
            geometry: SpatialGeometry = None,
            tile: str = None,
            tile_size = None) -> List[earthaccess.search.DataGranule]:
        return search_granules(
            concept_ID=self.concept_ID,
            date_UTC=date_UTC,
            start_date_UTC=start_date_UTC,
            end_date_UTC=end_date_UTC,
            geometry=geometry,
            tile=tile,
            tile_size=tile_size
        )
    
    def granule(
            self,
            date_UTC: Union[date, str] = None,
            tile: str = None,
            download_directory: str = DOWNLOAD_DIRECTORY) -> GranuleClass:
        return retrieve_granule(
            date_UTC=date_UTC,
            tile=tile,
            download_directory=download_directory
        )
    
    def variable(
            self,
            variable: str,
            date_UTC: Union[date, str],
            geometry: RasterGeometry = None,
            tile: str = None,
            tile_size: int = None,
            filename: str = None,
            resampling: str = None) -> Raster:
        if geometry is None and tile_size is None:
            raise ValueError("neither geometry nor tile size given")

        if geometry is None:
            geometry = generate_modland_grid(tile=tile, tile_size=tile_size)

        remote_granules = self.search(
            date_UTC=date_UTC,
            geometry=geometry,
            tile=tile,
            tile_size=tile_size
        )

        granules = [
            retrieve_granule(remote_granule)
            for remote_granule 
            in remote_granules
        ]

        images = [
            granule.variable(variable)
            for granule 
            in granules
        ]

        mosaic = rt.mosaic(
            images=images,
            geometry=geometry,
            resampling=resampling
        )

        return mosaic
    