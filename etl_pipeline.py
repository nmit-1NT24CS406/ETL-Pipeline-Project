
import requests
import pandas as pd
from pathlib import Path


API_URL = "https://jsonplaceholder.typicode.com/users"

OUTPUT_FILE = Path("data/users_cleaned.csv")


# 1. EXTRACT
def extract_data(url=API_URL):
    response = requests.get(url, timeout=10)

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Expected a list of users")

    return data


# 2. TRANSFORM
def transform_data(data):
    # Convert list of dictionaries into DataFrame
    df = pd.DataFrame(data)

    # Select required columns
    columns = [
        "id",
        "name",
        "username",
        "email",
        "address",
        "company"
    ]

    available_columns = [
        column
        for column in columns
        if column in df.columns
    ]

    cleaned_df = df[available_columns].copy()

    # Extract city from address
    if "address" in cleaned_df.columns:

        cleaned_df["city"] = cleaned_df["address"].apply(
            lambda address: (
                address.get("city", "")
                if isinstance(address, dict)
                else ""
            )
        )

        cleaned_df = cleaned_df.drop(
            columns=["address"]
        )

    # Extract company name
    if "company" in cleaned_df.columns:

        cleaned_df["company"] = cleaned_df["company"].apply(
            lambda company: (
                company.get("name", "")
                if isinstance(company, dict)
                else ""
            )
        )

    # Clean text columns
    text_columns = [
        "name",
        "username",
        "email",
        "city",
        "company"
    ]

    for column in text_columns:

        if column in cleaned_df.columns:

            cleaned_df[column] = (
                cleaned_df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # Convert emails to lowercase
    if "email" in cleaned_df.columns:

        cleaned_df["email"] = (
            cleaned_df["email"].str.lower()
        )

    # Remove rows without ID
    if "id" in cleaned_df.columns:

        cleaned_df = cleaned_df.dropna(
            subset=["id"]
        )

        # Remove duplicate IDs
        cleaned_df = cleaned_df.drop_duplicates(
            subset=["id"]
        )

    return cleaned_df


# 3. LOAD
def load_data(df, output_file=OUTPUT_FILE):

    # Create the data folder if it does not exist
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save cleaned data as CSV
    df.to_csv(
        output_file,
        index=False
    )

    return output_file


# 4. RUN COMPLETE ETL PIPELINE
def run_pipeline():

    # Extract data
    extracted_data = extract_data()

    # Transform data
    transformed_data = transform_data(
        extracted_data
    )

    # Load data
    output_file = load_data(
        transformed_data
    )

    return output_file


# 5. EXECUTE PROGRAM
if __name__ == "__main__":

    try:

        output_file = run_pipeline()

        print(
            "ETL Pipeline executed successfully!"
        )

        print(
            f"Cleaned data saved to: {output_file}"
        )

    except Exception as error:

        print(
            f"ETL Pipeline failed: {error}"
        )