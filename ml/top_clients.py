import os
import pandas as pd
import matplotlib.pyplot as plt

# Project paths

PROJECT_DIR = r"C:\Hadoop\web-log-project"
INPUT_FILE = os.path.join(PROJECT_DIR, "client_requests.txt")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load Hadoop MapReduce output

df = pd.read_csv(
INPUT_FILE,
sep=r"\s+",
header=None,
names=["Client", "Requests"],
engine="python"
)

# Ensure request counts are numeric

df["Requests"] = pd.to_numeric(df["Requests"], errors="coerce")
df = df.dropna(subset=["Requests"])

# Sort clients by request count

top_clients = df.sort_values(
by="Requests",
ascending=False
).head(20)

# Display results

print("\nTOP 20 MOST ACTIVE CLIENTS")
print("=" * 60)
print(top_clients.to_string(index=False))

# Save results to CSV

csv_path = os.path.join(OUTPUT_DIR, "top_20_clients.csv")
top_clients.to_csv(csv_path, index=False)

print(f"\nCSV saved to: {csv_path}")
print(f"Unique clients analyzed: {len(df):,}")

# Create bar chart

chart_data = top_clients.sort_values("Requests", ascending=True)

plt.figure(figsize=(12, 8))
plt.barh(chart_data["Client"], chart_data["Requests"])
plt.xlabel("Number of Requests")
plt.ylabel("Client")
plt.title("Top 20 Most Active Clients in NASA HTTP Logs")
plt.tight_layout()

chart_path = os.path.join(OUTPUT_DIR, "top_20_clients.png")
plt.savefig(chart_path, dpi=200, bbox_inches="tight")
plt.close()

print(f"Chart saved to: {chart_path}")
