# 🟣 Polymarket 预测市场数据查询工具

[English](#-polymarket-prediction-market-scraper) | [中文](#-polymarket-预测市场数据查询工具)

---

## 🟣 Polymarket Prediction Market Scraper

A free API-based tool for querying Polymarket prediction market data.

### Features

- 📊 List active markets (sorted by volume)
- 🔍 Search markets by keywords
- 📈 View market details (order book, recent trades)
- 💰 Get real-time prices
- 🏷️ Filter by tags (crypto, sports, politics, finance, etc.)
- 📅 Sort by volume24hr, volume1wk, or endDate

### Installation

```bash
git clone https://github.com/wclxs11/polymarket-scrapling.git
cd polymarket-scrapling
pip install -r requirements.txt
```

### Usage

#### Command Line

```bash
python main.py
```

Options:
1. **List Active Markets** - Show Top 10 popular markets
2. **Search Markets** - Search by keyword
3. **View Market Details** - Input Condition ID to view order book and trades

#### Python Code

```python
from polymarket_client import PolymarketClient, query_markets

client = PolymarketClient()

# Query crypto markets by 24h volume
rows = query_markets(
    client,
    tag_slug='crypto',
    related_tags=True,
    top_n=10,
    sort_field='volume24hr',
)

for r in rows:
    print(r['question'], r.get('volume24hr'))
```

### Available Tags

| Tag | Description |
|-----|-------------|
| crypto | Cryptocurrency |
| sports | Sports |
| politics | Politics |
| finance | Finance/Economics |
| entertainment | Entertainment |
| weather | Weather/Climate |
| science | Science |

### Free API

Based on [Polymarket API](https://docs.polymarket.com/):

| Endpoint | Free | Rate Limit |
|----------|------|-------------|
| Market Data | ✅ | 1000/hour |
| Price Query | ✅ | 1000/hour |
| Order Book | ✅ | 1000/hour |
| Trade History | ✅ | 1000/hour |

### Example Output

```
🟣 Polymarket Query Tool
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. List Active Markets (Top 10)
2. Search Markets
3. View Market Details
4. Exit
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Will BTC reach $100k by end of 2026?
   ID: 0x1234...
   Volume 24h: $1,234,567
   Liquidity: $98,765
   🟢 Yes: 45.2%
   🔴 No:  54.8%
```

### Tech Stack

- Python 3
- requests
- Polymarket CLOB API

---

## 🟣 Polymarket 预测市场数据查询工具

基于官方免费 API 查询 Polymarket 预测市场数据。

### 功能

- 📊 列出活跃市场（按成交量排序）
- 🔍 搜索市场
- 📈 查看市场详情（订单簿、最近成交）
- 💰 获取实时价格
- 🏷️ 按标签筛选（加密货币、体育、政治、金融等）
- 📅 按成交量、流动性、结束时间排序

### 安装

```bash
git clone https://github.com/wclxs11/polymarket-scrapling.git
cd polymarket-scrapling
pip install -r requirements.txt
```

### 使用方法

#### 命令行

```bash
python main.py
```

选项：
1. **列出活跃市场** - 显示 Top 10 热门市场
2. **搜索市场** - 按关键词搜索
3. **查看市场详情** - 输入 Condition ID 查看订单簿和成交

#### Python 代码

```python
from polymarket_client import PolymarketClient, query_markets

client = PolymarketClient()

# 查询加密货币24h成交前10
rows = query_markets(
    client,
    tag_slug='crypto',
    related_tags=True,
    top_n=10,
    sort_field='volume24hr',
)

for r in rows:
    print(r['question'], r.get('volume24hr'))
```

### 可用标签

| 标签 | 说明 |
|------|------|
| crypto | 加密货币 |
| sports | 体育 |
| politics | 政治 |
| finance | 金融/经济 |
| entertainment | 娱乐 |
| weather | 天气/气候 |
| science | 科学 |

### 免费 API

基于 [Polymarket API 文档](https://docs.polymarket.com/):

| 接口 | 免费 | 速率限制 |
|------|------|----------|
| 市场数据 | ✅ | 1000次/小时 |
| 价格查询 | ✅ | 1000次/小时 |
| 订单簿 | ✅ | 1000次/小时 |
| 成交记录 | ✅ | 1000次/小时 |

### 示例输出

```
🟣 Polymarket 市场查询工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 列出活跃市场 (Top 10)
2. 搜索市场
3. 查看市场详情
4. 退出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Will BTC reach $100k by end of 2026?
   ID: 0x1234...
   成交量: $1,234,567
   流动性: $98,765
   🟢 Yes: 45.2%
   🔴 No:  54.8%
```

### 技术栈

- Python 3
- requests
- Polymarket CLOB API

---

Made with ❤️ for free market data exploration
