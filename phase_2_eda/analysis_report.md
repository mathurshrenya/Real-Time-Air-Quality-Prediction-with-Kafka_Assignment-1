# Phase 2 Analysis Report: Air Quality Data Exploration

## Introduction
This report presents an exploratory data analysis (EDA) of the UCI Air Quality dataset (`AirQualityUCI.csv`) as part of Phase 2 of the "Real-Time Air Quality Prediction with Kafka" project. Using time-series plots, decomposition, autocorrelation, partial autocorrelation, and correlation heatmaps, we analyze patterns in CO(GT), NOx(GT), and C6H6(GT) concentrations from March 2004 to March 2005. The findings identify key factors influencing air quality variations and inform the modeling approach for Phase 3, where real-time predictions will be implemented using Kafka.

## Basic Visualizations

### Time-Series Plots of CO(GT), NOx(GT), and C6H6(GT)
The time-series plots (Figure 1) show hourly concentrations of CO(GT), NOx(GT), and C6H6(GT) from March 2004 to March 2005. Several patterns emerge:
- **CO(GT)**: Concentrations fluctuate between 0 and 10 mg/m³, with peaks often reaching 5-7 mg/m³. Notable spikes occur in March-April 2004, July 2004, and November 2004-February 2005, suggesting seasonal influences. A significant data gap appears around September 2004, indicating missing values (likely -200 in the raw data).
- **NOx(GT)**: Concentrations range from 0 to 1500 µg/m³, with peaks around 1000 µg/m³. The pattern mirrors CO(GT), with spikes in the same periods (e.g., March-April 2004 and winter months). This suggests a potential correlation between CO and NOx emissions.
- **C6H6(GT)**: Benzene levels vary from 0 to 60 µg/m³, with peaks around 40 µg/m³. The trend aligns with CO and NOx, showing higher concentrations in spring and winter, and a similar data gap in September 2004.
- **Observation**: All pollutants exhibit synchronized peaks, hinting at shared sources (e.g., traffic or industrial activity) and seasonal effects (e.g., winter temperature inversions trapping pollutants).

### Daily/Weekly Patterns
The decomposition plot (second figure) breaks down CO(GT) into trend, seasonal, and residual components:
- **Trend**: CO(GT) concentrations show a slight decline from March to June 2004, a dip in September (due to missing data), and a rise in winter 2004-2005. This suggests a long-term seasonal cycle.
- **Seasonal**: The seasonal component reveals a clear daily (24-hour) cycle, with peaks around 0-1 and troughs around -1. Mapping this to hours (as shown in the hourly average subplot), CO(GT) peaks around 8-9 AM and 6-8 PM, likely corresponding to rush hours, and dips at night (2-4 AM).
- **Residuals**: The residuals plot shows random noise with occasional spikes, indicating unmodeled events (e.g., sudden emission increases).
- **Observation**: The 24-hour periodicity suggests traffic as a primary driver, with potential weekly patterns (e.g., lower weekend emissions) to explore further.

### Correlation Heatmap Between Pollutants
The correlation heatmap (third figure) shows Pearson correlations between CO(GT), NOx(GT), and C6H6(GT):
- CO(GT) and NOx(GT): 0.79 (strong positive correlation).
- CO(GT) and C6H6(GT): 0.78 (strong positive correlation).
- NOx(GT) and C6H6(GT): 0.64 (moderate positive correlation).
- **Observation**: The strong correlations suggest these pollutants share common sources, likely vehicular emissions (e.g., CO and NOx from exhaust, C6H6 from fuel combustion). This multicollinearity will influence feature selection in modeling.

## Advanced Visualizations

### Autocorrelation and Partial Autocorrelation Plots
The autocorrelation (ACF) and partial autocorrelation (PACF) plots for CO(GT) (first and fourth figures) provide insights into its time-series structure:
- **ACF**: Shows significant autocorrelation at lags 1-5 (0.75 to 0.25), with a repeating pattern every 24 lags (e.g., peaks at lags 24 and 48). This confirms a strong daily seasonality (24-hour cycle), consistent with the decomposition plot. The slow decay suggests a non-stationary series with trend and seasonality.
- **PACF**: Shows a significant spike at lag 1 (0.75), smaller spikes at lags 2-5, and a peak at lag 24 (around 0.25). This indicates that after accounting for lag 1, the direct effect of further lags diminishes, but the seasonal lag (24) remains influential.
- **Observation**: The daily seasonality (lag 24) and short-term dependencies (lags 1-5) will guide ARIMA/SARIMA modeling, with a seasonal period of 24 hours.

### Decomposition of Time Series
The decomposition plot (second figure) further confirms:
- **Trend**: Seasonal fluctuations with higher concentrations in spring and winter.
- **Seasonal**: A consistent 24-hour cycle, as noted.
- **Residuals**: Random noise with occasional outliers, suggesting external factors (e.g., weather events) not captured by trend or seasonality.
- **Observation**: The decomposition highlights the need for a model that captures both trend and daily seasonality, such as SARIMA, while residuals suggest potential exogenous variables (e.g., temperature, traffic data).

## Analysis of Potential Factors Influencing Air Quality Variations
Several factors likely influence the observed air quality patterns:
1. **Traffic Patterns**: The 24-hour cycle, with peaks during morning and evening rush hours (8-9 AM, 6-8 PM), points to vehicular emissions as a primary source. CO, NOx, and C6H6 are all byproducts of combustion, and their high correlation (0.64-0.79) supports this hypothesis.
2. **Seasonal Effects**: Higher concentrations in spring (March-April 2004) and winter (November 2004-February 2005) may result from meteorological conditions. Winter temperature inversions can trap pollutants near the ground, increasing concentrations, while spring may see increased traffic or industrial activity.
3. **Data Gaps**: The missing data in September 2004 (marked as -200 in the raw dataset) indicates sensor failures or maintenance. This requires preprocessing (e.g., imputation) before modeling to avoid bias.
4. **External Factors**: Residual spikes suggest unmodeled influences, such as weather (e.g., wind speed, humidity) or events (e.g., industrial emissions, festivals). Incorporating exogenous variables could improve model accuracy.

## How Findings Inform the Modeling Approach
The EDA findings directly shape the modeling strategy for Phase 3:
- **Model Selection**:
  - **SARIMA**: The strong 24-hour seasonality (lag 24 in ACF/PACF) and non-stationarity (slow decay in ACF) make SARIMA a suitable choice for CO(GT). A seasonal period of 24 will be used, with initial parameters like `(1,1,1)(1,0,0,24)` based on PACF spikes at lag 1 and seasonal lag 24. The trend component suggests differencing (d=1).
  - **Random Forest**: The correlation between pollutants and daily patterns (e.g., hour of day) supports using Random Forest with engineered features like lagged CO values (lags 1-3), hour, day, and rolling statistics (mean/std over 24 hours). RF can also handle non-linear relationships and exogenous variables.
- **Feature Engineering**:
  - **Time-Based Features**: Hour, day, and month to capture daily and seasonal cycles.
  - **Lagged Features**: CO(GT) lags 1-3, based on ACF/PACF, to model short-term dependencies.
  - **Rolling Statistics**: 24-hour rolling mean and std to capture local trends.
  - **Exogenous Variables**: Include NOx(GT) and C6H6(GT) due to high correlations, but address multicollinearity (e.g., via PCA or feature selection). Weather data (e.g., temperature, wind) could model residual spikes.
- **Preprocessing**:
  - Replace -200 values with imputed estimates (e.g., mean or interpolated
