# 🟣 Polymarket 市场查询工具

基于官方免费 API 查询 Polymarket 市场数据。

## 功能

- 📊 列出活跃市场（成交量排序）
- 🔍 搜索市场
- 📈 查看市场详情（订单簿、最近成交）
- 💰 获取实时价格

## 安装

```bash
cd polymarket-query
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

### 选项

1. **列出活跃市场** - 显示 Top 10 热门市场
2. **搜索市场** - 按关键词搜索
3. **查看详情** - 输入 Condition ID 查看订单簿和成交

## 免费 API

基于 [Polymarket API 文档](https://docs.polymarket.com/):

| 接口 | 免费 | 速率限制 |
|------|------|----------|
| 市场数据 | ✅ | 1000次/小时 |
| 价格查询 | ✅ | 1000次/小时 |
| 订单簿 | ✅ | 1000次/小时 |
| 成交记录 | ✅ | 1000次/小时 |

## 示例输出

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

## 技术栈

- Python 3
- requests
- Polymarket CLOB API

---
Made with ❤️ for free market data exploration
