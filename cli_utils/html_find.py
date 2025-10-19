#!/usr/bin/env python3

import os
import argparse
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
import time

# Use lxml for faster parsing. Install with: pip install lxml
# If lxml is not available, it will fall back to the slower html.parser.
try:
    import lxml
    PARSER = 'lxml'
except ImportError:
    print("Warning: lxml not found. Falling back to the slower 'html.parser'. For a significant speed-up, run: pip install lxml")
    PARSER = 'html.parser'

def search_file(file_path, compiled_regexes):
    """
    Processes a single file. Designed to be run in a separate process.
    Returns the file_path if it's a match, otherwise None.
    """
    try:
        # Assume UTF-8 first, it's the most common. Fallback is slower.
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except UnicodeDecodeError:
        # Fallback for non-UTF-8 files. This is slower.
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            # Note: chardet is slow, so this fallback path will impact performance for these specific files.
            # We're assuming it's the exception, not the rule.
            import chardet
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            html_content = raw_data.decode(encoding, errors='ignore')
        except Exception:
            return None # Failed to read/decode the file

    try:
        soup = BeautifulSoup(html_content, PARSER)

        # Prioritize structured data if it exists
        json_script = soup.find('script', type='application/ld+json')
        if json_script and json_script.string:
            try:
                json_data = json.loads(json_script.string)
                # Ensure description is a string before processing
                description = json_data.get('description', '')
                text_to_search = description if isinstance(description, str) else ''
            except json.JSONDecodeError:
                # If JSON is malformed, fall back to the whole page text
                text_to_search = soup.get_text()
        else:
            # Fallback to getting all text from the page
            text_to_search = soup.get_text()
        
        lower_text = text_to_search.lower()

        # Use pre-compiled regexes and check for all matches
        if all(regex.search(lower_text) for regex in compiled_regexes):
            return "file://" + os.path.abspath(file_path)
            
    except Exception:
        # Catch any parsing or processing errors for a single file
        return None
    
    return None

def main():
    p = argparse.ArgumentParser(
        description="Print names of HTML files containing the given keywords in a given directory. Search is always case insensitive."
    )
    p.add_argument('HTML_DIR', help='Directory in which to look for the HTML files')
    p.add_argument('SEARCH_TERMS', nargs='+', help='Names of files containing ALL of these search terms will be printed')
    p.add_argument('-w', '--workers', type=int, default=os.cpu_count(), help='Number of worker processes to use (defaults to all available cores)')
    args = p.parse_args()

    html_dir = os.path.abspath(args.HTML_DIR)
    search_terms = [term.lower() for term in args.SEARCH_TERMS]

    if not os.path.isdir(html_dir):
        p.error(f"Source directory does not exist or is not a directory: {html_dir}")

    start_time = time.time()

    # Pre-compile regexes once before starting the search
    # Using \b for whole-word matching.
    compiled_regexes = [re.compile(r'\b' + re.escape(term) + r'\b') for term in search_terms]

    # Collect all file paths first
    html_files_to_search = []
    for root, _, files in os.walk(html_dir):
        for filename in files:
            if filename.endswith((".html", ".htm")):
                html_files_to_search.append(os.path.join(root, filename))

    num_htmls_to_search = len(html_files_to_search)
    if num_htmls_to_search == 0:
        print("No HTML files found in the specified directory.")
        return
        
    print(f"Found {num_htmls_to_search} HTML files. Starting search with {args.workers} worker processes...")

    results = []
    # Use a Process Pool to parallelize the work across CPU cores
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        # Create a partial function to pass the constant regex list to the worker function
        search_func = partial(search_file, compiled_regexes=compiled_regexes)
        
        # Map the function to the file list and get futures
        futures = {executor.submit(search_func, file_path): file_path for file_path in html_files_to_search}

        # Process results as they are completed
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                print(result) # Print matches as they are found
                results.append(result)
            
            # Optional: print progress
            # print(f"\rProcessed: {i + 1}/{num_htmls_to_search}", end="", flush=True)

    end_time = time.time()
    
    print("\n\n--- Search Complete ---")
    print(f"Total number of HTML files that contain all the search terms: {len(results)}")
    print(f"Total number of HTML files searched: {num_htmls_to_search}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
