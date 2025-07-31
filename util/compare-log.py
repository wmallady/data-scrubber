import pandas as pd

### THIS SCRIPT COMPARES TWO CSV FILES AND ADDS A COLUMN TO THE FIRST BASED ON THE SECOND
### THE FIRST CSV IS THE WOMENS HEALTH LIST, THE SECOND IS THE TWILIO LOG
### THE NEW COLUMN IS f_sent, WHICH IS 1 IF THE STATUS IN THE TWILIO LOG IS 'delivered' OR 'sent', ELSE 0
### THE MATCHING IS DONE ON PHONE NUMBER, NORMALIZED TO STRIP +1, SPACES, DASHES, ETC.

# Load both CSVs
df1 = pd.read_csv('log1.csv')
df2 = pd.read_csv('log2.csv')

# Normalize phone numbers for matching (remove + and spaces)
""" def normalize(phone):
    digits = ''.join(filter(str.isdigit, str(phone)))
    # Remove leading '1' if it's an 11-digit US number
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    return digits

df1['recipients'] = df1['cell_phone'].apply(normalize)
df2['recipients'] = df2['To'].apply(normalize)
 """
# Create a mapping from phone to status in df2
status_map = dict(zip(df2['Recipients'], df2['Status']))

# Function to determine f_sent value
def get_f_sent(row):
    status = status_map.get(row['To_norm'], None)
    if status is not None and status.lower() in ['delivered', 'sent']:
        return 1
    else:
        return 0

# Apply the function to create the new column
df1['f_sent'] = df1.apply(get_f_sent, axis=1)

# Drop the normalization helper column
df1 = df1.drop(columns=['To_norm'])

# Save to new CSV
df1.to_csv('result.csv', index=False)
print("Done! Output written to result.csv")