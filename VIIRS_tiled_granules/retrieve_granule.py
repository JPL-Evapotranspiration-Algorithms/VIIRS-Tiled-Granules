import os
from os.path import join, abspath, expanduser
from pathlib import Path
import earthaccess
from modland import generate_modland_grid
from .VIIRS_tiled_granules import VIIRSTiledGranule
from .granule_ID import *

def anonymize_home_path(file_path) -> str:
    """
    Anonymize the home directory in a file path by replacing it with '~'.
    
    Args:
        file_path: File path as string or Path object
        
    Returns:
        str: Anonymized path as string
    """
    # Convert to string if it's a Path object
    if isinstance(file_path, Path):
        file_path_str = str(file_path)
    else:
        file_path_str = file_path
    
    home_dir = os.path.expanduser("~")
    
    if file_path_str.startswith(home_dir):
        return file_path_str.replace(home_dir, "~", 1)
    
    return file_path_str

def retrieve_granule(
        remote_granule: earthaccess.results.DataGranule, 
        download_directory: str = ".",
        parent_directory: str = None) -> VIIRSTiledGranule:
    """
    Retrieve and download a VIIRS granule from a remote source.

    Args:
        remote_granule (earthaccess.results.DataGranule): The remote granule to be downloaded.
        download_directory (str): The directory where the granule will be downloaded.

    Returns:
        VIIRSTiledGranule: The downloaded and processed VIIRS tiled granule.
    """
    # Extract the granule ID from the remote granule metadata
    granule_ID = remote_granule["meta"]["native-id"]
    
    # Parse the product name, build number, and date from the granule ID
    product_name = parse_VIIRS_product(granule_ID)
    build_number = parse_VIIRS_build(granule_ID)
    date_UTC = parse_VIIRS_date(granule_ID)
    
    if parent_directory is None:
        # Construct the parent directory path for the download
        parent_directory = join(
            download_directory, 
            f"{product_name}.{build_number:03d}", 
            date_UTC.strftime("%Y-%m-%d")
        )
    
    # Download the granule to the specified directory and get the filename
    filename = earthaccess.download(remote_granule, local_path=abspath(expanduser(parent_directory)))[0]
    
    # Anonymize the home path in the filename
    filename = anonymize_home_path(filename)
    
    # Create a VIIRSTiledGranule object from the downloaded file
    granule = VIIRSTiledGranule(filename)
    
    return granule
