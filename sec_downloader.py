#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SEC EDGAR US Stock Report Downloader
Download 10-K, 10-Q etc from SEC EDGAR
"""

import time
import requests
import argparse
from datetime import datetime
from pathlib import Path

SAVE_PATH = "./sec_reports"
SEC_BASE_URL = "https://www.sec.gov"
EDGAR_BASE_URL = "https://data.sec.gov/submissions"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def get_cik(ticker):
    url = f"{SEC_BASE_URL}/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    data = response.json()
    for key, entry in data.items():
        if entry.get('ticker') == ticker.upper():
            return {
                'ticker': entry.get('ticker'),
                'cik': str(entry.get('cik_str')),
                'title': entry.get('title', '')
            }
    return None

def pad_cik(cik):
    return str(cik).zfill(10)

def get_submissions(cik):
    url = f"{EDGAR_BASE_URL}/CIK{pad_cik(cik)}.json"
    response = requests.get(url, headers=HEADERS, timeout=30)
    return response.json()

def filter_filings(submissions, form_types, cik, start_year=None, end_year=None):
    filings = submissions.get('filings', {}).get('recent', {})
    forms = filings.get('form', [])
    dates = filings.get('filingDate', [])
    accession_numbers = filings.get('accessionNumber', [])
    primary_documents = filings.get('primaryDocument', [])
    sizes = filings.get('size', [])

    results = []
    for i, form in enumerate(forms):
        if form not in form_types:
            continue
        date_str = dates[i] if i < len(dates) else ''
        if date_str:
            year = int(date_str.split('-')[0])
            if start_year and year < start_year:
                continue
            if end_year and year > end_year:
                continue
        accession_number = accession_numbers[i] if i < len(accession_numbers) else ''
        primary_doc = primary_documents[i] if i < len(primary_documents) else ''
        url = f"{SEC_BASE_URL}/Archives/edgar/data/{cik}/{accession_number.replace('-', '')}/{primary_doc}"
        results.append({
            'form': form,
            'date': date_str,
            'url': url,
            'size': sizes[i] if i < len(sizes) else 0,
        })
    return results

def download_file(url, save_path):
    try:
        response = requests.get(url, headers=HEADERS, timeout=60)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"  Download failed: {e}")
    return False

def main():
    parser = argparse.ArgumentParser(description="SEC EDGAR US Stock Report Downloader")
    parser.add_argument("--stock", "-s", default="TSLA")
    parser.add_argument("--types", "-t", default="10-K")
    parser.add_argument("--start-year", "-y1", type=int, default=None)
    parser.add_argument("--end-year", "-y2", type=int, default=None)
    parser.add_argument("--path", "-p", default=SAVE_PATH)
    parser.add_argument("--list", "-l", action="store_true")
    args = parser.parse_args()

    form_types = args.types.split(',') if ',' in args.types else [args.types]
    if args.start_year is None:
        args.start_year = datetime.now().year - 5
    if args.end_year is None:
        args.end_year = datetime.now().year

    save_path = Path(args.path)
    save_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Downloading: {args.stock}")
    print(f"Types: {', '.join(form_types)}")
    print(f"Years: {args.start_year} - {args.end_year}")
    print(f"Path: {save_path}")
    print(f"{'='*50}\n")

    company = get_cik(args.stock)
    if not company:
        print(f"Ticker not found: {args.stock}")
        return
    print(f"Found: {company.get('title', '')} ({args.stock}), CIK: {company['cik']}")

    try:
        submissions = get_submissions(company['cik'])
    except Exception as e:
        print(f"Failed to get submissions: {e}")
        return

    filings = filter_filings(submissions, form_types, company['cik'], args.start_year, args.end_year)
    print(f"Found {len(filings)} filings\n")

    if args.list:
        for f in filings:
            size_kb = int(f['size']) / 1024 if f['size'] else 0
            print(f"{f['date']} | {f['form']} | {size_kb:.1f} KB")
        return

    if not filings:
        print("No filings found")
        return

    downloaded = []
    for i, filing in enumerate(filings, 1):
        date_str = filing['date'].replace('-', '')
        ext = filing['url'].split('.')[-1]
        filename = f"{args.stock}_{filing['form']}_{date_str}.{ext}"
        print(f"[{i}/{len(filings)}] {filing['form']} - {filing['date']}")
        if download_file(filing['url'], save_path / filename):
            print(f"  Saved: {filename}")
            downloaded.append(filename)
        time.sleep(0.5)

    print(f"\nDone! Downloaded {len(downloaded)} files")

if __name__ == "__main__":
    main()