#!/usr/bin/env python3
import argparse
import csv
import os
import sys
import time

def query_csv_file(csv_path, base_dir, query_pairs, days=None):
    """
    Queries a CSV file for rows matching all specified criteria and prints the
    full path for the 'Filename' column of each match.

    Args:
        csv_path (str): The path to the input CSV file.
        base_dir (str): The base directory to prepend to the filenames.
        query_pairs (list): A list of (column_name, keyword) tuples to query.
        days (int, optional): If provided, only list files modified within this many days.
    """
    try:
        with open(csv_path, mode='r', encoding='utf-8', newline='') as infile:
            reader = csv.DictReader(infile)
            
            # --- Validation Step ---
            # Ensure all query columns exist in the CSV header.
            header = reader.fieldnames
            if not header:
                print(f"Error: CSV file '{csv_path}' is empty or has no header.", file=sys.stderr)
                return

            # The first column must be 'Filename'.
            if 'Filename' not in header:
                print(f"Error: The required 'Filename' column was not found in '{csv_path}'.", file=sys.stderr)
                return

            query_columns = {col for col, kw in query_pairs}
            missing_cols = query_columns - set(header)
            if missing_cols:
                print(f"Error: The following query columns were not found in the CSV header: {', '.join(missing_cols)}", file=sys.stderr)
                print(f"Available columns are: {', '.join(header)}", file=sys.stderr)
                return

            # --- Processing Rows ---
            match_found = False
            for row_num, row in enumerate(reader, start=2): # Start from 2 to account for header
                # Assume the row is a match until proven otherwise
                is_match = True
                for column, keyword in query_pairs:
                    # Check if the cell value exists and contains the keyword (case-insensitive)
                    cell_value = row.get(column, '')
                    if keyword.lower() not in cell_value.lower():
                        is_match = False
                        break # No need to check other criteria for this row
                
                if is_match:
                    filename = row.get('Filename')
                    if filename:
                        full_path = os.path.join(base_dir, filename)

                        if days is not None:
                            try:
                                file_mod_time = os.path.getmtime(full_path)
                                # Check if the file is older than the specified days
                                if time.time() - file_mod_time > days * 24 * 60 * 60:
                                    continue # Skip to the next row
                            except FileNotFoundError:
                                # If file doesn't exist, it can't match the time criteria
                                continue

                        print("file://" + full_path)
                        match_found = True
            
            if not match_found:
                print("No matching rows found.")

    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

def main():
    """Main function to parse arguments and run the query."""
    parser = argparse.ArgumentParser(
        description="Query a CSV file and print the 'Filename' of matching rows.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Example Usage:
--------------
Let's say you have a file 'data.csv' with columns: 'Filename', 'Company name', 'Tech stack'

To find all files where the company is 'Amazon' and the tech stack includes 'Rust':
  python query_csv.py data.csv /path/to/my/files "Company name" "Amazon" "Tech stack" "Rust"

To find all files where the 'Company name' contains 'Google':
  python query_csv.py data.csv /path/to/my/files "Company name" "Google"
"""
    )

    parser.add_argument("csv_file", help="The path to the CSV file to query.")
    parser.add_argument("base_dir", help="The directory where files listed in the 'Filename' column reside.")
    parser.add_argument(
        "--days",
        type=float,
        help="Optional: Only show files modified within the last N days."
    )
    parser.add_argument(
        "queries",
        nargs='+',
        help="Query arguments in pairs: 'Column Name' 'Keyword to find'. You can specify multiple pairs."
    )

    args = parser.parse_args()

    # The queries come in a flat list, e.g., ['Col1', 'Val1', 'Col2', 'Val2']
    # We need to pair them up. First, check if the count is even.
    if len(args.queries) % 2 != 0:
        print("Error: Query arguments must be provided in pairs of 'Column Name' and 'Keyword'.", file=sys.stderr)
        print(f"You provided an odd number of query arguments ({len(args.queries)}).", file=sys.stderr)
        sys.exit(1)

    # Create pairs of (column, keyword)
    query_pairs = list(zip(args.queries[0::2], args.queries[1::2]))

    query_csv_file(args.csv_file, args.base_dir, query_pairs, args.days)

if __name__ == "__main__":
    main()
