import csv
import re
import argparse
from pathlib import Path
from decimal import Decimal, InvalidOperation
from collections import defaultdict


REQUIRED_COLUMNS = {"customer_id", "name", "email", "amount"}


def validate_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))


def process_file(input_path, output_dir):
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("The input CSV is empty or has no header.")

        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Missing required columns: {', '.join(sorted(missing))}"
            )

        columns = list(reader.fieldnames)
        rows = []
        seen_records = set()
        processed = 0
        duplicates = 0

        # Read and normalize the input before classifying records.
        for row in reader:
            if not row or all(
                value is None or not value.strip()
                for value in row.values()
            ):
                continue

            processed += 1
            record = {
                key: (value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            record["email"] = record["email"].lower()

            fingerprint = tuple(record.get(column, "") for column in columns)

            if fingerprint in seen_records:
                duplicates += 1
                continue

            seen_records.add(fingerprint)
            rows.append(record)

    # Find every non-empty customer ID associated with different details.
    records_by_id = defaultdict(list)
    for record in rows:
        customer_id = record["customer_id"]
        if customer_id:
            records_by_id[customer_id].append(record)

    conflict_ids = {
        customer_id
        for customer_id, records in records_by_id.items()
        if len({tuple(r.get(c, "") for c in columns if c != "customer_id")
                for r in records}) > 1
    }

    valid_records = []
    invalid_records = []
    conflict_records = []

    for record in rows:
        issues = []

        if not record["customer_id"]:
            issues.append("Missing customer ID")
        if not record["name"]:
            issues.append("Missing name")
        if not validate_email(record["email"]):
            issues.append("Invalid email")

        try:
            amount = Decimal(record["amount"])
            if not amount.is_finite():
                issues.append("Amount must be a finite number")
            elif amount < 0:
                issues.append("Amount cannot be negative")
            else:
                record["amount"] = str(amount)
        except InvalidOperation:
            issues.append("Amount must be numeric")

        if record["customer_id"] in conflict_ids:
            conflict_records.append(record.copy())

        if issues:
            invalid_record = record.copy()
            invalid_record["issues"] = "; ".join(issues)
            invalid_records.append(invalid_record)
        elif record["customer_id"] not in conflict_ids:
            valid_records.append(record.copy())

    def write_csv(path, records, fieldnames):
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

    write_csv(output_dir / "cleaned_customers.csv", valid_records, columns)
    write_csv(
        output_dir / "invalid_customers.csv",
        invalid_records,
        columns + ["issues"],
    )
    write_csv(
        output_dir / "customer_id_conflicts.csv",
        conflict_records,
        columns,
    )

    summary = {
        "processed": processed,
        "valid": len(valid_records),
        "invalid": len(invalid_records),
        "duplicates": duplicates,
        "conflict_records": len(conflict_records),
        "conflicting_customer_ids": len(conflict_ids),
    }

    with (output_dir / "summary.txt").open("w", encoding="utf-8") as file:
        for label, count in summary.items():
            file.write(f"{label.replace('_', ' ').capitalize()}: {count}\n")

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Validate and clean customer CSV data."
    )
    parser.add_argument("--input", default="data/customers.csv")
    parser.add_argument("--output", default="output")
    args = parser.parse_args()

    try:
        summary = process_file(args.input, args.output)
        print("Processing completed successfully.")
        for label, count in summary.items():
            print(f"{label.replace('_', ' ').capitalize()}: {count}")
    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
