#!/usr/bin/env python3
"""
gonggaotong-download 直接API下载工具
绕过GUI，直接调用巨潮API下载A股公告
"""

import os
import time
import json
import requests
import argparse
from datetime import datetime
from pathlib import Path
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 配置
SAVE_PATH = "/home/tianwen/年报数据"
CNINFO_BASE_URL = "http://www.cninfo.com.cn"
STATIC_BASE_URL = "http://static.cninfo.com.cn"

class JuchaoDownloader:
    """巨潮A股公告下载器"""

    def __init__(self, save_path=SAVE_PATH):
        self.save_path = Path(save_path)
        self.save_path.mkdir(parents=True, exist_ok=True)
        # 创建新的 session 避免连接问题
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': CNINFO_BASE_URL,
        })

    def get_company_info(self, stock_code):
        """获取公司信息"""
        url = f"{CNINFO_BASE_URL}/new/data/szse_stock.json"
        response = self.session.get(url, timeout=30)
        data = response.json()

        for company in data.get('stockList', []):
            if company['code'] == stock_code:
                return {
                    'code': company['code'],
                    'name': company.get('zwjc', ''),
                    'orgId': company['orgId'],
                }
        return None

    def search_announcements(self, stock_code, start_date, end_date):
        """搜索公告"""
        company = self.get_company_info(stock_code)
        if not company:
            print(f"未找到股票代码: {stock_code}")
            return []

        print(f"找到公司: {company['name']} ({company['code']}), orgId: {company['orgId']}")

        params = {
            'pageNum': 1,
            'pageSize': 100,
            'column': 'szse',
            'tabName': 'fulltext',
            'plate': '',
            'stock': f"{stock_code},{company['orgId']}",
            'searchkey': '',
            'secid': '',
            'category': 'category_ndbg_szsh',
            'trade': '',
            'seDate': f"{start_date}~{end_date}",
            'sortName': '',
            'sortType': '',
            'isHLtitle': True,
        }

        url = f"{CNINFO_BASE_URL}/new/hisAnnouncement/query"
        response = self.session.post(url, data=params, timeout=30)
        result = response.json()

        announcements = []
        for item in result.get('announcements', []):
            announcements.append({
                'title': item['announcementTitle'],
                'time': item['announcementTime'],
                'url': item['adjunctUrl'],
                'size': item['adjunctSize'],
                'type': item['adjunctType'],
            })

        return announcements

    def download_file(self, url, filename):
        """下载文件"""
        if not url:
            return False

        # 确保 URL 格式正确
        if not url.startswith('/'):
            url = '/' + url
        file_url = f"{STATIC_BASE_URL}{url}"
        save_path = self.save_path / filename

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/pdf,*/*',
                'Referer': 'http://www.cninfo.com.cn/',
            }
            response = self.session.get(file_url, headers=headers, timeout=60, stream=True)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  ✓ 已下载: {filename}")
                return True
        except Exception as e:
            print(f"  ✗ 下载失败: {e}")
        return False

    def download(self, stock_code, start_year, end_year=None):
        """执行下载"""
        if end_year is None:
            end_year = datetime.now().year

        start_date = f"{start_year}-01-01"
        end_date = f"{end_year}-12-31"

        print(f"\n{'='*50}")
        print(f"开始下载: {stock_code}")
        print(f"时间范围: {start_date} ~ {end_date}")
        print(f"保存路径: {self.save_path}")
        print(f"{'='*50}\n")

        announcements = self.search_announcements(stock_code, start_date, end_date)
        print(f"找到 {len(announcements)} 条公告\n")

        if not announcements:
            print("未找到任何公告")
            return

        for i, ann in enumerate(announcements, 1):
            time_str = datetime.fromtimestamp(ann['time'] / 1000).strftime('%Y-%m-%d')
            filename = f"{stock_code}_{ann['title']}_{time_str}.{ann['type']}"
            for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                filename = filename.replace(char, '_')

            print(f"[{i}/{len(announcements)}] {ann['title']}")
            self.download_file(ann['url'], filename)
            time.sleep(0.5)

        print(f"\n✓ 下载完成，共 {len(announcements)} 个文件")

def main():
    parser = argparse.ArgumentParser(description="巨潮A股公告下载工具")
    parser.add_argument("--stock", "-s", default="601318", help="股票代码 (默认: 601318)")
    parser.add_argument("--start-year", "-y1", type=int, default=2020, help="开始年份 (默认: 2020)")
    parser.add_argument("--end-year", "-y2", type=int, default=None, help="结束年份 (默认: 今年)")
    parser.add_argument("--path", "-p", default=SAVE_PATH, help="保存路径")
    parser.add_argument("--list", "-l", action="store_true", help="仅列出公告，不下载")

    args = parser.parse_args()

    if args.end_year is None:
        args.end_year = datetime.now().year

    downloader = JuchaoDownloader(save_path=args.path)

    if args.list:
        announcements = downloader.search_announcements(
            args.stock,
            f"{args.start_year}-01-01",
            f"{args.end_year}-12-31"
        )
        for ann in announcements:
            time_str = datetime.fromtimestamp(ann['time'] / 1000).strftime('%Y-%m-%d')
            print(f"{time_str} | {ann['title']} | {ann['size']}KB")
    else:
        downloader.download(args.stock, args.start_year, args.end_year)

if __name__ == "__main__":
    main()