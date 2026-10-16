# 微博热搜数据采集项目

基于 Python 的微博热搜数据采集、清洗与可视化分析项目，覆盖数据爬取、数据处理、数据分析与可视化的完整流程。

## 项目简介

本项目通过模拟浏览器请求微博热搜接口，采集微博热搜数据（总榜、娱乐榜、生活榜、社会榜），并进行数据清洗、分类标准化、关键词提取、话题传播路径分析与用户参与度分析，最终生成可视化图表与洞察报告。

## 功能特性

- **数据采集**：调用微博热搜接口，采集总榜、娱乐、生活、社会四个板块的热搜数据
- **数据清洗**：分类体系标准化、艺人字段规范化、敏感内容标记、数值信息提取、特殊字符清理
- **关键词提取**：基于 jieba 中文分词 + NLTK 停用词过滤的准确关键词提取
- **可视化分析**：话题传播路径、用户参与度、热度分布等多维度图表
- **洞察报告**：自动生成数据分析洞察报告（CSV 格式）

## 项目结构

```
微博热搜数据采集项目/
├── 完成代码各部分合集/          # 完整代码（.py 文件）
│   ├── python_grab_code.py     # 数据采集代码
│   ├── python_clean_code.py    # 数据清洗代码
│   └── python_visable_code.py  # 数据可视化与分析代码
├── 测试与运行代码部分/          # 测试与运行代码（.ipynb 文件）
│   ├── 微博热搜数据爬取部分v1.ipynb
│   ├── 微博热搜数据爬取部分v2.ipynb
│   ├── 微博数据清洗部分.ipynb
│   ├── 可视化部分测试代码.ipynb
│   └── 关键词词云.ipynb
├── python_grab_code.txt        # 采集代码（文本格式）
├── python_clean_code.txt       # 清洗代码（文本格式）
├── python_visable_code.txt     # 可视化代码（文本格式）
└── 微博热搜数据采集项目文档.docx  # 项目文档
```

## 技术栈

| 类别 | 技术 |
|------|------|
| 数据采集 | requests、BeautifulSoup |
| 数据处理 | pandas、numpy |
| 中文分词 | jieba、NLTK |
| 可视化 | matplotlib、seaborn、wordcloud |
| 数据存储 | CSV、JSON、openpyxl |

## 快速开始

### 环境依赖

```bash
pip install requests beautifulsoup4 pandas numpy jieba nltk matplotlib seaborn wordcloud openpyxl
```

### 运行步骤

1. **采集数据**：运行 `python_grab_code.py`，需替换为你的有效微博 Cookie
2. **清洗数据**：运行 `python_clean_code.py`，对采集的数据进行分类标准化与特征提取
3. **可视化分析**：运行 `python_visable_code.py`，生成传播路径、参与度分析图表与洞察报告

## 数据流程

```
微博热搜接口 → JSON 数据 → CSV 原始数据 → 数据清洗 → 清洗后 CSV → 可视化分析 → 图表 + 洞察报告
```

## 主要功能模块

### 数据采集（python_grab_code.py）

- `get_life_json()`：采集生活榜热搜数据
- `get_social_json()`：采集社会榜热搜数据
- `get_entertainment_json()`：采集娱乐榜热搜数据
- `process_lifeAndSocial_json_to_csv()`：生活/社会榜 JSON 转 CSV
- `process_entertainment_json_to_csv()`：娱乐榜 JSON 转 CSV

### 数据清洗（python_clean_code.py）

- `clean_entertainment_hotsearch()`：娱乐榜数据清洗（分类细化、艺人标准化）
- `clean_life_hotsearch_final()`：生活榜数据清洗（分类标准化、关键词提取）
- `clean_social_hotsearch_final()`：社会榜数据清洗（敏感内容标记、数值提取）
- `clean_total_hotsearch_final()`：总榜数据清洗（基于内容自动分类）

### 可视化分析（python_visable_code.py）

- `take_content_into_txt()`：提取内容到文本文件
- `extract_keywords_from_txt()`：基于 jieba 的关键词提取
- `analyze_topic_propagation()`：话题传播路径分析
- `create_propagation_visualizations()`：传播路径可视化
- `analyze_user_engagement_patterns()`：用户参与度分析
- `generate_insights_report()`：洞察报告生成

## 注意事项

- 微博热搜接口需要有效的 Cookie 才能访问，使用前请替换代码中的 Cookie
- 请遵守微博的相关服务条款与 robots 协议，合理控制请求频率
- 数据采集仅供学习研究使用，请勿用于商业用途

## License

本项目仅供学习交流使用。
