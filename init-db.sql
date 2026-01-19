-- Create airflow database for Airflow
CREATE DATABASE airflow;

-- Grant all privileges to postgres user (already the owner, but explicitly setting)
GRANT ALL PRIVILEGES ON DATABASE airflow TO kknaks;
