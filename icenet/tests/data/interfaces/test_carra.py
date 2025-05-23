import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from icenet.data.interfaces.carra import CARRADownloader, get_carra_available_date_range
from icenet.data.interfaces.cds import ERA5Downloader # For CDI_MAP initially


class TestCARRADownloader(unittest.TestCase):

    @patch('icenet.data.interfaces.cds.ERA5Downloader.__init__')
    def setUp(self, mock_era5_init):
        """
        Set up the test environment for CARRADownloader tests.
        Mocks the ERA5Downloader.__init__ to simplify setup, as CARRADownloader
        inherits from it and might call complex parent initialization logic.
        """
        mock_era5_init.return_value = None # Ensure the mock __init__ doesn't return a MagicMock

        # Provide minimal, valid arguments for CARRADownloader instantiation
        # Many of these are passed to ClimateDownloader (parent of ERA5Downloader)
        self.downloader = CARRADownloader(
            identifier="carra_test_id", # This will be overridden by CARRADownloader's __init__
            hemisphere="north", # This is used by DataProducer, parent of ClimateDownloader
            path="testdata/interfaces/carra", # Used by DataProducer
            var_names=["tas"], # Used by ClimateDownloader
            levels=[None], # Used by ClimateDownloader, must match var_names length
            dates=[pd.to_datetime("2023-01-01")], # Used by ClimateDownloader
            delete_tempfiles=False, # Used by ClimateDownloader
            max_threads=1, # Used by ClimateDownloader
            # The following are args for DataProducer, parent of ClimateDownloader
            north=True,
            south=False,
            # The following are args specific to ERA5Downloader, which CARRADownloader calls super on
            # We mock ERA5Downloader.__init__, so these specific args to it are less critical here
            # but good to be aware of.
            # cdi_map=ERA5Downloader.CDI_MAP, # This is set by CARRADownloader itself
            show_progress=False
        )
        # Overwrite client that would have been set by ERA5Downloader.__init__
        self.downloader.client = MagicMock(spec=ERA5Downloader.client)
        # Ensure _cdi_map is set as CARRADownloader.__init__ would do
        self.downloader._cdi_map = CARRADownloader.CDI_MAP


    def test_initialization(self):
        """Test that CARRADownloader initializes with correct attributes."""
        self.assertEqual(self.downloader.identifier, "carra")
        self.assertEqual(self.downloader._cdi_map, ERA5Downloader.CDI_MAP)
        # Check if the client was at least set (even if by mock in setUp)
        self.assertIsNotNone(self.downloader.client)

    @patch('cdsapi.Client') # Mock cdsapi.Client where CARRADownloader tries to use it
    def test_single_api_download_placeholder_names(self, mock_cds_client_constructor):
        """
        Test _single_api_download constructs CDS API requests with placeholder dataset names.
        """
        # Instance of the mocked client
        mock_client_instance = mock_cds_client_constructor.return_value
        # self.downloader.client is already a MagicMock from setUp.
        # We need to ensure the _single_api_download method uses the one from cdsapi.Client
        # The CARRADownloader's __init__ (which calls super().__init__ for ERA5Downloader)
        # is what sets self.client = cds.Client(). Since we mocked ERA5Downloader.__init__,
        # we need to assign the new mock here if the method directly uses self.client
        # that was supposed to be initialized by the parent.
        # However, CARRADownloader uses self._client.retrieve, and _client is set in ERA5Downloader
        # So, let's ensure self.downloader._client is the instance we want to check.
        
        # Re-assign self.downloader._client to the instance from this patch
        # This assumes _single_api_download uses self._client
        # CARRADownloader actually uses self.client (from ERA5Downloader)
        # and ERA5Downloader uses self.client.retrieve
        
        # Let's assume self.downloader.client is used. It was set to a MagicMock in setUp.
        # We will use that existing mock.
        mock_retrieve = self.downloader.client.retrieve
        
        test_dates = pd.to_datetime(["2023-01-01", "2023-01-02"])
        dummy_download_path = "/tmp/dummy_download.grib"

        # Test for single-level (level is None)
        self.downloader._single_api_download(
            req_dates=test_dates,
            var_prefix="tas", # 2m_temperature
            level=None,
            download_path=dummy_download_path
        )
        mock_retrieve.assert_called()
        args_single, kwargs_single = mock_retrieve.call_args
        self.assertEqual(args_single[0], "reanalysis-carra-single-levels")
        self.assertEqual(args_single[1]['product_type'], "reanalysis")
        self.assertEqual(args_single[1]['variable'], "2m_temperature") # from CDI_MAP

        # Reset mock for the next call
        mock_retrieve.reset_mock()

        # Test for pressure-level
        self.downloader._single_api_download(
            req_dates=test_dates,
            var_prefix="ta", # temperature at a level
            level="500hPa",
            download_path=dummy_download_path
        )
        mock_retrieve.assert_called()
        args_plevel, kwargs_plevel = mock_retrieve.call_args
        self.assertEqual(args_plevel[0], "reanalysis-carra-pressure-levels")
        self.assertEqual(args_plevel[1]['product_type'], "reanalysis")
        self.assertEqual(args_plevel[1]['variable'], "temperature") # from CDI_MAP
        self.assertEqual(args_plevel[1]['pressure_level'], "500")


    def test_get_carra_available_date_range_placeholder(self):
        """Test the placeholder get_carra_available_date_range function."""
        start_date, end_date = get_carra_available_date_range("test_dataset_name")
        self.assertEqual(start_date, pd.to_datetime("1990-01-01"))
        self.assertEqual(end_date, pd.to_datetime("2023-12-31"))

if __name__ == '__main__':
    unittest.main()
