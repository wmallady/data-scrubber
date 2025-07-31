import os
import re
import pandas as pd
import uuid
from datetime import datetime, timezone, timedelta

# Validation functions
def is_valid_guid(guid):
    try:
        uuid.UUID(str(guid))
        return True
    except ValueError:
        return False

def transform_phone_number(phone_number):
    # Remove spaces, parentheses, and dashes
    phone_number = "".join(re.findall(r'\d+', phone_number))
    
    # Remove the first digit if it's '1'
    if phone_number.startswith('1'):
        phone_number = phone_number[1:]
    
    #Optionally remove trailing zero, which sometimes pops up on phones due to formatting artifacts
    #phone_number=phone_number[:-1] 
    
    return phone_number


def convert_date_format(date_str):
    try:
        date_str = date_str.split(" ")[0]  # Remove trailing time
        try:
            # Check for YYYYMMDD format
            if len(date_str) == 8 and date_str.isdigit():
                date_obj = datetime.strptime(date_str, '%Y%m%d')
            else:
                # Try MM/DD/YYYY first
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')
        except ValueError:
            # Try MM/DD/YY if MM/DD/YYYY fails
            date_obj = datetime.strptime(date_str, '%m/%d/%y')
            # If year is in the future, assume 1900s
            if date_obj.year > datetime.now().year:
                date_obj = date_obj.replace(year=date_obj.year - 100)
        utc_offset = timezone(timedelta(hours=0))
        date_obj_utc = date_obj.replace(tzinfo=utc_offset)
        return date_obj_utc.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return f"Invalid date format: Original String {date_str}"

def clean_headers(df):
    """Clean DataFrame headers by removing whitespace and special characters"""
    df.columns = [col.strip() for col in df.columns]
    return df

# Main processing function
def clean_and_process_csv(input_file, output_file, insert_group_number, group_name):
    # Read input CSV file into DataFrame with optional dtypes
    try:
        # Try reading with Medicaid Number column specification
        df = pd.read_csv(input_file, dtype={'Medicaid Number': str})
    except:
        # If that fails, read without specifying dtype
        df = pd.read_csv(input_file)
    
    # Clean headers
    df = clean_headers(df)

    # Initialize new columns
    df["InsertGroup"] = ""
    df["GroupName"] = ""

    # Check if Person_id column exists
    has_person_id = 'Person_id' in df.columns
    
    # Only validate GUIDs if Person_id exists
    if has_person_id:
        df['Person_id'] = df['Person_id'].astype(str)
        df['is_valid_guid'] = df['Person_id'].apply(is_valid_guid)
        
        valid_df = df[df['is_valid_guid']].copy()
        invalid_df = df[~df['is_valid_guid']]
        
        # Log invalid GUIDs if found
        if not invalid_df.empty:
            invalid_data_log = f'{group_name}-invalid-data-{datetime.now().strftime("%Y-%m-%d")}.csv'
            print(f"Invalid GUIDs found in rows. Logging to {invalid_data_log}.")
            invalid_df.to_csv(invalid_data_log, index=False)
    else:
        valid_df = df.copy()
        print("Note: No Person_id column found, skipping GUID validation.")

    # Apply transformations for columns that exist
    if 'Phone' in valid_df.columns:
        valid_df.loc[:, 'Phone'] = valid_df['Phone'].astype(str).apply(transform_phone_number)
    
    if 'Date of Birth' in valid_df.columns:
        valid_df.loc[:, 'Date of Birth'] = valid_df['Date of Birth'].astype(str).apply(convert_date_format)
    
    if 'First Name' in valid_df.columns:
        valid_df.loc[:, 'First Name'] = valid_df['First Name'].replace(r"^ +| +$", r"", regex=True)

    # Add InsertGroup # and GroupName from user input
    valid_df.loc[:, 'InsertGroup'] = insert_group_number
    valid_df.loc[:, 'GroupName'] = group_name

    # Create a column mapping dictionary
    column_mapping = {}
    
    # Add mappings only for columns that exist
    if 'Medicaid Number' in valid_df.columns:
        column_mapping['Medicaid Number'] = 'mem_nbr'
    if 'Last Name' in valid_df.columns:
        column_mapping['Last Name'] = 'last'
    if 'First Name' in valid_df.columns:
        column_mapping['First Name'] = 'first'
    if 'Person_id' in valid_df.columns:
        column_mapping['Person_id'] = 'person_id'
    if 'Phone' in valid_df.columns:
        column_mapping['Phone'] = 'cell_phone'
    if 'Date of Birth' in valid_df.columns:
        column_mapping['Date of Birth'] = 'DOB'

    # Rename only columns that exist in the mapping
    valid_df = valid_df.rename(columns=column_mapping)

    # Prepare list of columns for final output
    final_columns = []
    for col in ['first', 'last', 'DOB', 'cell_phone', 'InsertGroup', 'GroupName']:
        if col in valid_df.columns:
            final_columns.append(col)
    
    # Add optional columns if they exist
    if 'mem_nbr' in valid_df.columns:
        final_columns.append('mem_nbr')
    if 'person_id' in valid_df.columns:
        final_columns.append('person_id')

    # Reorder columns, but only include those that exist
    valid_df = valid_df[final_columns]

    # Write cleaned data to output file
    valid_df.to_csv(output_file, index=False)
    print(f"CSV file processed and written to '{output_file}'.")
    print(f"Columns in output: {', '.join(final_columns)}")

# Interactive user interface
def interactive_mode():
    print("Thank you for using DataScrubber ;>")
    print("Make sure your column names match these exactly: Last Name, First Name, Phone, DOB, Person_id")
    
 
    
    # Original single file processing code
    while True:
        input_file = input("Please enter the full path of your input CSV file: ").strip()
        if os.path.isfile(input_file) and input_file.lower().endswith('.csv'):
            print(f"File '{input_file}' found and is a valid CSV.")
            break
        else:
            print("Invalid file. Please ensure the file exists and has a '.csv' extension.")

    # Take Insert Group Number input and validate it
    while True:
        try:
            insert_group_number = int(input("Please enter the Insert Group Number (must be a number): "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number for the Insert Group Number.")

    # Take Group Name input
    group_name = input("Please enter the Group Name: ")

    # Define output file dynamically based on the Group Name input
    output_file = f"{group_name}.csv"

    # Process the CSV with the provided inputs
    clean_and_process_csv(input_file, output_file, insert_group_number, group_name)

# Run interactive mode
if __name__ == "__main__":
    interactive_mode()
