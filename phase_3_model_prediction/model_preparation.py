import pandas as pd
import numpy as np

df = pd.read_csv('received_air_quality.csv', sep=';')
print(f"Initial rows from received_air_quality.csv: {len(df)}")
print("Initial data preview:")
print(df.head())

keep_columns = ['Date', 'Time', 'CO(GT)']  
df = df[keep_columns]
print(f"Columns kept: {df.columns.tolist()}")

df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H.%M.%S')
df.set_index('DateTime', inplace=True)

target = 'CO(GT)'

df['Hour'] = df.index.hour
df['Day'] = df.index.day
df['Month'] = df.index.month

df['CO_lag1'] = df[target].shift(1)
df['CO_lag2'] = df[target].shift(2)
df['CO_lag3'] = df[target].shift(3)
print(f"Rows after lagging: {len(df)}")
print("After lagging preview:")
print(df[[target, 'CO_lag1', 'CO_lag2', 'CO_lag3']].head())

df['CO_roll_mean'] = df[target].rolling(window=24).mean()
df['CO_roll_std'] = df[target].rolling(window=24).std()
print(f"Rows after rolling: {len(df)}")
print("After rolling preview:")
print(df[[target, 'CO_roll_mean', 'CO_roll_std']].head(25))

feature_columns = ['Hour', 'Day', 'Month', 'CO_lag1', 'CO_lag2', 'CO_lag3', 'CO_roll_mean', 'CO_roll_std', target]
df = df[feature_columns].dropna()
print(f"Rows after dropna: {len(df)}")
print("Final data preview:")
print(df.head())

if len(df) > 0:
    df.to_csv('processed_data.csv')
    print("Features engineered and data saved to 'processed_data.csv'")
else:
    print("No data to save - processed_data.csv will be empty")
