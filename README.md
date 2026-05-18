# Report_download_skill - 中美港股公告批量下载工具

支持 A股、美股和港股公告的批量下载工具。

## 功能特点

- **A股下载**: 基于巨潮网 API，支持年报、半年报、一季报和三季报
- **美股下载**: 基于 SEC EDGAR API，支持 10-K(美国本土公司)、20-F(外国公司)
- **港股下载**: 基于 HKEX Title Search API，支持年报、半年报、一季度运营数据和三季度运营数据
- 文件命名规范，包含股票代码、文档类型、日期

## 环境要求

- Python 3.8+
- requests 库 (`pip install requests`)

## 安装

```bash
git clone https://github.com/TCTIANWEN/Report_download_skill.git
cd Report_download_skill
pip install requests
```

## 快速使用

### A股公告下载

```bash
# 年报: python juchao_downloader.py -s 股票代码 --year 年份 -t annual
python juchao_downloader.py -s 002475 --year 2024 -t annual

# 半年报: python juchao_downloader.py -s 股票代码 --year 年份 -t interim
python juchao_downloader.py -s 002475 --year 2024 -t interim

# 一季报和三季报: python juchao_downloader.py -s 股票代码 --year 年份 -t quarterly
python juchao_downloader.py -s 002475 --year 2024 -t quarterly

# 示例: 下载立讯精密2024年年报 (保存到当前目录)
python juchao_downloader.py -s 002475 --year 2024 -t annual

# 示例: 下载立讯精密2024年季报(一季报和三季报)
python juchao_downloader.py -s 002475 --year 2024 -t quarterly

# 示例: 仅列出格力电器2024年季报
python juchao_downloader.py -s 000651 --year 2024 -t quarterly -l

# 示例: 下载立讯精密2024年年报到指定目录
python juchao_downloader.py -s 002475 --year 2024 -t annual -p ./reports
```

### 美股公告下载

```bash
# 年报: python sec_downloader.py -s TICKER --year 年份 -t annual
python sec_downloader.py -s TSLA --year 2024 -t annual

# 半年报: python sec_downloader.py -s TICKER --year 年份 -t interim
python sec_downloader.py -s TSLA --year 2024 -t interim

# 一季报: python sec_downloader.py -s TICKER --year 年份 -t q1
python sec_downloader.py -s TSLA --year 2024 -t q1

# 三季报: python sec_downloader.py -s TICKER --year 年份 -t q3
python sec_downloader.py -s TSLA --year 2024 -t q3

# 示例: 下载特斯拉2024年年报 (保存到当前目录)
python sec_downloader.py -s TSLA --year 2024 -t annual

# 示例: 下载特斯拉2024年Q1季报
python sec_downloader.py -s TSLA --year 2024 -t q1

# 示例: 下载京东(JD) 2024年 20-F (外国公司年报)
python sec_downloader.py -s JD --year 2024 -t annual

# 示例: 仅列出特斯拉2024年Q1季报
python sec_downloader.py -s TSLA --year 2024 -t q1 -l

# 示例: 下载特斯拉2024年Q1季报到指定目录
python sec_downloader.py -s TSLA --year 2024 -t q1 -p ./sec_data
```

**美股说明**: 美股季报分10-Q(一季报)、10-Q(二季报/半年报)、10-Q(三季报)，年报为10-K。

### 港股公告下载

```bash
# 年报: python hkex_downloader.py -s 股票代码 --year 年份 -t annual
python hkex_downloader.py -s 3690 --year 2024 -t annual

# 半年报: python hkex_downloader.py -s 股票代码 --year 年份 -t interim
python hkex_downloader.py -s 3690 --year 2024 -t interim

# 一季度运营数据: python hkex_downloader.py -s 股票代码 --year 年份 -t q1
python hkex_downloader.py -s 3690 --year 2024 -t q1

# 三季度运营数据: python hkex_downloader.py -s 股票代码 --year 年份 -t q3
python hkex_downloader.py -s 3690 --year 2024 -t q3

# 示例: 下载美团2024年年报 (保存到当前目录)
python hkex_downloader.py -s 3690 --year 2024 -t annual

# 示例: 下载美团2024年Q1运营数据
python hkex_downloader.py -s 3690 --year 2024 -t q1

# 示例: 下载美团2024年Q3运营数据
python hkex_downloader.py -s 3690 --year 2024 -t q3

# 示例: 仅列出腾讯2024年Q3运营数据
python hkex_downloader.py -s 0700 --year 2024 -t q3 -l

# 示例: 下载美团2024年Q1运营数据到指定目录
python hkex_downloader.py -s 3690 --year 2024 -t q1 -p ./hkex_data
```

**港股说明**: 港股没有A股意义上的季报，但有季度运营数据公告（Quarterly Results），只有Q1和Q3的运营数据。

## 详细参数

### A股 (juchao_downloader.py)

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stock` | `-s` | 股票代码（如 601318, 002475） | 601318 |
| `--year` | `-y` | 年份 | 2024 |
| `--type` | `-t` | 报告类型: annual/interim/quarterly | annual |
| `--path` | `-p` | 保存路径 | 当前目录 |
| `--list` | `-l` | 仅列出公告，不下载 | False |

**报告类型 (--type)**:
- `annual`: 年报
- `interim`: 半年报
- `quarterly`: 一季报和三季报

### 美股 (sec_downloader.py)

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stock` | `-s` | Ticker代码（如 TSLA, AAPL, JD） | TSLA |
| `--year` | `-y` | 年份 | 2024 |
| `--type` | `-t` | 报告类型: annual/interim/q1/q2/q3 | annual |
| `--path` | `-p` | 保存路径 | 当前目录 |
| `--list` | `-l` | 仅列出公告，不下载 | False |

**报告类型 (--type)**:
- `annual`: 10-K 年报
- `interim`: 10-Q 全部季报(Q1/Q2/Q3)
- `q1`: 10-Q 一季报(4月发布)
- `q2`: 10-Q 二季报/半年报(7月发布)
- `q3`: 10-Q 三季报(10月发布)
| `--list` | `-l` | 仅列出公告，不下载 | False |

### 港股 (hkex_downloader.py)

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stock` | `-s` | 股票代码（如 3690, 0700） | 3690 |
| `--year` | `-y` | 年份 | 2024 |
| `--type` | `-t` | 报告类型: annual/interim/q1/q3 | annual |
| `--path` | `-p` | 保存路径 | 当前目录 |
| `--list` | `-l` | 仅列出公告，不下载 | False |

**报告类型 (--type)**:
- `annual`: 年报
- `interim`: 半年报
- `q1`: 一季度运营数据公告
- `q3`: 三季度运营数据公告

## 美股文档类型说明

| 类型 | 说明 | 适用公司 |
|------|------|----------|
| `10-K` | 年报 | 美国本土公司（如 TSLA, AAPL, MSFT） |
| `20-F` | 外国公司年报 | 在美上市的外国公司（如 JD, BABA） |
| `10-Q` | 季报 | 所有公司 |
| `8-K` | 重大事件报告 | 所有公司 |

**如何判断用 10-K 还是 20-F？**
- 美国公司（非美国注册）→ 10-K
- 外国公司（在美上市）→ 20-F
- 一般中国公司在美上市都是 20-F（如 JD, BABA）

## 输出示例

**A股年报下载**:
```
==================================================
开始下载: 002475
报告类型: annual
时间范围: 2024-01-01 ~ 2024-12-31
保存路径: .
==================================================
找到公司: 立讯精密 (002475), orgId: 9900014448
找到 1 条公告

[1/1] 2024年年度报告
  ✓ 已下载: 002475_2024年年度报告_2025-04-26.PDF
✓ 下载完成，共 1 个文件
```

**A股季报下载**:
```
==================================================
开始下载: 002475
报告类型: quarterly
时间范围: 2024-01-01 ~ 2024-12-31
保存路径: .
==================================================
找到公司: 立讯精密 (002475), orgId: 9900014448
找到 2 条公告

[1/2] 2024年三季度报告
  ✓ 已下载: 002475_2024年三季度报告_2024-10-26.PDF
[2/2] 2024年一季度报告
  ✓ 已下载: 002475_2024年一季度报告_2024-04-25.PDF
✓ 下载完成，共 2 个文件
```

**美股年报下载**:
```
==================================================
Downloading: TSLA
Report Type: annual
Form Types: ['10-K']
Year: 2024
Path: .
==================================================
Found: Tesla, Inc. (TSLA), CIK: 1318605
Found 1 filings

[1/1] 10-K - 2024-01-29
  Saved: TSLA_10-K_20240129.htm
Done! Downloaded 1 files
```

**美股季报下载**:
```
==================================================
Downloading: TSLA
Report Type: q1
Form Types: ['10-Q']
Year: 2024
Quarter: q1
Path: .
==================================================
Found: Tesla, Inc. (TSLA), CIK: 1318605
Found 1 filings

[1/1] 10-Q - 2024-04-24
  Saved: TSLA_10-Q_20240424.htm
Done! Downloaded 1 files
```

**港股年报下载**:
```
==================================================
港股公告下载: 3690
年份: 2024
报告类型: annual
保存路径: .
==================================================
正在查询港交所披露易: 股票代码 3690, 年份 2024, 类型 annual...
股票代码 3690 对应的stockId: 198419
搜索日期范围: 20240101 - 20250630
找到 3 个表格行
找到 1 条包含年份 2024 的报告

找到 1 条公告

[1/1] 2024 ANNUAL REPORT...
  已下载: 3690_2025-04-28_2024 ANNUAL REPORT.pdf
完成! 下载 1 个文件
```

**港股Q1运营数据下载**:
```
==================================================
港股公告下载: 3690
年份: 2024
报告类型: q1
保存路径: .
==================================================
正在查询港交所披露易: 股票代码 3690, 年份 2024, 类型 q1...
股票代码 3690 对应的stockId: 198419
搜索日期范围: 20240401 - 20240630
找到 44 个表格行
找到 1 条包含年份 2024 的报告

找到 1 条公告

[1/1] ANNOUNCEMENT OF THE RESULTS FOR THE THREE MONTHS E...
  已下载: 3690_2024-06-06_ANNOUNCEMENT OF THE RESULTS FO.pdf
完成! 下载 1 个文件
```

## 目录结构

```
Report_download_skill/
├── juchao_downloader.py    # A股下载脚本
├── sec_downloader.py       # 美股下载脚本
├── hkex_downloader.py     # 港股下载脚本
├── README.md              # 本文件
└── requirements.txt       # 依赖
```

## 常见问题

**Q: 如何知道一个股票是 10-K 还是 20-F？**
A: 一般来说：
- 美国公司（非美国注册）：10-K
- 中国公司在美上市（如京东、阿里巴巴）：20-F
- 不确定时，可以先用 `--list` 参数查看有哪些 filing 类型

**Q: 下载失败怎么办？**
A: 程序会自动重试。如果持续失败，可能是网络问题或 SEC 限流，请稍后再试。

**Q: 支持哪些中国公司？**
A: 任何在巨潮网可查询的 A 股公司都可以，支持沪深北交所所有股票。

**Q: A股季报为什么只有一季报和三季报，没有二季报？**
A: A股季报制度中，二季度报告包含在半年报里，所以没有单独的"二季报"。

## 致谢

本项目基于 [gonggaotong-download](https://github.com/gonggaotong/gonggaotong-download) 修改，感谢 [gonggaotong](https://github.com/gonggaotong) 的开源贡献。

港股下载部分参考了 [FS-Capture](https://github.com/Eric-KY-Zhang/FS-Capture) 项目，特别感谢 [Eric-Zhang](https://github.com/Eric-KY-Zhang) 的研究贡献。

## 注意事项

1. 本工具仅供学习研究使用
2. 下载的文件仅供个人学习研究，请勿用于商业用途
3. 请尊重版权，合理使用
4. 大量下载时请适当控制频率

## License

MIT License - 仅供学习研究使用