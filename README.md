# Report_download_skill - 中美股年报批量下载工具

支持 A股年报和美股年报(10-K/20-F)的批量下载工具。

## 功能特点

- **A股下载**: 基于巨潮网 API，无需 GUI，直接命令行下载
- **美股下载**: 基于 SEC EDGAR API，支持 10-K(美国本土公司)、20-F(外国公司)
- 自动识别公司类型
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

### A股年报下载

```bash
# 下载中国平安(601318) 2020-2024年年报
python juchao_downloader.py --stock 601318 --start-year 2020 --end-year 2024

# 下载立讯精密(002475)近5年
python juchao_downloader.py --stock 002475 --start-year 2020
```

### 美股年报下载

```bash
# 下载特斯拉(TSLA) 2024-2025年 10-K (美国本土公司)
python sec_downloader.py --stock TSLA --types 10-K --start-year 2024 --end-year 2025

# 下载京东(JD) 2024-2025年 20-F (外国公司)
python sec_downloader.py --stock JD --types 20-F --start-year 2024 --end-year 2025

# 查看苹果(AAPL)近两年10-K列表
python sec_downloader.py --stock AAPL --types 10-K --start-year 2023 --list
```

## 详细参数

### A股 (juchao_downloader.py)

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stock` | `-s` | 股票代码（如 601318, 002475） | 601318 |
| `--start-year` | `-y1` | 开始年份 | 2020 |
| `--end-year` | `-y2` | 结束年份 | 今年 |
| `--path` | `-p` | 保存路径 | ~/年报数据 |
| `--list` | `-l` | 仅列出公告，不下载 | False |

### 美股 (sec_downloader.py)

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stock` | `-s` | Ticker代码（如 TSLA, AAPL, JD） | TSLA |
| `--types` | `-t` | 文档类型 | 10-K |
| `--start-year` | `-y1` | 开始年份 | 五年前 |
| `--end-year` | `-y2` | 结束年份 | 今年 |
| `--path` | `-p` | 保存路径 | ./sec_reports |
| `--list` | `-l` | 仅列出公告，不下载 | False |

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

**A股下载**:
```
==================================================
开始下载: 601318
时间范围: 2020-01-01 ~ 2024-12-31
==================================================
找到公司: 中国平安 (601318), orgId: 9900002221
找到 14 条公告
[1/14] 中国平安2023年年度报告
  ✓ 已下载: 601318_中国平安2023年年度报告_2024-03-22.PDF
✓ 下载完成，共 14 个文件
```

**美股下载**:
```
==================================================
Downloading: TSLA
Types: 10-K
Years: 2024 - 2025
==================================================
Found: Tesla, Inc. (TSLA), CIK: 1318605
Found 2 filings
[1/2] 10-K - 2025-01-30
  Saved: TSLA_10-K_20250130.htm
[2/2] 10-K - 2024-01-29
  Saved: TSLA_10-K_20240129.htm
Done! Downloaded 2 files
```

## 目录结构

```
Report_download_skill/
├── juchao_downloader.py    # A股下载脚本
├── sec_downloader.py       # 美股下载脚本
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

## 致谢

本项目基于 [gonggaotong-download](https://github.com/gonggaotong/gonggaotong-download) 修改。感谢 [gonggaotong](https://github.com/gonggaotong) 的开源贡献。

## 注意事项

1. 本工具仅供学习研究使用
2. 下载的文件仅供个人学习研究，请勿用于商业用途
3. 请尊重版权，合理使用
4. 大量下载时请适当控制频率

## License

MIT License - 仅供学习研究使用