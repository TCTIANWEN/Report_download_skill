# Report_download - A股公告批量下载工具

A simple Python tool for batch downloading Chinese A-share listed companies' annual reports from Juchao (巨潮) website.

## 致谢

本项目基于 [gonggaotong-download](https://github.com/gonggaotong/gonggaotong-download) 修改。

gonggaotong-download 是一个功能完整的 Electron + Vue 桌面应用，支持 A股和美股公告批量下载。本项目在其基础上提取了核心的 A股年报下载功能，去除了 GUI 依赖，实现了纯命令行操作，便于集成到其他项目中。

感谢 [gonggaotong](https://github.com/gonggaotong) 的开源贡献。

## 功能特点

- 无需手动操作GUI，直接命令行下载
- 支持批量下载多个股票的年报、半年报等
- 自动重试机制，保证下载稳定性
- 文件命名规范，包含股票代码、标题、日期

## 环境要求

- Python 3.8+
- requests 库
- 网络连接正常

## 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/Report_download.git
cd Report_download

# 安装依赖（如果没有安装requests）
pip install requests
```

## 使用方法

### 基本命令

```bash
# 查看公告列表（不下载）
python juchao_downloader.py --stock 股票代码 --start-year 开始年份 --end-year 结束年份 --list

# 下载公告
python juchao_downloader.py --stock 股票代码 --start-year 开始年份 --end-year 结束年份

# 指定保存路径
python juchao_downloader.py --stock 股票代码 --start-year 2020 --end-year 2024 --path /your/save/path
```

### 参数说明

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--stock` | `-s` | 股票代码（如 601318, 002475） | 601318 |
| `--start-year` | `-y1` | 开始年份 | 2020 |
| `--end-year` | `-y2` | 结束年份 | 今年 |
| `--path` | `-p` | 保存路径 | ~/年报数据 |
| `--list` | `-l` | 仅列出公告，不下载 | False |

### 示例

**1. 下载中国平安(601318) 2020-2024年年报**

```bash
python juchao_downloader.py --stock 601318 --start-year 2020 --end-year 2024
```

**2. 查看立讯精密(002475)近5年公告（不下载）**

```bash
python juchao_downloader.py --stock 002475 --start-year 2020 --list
```

**3. 下载到指定目录**

```bash
python juchao_downloader.py --stock 002475 --start-year 2020 --path ./my_reports
```

**4. 下载多个年份**

```bash
python juchao_downloader.py --stock 600000 --start-year 2018 --end-year 2023
```

## 输出示例

```
$ python juchao_downloader.py --stock 601318 --start-year 2020 --end-year 2024

==================================================
开始下载: 601318
时间范围: 2020-01-01 ~ 2024-12-31
保存路径: /home/user/年报数据
==================================================

找到公司: 中国平安 (601318), orgId: 9900002221
找到 14 条公告

[1/14] 中国平安2023年年度报告摘要
  ✓ 已下载: 601318_中国平安2023年年度报告摘要_2024-03-22.PDF
[2/14] 中国平安2023年年度报告
  ✓ 已下载: 601318_中国平安2023年年度报告_2024-03-22.PDF
...

✓ 下载完成，共 14 个文件
```

## 文件命名规则

```
{股票代码}_{公告标题}_{发布日期}.{文件类型}
```

示例：`601318_中国平安2023年年度报告_2024-03-22.PDF`

## 注意事项

1. 本工具仅供学习研究使用
2. 下载的文件仅供个人学习研究，请勿用于商业用途
3. 请尊重版权，合理使用
4. 大量下载时请适当控制频率，避免对服务器造成压力

## 目录结构

```
Report_download/
├── juchao_downloader.py    # 主程序
├── README.md              # 使用说明
├── demo_data/             # 示例数据（可选）
│   ├── 002475_2024年年度报告.PDF
│   ├── 002475_2023年年度报告.PDF
│   └── ...
└── requirements.txt        # 依赖清单（可选）
```

## 常见问题

**Q: 下载失败怎么办？**

A: 程序会自动重试3次。如果持续失败，可能是网络问题或服务器限制，请稍后再试。

**Q: 如何下载其他类型的公告？**

A: 当前脚本默认下载年报（category_ndbg_szsh）。如需下载其他类型（如季报、半年报），可以修改脚本中的 `category` 参数。

**Q: 支持美股吗？**

A: 当前版本仅支持A股。如需美股下载，请访问 [gonggaotong-download](https://github.com/gonggaotong/gonggaotong-download)。

## License

MIT License - 仅供学习研究使用