import pandas as pd
import json

input_filepath = "data.xlsx"

# Read without specifying a header
df = pd.read_excel(input_filepath, header=None)

# Drop completely empty rows
df = df.dropna(how='all')

# Find first row that looks like headers (non-NaN values)
header_row_index = df.first_valid_index()

# Set that row as header
df.columns = df.iloc[header_row_index]
df = df.drop(index=header_row_index)

# Drop completely empty columns (optional, to clean)
df = df.dropna(axis=1, how='all')

# Reset index (optional for clean dataframe)
df = df.reset_index(drop=True)

# Now convert to list of dicts
table_data = df.to_dict(orient="records")

# JSON output
table_data_json = json.dumps(table_data, indent=2)

# Output
print("✅ Extracted Table Data:")
print(table_data)

print("\n✅ JSON Output:")
print(table_data_json)
