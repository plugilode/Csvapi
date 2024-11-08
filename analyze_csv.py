import pandas as pd

# Read the CSV file
df = pd.read_csv('ricarda.ricarda.csv')

# Display information about the DataFrame
print("\nDataFrame Info:")
print("==============")
df.info()

print("\nColumn Names:")
print("============")
print(df.columns.tolist())

print("\nFirst Few Rows:")
print("==============")
print(df.head())

print("\nSummary Statistics:")
print("==================")
print(df.describe())
