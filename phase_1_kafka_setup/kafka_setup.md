# Kafka Setup Documentation

## Overview
This document details the setup process for Apache Kafka to stream air quality data from the UCI Air Quality dataset (`AirQualityUCI.csv`) as part of Phase 1 of the "Real-Time Air Quality Prediction with Kafka" project. It covers the installation, configuration, execution steps, challenges encountered, and their resolutions, ensuring a functional pipeline for real-time data streaming.

## Prerequisites
- **Kafka**: Version 2.13-3.7.0, downloaded from [kafka.apache.org](https://kafka.apache.org/downloads).
- **Python**: 3.12, running in a virtual environment (`.venv`).
- **Dependencies**: `kafka-python==2.0.2`, `pandas==2.2.2`, installed via `pip install -r requirements.txt`.
- **Operating System**: macOS (tested on Shrenya’s MacBook Air).
- **Dataset**: `AirQualityUCI.csv`, placed in `data/` subdirectory relative to `/Users/shrenyamathur/Documents/kafka`.

## Setup Process

### Step 1: Kafka Installation
- Downloaded the Kafka 2.13-3.7.0 tarball from the official website.
- Extracted it to a local directory, specifically `/Users/shrenyamathur/kafka`, using commands in a terminal to unzip and move the files. This established the base directory for Kafka operations.

### Step 2: Start Zookeeper
- Zookeeper, required for Kafka coordination, was started from the Kafka directory using the default configuration file `config/zookeeper.properties`.
- Executed in a dedicated terminal window, it ran on `localhost:2181`. The terminal remained open to keep Zookeeper active, with logs confirming it was listening for connections.

### Step 3: Start Kafka Broker
- The Kafka broker was launched using `config/server.properties`, also from the Kafka directory, in a separate terminal.
- It operated on `localhost:9092` with a single-broker setup for simplicity. Logs in the terminal verified the broker started successfully and was ready to handle messages.

### Step 4: Running the Pipeline
- The pipeline required Zookeeper and the Kafka broker to be running first.
- In one terminal, the consumer was started from the project directory (`/Users/shrenyamathur/Documents/kafka`) to listen to the `air_quality_data` topic.
- In another terminal, the producer was executed from the same directory to send data to the topic, simulating real-time streaming with a 0.1-second delay between messages.

## Challenges Encountered and Resolutions

### Challenge 1: Kafka Not Starting
- **Issue**: Zookeeper failed to launch due to a "port already in use" error on `localhost:2181`, indicating another process was occupying the port.
- **Resolution**: Investigated running processes using a command to list them, identified the conflicting process ID, and terminated it with a kill command. Restarted Zookeeper, which then ran without issues.

### Challenge 2: Producer Connection Error
- **Issue**: The producer encountered a `KafkaTimeoutError`, unable to connect to the broker at `localhost:9092`.
- **Resolution**: Confirmed the broker wasn’t running when the producer started. Ensured the broker was active first by checking its terminal output, then reran the producer, which connected successfully after verifying the port.

### Challenge 3: Consumer Not Receiving Messages
- **Issue**: The consumer initialized but didn’t log any messages, even as the producer appeared to send data.
- **Resolution**: Adjusted the consumer to read from the topic’s beginning by setting an appropriate offset parameter. Also ensured the producer flushed its messages to the topic before the consumer started listening, resolving the issue by restarting both in the correct sequence.

### Challenge 4: Data Parsing Issues
- **Issue**: The dataset (`AirQualityUCI.csv`) wasn’t loading correctly due to its semicolon-separated values and comma decimals, causing malformed data in the pipeline.
- **Resolution**: Inspected the CSV file to identify its structure, then adjusted the loading parameters in the producer to use semicolon separators and comma decimals. Tested with a sample to confirm correct parsing before streaming.

## Verification
- The producer completed its run, indicating all data was sent to the `air_quality_data` topic (e.g., 9357 rows from `AirQualityUCI.csv` or a subset if interrupted).
- The consumer logged messages in real-time, such as entries from March 10, 2004, with `CO(GT)` values like 2.6 and 2.0, matching the dataset. This confirmed the pipeline streamed data end-to-end successfully.

## Notes
- No manual topic creation was needed; the producer auto-created `air_quality_data` upon sending the first message.
- The setup uses a single local broker for simplicity; a production environment would require a multi-broker cluster.
- Challenges were resolved through systematic debugging, ensuring a robust foundation for subsequent phases.

## Conclusion
The Kafka setup process established a functional streaming pipeline, overcoming port conflicts, connection timeouts, and parsing errors. Zookeeper and the Kafka broker were configured to support the producer and consumer, verified by successful data transmission from `AirQualityUCI.csv` to the consumer’s logs, completing Phase 1 objectives.
