import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FILE = "SOLETE_Pombo_1min.h5"
KEY = "DATA"

SIGNAL_COL = "P_Solar[kW]"

WINDOW = 256          # 256 minút
STEP = 256            # bez prekryvu; môžeš dať napr. 64 pre sliding window
P_ENERGY = 0.90       # 90 % energie
DT_MINUTES = 1.0      # dataset je po 1 minúte

MIN_INTERVAL = 1.0    # najkratší interval posielania [min]
MAX_INTERVAL = 60.0   # najdlhší interval posielania [min]
SAFETY = 0.8          # bezpečnostný faktor voči Nyquistovi

NIGHT_POWER_THRESHOLD = 0.05  # kW, pod tým berieme signál ako noc / nezaujímavý stav


def compute_fft_features(series, window=256, step=256, p_energy=0.90):
    x = series.to_numpy(dtype=float)
    times = series.index

    hann = np.hanning(window)
    hann_power = np.sum(hann ** 2)

    # frekvencie v cykloch za minútu
    freqs = np.fft.rfftfreq(window, d=DT_MINUTES)

    results = []

    for start in range(0, len(x) - window + 1, step):
        segment = x[start:start + window]

        if not np.all(np.isfinite(segment)):
            continue

        mean_power = float(np.mean(segment))
        std_power = float(np.std(segment))

        # odčítanie priemeru je dôležité,
        # inak bude FFT dominovaná DC zložkou
        segment_centered = segment - mean_power
        segment_windowed = segment_centered * hann

        X = np.fft.rfft(segment_windowed)
        E = (np.abs(X) ** 2) / hann_power

        # DC zložku ignorujeme, lebo chceme dynamiku zmeny
        E[0] = 0.0

        E_total = float(np.sum(E))

        if mean_power < NIGHT_POWER_THRESHOLD or E_total <= 1e-12:
            k90_bins = 0
            k90_ratio = 0.0
            f90 = 0.0
            spectral_entropy = 0.0
            recommended_interval = MAX_INTERVAL

        else:
            # 1. Energetická kompaktnosť: koľko najväčších zložiek stačí na 90 %
            E_sorted = np.sort(E)[::-1]
            cumulative_sorted = np.cumsum(E_sorted) / E_total

            k90_bins = int(np.searchsorted(cumulative_sorted, p_energy) + 1)
            k90_ratio = k90_bins / len(E)

            # 2. Energetická šírka pásma: do akej frekvencie leží 90 % energie
            cumulative_by_freq = np.cumsum(E) / E_total
            idx90 = int(np.searchsorted(cumulative_by_freq, p_energy))
            f90 = float(freqs[idx90])

            # 3. Spektrálna entropia
            p = E / E_total
            p_nonzero = p[p > 0]
            spectral_entropy = float(
                -np.sum(p_nonzero * np.log2(p_nonzero)) / np.log2(len(E))
            )

            # 4. Odporúčaný interval podľa Nyquistovej logiky
            if f90 <= 0:
                recommended_interval = MAX_INTERVAL
            else:
                recommended_interval = SAFETY / (2 * f90)
                recommended_interval = float(
                    np.clip(recommended_interval, MIN_INTERVAL, MAX_INTERVAL)
                )

        results.append({
            "start_time": times[start],
            "end_time": times[start + window - 1],
            "mean_power_kw": mean_power,
            "std_power_kw": std_power,
            "total_dynamic_energy": E_total,
            "k90_bins": k90_bins,
            "k90_ratio": k90_ratio,
            "f90_cycles_per_min": f90,
            "period90_min": 1 / f90 if f90 > 0 else np.inf,
            "spectral_entropy": spectral_entropy,
            "recommended_interval_min": recommended_interval,
        })

    return pd.DataFrame(results)


# ==========================
# Main
# ==========================

df = pd.read_hdf(FILE, key=KEY)

print(df.shape)
print(df.columns)

signal = df[SIGNAL_COL].dropna()

features = compute_fft_features(
    signal,
    window=WINDOW,
    step=STEP,
    p_energy=P_ENERGY
)

features.to_csv("adaptive_fft_baseline_results.csv", index=False)

print(features.head())
print(features["recommended_interval_min"].describe())

# Graf odporúčaného intervalu
plt.figure(figsize=(12, 5))
plt.plot(features["start_time"], features["recommended_interval_min"])
plt.xlabel("Time")
plt.ylabel("Recommended sending interval [min]")
plt.title("Adaptive FFT-based sending interval")
plt.grid(True)
plt.tight_layout()
plt.savefig("adaptive_interval.png", dpi=300)
plt.show()

# Histogram intervalov
plt.figure(figsize=(8, 5))
plt.hist(features["recommended_interval_min"], bins=30)
plt.xlabel("Recommended interval [min]")
plt.ylabel("Number of windows")
plt.title("Histogram of adaptive sending intervals")
plt.grid(True)
plt.tight_layout()
plt.savefig("adaptive_interval_histogram.png", dpi=300)
plt.show()