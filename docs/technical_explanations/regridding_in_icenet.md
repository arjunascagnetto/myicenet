# Regridding in the IceNet Codebase

This document explains how spatial regridding (the process of transforming data from its native grid to a different target grid) is handled within the IceNet project.

## Overview

Regridding is a crucial step in preparing diverse meteorological and oceanographic datasets for use in the IceNet model. The primary goal is to harmonize these datasets onto a common spatial grid, which is typically the **EASE-Grid (Equal-Area Scalable Earth Grid)**.

The IceNet codebase employs a strategy where spatial regridding is primarily handled at two main stages:

1.  **Data Ingestion and Preparation:** When raw data is downloaded or accessed from various sources.
2.  **Forecasting and Prediction:** During specific forecast or prediction tasks.

The core data preprocessing pipeline (which handles normalization, trend calculation, etc.) generally expects the data to have already been regridded.

## Key Stages and Components for Regridding

### 1. Data Ingestion (via `icenet.data.interfaces`)

This is the primary stage where regridding of source data occurs.

*   **Location:** Modules within the `icenet/data/interfaces/` directory (e.g., `cds.py` for Copernicus Climate Data Store, `cmems.py` for Copernicus Marine Environment Monitoring Service, `esgf.py` for Earth System Grid Federation, `mars.py` for ECMWF MARS archive).
*   **Orchestration:** The `icenet/data/interfaces/downloader.py` module likely contains centralized logic or helper functions for regridding operations.
*   **Process:**
    *   When data is fetched from an external source, the corresponding interface module is responsible for its initial processing.
    *   If the data is not on the target EASE-Grid, the interface module uses the `iris` Python library (specifically the `iris.regrid` function) to perform the regridding.
    *   Other libraries like `xarray` and `Cartopy` (for projection information) support this process.
*   **Outcome:** Data from various sources are transformed to the common EASE-Grid before being passed to subsequent preprocessing steps.

### 2. Forecasting and Prediction (via `icenet.process`)

Regridding may also occur during model forecasting and prediction generation.

*   **Location:**
    *   `icenet/process/forecasts.py`
    *   `icenet/process/predict.py`
*   **Process:**
    *   These modules may use `iris.regrid` to ensure that different input fields for a model run are aligned, that model outputs conform to a specific forecast grid, or to compare model data with observations on a common grid.

### 3. Time Resampling (Not Spatial Regridding)

*   **Location:** `icenet/data/process.py` (within the `IceNetPreProcessor` class).
*   **Process:** This class handles resampling of data along the time dimension (e.g., converting hourly data to daily means using methods like `xarray.DataArray.resample(time="1D").mean()`). This is a 1D regridding operation on the time axis and is distinct from spatial regridding.

## Components NOT Performing General Spatial Regridding

*   **Main Data Preprocessors (`icenet.data.process.IceNetPreProcessor` and its subclasses in `icenet.data.processors/`):**
    *   These classes (e.g., `IceNetCMIPPreProcessor`, `IceNetERA5PreProcessor`, `IceNetOSIPreProcessor`) do **not** perform general spatial regridding. They operate under the assumption that the input data they receive has already been spatially regridded to the target EASE-Grid by the `icenet.data.interfaces` layer.
*   **Specific Interpolation Utilities (e.g., `sic_interpolate`):**
    *   **Location:** `icenet/data/processors/utils.py`
    *   **Function:** The `sic_interpolate` function uses `scipy.interpolate.griddata` to fill missing values (NaNs) and polar holes, particularly in Sea Ice Concentration (SIC) data. This is a spatial interpolation for data cleaning/completion, not a general transformation between different grid resolutions or projections.

## Supporting Utilities

*   **Coordinate System Utilities (`icenet/data/utils.py`):** This file may contain utility functions for defining or handling coordinate reference systems, which are essential for accurate regridding.
*   **Plotting Utilities (`icenet/plotting/utils.py`):** This module handles grid projections and transformations specifically for visualization purposes. While related to grids, this does not change the underlying data used in processing.

## Summary of Libraries

*   **`iris`:** The core library used for spatial regridding (via `iris.regrid`).
*   **`xarray`:** Used for data handling and time-based resampling.
*   **`scipy`:** Used for specific interpolation tasks (e.g., `scipy.interpolate.griddata` in `sic_interpolate`).
*   **`Cartopy`:** Used for handling map projections and coordinate reference systems.

This approach ensures that data from diverse sources are consistently processed and aligned, making the subsequent modeling and analysis steps more robust.
