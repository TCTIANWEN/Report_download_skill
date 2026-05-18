#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HKEX 港股公告下载器
使用 HKEX Title Search API 下载年报
基于 FS-Capture 项目的研究成果
"""

import re
import time
import argparse
import datetime
from pathlib import Path
from urllib.parse import urljoin
import requests

SAVE_PATH = "."
_TITLESEARCH_URL = "https://www1.hkexnews.hk/search/titlesearch.xhtml"
_PDF_HOST = "https://www1.hkexnews.hk"
_PREFIX_URL = "https://www1.hkexnews.hk/search/prefix.do"

_HEADERS = {
    "Origin": "https://www1.hkexnews.hk",
    "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
}

# 文档类型代码 (t1code)
_DOC_TYPES = {
    "annual": ("40000", "年报"),
    "interim": ("40000", "中期报告"),
    "q1": ("40001", "一季度运营数据"),
    "q3": ("40001", "三季度运营数据"),
}

# 排除的关键词
_EXCLUDE_KEYWORDS = (
    "esg", "sustainability", "notification", "letter",
    "circular", "proxy form", "環境、社會及管治",
    "環境、社會及管治", "通知", "通函", "業績", "业绩",
    "share buyback", "next day disclosure", "monthly return",
    "date of board meeting", "grant of restricted share",
)

# 包含的关键词
_REPORT_KEYWORDS = (
    "annual report", "年報", "年度報告", "年报", "年度报告",
    "quarterly results", "interim results", "中期业绩", "季度业绩",
    "results for the three months", "results for the three and six months",
    "first quarter", "third quarter",  # Q1, Q3运营数据
)


def _normalize_code(code: str) -> str:
    """标准化股票代码为5位数字"""
    c = code.strip().upper()
    c = re.sub(r"\D", "", c)
    return c.zfill(5)


def _get_stock_id(stock_code: str) -> str:
    """通过HKEX API获取股票的内部stockId"""
    norm = _normalize_code(stock_code)

    # JSONP callback
    params = {
        "callback": "callback",
        "lang": "EN",
        "type": "A",
        "name": norm,
        "market": "SEHK",
    }

    headers = {
        "Referer": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en",
        "Accept": "application/javascript,text/javascript,*/*;q=0.1",
    }

    response = requests.get(_PREFIX_URL, params=params, headers=headers, timeout=30)
    text = response.text

    # 解析JSONP响应: callback({...});
    jsonp_match = re.match(r"^[^(]*\((.*)\)\s*;?\s*$", text.strip(), re.DOTALL)
    if not jsonp_match:
        raise ValueError(f"无法解析HKEX prefix响应: {text[:200]}")

    import json
    payload = json.loads(jsonp_match.group(1))

    for item in payload.get("stockInfo") or []:
        code = str(item.get("code") or "").strip().zfill(5)
        if code != norm:
            continue
        stock_id = item.get("stockId")
        if stock_id is None or str(stock_id).strip() == "":
            continue
        return str(stock_id).strip()

    raise ValueError(f"找不到股票代码 {stock_code} 的HKEX stockId")


def _search_announcements(stock_id: str, stock_code: str, from_date: str, to_date: str, doc_type: str = "annual") -> list:
    """搜索公告"""
    t1code, _ = _DOC_TYPES.get(doc_type, ("40000", "年报"))

    params = {
        "lang": "EN",
        "category": "0",
        "market": "SEHK",
        "searchType": "1",  # 关键: 使用1而不是0(GUI用的)
        "documentType": "-1",
        "t1code": t1code,
        "t2Gcode": "-2",
        "t2code": "-2",
        "stockId": stock_id,
        "from": from_date,
        "to": to_date,
        "MB-Daterange": "0",
        "title": "",
    }

    time.sleep(1)  # 避免请求过快

    response = requests.post(_TITLESEARCH_URL, data=params, headers=_HEADERS, timeout=60)
    response.raise_for_status()

    return _parse_results(response.text, stock_code)


def _squash(text: str) -> str:
    """规范化空白字符"""
    return " ".join(text.split())


def _strip_mobile_heading(text: str) -> str:
    """去除移动端标题前缀"""
    return re.sub(r"^(Release Time|Stock Code|Stock Short Name|Document):\s*", "", text).strip()


def _parse_release_date(value: str):
    """解析发布日期"""
    value = _strip_mobile_heading(value)
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _node_text(node) -> str:
    """获取节点文本"""
    if node is None:
        return ""
    try:
        return _squash(node.text(separator=" ", strip=True))
    except TypeError:
        return _squash(node.text(strip=True))


def _parse_results(html_text: str, stock_code: str) -> list:
    """解析搜索结果HTML"""
    results = []

    # 查找表格行 - 使用新的方式匹配
    tr_pattern = re.compile(r'<tr>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*</tr>', re.DOTALL)

    rows = tr_pattern.findall(html_text)
    print(f"找到 {len(rows)} 个表格行")

    for date_cell, stock_cell, name_cell, doc_cell in rows:
        # 解析日期
        date_txt = _strip_mobile_heading(_squash(re.sub(r'<[^>]+>', ' ', date_cell)))

        # 解析股票代码
        stock_text = _strip_mobile_heading(_squash(re.sub(r'<[^>]+>', ' ', stock_cell)))

        # 解析股票名称
        name_text = _squash(re.sub(r'<[^>]+>', ' ', name_cell))

        # 查找PDF链接
        a_pattern = re.compile(r'<a[^>]*href=["\']([^"\']*\.pdf[^"\']*)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
        links = a_pattern.findall(doc_cell)
        if not links:
            continue

        href = links[0][0]
        link_text = _squash(re.sub(r'<[^>]+>', ' ', links[0][1]))

        # 完整URL
        if not href.startswith(("http://", "https://")):
            href = urljoin(_PDF_HOST, href)

        # 查找 headline
        headline_pattern = re.compile(r'<div[^>]*class=["\']headline["\'][^>]*>(.*?)</div>', re.DOTALL | re.IGNORECASE)
        headline_match = headline_pattern.search(doc_cell)
        headline = ""
        if headline_match:
            headline = _squash(re.sub(r'<[^>]+>', ' ', headline_match.group(1)))

        # 提取文档类型
        doc_type = ""
        bracket_match = re.search(r'\[([^\]]+)\]', headline)
        if bracket_match:
            doc_type = _squash(bracket_match.group(1))
        elif " - " in headline:
            doc_type = _squash(headline.rsplit(" - ", 1)[-1])

        # 提取股票代码
        stock_codes = re.findall(r'\b(\d{5})\b', stock_text)

        results.append({
            "url": href,
            "title": link_text,
            "headline": headline,
            "doc_type": doc_type,
            "date": date_txt,
            "filing_date": _parse_release_date(date_txt),
            "stock_codes": tuple(stock_codes),
            "stock_names": name_text,
        })

    return results


def _contains_any(text: str, keywords: tuple) -> bool:
    """检查文本是否包含任意关键词"""
    lowered = text.lower()
    return any(kw.lower() in lowered for kw in keywords)


def _is_report_candidate(row: dict, doc_type: str = "annual") -> bool:
    """检查是否是报告候选"""
    title = row.get("title") or ""
    headline = row.get("headline") or ""
    doc_type_label = row.get("doc_type") or ""

    # 排除非报告
    if _contains_any(title, _EXCLUDE_KEYWORDS):
        return False

    # 年报/半年报
    if doc_type in ("annual", "interim"):
        if _contains_any(title, _REPORT_KEYWORDS):
            return True
        return _contains_any(doc_type_label, _REPORT_KEYWORDS)

    # Q1: 一季度运营数据
    if doc_type == "q1":
        return _contains_any(title, ("first quarter", "results for the three months ended march")) or \
               _contains_any(doc_type_label, ("Quarterly Results",))

    # Q3: 三季度运营数据
    if doc_type == "q3":
        return _contains_any(title, ("third quarter", "results for the three months ended september")) or \
               _contains_any(doc_type_label, ("Quarterly Results",))

    return False


def search_reports(stock_code: str, year: int, doc_type: str = "annual") -> list:
    """搜索指定类型和年份的报告"""
    print(f"正在查询港交所披露易: 股票代码 {stock_code}, 年份 {year}, 类型 {doc_type}...")

    # 获取stockId
    try:
        stock_id = _get_stock_id(stock_code)
        print(f"股票代码 {stock_code} 对应的stockId: {stock_id}")
    except Exception as e:
        print(f"获取stockId失败: {e}")
        return []

    # 设置搜索日期范围
    if doc_type == "annual":
        # 年报通常在次年发布
        from_date = f"{year}0101"
        to_date = f"{year + 1}0630"
    elif doc_type == "interim":
        # 半年报通常在下半年发布
        from_date = f"{year}0101"
        to_date = f"{year}1231"
    elif doc_type == "q1":
        # 一季度运营数据: 4月发布
        from_date = f"{year}0401"
        to_date = f"{year}0630"
    elif doc_type == "q3":
        # 三季度运营数据: 10月发布
        from_date = f"{year}1001"
        to_date = f"{year}1231"
    else:
        from_date = f"{year}0101"
        to_date = f"{year + 1}0331"

    print(f"搜索日期范围: {from_date} - {to_date}")

    # 搜索公告
    rows = _search_announcements(stock_id, stock_code, from_date, to_date, doc_type)
    print(f"搜索返回 {len(rows)} 条结果")

    # 过滤报告
    candidates = [row for row in rows if _is_report_candidate(row, doc_type)]

    # 进一步过滤包含年份的结果
    year_str = str(year)
    year_candidates = [r for r in candidates if year_str in (r.get("title") or "")]

    if year_candidates:
        print(f"找到 {len(year_candidates)} 条包含年份 {year} 的报告")
        return year_candidates
    elif candidates:
        print(f"找到 {len(candidates)} 条报告(未精确匹配年份)")
        return candidates
    else:
        print("未找到报告")
        return rows  # 返回所有结果供查看


def search_annual_reports(stock_code: str, year: int) -> list:
    """搜索指定年份的年报"""
    print(f"正在查询港交所披露易: 股票代码 {stock_code}, 年份 {year}...")

    # 获取stockId
    try:
        stock_id = _get_stock_id(stock_code)
        print(f"股票代码 {stock_code} 对应的stockId: {stock_id}")
    except Exception as e:
        print(f"获取stockId失败: {e}")
        return []

    # 设置搜索日期范围 (年报通常在次年发布)
    from_date = f"{year}0101"
    to_date = f"{year + 1}0630"  # 年报最晚可能在次年6月发布

    print(f"搜索日期范围: {from_date} - {to_date}")

    # 搜索年报
    rows = _search_announcements(stock_id, stock_code, from_date, to_date, "annual")
    print(f"搜索返回 {len(rows)} 条结果")

    # 过滤年报
    candidates = [row for row in rows if _is_report_candidate(row)]

    # 进一步过滤包含年份的结果
    year_str = str(year)
    year_candidates = [r for r in candidates if year_str in (r.get("title") or "")]

    if year_candidates:
        print(f"找到 {len(year_candidates)} 条包含年份 {year} 的年报")
        return year_candidates
    elif candidates:
        print(f"找到 {len(candidates)} 条年报(未精确匹配年份)")
        return candidates
    else:
        print("未找到年报")
        return rows  # 返回所有结果供查看


def download_file(url: str, filename: str, save_path: Path) -> bool:
    """下载文件"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www1.hkexnews.hk/",
    }
    try:
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                save_file = save_path / filename
                with open(save_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
    except Exception as e:
        print(f"  下载失败: {e}")
    return False


def search_quarterly_reports(stock_code: str, year: int) -> list:
    """搜索指定年份的季度报告"""
    return search_reports(stock_code, year, "quarterly")


def main():
    parser = argparse.ArgumentParser(description="HKEX 港股公告下载工具", formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
快速使用:
  年报:  python hkex_downloader.py -s 3690 --year 2024 -t annual
  半年报: python hkex_downloader.py -s 3690 --year 2024 -t interim
  一季度运营数据: python hkex_downloader.py -s 3690 --year 2024 -t q1
  三季度运营数据: python hkex_downloader.py -s 3690 --year 2024 -t q3

报告类型:
  annual - 年报 (Annual Report)
  interim - 半年报 (Interim Report)
  q1 - 一季度运营数据公告 (Quarterly Results for Q1)
  q3 - 三季度运营数据公告 (Quarterly Results for Q3)

注意: 港股没有A股意义上的季报，但有季度运营数据公告(Q1和Q3)

示例:
  下载美团2024年年报: hkex_downloader.py -s 3690 --year 2024 -t annual
  下载美团2024年半年报: hkex_downloader.py -s 3690 --year 2024 -t interim
  下载美团2024年Q1运营数据: hkex_downloader.py -s 3690 --year 2024 -t q1
  下载美团2024年Q3运营数据: hkex_downloader.py -s 3690 --year 2024 -t q3
  仅列出腾讯2024年Q3运营数据: hkex_downloader.py -s 0700 --year 2024 -t q3 -l
        """)
    parser.add_argument("--stock", "-s", default="3690", help="股票代码 (默认: 3690)")
    parser.add_argument("--year", "-y", type=int, default=2024, help="年份 (默认: 2024)")
    parser.add_argument("--type", "-t", default="annual",
                        choices=["annual", "interim", "q1", "q3"],
                        help="报告类型: annual(年报), interim(半年报), q1(一季度运营数据), q3(三季度运营数据)")
    parser.add_argument("--path", "-p", default=SAVE_PATH, help=f"保存路径 (默认: {SAVE_PATH})")
    parser.add_argument("--list", "-l", action="store_true", help="仅列出，不下载")

    args = parser.parse_args()

    save_path = Path(args.path)
    save_path.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"港股公告下载: {args.stock}")
    print(f"年份: {args.year}")
    print(f"报告类型: {args.type}")
    print(f"保存路径: {save_path}")
    print(f"{'='*50}\n")

    try:
        results = search_reports(args.stock, args.year, args.type)
        print(f"\n找到 {len(results)} 条公告\n")

        if args.list:
            for r in results:
                print(f"{r['date']} | {r['title'][:60]} | {r.get('doc_type', '')}")
            return

        if not results:
            print("未找到公告")
            return

        downloaded = 0
        for i, r in enumerate(results, 1):
            # 构建文件名
            date_str = r.get("filing_date", "")
            if date_str:
                date_str = date_str.strftime("%Y-%m-%d")
            else:
                date_str = r["date"].replace("/", "-")

            safe_title = re.sub(r"[^\w\-_. ()]", "_", r["title"])[:30]
            filename = f"{args.stock}_{date_str}_{safe_title}.pdf"
            filename = re.sub(r"_+", "_", filename)

            print(f"[{i}/{len(results)}] {r['title'][:50]}...")
            if download_file(r["url"], filename, save_path):
                downloaded += 1
                print(f"  已下载: {filename}")

        print(f"\n完成! 下载 {downloaded} 个文件")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
