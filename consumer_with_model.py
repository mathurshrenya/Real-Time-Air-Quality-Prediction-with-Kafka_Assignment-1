import json
import pandas as pd
from kafka import KafkaConsumer
import pickle
import logging

#for only random forest
with open('rf_model.pkl', 'rb') as f:
    model = pickle.load(f)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer = KafkaConsumer(
    'air_quality_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def prepare_features(record, prev_data):
    df = pd.DataFrame([record])
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H.%M.%S')
    df.set_index('DateTime', inplace=True)
    
    df['Hour'] = df.index.hour
    df['Day'] = df.index.day
    df['Month'] = df.index.month
    
    prev_data.append(record['CO(GT)'])
    if len(prev_data) > 24:
        prev_data.pop(0)
    df['CO_lag1'] = prev_data[-2] if len(prev_data) >= 2 else prev_data[-1]
    df['CO_lag2'] = prev_data[-3] if len(prev_data) >= 3 else prev_data[-1]
    df['CO_lag3'] = prev_data[-4] if len(prev_data) >= 4 else prev_data[-1]
    df['CO_roll_mean'] = pd.Series(prev_data).mean()
    df['CO_roll_std'] = pd.Series(prev_data).std()
    
    features = ['Hour', 'Day', 'Month', 'CO_lag1', 'CO_lag2', 'CO_lag3', 'CO_roll_mean', 'CO_roll_std']
    return df[features]

prev_data = []
logger.info("Starting consumer with prediction...")
for message in consumer:
    record = message.value
    logger.info(f"Received: {record['Date']} {record['Time']}, CO(GT): {record['CO(GT)']}")
    
    X = prepare_features(record, prev_data)
    prediction = model.predict(X)[0]
    logger.info(f"Predicted CO(GT): {prediction:.3f}")