import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle

df = pd.read_csv('received_air_quality.csv', sep=';')
df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H.%M.%S')
df.set_index('DateTime', inplace=True)
y = df['CO(GT)'].dropna()

train_size = int(len(y) * 0.8)
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

#Using Sarima model
sarima_model = SARIMAX(y_train, order=(1, 1, 0), seasonal_order=(1, 0, 0, 24))
sarima_fit = sarima_model.fit(disp=False)

y_pred = sarima_fit.forecast(steps=len(y_test))

y_baseline = y_test.shift(1).dropna()
y_test_baseline = y_test[1:]

sarima_mae = mean_absolute_error(y_test, y_pred)
sarima_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
baseline_mae = mean_absolute_error(y_test_baseline, y_baseline)
baseline_rmse = np.sqrt(mean_squared_error(y_test_baseline, y_baseline))

print(f"SARIMA - MAE: {sarima_mae:.3f}, RMSE: {sarima_rmse:.3f}")
print(f"Baseline - MAE: {baseline_mae:.3f}, RMSE: {baseline_rmse:.3f}")

with open('arima_model.pkl', 'wb') as f:
    pickle.dump(sarima_fit, f)
print("SARIMA model saved to 'arima_model.pkl'")
