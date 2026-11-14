# 🛰️ TrendLens — NASA Earth System Trend Detective
**NASA Space Apps Challenge 2026** | *Challenge: Be An Earth System Trend Detective!*

---

## 🌟 Overview & Mission
**TrendLens** is an interactive, full-stack Earth science dashboard developed strictly for the **NASA Space Apps Challenge 2026**. It transforms petabytes of complex NASA satellite telemetry and NOAA surface observations into clear, statistically-validated answers to the challenge's five core detective questions:
1. **What changed?** (Surface Air Temperature, Soil Moisture, Precipitation, Humidity, Wind Dynamics)
2. **Where did it change?** (10 global hotspots across multiple biomes & latitude sectors)
3. **When did it change?** (24-year historical continuum from 2000 to 2023)
4. **How much did it change?** (Theil-Sen robust slope estimator per decade)
5. **Is it statistically significant?** (Mann-Kendall non-parametric test with explicit $p$-values and 95% confidence intervals)

---

## 🏛️ Official NASA Space Apps Challenge Resources Used
This project strictly relies on the official resources provided in the hackathon challenge brief:

| Resource | Official URL / Citation | Role in TrendLens |
| :--- | :--- | :--- |
| **NASA POWER / MERRA-2** | [power.larc.nasa.gov](https://power.larc.nasa.gov/) | Primary satellite & reanalysis satellite feed for 2000–2023 (288 continuous monthly timesteps per region). |
| **NOAA CDO (GHCND)** | [ncei.noaa.gov/cdo-web](https://www.ncei.noaa.gov/cdo-web/) | Ground truth cross-validation against physical weather stations (Token authenticated). |
| **Mann-Kendall & Sen's Slope** | [Statistical Test Methods in Time Series](https://medium.com/@snp.kriss/statistical-test-methods-to-detect-trends-in-time-series-data-b361a0ec530b) | Primary mathematical framework for trend slope and non-parametric hypothesis testing. |
| **Statistical Significance Guide** | [Comprehensive Guide to Significance](https://www.statsig.com/perspectives/a-comprehensive-guide-to-statistical-significance) | Determining true climate shifts vs. natural seasonal fluctuations at $\alpha = 0.05$. |

---

## 🚀 Key Architectural Capabilities

### 1. 🔮 Future Trend Forecasting Engine (2024 → 2050)
- Extrapolates historical trends using the non-parametric **Theil-Sen slope estimator** to prevent skew from outlier years.
- Dynamically generates **95% Confidence Interval (CI) uncertainty envelopes** projecting potential variance through year 2050.
- Switchable across multiple climate variables (`TEMP`, `HUM`, `PREC`, `WIND`) with live narrative detective synthesis.

### 2. 📡 NOAA CDO Ground Station Cross-Validation
- Validates NASA satellite observations directly against NOAA Global Historical Climatology Network (GHCND) stations.
- Automatically calculates:
  - **Mean Bias Error (°C)**
  - **Root Mean Square Error (RMSE)**
  - **Pearson Correlation Coefficient ($r$)**
  - **Agreement Rating** (`EXCELLENT`, `GOOD`, `MODERATE`)
- Validated across 8 global stations with continuous record caches (Nuuk, Tura, Ash Mountain, King Khaled Airport, Comodoro Rivadavia, Goure, Amraoti, Itacoatiara).

### 3. 🎨 High-Fidelity NASA Telemetry Glassmorphism UX
- Built on top of the dark-mode cybernetic telemetry layout (Deep Space palette `#10131c`, Electric Cyan `#4cd6fb`, Cosmic Magenta `#ffafd1`, Neon Violet `#8a3ffc`).
- 4 Core Real-time Climate Telemetry Modules (Thermal Dynamics, Atmospheric Moisture, Precipitation Radar, Vector Wind Dynamics).
- Dynamic SVG Sparklines, responsive progress gauges, live mission clocks, and real-time downlink logs.
- Clickable 10-region latitude anomaly matrix that instantly switches all charts, forecasting projections, and station validations in real time.

---

## 🌍 Verified Hotspot Benchmark Results

| Region | Latitude Sector | Mean Temp | Sen's Slope / Decade | $p$-value | Significance | NOAA Station Match |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cairo, Egypt** | 30.04°N, 31.24°E | 21.8°C | **+0.272°C/dec** | $p = 0.0033$ | ★ Confirmed | NASA Satellite Only |
| **Amazon Rainforest** | -3.47°S, -62.22°W | 26.6°C | **+0.205°C/dec** | $p < 0.0001$ | ★ Confirmed | Itacoatiara ($r = 0.76$) |
| **Siberia, Russia** | 61.52°N, 105.19°E | -6.7°C | **+0.655°C/dec** | $p = 0.0060$ | ★ Confirmed | Tura Station ($r = 0.93$) |
| **Sahel, Africa** | 15.50°N, 17.50°E | 27.9°C | **-0.292°C/dec** | $p = 0.0056$ | ★ Confirmed | Goure Station ($r = 0.54$) |
| **California Valley** | 36.78°N, -119.42°W | 14.7°C | **+0.510°C/dec** | $p = 0.0004$ | ★ Confirmed | Ash Mountain ($r = 0.85$) |
| **Arabian Peninsula** | 23.69°N, 45.07°E | 25.9°C | **+0.302°C/dec** | $p = 0.0001$ | ★ Confirmed | King Khaled Intl ($r = 0.60$) |
| **Greenland Ice Sheet** | 72.00°N, -40.00°W | -27.0°C | **-0.243°C/dec** | $p = 0.2433$ | ~NS (Fluctuation) | Nuuk ($r = 0.82$) |
| **Patagonia, Argentina**| -45.00°S, -69.00°W | 9.2°C | **+0.388°C/dec** | $p = 0.0003$ | ★ Confirmed | Comodoro Rivadavia ($r = 0.85$) |
| **Baghdad, Iraq** | 33.32°N, 44.37°E | 24.0°C | **+0.637°C/dec** | $p < 0.0001$ | ★ Confirmed | NASA Satellite Only |

---

## 🛠️ How to Launch the Application

### Method 1: Instant Launch (Windows)
Double-click:
```cmd
start_app.bat
```

### Method 2: Manual Terminal Execution
```bash
# Navigate to directory
cd "c:\Users\Ahmed Anter\Desktop\Nasa Space Apps"

# Start the Fast-API & Telemetry Server
python run_server.py
```

Now open your browser and navigate to:
👉 **`http://localhost:8000`**
