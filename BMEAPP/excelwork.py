import pandas as pd

# Load your Excel file
df = pd.read_excel(r"C:\Users\hp\Downloads\MASTER_EQUIPMENT_LIST_CARITAS.xlsx")  # Replace with your actual file name

# Assume the CH codes are in a column named 'Code' (change as needed)
# Remove spaces from the 'Code' column
df['Code'] = df['Code'].str.replace(" ", "", regex=False)

# Save to a new Excel file
df.to_excel('cleaned_codes.xlsx', index=False)

print("CH codes cleaned and saved to 'cleaned_codes.xlsx'.")
