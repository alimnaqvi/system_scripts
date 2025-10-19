#!/usr/bin/env python3

import os
import argparse
from bs4 import BeautifulSoup
import json
import chardet
import re

# Arguments
p = argparse.ArgumentParser(
    description="Print names of HTML files containing the given keywords in a given directory. Search is always case insensitive."
)
p.add_argument('HTML_DIR', help='Directory in which to look for the HTML files')
p.add_argument('SEARCH_TERMS', nargs='+', help='Names of files containing ALL of these search terms will be printed')
args = p.parse_args()

HTML_DIR = os.path.abspath(args.HTML_DIR)
orig_search_terms = args.SEARCH_TERMS
SEARCH_TERMS = [term.lower() for term in orig_search_terms]

HOME = os.getenv('HOME')
if not HOME:
    print("HOME not found in the environment. Exiting.")
    exit(1)

if not os.path.isdir(HTML_DIR):
    p.error(f"Source directory does not exist or is not a directory: {HTML_DIR}")

# Globals for stats
num_htmls_searched = 0
num_htmls_result = 0
error_htmls = 0

def read_file_with_auto_detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    detected = chardet.detect(raw_data)
    encoding = detected['encoding'] or 'utf-8'
    return raw_data.decode(encoding)

# Match whole words
def contains_term(word, text):
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text))

def search_job_description(file_path):
    global num_htmls_searched
    global num_htmls_result
    global error_htmls

    try:
        html_content = read_file_with_auto_detect_encoding(file_path)
        soup = BeautifulSoup(html_content, 'html.parser')

        json_script = soup.find('script', type='application/ld+json')
        if json_script:
            json_data = json.loads(json_script.string)
            job_description = json_data.get('description', '')
        else:
            job_description = soup.get_text()

        lower_jd=job_description.lower()
        if (all(contains_term(term, lower_jd) for term in SEARCH_TERMS)):
            print("file://" + os.path.abspath(file_path))
            num_htmls_result += 1

        num_htmls_searched += 1
        
    except Exception as e:
        # print(f"Error processing file {file_path}: {str(e)}")
        error_htmls += 1

def main():
        
    for root, dirs, files in os.walk(HTML_DIR):
        for filename in files:
            if filename.endswith(".html"):
                file_path = os.path.join(root, filename)
                search_job_description(file_path)
    
    print("")
    print("Total number of HTML files that contain all the search terms:", num_htmls_result)
    print("Total number of HTML files searched:", num_htmls_searched)
    print("Number of HTML files failed to process:", error_htmls)

if __name__ == "__main__":
    main()
