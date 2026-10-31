
import os
import pandas as pd
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt

# Project paths
PROJECT_DIR = r"C:\Hadoop\web-log-project"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

INPUT_FILE = os.path.join(OUTPUT_DIR, "ml_features.csv")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "anomaly_results.csv")
PLOT_FILE = os.path.join(OUTPUT_DIR, "anomaly_detection.png")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load feature dataset
df = pd.read_csv(INPUT_FILE)

# Features used by the model
feature_columns = [
    "Total_Requests",
    "HTTP_403_Count",
    "HTTP_404_Count",
    "HTTP_500_Count",
    "HTTP_501_Count",
    "Total_Errors",
    "Error_Rate"
]

X = df[feature_columns].fillna(0)

# Build the Isolation Forest model
model = IsolationForest(
    n_estimators=100,
    contamination=0.01,
    random_state=42
)

# Predict normal and unusual patterns
df["Anomaly_Prediction"] = model.fit_predict(X)

# Convert predictions to readable labels
df["Anomaly_Status"] = df["Anomaly_Prediction"].map({
    1: "Normal",
    -1: "Potential Anomaly"
})

# Calculate anomaly scores
df["Anomaly_Score"] = model.decision_function(X)

# Save results, with potential anomalies first
df = df.sort_values(
    by="Anomaly_Score",
    ascending=True
)

df.to_csv(OUTPUT_FILE, index=False)

# Print summary
anomaly_count = (df["Anomaly_Status"] == "Potential Anomaly").sum()
normal_count = (df["Anomaly_Status"] == "Normal").sum()

print("\nWEB LOG ANOMALY DETECTION RESULTS")
print("=" * 65)
print(f"Total clients analyzed: {len(df):,}")
print(f"Normal clients: {normal_count:,}")
print(f"Potential anomalies: {anomaly_count:,}")

print("\nTop 20 potential anomalies:")
print(
    df[df["Anomaly_Status"] == "Potential Anomaly"][
        [
            "Client",
            "Total_Requests",
            "Total_Errors",
            "Error_Rate",
            "Anomaly_Score"
        ]
    ].head(20).to_string(index=False)
)

# Plot request counts for normal clients and potential anomalies
plt.figure(figsize=(10, 6))

for status, group in df.groupby("Anomaly_Status"):
    plt.scatter(
        group["Total_Requests"],
        group["Total_Errors"],
        label=status,
        alpha=0.6,
        s=20
    )

plt.xlabel("Total Requests")
plt.ylabel("Total Selected HTTP Errors")
plt.title("Web Log Anomaly Detection Using Isolation Forest")
plt.legend()
plt.tight_layout()
plt.savefig(PLOT_FILE, dpi=300)
plt.close()

print(f"\nResults saved to: {OUTPUT_FILE}")
print(f"Visualization saved to: {PLOT_FILE}")
print("\nAnomaly detection completed successfully.")
print("Note: Potential anomalies require further investigation.")

