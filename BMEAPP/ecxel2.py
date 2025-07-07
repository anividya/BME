import pandas as pd

# Load the Excel file
file_path = r"D:\Hospinorm-DIC\DIC_Assets_16_04_25.xlsx"
df = pd.read_excel(file_path, sheet_name='Sheet4')

# Drop duplicates based on 'Manufacturer' and 'Model'
unique_combinations = df.drop_duplicates(subset=['Manufacturer', 'Model'])

# Optional: Reset index
unique_combinations.reset_index(drop=True, inplace=True)

# Save to a new Excel file
output_path = r"D:\Hospinorm-DIC\Unique_Manufacturer_Model.xlsx"
unique_combinations.to_excel(output_path, index=False)

print("Done! File saved:", output_path)
