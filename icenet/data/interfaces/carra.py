import logging
import os
import pandas as pd
import xarray as xr
import cdsapi as cds

from icenet.data.cli import download_args
from icenet.data.interfaces.downloader import ClimateDownloader

class CARRADownloader(ClimateDownloader):
    """Downloader for Copernicus CARRA reanalysis data."""

    CDI_MAP = {
        'tas': '2m_temperature',
        'psl': 'surface_pressure',
        'uas': '10m_u_component_of_wind',
        'vas': '10m_v_component_of_wind',
        'rlds': 'surface_thermal_radiation_downwards',
        'rsds': 'surface_solar_radiation_downwards',
        'tos': 'sea_surface_temperature',
    }

    def __init__(self, *args, identifier: str = "carra", cdi_map: object = CDI_MAP,
                 show_progress: bool = False, **kwargs):
        super().__init__(*args,
                         drop_vars=["lambert_azimuthal_equal_area"],
                         identifier=identifier,
                         **kwargs)
        self.client = cds.Client(progress=show_progress)
        self._cdi_map = cdi_map
        self.download_method = self._single_api_download

    def _single_api_download(self, var: str, level: object, req_dates: object,
                             download_path: object):
        logging.debug("Processing {} dates".format(len(req_dates)))
        var_prefix = var[0:-(len(str(level)))] if level else var
        retrieve_dict = {
            "product_type": "reanalysis",
            "variable": self._cdi_map[var_prefix],
            "year": req_dates[0].year,
            "month": list(set(["{:02d}".format(rd.month) for rd in sorted(req_dates)])),
            "day": ["{:02d}".format(d) for d in range(1, 32)],
            "time": ["{:02d}:00".format(h) for h in range(0, 24)],
            "format": "netcdf",
            "area": self.hemisphere_loc,
        }
        dataset = "reanalysis-carra-single-levels"
        if level:
            dataset = "reanalysis-carra-pressure-levels"
            retrieve_dict["pressure_level"] = level
        try:
            logging.info("Downloading data for {}...".format(var))
            self.client.retrieve(dataset, retrieve_dict, download_path)
            logging.info("Download completed: {}".format(download_path))
        except Exception as e:
            logging.exception("{} not deleted, look at the problem".format(download_path))
            raise RuntimeError(e)

    def postprocess(self, var: str, download_path: object):
        logging.info("Postprocessing CARRA data at {}".format(download_path))
        temp_path = "{}.bak{}".format(*os.path.splitext(download_path))
        logging.debug("Moving to {}".format(temp_path))
        os.rename(download_path, temp_path)
        ds = xr.open_dataset(temp_path)
        omit_vars = set(["number", "expver"])
        data_vars = set(ds.data_vars)
        var_list = list(data_vars.difference(omit_vars))
        nom = var_list[0]
        da = getattr(ds.rename({"valid_time": "time", nom: var}), var)
        if "pressure_level" in da.dims:
            da = da.squeeze(dim="pressure_level").drop_vars("pressure_level")
        if "number" in da.coords:
            da = da.drop_vars("number")
        da = da.sortby("time").resample(time='1D').mean()
        da.to_netcdf(download_path)

    def additional_regrid_processing(self, datafile: str, cube_ease: object):
        pass


def main():
    args = download_args(choices=["cdsapi"],
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
    carra = CARRADownloader(
        var_names=args.vars,
        dates=[pd.to_datetime(date).date() for date in pd.date_range(args.start_date, args.end_date, freq="D")],
        delete_tempfiles=args.delete,
        download=args.download,
        levels=args.levels,
        max_threads=args.workers,
        postprocess=args.postprocess,
        north=args.hemisphere == "north",
        south=args.hemisphere == "south",
        ease_resolution=12.5,
    )
    carra.download()
    carra.regrid()

if __name__ == "__main__":
    main()
