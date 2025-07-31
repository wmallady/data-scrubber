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

def convert_date_format(date_str):
    try:
        # Debugging: Print the input date string
        print(f"Processing date: {date_str}")
        
        # Remove trailing time if present
        date_str = date_str.split(" ")[0]
        
        # Check for YYYYMMDD format
        if len(date_str) == 8 and date_str.isdigit():
            date_obj = datetime.strptime(date_str, '%Y%m%d')
        else:
            try:
                # Try MM/DD/YYYY format
                date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            except ValueError:
                # Try MM/DD/YY format
                date_obj = datetime.strptime(date_str, '%m/%d/%y')
                # If year is in the future, assume 1900s
                if date_obj.year > datetime.now().year:
                    date_obj = date_obj.replace(year=date_obj.year - 100)
        
        # Convert to UTC and return formatted date
        utc_offset = timezone(timedelta(hours=0))
        date_obj_utc = date_obj.replace(tzinfo=utc_offset)
        return date_obj_utc.strftime('%Y-%m-%d')
    except (ValueError, TypeError) as e:
        # Debugging: Print the error and return None
        print(f"Error processing date '{date_str}': {e}")
        return None

def clean_headers(df):
    """Clean DataFrame headers by removing whitespace and special characters"""
    df.columns = [col.strip() for col in df.columns]
    return df

# Main processing function
def clean_and_process_csv(input_file, output_file, insert_group_number, group_name):
    # Read input CSV file into DataFrame
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Clean headers
    df = clean_headers(df)

    # Initialize new columns
    df["InsertGroup"] = insert_group_number
    df["GroupName"] = group_name

    # Apply transformations for columns that exist
    if 'Date of Birth' in df.columns:
        df['Date of Birth'] = df['Date of Birth'].astype(str).apply(convert_date_format)
    if 'person_id' in df.columns:
        df['person_id'] = df['person_id'].astype(str).apply(lambda x: x if is_valid_guid(x) else None)

    # Rename columns to match database schema
    column_mapping = {
        'First Name': 'first',
        'Last Name': 'last',
        'Email': 'Email',
        'Date of Birth': 'DOB',
        'Person_id': 'person_id'
    }
    df = df.rename(columns=column_mapping)

    # Prepare list of columns for final output
    final_columns = [
        'InsertGroup', 'GroupName', 'person_id', 'first', 'last', 'Email', 'DOB'
    ]
    # Ensure only columns that exist in the DataFrame are included
    final_columns = [col for col in final_columns if col in df.columns]

    # Reorder columns
    df = df[final_columns]

    if df['DOB'].apply(lambda x: bool(re.match(r'^\d{4}-\d{2}-\d{2}$', str(x)))).all():
        print("DOB column processed successfully.")
    else:
        print("DOB ERROR: Some dates could not be converted.")
        print("DOB column before processing:")
        print(df['DOB'].head())
        df['DOB'] = df['DOB'].astype(str).apply(convert_date_format)

    # Write cleaned data to output file
    df.to_csv(output_file, index=False)
    print(f"CSV file processed and written to '{output_file}'.")
    print(f"Columns in output: {', '.join(final_columns)}")

# Interactive user interface
def interactive_mode():
    print("Thank you for using DataScrubber for GH_Process_MassEmail!")
    print("Make sure your column names match these exactly: First Name, Last Name, Email, Date of Birth, person_id")
    
    while True:
        input_file = input("Please enter the full path of your input CSV file: ").strip()
        if os.path.isfile(input_file) and input_file.lower().endswith('.csv'):
            print(f"File '{input_file}' found and is a valid CSV.")
            break
        else:
            print("Invalid file. Please ensure the file exists and has a '.csv' extension.")

    while True:
        try:
            insert_group_number = int(input("Please enter the Insert Group Number (must be a number): "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number for the Insert Group Number.")

    group_name = input("Please enter the Group Name: ")

    output_file = f"{group_name}_mass_email.csv"

    clean_and_process_csv(input_file, output_file, insert_group_number, group_name)

# Run interactive mode
if __name__ == "__main__":
    interactive_mode()