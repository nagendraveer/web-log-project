import os
import pandas as pd

# Project paths

PROJECT_DIR = r"C:\Hadoop\web-log-project"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

CLIENT_FILE = os.path.join(PROJECT_DIR, "client_requests.txt")
ERROR_FILE = os.path.join(PROJECT_DIR, "http_errors.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------

# 1. Load total request counts from Hadoop

# --------------------------------------------------

clients = pd.read_csv(
CLIENT_FILE,
sep=r"\s+",
header=None,
names=["Client", "Total_Requests"],
engine="python"
)

clients["Total_Requests"] = pd.to_numeric(
clients["Total_Requests"], errors="coerce"
)
clients = clients.dropna(subset=["Client", "Total_Requests"])

# --------------------------------------------------

# 2. Load HTTP error counts from Hadoop

# Hadoop key format: Client<TAB>StatusCode

# Final column: Count

# --------------------------------------------------

errors = pd.read_csv(
ERROR_FILE,
sep=r"\s+",
header=None,
names=["Client", "StatusCode", "Count"],
engine="python"
)

errors["StatusCode"] = pd.to_numeric(
errors["StatusCode"], errors="coerce"
)
errors["Count"] = pd.to_numeric(
errors["Count"], errors="coerce"
)
errors = errors.dropna(subset=["Client", "StatusCode", "Count"])

# --------------------------------------------------

# 3. Convert error status codes into separate columns

# --------------------------------------------------

error_pivot = errors.pivot_table(
index="Client",
columns="StatusCode",
values="Count",
aggfunc="sum",
fill_value=0
)

# Ensure all expected status code columns exist


for code in [403, 404, 500, 501]:
    if code not in error_pivot.columns:
        error_pivot[code] = 0

error_pivot = error_pivot[[403, 404, 500, 501]]

error_pivot.columns = [
    "HTTP_403_Count",
    "HTTP_404_Count",
    "HTTP_500_Count",
    "HTTP_501_Count"
]

error_pivot = error_pivot.reset_index()


# --------------------------------------------------

# 4. Merge total requests with error counts

# --------------------------------------------------

features = clients.merge(
error_pivot,
on="Client",
how="left"
)

error_columns = [
"HTTP_403_Count",
"HTTP_404_Count",
"HTTP_500_Count",
"HTTP_501_Count"
]

features[error_columns] = features[error_columns].fillna(0).astype(int)

# --------------------------------------------------

# 5. Calculate total errors and error rate

# --------------------------------------------------

features["Total_Errors"] = features[error_columns].sum(axis=1)

features["Error_Rate"] = (
features["Total_Errors"] / features["Total_Requests"] * 100
).fillna(0)

# Sort clients by request volume

features = features.sort_values(
by="Total_Requests",
ascending=False
)

# --------------------------------------------------

# 6. Save the machine learning dataset

# --------------------------------------------------

output_file = os.path.join(
OUTPUT_DIR,
"ml_features.csv"
)

features.to_csv(output_file, index=False)

# --------------------------------------------------

# 7. Display a summary

# --------------------------------------------------

print("\nMACHINE LEARNING FEATURE ENGINEERING")
print("=" * 65)

print(f"Total clients: {len(features):,}")
print(f"Total requests: {features['Total_Requests'].sum():,}")
print(f"Total selected HTTP errors: {features['Total_Errors'].sum():,}")

print("\nTop 10 clients by total requests:")
print(
features[
["Client", "Total_Requests", "Total_Errors", "Error_Rate"]
].head(10).to_string(index=False)
)

print(f"\nDataset saved to: {output_file}")
print(f"Number of features: {len(features.columns)}")
print("\nFeature engineering completed successfully.")
