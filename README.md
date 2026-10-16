# Python CSV Data Cleaning Automation

A Python command-line tool that validates customer data, identifies duplicate records, cleans text fields, and generates reports.

## Features

- Reads customer records from a CSV file.
- Validates required fields and email formats.
- Checks amounts for numeric values and negative numbers.
- Removes exact duplicate records after basic normalization.
- Saves valid and invalid records separately.
- Reports processed, valid, invalid, and duplicate counts.
- Handles missing input files and required columns.
- Includes automated unit tests.
- Detects customer IDs associated with different record details.
- Generates a separate customer_id_conflicts.csv report.
- Excludes conflicting customer records from the cleaned output.
- Includes conflict counts in the summary.

## Project Structure

```text
PythonAutomationDemo/
├── data/
│   └── customers.csv
├── output/
│   ├── cleaned_customers.csv
│   ├── invalid_customers.csv
│   └── summary.txt
├── main.py
├── test_main.py
└── README.md
```

## Requirements

- Python 3.10 or later
- No third-party packages required

## Run the Program

From the project directory:

```bash
python main.py
```

Specify a different input file or output directory:

```bash
python main.py --input data/customers.csv --output output
```

## Run Tests

```bash
python -m unittest -v test_main.py
```

## Output Files

- `cleaned_customers.csv`: records that passed validation.
- `invalid_customers.csv`: invalid records and their validation issues.
- `summary.txt`: counts for processed, valid, invalid, and duplicate records.
- `customer_id_conflicts.csv`: all distinct records associated with conflicting, non-empty customer IDs.

## Limitations

- The current version supports CSV input only.
- Email validation uses a basic format check, not verification that an address exists.
- Duplicate detection checks normalized record contents, not customer identity.
- The tool has been tested with sample data; larger real-world datasets require additional testing.

## Future Improvements

- Excel file support.
- Configurable validation rules.
- More edge-case tests and larger datasets.
- Structured logging and improved reporting.

## Project Status

Portfolio demo — tested with sample data. Not yet validated for production use.