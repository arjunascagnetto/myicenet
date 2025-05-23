import logging

from icenet.data.cli import process_args, process_date_args
from icenet.data.process import IceNetPreProcessor
# TODO: If CARRA data has specific file naming conventions after processing
# that need filtering, this might be needed. For now, assuming generic or no filter.
# from icenet.data.processor import Processor

class IceNetCARRAPreProcessor(IceNetPreProcessor):
    """
    IceNet pre-processor for CARRA data.
    """

    def __init__(self, *args, **kwargs):
        # Set the identifier for CARRA.
        # file_filters can be added here if specific naming patterns
        # for processed CARRA files are known. For now, it's omitted,
        # meaning it will default to the parent class's behavior or an empty list.
        super().__init__(*args, identifier="carra", **kwargs)
        logging.info("Initialised IceNetCARRAPreProcessor")

# Optional: main function for command-line execution
def main():
    """
    Main entry point for running the CARRA pre-processor.
    """
    args = process_args()
    dates = process_date_args(args)

    # TODO: Confirm if variable_config needs to be passed or is handled by generic CLI args
    # Example from ERA5:
    # from icenet.data.datasets.era5 import manifest as era5_manifest
    # manifest = era5_manifest
    # For CARRA, a similar manifest might be needed if specific variable configurations
    # are not passed via CLI or are standard for CARRA.

    logging.info("Starting CARRA pre-processing.")
    
    # Assuming standard configuration for now.
    # If CARRA has a specific manifest for variables, it should be loaded here.
    carra_preproc = IceNetCARRAPreProcessor(
        args.abs,
        args.anom,
        args.name,
        args.source_data, # This should point to the raw CARRA data
        args.target_data, # This is where processed data will be saved
        dates_override=dates,
        dry=args.dry,
        # variable_config=manifest, # Uncomment and adapt if a CARRA manifest is used
        # file_filters=[], # Explicitly empty or define if needed
    )
    
    # TODO: The actual processing logic is in the parent class's methods like
    # generate_files, process_month_files, etc.
    # This main function just sets up the class and could call a primary processing method if needed.
    # For now, we might just rely on the parent's methods being called elsewhere
    # or add a specific call here, e.g., carra_preproc.process_all_dates() if such a method exists.
    
    # Example: If there's a method to start the full processing pipeline
    # carra_preproc.run_processing() # This is hypothetical
    
    logging.info("IceNetCARRAPreProcessor setup complete. Further processing calls depend on IceNetPreProcessor implementation.")


if __name__ == "__main__":
    # Setup basic logging for CLI usage
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()
