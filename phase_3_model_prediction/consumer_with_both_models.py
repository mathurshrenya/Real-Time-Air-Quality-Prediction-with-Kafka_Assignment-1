import json
import pandas as pd
import numpy as np
from kafka import KafkaConsumer
import pickle
import logging
from statsmodels.tsa.statespace.sarimax import SARIMAX

with open('rf_model.pkl', 'rb') as f:
    rf_model = pickle.load(f)
with open('arima_model.pkl', 'rb') as f:
    sarima_model = pickle.load(f)  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer = KafkaConsumer(
    'air_quality_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def prepare_rf_features(record, prev_data):
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
arima_history = pd.Series(dtype=float)
update_interval = 24 
message_count = 0

logger.info("Starting consumer with RF and SARIMA predictions")

for message in consumer:
    record = message.value
    actual_co = record['CO(GT)']
    logger.info(f"Received: {record['Date']} {record['Time']}, CO(GT): {actual_co}")

    # Random Forest
    rf_X = prepare_rf_features(record, prev_data)
    rf_pred = rf_model.predict(rf_X)[0]
    logger.info(f"RF Predicted CO(GT): {rf_pred:.3f}")

    # SARIMA 
    arima_history = pd.concat([arima_history, pd.Series([actual_co])], ignore_index=True)
    if len(arima_history) > 168:
        arima_history = arima_history[-168:] 
    
    #refitting SARIMA model
    try:
        if len(arima_history) < 48:
            sarima_pred = sarima_model.forecast(steps=1).iloc[0]
            logger.info(f"SARIMA Predicted CO(GT) (pre-trained): {sarima_pred:.3f}")
        else:
            if message_count % update_interval == 0:
                sarima_model = SARIMAX(arima_history, order=(1, 1, 0), seasonal_order=(1, 0, 0, 24)).fit(disp=False)
                logger.info("SARIMA model updated")
            sarima_pred = sarima_model.forecast(steps=1).iloc[0]
            logger.info(f"SARIMA Predicted CO(GT): {sarima_pred:.3f}")
    except Exception as e:
        logger.error(f"SARIMA prediction failed: {type(e).__name__}: {e}")
    
    message_count += 1
