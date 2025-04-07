import json
from kafka import KafkaConsumer
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer = KafkaConsumer(
    'air_quality_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',  # Start from the beginning
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

received_data = []

try:
    logger.info("Starting consumer...")
    for message in consumer:
        record = message.value
        received_data.append(record)
        logger.info(f"Received record: {record['Date']} {record['Time']}")
except KeyboardInterrupt:
    logger.info("Consumer stopped by user.")
except Exception as e:
    logger.error(f"Error in consumer: {e}")
finally:
    if received_data:
        df = pd.DataFrame(received_data)
        df.to_csv('received_air_quality.csv', index=False, sep=';')
        logger.info("Data saved to received_air_quality.csv")
    else:
        logger.warning("No data received to save.")

consumer.close()
