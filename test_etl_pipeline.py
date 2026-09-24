
import pandas as pd
import pytest
import requests

from etl_pipeline import (
    extract_data,
    transform_data,
    load_data
)


# ==========================================
# TEST 1: EXTRACT DATA
# ==========================================

def test_extract_data(monkeypatch):

    class MockResponse:

        def raise_for_status(self):
            pass

        def json(self):

            return [
                {
                    "id": 1,
                    "name": "John"
                }
            ]

    def mock_get(url, timeout):

        return MockResponse()

    monkeypatch.setattr(
        requests,
        "get",
        mock_get
    )

    result = extract_data(
        "https://example.com/users"
    )

    assert isinstance(result, list)

    assert len(result) == 1

    assert result[0]["id"] == 1


# ==========================================
# TEST 2: TRANSFORM DATA
# ==========================================

def test_transform_data():

    sample_data = [

        {
            "id": 1,
            "name": " John Doe ",
            "username": " John123 ",
            "email": " JOHN@EMAIL.COM ",

            "address": {
                "city": " Bangalore "
            },

            "company": {
                "name": " ABC Company "
            }
        }

    ]

    df = transform_data(
        sample_data
    )

    assert isinstance(
        df,
        pd.DataFrame
    )

    assert df.loc[0, "name"] == "John Doe"

    assert df.loc[0, "username"] == "John123"

    assert df.loc[0, "email"] == "john@email.com"

    assert df.loc[0, "city"] == "Bangalore"

    assert df.loc[0, "company"] == "ABC Company"


# ==========================================
# TEST 3: DUPLICATE REMOVAL
# ==========================================

def test_duplicate_removal():

    sample_record = {

        "id": 1,
        "name": "John",
        "username": "john123",
        "email": "john@email.com",

        "address": {
            "city": "Bangalore"
        },

        "company": {
            "name": "ABC"
        }

    }

    df = transform_data(
        [
            sample_record,
            sample_record.copy()
        ]
    )

    assert len(df) == 1


# ==========================================
# TEST 4: CSV CREATION
# ==========================================

def test_load_data(tmp_path):

    data = {

        "id": [1],
        "name": ["John"],
        "username": ["john123"],
        "email": ["john@email.com"],
        "city": ["Bangalore"],
        "company": ["ABC"]

    }

    df = pd.DataFrame(data)

    output_file = (
        tmp_path / "test_users.csv"
    )

    returned_path = load_data(
        df,
        output_file
    )

    assert returned_path == output_file

    assert output_file.exists()

    saved_df = pd.read_csv(
        output_file
    )

    assert len(saved_df) == 1

    assert saved_df.loc[0, "name"] == "John"


# ==========================================
# TEST 5: API ERROR HANDLING
# ==========================================

def test_extract_data_http_error(
    monkeypatch
):

    def mock_get(url, timeout):

        response = requests.Response()

        response.status_code = 500

        response.url = url

        return response

    monkeypatch.setattr(
        requests,
        "get",
        mock_get
    )

    with pytest.raises(
        requests.HTTPError
    ):

        extract_data(
            "https://example.com/users"
        )