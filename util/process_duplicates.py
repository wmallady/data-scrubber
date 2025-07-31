import pandas as pd


#### THIS SCRIPT IDENTIFIES AND REPORTS ON DUPLICATE PHONE NUMBERS IN A CSV FILE ####

def process_phone_numbers(input_file):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Create a copy of the DataFrame with phone number duplicates
    phone_duplicates = df[df.duplicated(subset=['Phone'], keep=False)]
    
    # Create a DataFrame with unique phone numbers (not duplicated)
    unique_phones = df[~df.duplicated(subset=['Phone'], keep=False)]
    
    # Create a DataFrame for rows without Medicaid numbers
    no_medicaid = df[df['Medicaid Number'].isna() | (df['Medicaid Number'] == '')]
    
    # Remove rows without Medicaid numbers from unique_phones
    unique_phones = unique_phones[~unique_phones.index.isin(no_medicaid.index)]
    
    # Write the results to separate CSV files
    phone_duplicates.to_csv('duplicates.csv', index=False)
    no_medicaid.to_csv('noNumber.csv', index=False)
    unique_phones.to_csv('unique_phones.csv', index=False)
    
    # Print summary statistics
    print(f"Total records processed: {len(df)}")
    print(f"Records with duplicate phone numbers: {len(phone_duplicates)}")
    print(f"Records with missing Medicaid numbers: {len(no_medicaid)}")
    print(f"Records with unique phone numbers: {len(unique_phones)}")

if __name__ == "__main__":
    # Replace with your input file name
    input_file = "old.csv"
    process_phone_numbers(input_file)