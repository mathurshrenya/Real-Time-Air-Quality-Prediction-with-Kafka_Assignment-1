import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pickle

#Using Random Forest as the base model

df = pd.read_csv('processed_data.csv', index_col='DateTime', parse_dates=True)
X = df[['Hour', 'Day', 'Month', 'CO_lag1', 'CO_lag2', 'CO_lag3', 'CO_roll_mean', 'CO_roll_std']]
y = df['CO(GT)']

train_size = int(len(df) * 0.8)
X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]

rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

y_pred = rf_model.predict(X_test)

y_baseline = y_test.shift(1).dropna()
y_test_baseline = y_test[1:]

rf_mae = mean_absolute_error(y_test, y_pred)
rf_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
baseline_mae = mean_absolute_error(y_test_baseline, y_baseline)
baseline_rmse = np.sqrt(mean_squared_error(y_test_baseline, y_baseline))

print(f"Random Forest - MAE: {rf_mae:.3f}, RMSE: {rf_rmse:.3f}")
print(f"Baseline - MAE: {baseline_mae:.3f}, RMSE: {baseline_rmse:.3f}")

with open('rf_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)
print("Model saved to 'rf_model.pkl'")
