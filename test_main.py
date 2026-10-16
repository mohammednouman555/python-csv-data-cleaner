import csv
import tempfile
import unittest
from pathlib import Path

from main import process_file


class TestProcessFile(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.input_file = self.base / "customers.csv"
        self.output_dir = self.base / "output"

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_csv(self, headers, rows):
        with self.input_file.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

    def test_valid_and_invalid_records(self):
        headers = ["customer_id", "name", "email", "amount"]
        rows = [
            ["101", "Ayesha", "ayesha@example.com", "250"],
            ["102", "", "bad-email", "abc"],
        ]
        self.write_csv(headers, rows)

        result = process_file(self.input_file, self.output_dir)

        self.assertEqual(result["processed"], 2)
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["invalid"], 1)
        self.assertEqual(result["duplicates"], 0)

    def test_duplicate_record(self):
        headers = ["customer_id", "name", "email", "amount"]
        row = ["101", "Ayesha", "ayesha@example.com", "250"]
        self.write_csv(headers, [row, row])

        result = process_file(self.input_file, self.output_dir)

        self.assertEqual(result["processed"], 2)
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["duplicates"], 1)

    def test_missing_required_column(self):
        self.write_csv(
            ["customer_id", "name", "email"],
            [["101", "Ayesha", "ayesha@example.com"]],
        )

        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            process_file(self.input_file, self.output_dir)

    def test_missing_input_file(self):
        with self.assertRaisesRegex(FileNotFoundError, "Input file not found"):
            process_file(self.base / "missing.csv", self.output_dir)

    def test_conflicting_customer_ids(self):
        headers = ["customer_id", "name", "email", "amount"]
        rows = [
            ["101", "Ayesha", "ayesha@example.com", "250"],
            ["101", "Ayesha Khan", "ayesha.k@example.com", "300"],
            ["102", "Rahul", "rahul@example.com", "450"],
        ]
        self.write_csv(headers, rows)

        result = process_file(self.input_file, self.output_dir)

        self.assertEqual(result["conflicting_customer_ids"], 1)
        self.assertEqual(result["conflict_records"], 2)
        self.assertEqual(result["valid"], 1)

        with (self.output_dir / "customer_id_conflicts.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            conflicts = list(csv.DictReader(file))

        self.assertEqual(len(conflicts), 2)
        self.assertEqual(
            {record["customer_id"] for record in conflicts}, {"101"}
        )


if __name__ == "__main__":
    unittest.main()