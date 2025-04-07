import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


df = pd.read_csv('received_air_quality.csv', sep=';')

df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H.%M.%S')

df.set_index('DateTime', inplace=True)

pollutants = ['CO(GT)', 'NOx(GT)', 'C6H6(GT)']
df_pollutants = df[pollutants]

print(df_pollutants.head())
print(df_pollutants.describe())


plt.figure(figsize=(15, 10))

for i, pollutant in enumerate(pollutants, 1):
    plt.subplot(3, 1, i)
    plt.plot(df_pollutants.index, df_pollutants[pollutant], label=pollutant)
    plt.title(f'{pollutant} Concentration Over Time')
    plt.xlabel('DateTime')
    plt.ylabel('Concentration')
    plt.legend()

plt.tight_layout()
plt.savefig('time_series_plots.png')
plt.show()


plt.figure(figsize=(8, 6))
corr = df_pollutants.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('Correlation Between Pollutants')
plt.savefig('correlation_heatmap.png')
plt.show()


from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plt.figure(figsize=(12, 6))
plot_acf(df_pollutants['CO(GT)'].dropna(), lags=50, title='Autocorrelation - CO(GT)')
plt.savefig('acf_co.png')
plt.show()

plt.figure(figsize=(12, 6))
plot_pacf(df_pollutants['CO(GT)'].dropna(), lags=50, title='Partial Autocorrelation - CO(GT)')
plt.savefig('pacf_co.png')
plt.show()  


from statsmodels.tsa.seasonal import seasonal_decompose

decomp = seasonal_decompose(df_pollutants['CO(GT)'].dropna(), model='additive', period=24)
decomp.plot()
plt.savefig('decomposition_co.png')
plt.show()