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

SAVE_PATH = "."
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

# SEC表单类型
_FORM_TYPES = {
    "10-K",  # 年报
    "10-Q",  # 季报 (Q1, Q2, Q3)
}

# 报告类型映射到SEC表单
_REPORT_TYPE_MAP = {
    "annual": ["10-K"],
    "interim": ["10-Q"],  # 所有季报(Q1/Q2/Q3)
    "q1": ["10-Q"],
    "q2": ["10-Q"],
    "q3": ["10-Q"],
}

# 季度过滤 (按发布日期: Q1=4月, Q2=7月, Q3=10月)
_QUARTER_MONTHS = {
    "q1": [4],      # Q1 ended March, published April
    "q2": [7],      # Q2 ended June, published July (half-year)
    "q3": [10],     # Q3 ended September, published October
}

def _get_quarter_from_date(date_str: str) -> str:
    """根据发布日期判断季度 (SEC在季度结束后约一个月发布)
    Q1 ended March -> 发布约4月 -> month=4
    Q2 ended June -> 发布约7月 -> month=7
    Q3 ended September -> 发布约10月 -> month=10
    """
    month = int(date_str.split('-')[1]) if date_str else 0
    if month == 4:
        return "q1"
    elif month == 7:
        return "q2"
    elif month == 10:
        return "q3"
    return ""


def filter_filings(submissions, form_types, cik, start_year=None, end_year=None, quarter=None):
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
            # 季度过滤 (按发布日期: Q1=4月, Q2=7月, Q3=10月)
            if quarter:
                q_months = _QUARTER_MONTHS.get(quarter, [])
                month = int(date_str.split('-')[1]) if date_str else 0
                if month not in q_months:
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
    parser = argparse.ArgumentParser(
        description="SEC EDGAR US Stock Report Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
快速使用:
  年报:  python sec_downloader.py -s TSLA --year 2024 -t annual
  半年报: python sec_downloader.py -s TSLA --year 2024 -t interim
  一季报: python sec_downloader.py -s TSLA --year 2024 -t q1
  三季报: python sec_downloader.py -s TSLA --year 2024 -t q3

报告类型:
  annual - 10-K 年报
  interim - 10-Q 季报(含Q1/Q2/Q3所有季度)
  q1 - 10-Q 一季报(4月发布)
  q2 - 10-Q 半年报(7月发布)
  q3 - 10-Q 三季报(10月发布)

示例:
  下载特斯拉2024年年报: sec_downloader.py -s TSLA --year 2024 -t annual
  下载特斯拉2024年Q1季报: sec_downloader.py -s TSLA --year 2024 -t q1
  下载特斯拉2024年Q3季报: sec_downloader.py -s TSLA --year 2024 -t q3
  仅列出特斯拉2024年季报: sec_downloader.py -s TSLA --year 2024 -t q1 -l
        """)
    parser.add_argument("--stock", "-s", default="TSLA", help="Ticker代码 (默认: TSLA)")
    parser.add_argument("--year", "-y", type=int, default=2024, help="年份 (默认: 2024)")
    parser.add_argument("--type", "-t", default="annual",
                        choices=["annual", "interim", "q1", "q2", "q3"],
                        help="报告类型: annual(10-K年报), interim(10-Q), q1(Q1), q2(Q2/半年报), q3(Q3)")
    parser.add_argument("--path", "-p", default=SAVE_PATH, help=f"保存路径 (默认: {SAVE_PATH})")
    parser.add_argument("--list", "-l", action="store_true", help="仅列出，不下载")
    args = parser.parse_args()

    # 获取表单类型
    form_types = _REPORT_TYPE_MAP.get(args.type, ["10-K"])

    # 年份范围
    start_year = args.year
    end_year = args.year

    # 季度过滤 (q1/q2/q3 按月过滤，interim 不过滤)
    quarter = args.type if args.type in ("q1", "q2", "q3") else None

    save_path = Path(args.path)
    save_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Downloading: {args.stock}")
    print(f"Report Type: {args.type}")
    print(f"Form Types: {', '.join(form_types)}")
    print(f"Year: {args.year}")
    if quarter:
        print(f"Quarter: {quarter}")
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

    filings = filter_filings(submissions, form_types, company['cik'], start_year, end_year, quarter)
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