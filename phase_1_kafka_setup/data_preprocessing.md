# Data Preprocessing Strategy Documentation

## Overview
This document outlines the data preprocessing strategy for Phase 1 of the "Real-Time Air Quality Prediction with Kafka" project. The goal of Phase 1 is to establish a Kafka pipeline to stream raw air quality data from `AirQualityUCI.csv` in real-time, with minimal preprocessing to prioritize pipeline setup. Preprocessing is kept simple, focusing on loading and ordering the data for streaming, while deferring more complex transformations to later phases.

## Data Source
- **Dataset**: `AirQualityUCI.csv`, sourced from the UCI Machine Learning Repository.
- **Format**: CSV file with semicolon (`;`) separators and comma (`,`) decimals.
- **Columns Used**: `Date` (e.g., "10/03/2004"), `Time` (e.g., "18.00.00"), and `CO(GT)` (Carbon Monoxide Ground Truth values, e.g., 2.6 or -200 for missing).

## Preprocessing Steps

### Step 1: Loading Data
- The dataset was loaded from the `data/` subdirectory relative to the project root (`/Users/shrenyamathur/Documents/kafka`).
- Due to the non-standard CSV format (semicolon-separated with comma decimals), specific parameters were applied to ensure accurate parsing. This step ensured the raw data was read correctly into a structured format for streaming.

### Step 2: Chronological Sorting
- The data was sorted by `Date` and `Time` to enforce chronological order (e.g., from "10/03/2004 18.00.00" to "10/03/2004 19.00.00").
- This step aligned the data with its natural temporal sequence, preparing it for streaming in a way that mimics real-time collection and supports future time series analysis.

### Step 3: Message Formatting
- Each row was formatted into a JSON object containing `Date`, `Time`, and `CO(GT)` fields (e.g., `{"Date": "10/03/2004", "Time": "18.00.00", "CO(GT)": 2.6}`).
- This lightweight transformation prepared the data for Kafka, maintaining its raw form while ensuring compatibility with the streaming framework.

## Rationale
- **Minimal Processing**: Phase 1 emphasizes pipeline functionality over data transformation. Raw `CO(GT)` values, including missing entries marked as -200, were streamed as-is to validate the Kafka setup.
- **Temporal Integrity**: Sorting by date and time preserves the dataset’s time series nature, critical for real-time simulation and later modeling phases.
- **Deferral of Complex Steps**: Cleaning (e.g., handling -200 values) and feature engineering (e.g., lags, rolling statistics) were postponed to Phase 3, where predictive modeling requires such enhancements.

## Output
- The preprocessing resulted in a stream of JSON messages sent to the `air_quality_data` Kafka topic.
- Example message: A record from March 10, 2004, at 18:00 with a `CO(GT)` value of 2.6, formatted as a JSON object and streamed with a 0.1-second delay to simulate real-time data flow.

## Challenges Encountered and Resolutions

### Challenge: CSV Parsing Errors
- **Issue**: Initial attempts to load `AirQualityUCI.csv` failed because standard CSV parsing expected comma separators, resulting in malformed data (e.g., merged columns or incorrect numeric values).
- **Resolution**: Inspected the file to identify its semicolon-separated structure and comma decimals. Adjusted the loading process to use these specific parameters, ensuring columns like `Date`, `Time`, and `CO(GT)` were parsed correctly. Verified with a sample output to confirm accuracy before streaming.

## Verification
- The preprocessed data was validated by streaming it through the Kafka pipeline. The consumer logged messages matching the dataset (e.g., "10/03/2004 18.00.00, CO(GT): 2.6"), confirming that loading, sorting, and formatting preserved the data’s integrity.
- The process handled the full dataset (approximately 9357 rows) or a subset if interrupted, with no loss of temporal order.

## Notes
- **Raw Data Retention**: Missing values (-200) were not filtered in Phase 1, as the focus was on pipeline validation rather than data quality.
- **Scalability**: The strategy suits the UCI dataset’s size; larger datasets might require batch processing in future phases.
- **Future Enhancements**: Phase 3 will build on this by adding cleaning (e.g., replacing -200) and feature engineering for predictive modeling.

## Conclusion
The Phase 1 preprocessing strategy successfully prepared `AirQualityUCI.csv` for Kafka streaming with minimal intervention. By addressing parsing challenges and ensuring chronological order, it laid a solid foundation for real-time data flow, verified through consumer logs, while keeping advanced preprocessing for subsequent phases.
