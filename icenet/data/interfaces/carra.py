import logging
import os
import requests
import cdsapi as cds
import pandas as pd
import xarray as xr

from .cds import ERA5Downloader # Assuming cds.py is in the same directory

# TODO: This function might need to be adapted from get_era5_available_date_range
# or a more generic function created if CARRA has a different API structure for metadata.
# For now, let's assume it's similar enough or we'll use a placeholder.
def get_carra_available_date_range(dataset_name: str):
    # TODO: Verify CARRA dataset name on CDS
    # This is a placeholder implementation.
    # Actual implementation would query CDS API for dataset_name
    logging.warning(f"Placeholder: get_carra_available_date_range for {dataset_name} returning fixed range.")
    logging.warning("TODO: Implement actual CDS API query for date range.")
    return pd.to_datetime("1990-01-01"), pd.to_datetime("2023-12-31")


class CARRADownloader(ERA5Downloader):
    """
    Downloader for CARRA (Copernicus Arctic Regional Reanalysis) data using the CDS API.
    """
    # TODO: Refine CDI_MAP if CARRA variable names differ from ERA5
    # For now, using the ERA5 mapping.
    CDI_MAP = ERA5Downloader.CDI_MAP

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.identifier = "carra"
        self._cdi_map = CARRADownloader.CDI_MAP # Use the class attribute

        # CDS API client setup - similar to ERA5Downloader
        # self._client is initialized in the parent ERA5Downloader
        
        # The download_method and max_threads logic from ERA5Downloader constructor
        # are likely still relevant. If CARRA API has different characteristics,
        # this might need adjustment. For now, assume they are similar.
        # self.download_method = kwargs.get("download_method", "cdsapi")
        # if self.download_method == "requests":
        #     adapter = requests.adapters.HTTPAdapter(
        #         pool_connections=kwargs.get("max_threads", self.num_workers),
        #         pool_maxsize=kwargs.get("max_threads", self.num_workers)
        #     )
        #     self._session.mount("https://cds.climate.copernicus.eu", adapter)
        # The above is handled by the parent class or needs careful review if different.
        # For now, relying on parent __init__ for client and session setup.
        logging.info(f"Initialized CARRADownloader with identifier: {self.identifier}")

    def _single_api_download(
        self,
        req_dates: object,
        var_prefix: str,
        level: str or None,
        download_path: str,
    ):
        """
        Performs a single API download request for CARRA data.

        Args:
            req_dates (pd.DatetimeIndex): Dates for the request.
            var_prefix (str): Variable prefix (e.g., "tas" for temperature).
            level (str, optional): Pressure level or None for single-level.
            download_path (str): Path to save the downloaded file.
        """
        # TODO: Verify CARRA dataset name on CDS
        # Using "reanalysis-carra-single-levels" and "reanalysis-carra-pressure-levels" as placeholders.
        if level is None:
            dataset_name = "reanalysis-carra-single-levels"
        else:
            dataset_name = "reanalysis-carra-pressure-levels"
            logging.warning(f"Pressure level data for CARRA ({dataset_name}) is assumed. Verify dataset name.")
        
        logging.info(f"Preparing download for {var_prefix} from {dataset_name}")
        logging.info(f"Dates: {req_dates.min().strftime('%Y-%m-%d')} to {req_dates.max().strftime('%Y-%m-%d')}")
        if level:
            logging.info(f"Level: {level}")

        # Construct the retrieve_dict, similar to ERA5Downloader
        # Specifics might need adjustment for CARRA.
        retrieve_dict = {
            "product_type": "reanalysis", # This might be different for CARRA, e.g., "analysis" or "forecast"
            "format": "grib", # Or netcdf if preferred and available
            "variable": self.get_vars_for_api(var_prefix),
            "year": sorted(list(set(req_dates.year))),
            "month": sorted(list(set(req_dates.month))),
            "day": sorted(list(set(req_dates.day))),
            "time": sorted(list(set(t.strftime("%H:%M") for t in req_dates.time))),
            # TODO: Verify area parameter for CARRA.
            # ERA5 uses 'area': self.hemisphere_loc, which defines a bounding box.
            # CARRA is Arctic-specific, so this might be implicitly handled by the dataset
            # or require different coordinates. For now, assume self.hemisphere_loc is usable.
            "area": self.hemisphere_loc, 
        }

        if level:
            retrieve_dict["pressure_level"] = level.split("hPa")[0]

        logging.debug(f"CDS API request dictionary: {retrieve_dict}")

        try:
            if self.download_method == "cdsapi":
                logging.debug(f"Using cdsapi client to retrieve and download to {download_path}")
                self._client.retrieve(dataset_name, retrieve_dict, download_path)
            elif self.download_method == "requests":
                # This part assumes get_datastore_request_url and _datastore_request methods
                # are implemented and suitable for CARRA, or that the parent's are used.
                # This logic is more complex and might need to be inherited or adapted from ERA5Downloader.
                # For now, focusing on the cdsapi path.
                raise NotImplementedError("Requests download method not fully implemented for CARRA yet.")
            else:
                raise ValueError(f"Unknown download_method: {self.download_method}")

            logging.info(f"Successfully downloaded {var_prefix} to {download_path}")

        except Exception as e:
            logging.error(f"CDS API download failed for {var_prefix} to {download_path}: {e}")
            # Consider if specific error handling (e.g., for NoDataPresentsError) is needed
            # similar to ERA5Downloader.
            if os.path.exists(download_path):
                logging.debug(f"Removing incomplete file: {download_path}")
                os.remove(download_path)
            # Re-raise or handle as appropriate
            raise

        return download_path

    # Potentially, other methods from ERA5Downloader might need overrides or adjustments
    # For example:
    # - get_vars_for_api (if variable naming conventions differ significantly)
    # - collection_name (if CARRA uses a different GRIB collection name)
    # - preprocess_file (if CARRA GRIB files have different structure)

    # For now, we assume these can be inherited or will be addressed in future tasks.

def main():
    """
    Main entry point for downloading CARRA data via the CLI.
    """
    # TODO: The choices for download_args might need to be reviewed.
    # If CARRA has specific choices or if "cdsapi" is the implied choice,
    # this might be [] or ["cdsapi"] or similar.
    # For now, mirroring ERA5's use of "cdsapi" choice.
    # The extra_args are similar to what ERA5 uses for --do-not-download etc.
    args = download_args(choices=["cdsapi"], # Or specific "carra" choice if needed
                         workers=True,
                         extra_args=((("-n", "--do-not-download"),
                                      dict(dest="download",
                                           action="store_false",
                                           default=True)),
                                     (("-p", "--do-not-postprocess"),
                                      dict(dest="postprocess",
                                           action="store_false",
                                           default=True))))

    logging.info("CARRA Data Downloading")
    
    # Convert date strings from args to datetime.date objects
    start_date = args.start_date
    end_date = args.end_date
    
    if start_date is None or end_date is None:
        # TODO: Potentially fetch available date range if not provided,
        # or rely on downloader's internal handling if dates are optional.
        # For now, assume dates are required as per typical ERA5 usage.
        logging.error("Start and end dates are required for CARRA download.")
        return

    dates_pd = pd.date_range(start_date, end_date, freq="D")
    # Convert pandas Timestamps to datetime.date, as ERA5Downloader expects
    req_dates = [d.date() for d in dates_pd]

    downloader = CARRADownloader(
        var_names=args.vars,
        dates=req_dates,
        delete_tempfiles=args.delete,
        # download=args.download, # This seems to be handled by CARRADownloader._download
        levels=args.levels,
        max_threads=args.workers,
        # postprocess=args.postprocess, # This seems to be handled by CARRADownloader._postprocess
        north=args.hemisphere == "north",
        south=args.hemisphere == "south",
        # Pass other relevant args from download_args if needed
        # e.g. show_progress if that's an option in CARRADownloader or its parent
    )
    
    # Set the download and postprocess flags based on args
    # These flags are part of ClimateDownloader, parent of ERA5Downloader
    downloader._download = args.download
    downloader._postprocess = args.postprocess

    downloader.download()
    # TODO: Confirm if regrid is always needed or should be conditional
    downloader.regrid()
    logging.info("CARRA Data Download and Regrid Complete.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    # This makes the script executable for testing, assuming download_args can be parsed
    # from command line arguments when this script is run directly.
    # Note: For entry point, setup.py calls main() directly.
    main()

# Need to ensure download_args is imported
from icenet.data.cli import download_args
