import pandas as pd

# Load the JSON file
with open("./training.json", "r") as f:
    data = pd.read_json(f)

# Convert to CSV
data.to_csv("training.csv", index=False)
