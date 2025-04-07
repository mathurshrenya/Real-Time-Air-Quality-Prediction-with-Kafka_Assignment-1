# Kafka Integration Documentation

## Overview
This document details the integration of trained machine learning models—Random Forest (RF) and SARIMA—with Kafka for real-time air quality prediction in Phase 3 of the "Real-Time Air Quality Prediction with Kafka" project. It describes the mechanism to process incoming Kafka messages using these models and outlines the system's operation in a real-time environment, building on the pipeline established in Phase 1 and the EDA from Phase 2.

## Mechanism for Using Trained Models with Incoming Kafka Messages

### Model Training and Storage
- **Random Forest (RF)**: Trained on `AirQualityUCI.csv` with engineered features (e.g., hour, day, month, CO(GT) lags 1-3, 24-hour rolling mean/std). Saved as `rf_model.pkl` with MAE: 0.375, RMSE: 0.551, outperforming the baseline (MAE: 0.452).
- **SARIMA**: Trained on CO(GT) time series using parameters `(1,1,0)(1,0,0,24)` to capture daily seasonality (24-hour cycle). Saved as `arima_model.pkl` (MAE/RMSE pending due to earlier convergence issues, but simplified to ensure stability).
- Both models were serialized using Python's `pickle` module for easy loading during real-time prediction.

### Kafka Pipeline Recap
- **Producer**: Sends air quality data (`Date`, `Time`, `CO(GT)`) from `AirQualityUCI.csv` to the `air_quality_data` topic, sorted chronologically, with a 0.1-second delay to simulate real-time streaming.
- **Consumer**: Subscribes to `air_quality_data`, processes messages, and generates predictions.

### Real-Time Prediction Mechanism
The consumer script (`consumer_with_both_models.py`) integrates both models as follows:
- **Message Processing**:
  - Each incoming Kafka message contains `Date`, `Time`, and `CO(GT)`. The consumer deserializes the JSON message and extracts these fields.
  - A `DateTime` index is created by combining `Date` and `Time` (e.g., "10/03/2004 18.00.00") for temporal alignment.
- **Random Forest Prediction**:
  - Features are engineered on-the-fly:
    - **Time-Based**: Hour, day, and month extracted from `DateTime`.
    - **Lagged Features**: CO(GT) lags 1-3, maintained in a sliding window of the last 24 hours.
    - **Rolling Statistics**: 24-hour rolling mean and standard deviation of CO(GT).
  - These features match the training setup, ensuring consistency.
  - The pre-trained RF model (`rf_model.pkl`) is loaded at startup and used to predict CO(GT) for each message. Predictions are logged immediately (e.g., "RF Predicted CO(GT): 2.177").
- **SARIMA Prediction**:
  - A history of CO(GT) values is maintained in a time-series structure, appended with each new message’s value.
  - **Initial Phase**: For the first 48 messages (two days), the pre-trained SARIMA model (`arima_model.pkl`) generates forecasts without refitting, as the history is insufficient for stable refitting.
  - **Refitting Phase**: After 48 messages, the SARIMA model is refit every 24 messages (daily) using the latest 100 hours of data to capture recent trends and seasonality. The `(1,1,0)(1,0,0,24)` parameters are used, balancing stability and computational efficiency.
  - Predictions are logged (e.g., "SARIMA Predicted CO(GT): 2.543") or an error is logged if convergence fails.
- **Error Handling**:
  - Exceptions in SARIMA prediction (e.g., convergence issues) are caught and logged with details to prevent pipeline crashes.
  - RF predictions are more robust and serve as a fallback if SARIMA fails.

### Logging and Monitoring
- Each message processed logs the actual CO(GT), RF prediction, and SARIMA prediction (or status, e.g., "waiting for more data").
- Example log: "Received: 10/03/2004 18.00.00, CO(GT): 2.6 | RF Predicted CO(GT): 2.543 | SARIMA Predicted CO(GT) (pre-trained): 2.500".
- This allows real-time monitoring of model performance and debugging of issues like SARIMA convergence failures.

## System Operation in a Real-Time Environment

### Deployment Setup
- **Kafka Cluster**: In a real-time environment, Kafka would run on a distributed cluster (e.g., 3-5 brokers) for fault tolerance and scalability, unlike the local single-broker setup (`localhost:9092`) used in development. Zookeeper would manage the cluster, ensuring topic partitioning and replication.
- **Producer**: Instead of reading from a CSV, the producer would ingest live sensor data (e.g., from IoT devices measuring CO, NOx, C6H6) via APIs or direct feeds, sending JSON messages to `air_quality_data` with minimal latency.
- **Consumer Deployment**:
  - The consumer script would run as a service (e.g., using Docker or a Kubernetes pod) to ensure continuous operation.
  - Multiple consumer instances could be deployed in a consumer group to handle high message volumes, with Kafka balancing the load across partitions.
- **Model Storage**: Pre-trained models (`rf_model.pkl`, `arima_model.pkl`) would be stored in a centralized location (e.g., AWS S3, local filesystem) and loaded at consumer startup.

### Real-Time Workflow
1. **Data Ingestion**: Sensors push air quality readings every hour (or more frequently) to the producer, which formats them as JSON and sends them to `air_quality_data`.
2. **Message Consumption**: The consumer processes messages in real-time, maintaining a sliding window of historical CO(GT) values for feature engineering and SARIMA updates.
3. **Prediction**:
   - RF generates predictions instantly using engineered features, suitable for low-latency requirements.
   - SARIMA provides time-series forecasts, updating daily to adapt to evolving patterns, but requires at least 48 hours of initial data for stable refitting.
4. **Output**:
   - Predictions are logged to a file or database (e.g., PostgreSQL, Elasticsearch) for monitoring.
   - Alerts can be triggered if predicted CO(GT) exceeds a threshold (e.g., 10 mg/m³), notifying environmental agencies.
   - Predictions can be visualized on a dashboard (e.g., using Grafana) for real-time air quality monitoring.

### Performance and Scalability
- **Latency**: RF predictions are near-instantaneous (milliseconds), while SARIMA refitting every 24 messages introduces a slight delay (seconds), acceptable for hourly data. For higher-frequency data, refitting intervals would be optimized.
- **Throughput**: Kafka can handle thousands of messages per second in a distributed setup. The consumer scales horizontally by adding instances, ensuring it keeps up with message rates.
- **Model Updates**: Models can be retrained offline (e.g., weekly) on new data, with updated `.pkl` files deployed to the consumer without downtime using a rolling update strategy.

### Challenges and Mitigations
- **Missing Data**: Sensors may fail, sending -200 values. The consumer preprocesses these by imputing with the last valid value or a rolling mean to maintain prediction continuity.
- **SARIMA Stability**: Convergence issues (as seen in development) are mitigated by using a simpler model `(1,1,0)(1,0,0,24)` and limiting refitting frequency. If SARIMA fails, RF predictions ensure the system remains operational.
- **Resource Constraints**: SARIMA refitting is computationally intensive. In production, this could be offloaded to a dedicated worker (e.g., using Celery) to avoid blocking the consumer.
- **Data Drift**: Air quality patterns may shift over time (e.g., due to policy changes). Regular model retraining and monitoring of prediction errors (e.g., MAE in real-time) will detect drift, triggering updates.

## Conclusion
The Kafka integration enables real-time air quality prediction by combining RF’s feature-based approach with SARIMA’s time-series modeling. The consumer processes incoming messages efficiently, generating predictions with minimal latency, and scales for production use. In a real-time environment, the system ensures continuous operation, handles missing data, and adapts to evolving patterns, providing actionable insights for air quality management.
