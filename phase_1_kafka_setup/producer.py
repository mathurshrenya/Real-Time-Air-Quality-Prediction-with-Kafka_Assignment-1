import time
import json
import pandas as pd
from kafka import KafkaProducer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

data_path = 'data/AirQualityUCI.csv'  # Adjust if needed
df = pd.read_csv(data_path, sep=';', decimal=',')
logger.info("CSV file loaded successfully.")

df.replace(-200, float('nan'), inplace=True)
df.fillna(method='ffill', inplace=True)
logger.info("Missing values replaced and forward-filled.")

def send_to_kafka(row):
    try:
        record = row.to_dict()
        for key, value in record.items():
            if isinstance(value, (pd.Timestamp, pd.Timedelta)):
                record[key] = str(value)
            elif isinstance(value, float):
                record[key] = float(value)
        producer.send('air_quality_data', value=record)
        logger.info(f"Sent record: {record['Date']} {record['Time']}")
    except Exception as e:
        logger.error(f"Error sending record: {e}")

for index, row in df.iterrows():
    send_to_kafka(row)
    time.sleep(1)  

producer.flush()
producer.close()
logger.info("Producer finished sending all records.")
