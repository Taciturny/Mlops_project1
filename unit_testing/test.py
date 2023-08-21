import pytest
import psycopg
from monitoring.evidently_metrics import prep_db, calculate_metrics_postgresql
import sys
import os



# Add the path to your project directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


# Define a fixture to mock the PostgreSQL connection
@pytest.fixture
def test_mock_postgresql_connection(mocker):
    # Mock the psycopg.connect method
    mocker.patch('psycopg.connect')
    return psycopg.connect()

# Test the prep_db function
def test_prep_db(mock_postgresql_connection):
    # Call the prep_db function
    prep_db()

    # Ensure psycopg.connect is called with the correct arguments
    psycopg.connect.assert_called_once_with(
        "host=localhost port=5432 user=postgres password=example", autocommit=True
    )

# Test the calculate_metrics_postgresql function
def test_calculate_metrics_postgresql(mock_postgresql_connection):
    # You need to mock the report.run method to avoid actual execution
    mocker = pytest.importorskip('pytest_mock')
    mock_report_run = mocker.patch('your_script.report.run')

    # Create a mock result for report.run
    mock_report_result = {
        'metrics': [
            {'result': {'drift_score': 0.2}},
            {'result': {'number_of_drifted_columns': 3}},
            {'result': {'current': {'share_of_missing_values': 0.1}}}
        ]
    }
    mock_report_run.return_value = mock_report_result

    # Call the calculate_metrics_postgresql function
    calculate_metrics_postgresql(test_mock_postgresql_connection, 0)

    # Ensure that report.run was called with the correct arguments
    mock_report_run.assert_called_once_with(
        reference_data=pytest.any(),
        current_data=pytest.any(),
        column_mapping=pytest.any()
    )

    # Assert that the function returns the expected values based on the mock result
    expected_prediction_drift = 0.2
    expected_num_drifted_columns = 3
    expected_share_missing_values = 0.1

    # Replace with actual function call and return values
    result = calculate_metrics_postgresql(mock_postgresql_connection, 0)
    assert result == (expected_prediction_drift, expected_num_drifted_columns, expected_share_missing_values)


if __name__ == '__main__':
    pytest.main()




# import pytest
# from unittest.mock import MagicMock
# from Monitoring.evidently_metrics import prep_db, calculate_metrics_postgresql
# import sys
# import os

# # Get the absolute path to the 'Monitoring' directory
# monitoring_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Monitoring'))
# print(monitoring_dir)

# # Add the 'Monitoring' directory to the Python path
# sys.path.append(monitoring_dir)

# # Mock the database connection
# def mock_db_connection():
#     with psycopg.connect() as conn:
#         yield conn

# # Mock the report and report.run() method
# def mock_report():
#     mock_report = MagicMock()
#     mock_report.as_dict.return_value = {
#         'metrics': [
#             {'result': {'drift_score': 0.1}},
#             {'result': {'number_of_drifted_columns': 2}},
#             {'result': {'current': {'share_of_missing_values': 0.05}}}
#         ]
#     }
#     return mock_report

# def test_prep_db(mock_db_connection):
#     # Ensure that prep_db() creates the 'test' database
#     prep_db()
#     cursor = mock_db_connection.cursor()
#     cursor.execute("SELECT datname FROM pg_database WHERE datname='test'")
#     result = cursor.fetchone()
#     assert result is not None

# def test_calculate_metrics_postgresql(mock_db_connection, mock_report):
#     # Mock the cursor
#     mock_cursor = MagicMock()
#     mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor

#     # Call calculate_metrics_postgresql() with the mocked parameters
#     calculate_metrics_postgresql(mock_cursor, 1)

#     # Verify that the SQL statement was executed with the expected arguments
#     mock_cursor.execute.assert_called_once_with(
#         "insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
#         (pytest.approx(1), pytest.approx(0.1), 2, pytest.approx(0.05))
#     )

# # You can add more test cases as needed

# if __name__ == '__main__':
#     pytest.main()
