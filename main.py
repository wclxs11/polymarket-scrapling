#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Polymarket 通用市场查询器
- 发现市场：Gamma API
- 盘口/价格：CLOB read API
- 支持任意 tag / 任意筛选条件 / 任意排序
"""

from __future__ import annotations

import json
import time
import requests
from typing import Any, Dict, List, Optional, Iterable

GAMMA_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"

DEFAULT_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 500


class PolymarketQueryError(Exception):
    pass


class PolymarketClient:
    def __init__(
        self,
        gamma_base: str = GAMMA_BASE,
        clob_base: str = CLOB_BASE,
        timeout: int = DEFAULT_TIMEOUT,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.gamma_base = gamma_base.rstrip("/")
        self.clob_base = clob_base.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def _get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, url: str, json_body: Optional[Dict[str, Any]] = None) -> Any:
        resp = self.session.post(url, json=json_body, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_tag_by_slug(self, slug: str) -> Dict[str, Any]:
        return self._get(f"{self.gamma_base}/tags/slug/{slug}")

    def list_tags(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        return self._get(f"{self.gamma_base}/tags", params={"limit": limit, "offset": offset})

    def resolve_tag_id(self, tag_slug: Optional[str] = None, tag_id: Optional[int] = None) -> Optional[int]:
        if tag_id is not None:
            return int(tag_id)
        if tag_slug:
            tag = self.get_tag_by_slug(tag_slug)
            return int(tag["id"])
        return None

    def list_markets_page(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._get(f"{self.gamma_base}/markets", params=params)

    def list_markets_all(
        self,
        *,
        limit_per_page: int = DEFAULT_PAGE_SIZE,
        max_pages: Optional[int] = None,
        sleep_sec: float = 0.0,
        **filters: Any,
    ) -> List[Dict[str, Any]]:
        all_markets: List[Dict[str, Any]] = []
        offset = int(filters.pop("offset", 0))
        page = 0

        while True:
            params = dict(filters)
            params["limit"] = limit_per_page
            params["offset"] = offset

            batch = self.list_markets_page(params)
            if not batch:
                break

            all_markets.extend(batch)

            if len(batch) < limit_per_page:
                break

            offset += limit_per_page
            page += 1

            if max_pages is not None and page >= max_pages:
                break

            if sleep_sec > 0:
                time.sleep(sleep_sec)

        return all_markets

    def get_order_book(self, token_id: str) -> Dict[str, Any]:
        return self._get(f"{self.clob_base}/book", params={"token_id": token_id})

    def get_market_prices(self, token_ids: List[str], side: Optional[str] = None) -> Any:
        params: Dict[str, Any] = []
        query_params = [("token_ids", tid) for tid in token_ids]
        if side:
            query_params.append(("side", side))
        return self._get(f"{self.clob_base}/prices", params=query_params)

    def get_last_trade_prices(self, token_ids: List[str]) -> Any:
        query_params = [("token_ids", tid) for tid in token_ids]
        return self._get(f"{self.clob_base}/last-trades-prices", params=query_params)


def chunked(items: Iterable[Any], size: int) -> Iterable[List[Any]]:
    buf: List[Any] = []
    for x in items:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def parse_json_maybe(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def parse_clob_token_ids(raw: Any) -> List[str]:
    value = parse_json_maybe(raw)
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    return []


def top_levels(levels: List[Dict[str, Any]], n: int = 3) -> List[Dict[str, float]]:
    out = []
    for lv in levels[:n]:
        out.append(
            {
                "price": safe_float(lv.get("price")),
                "size": safe_float(lv.get("size")),
            }
        )
    return out


def summarize_book(book: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not book:
        return {
            "best_bid": None,
            "best_ask": None,
            "spread": None,
            "last_trade_price": None,
            "bids_top": [],
            "asks_top": [],
        }

    bids = book.get("bids") or []
    asks = book.get("asks") or []

    best_bid = safe_float(bids[0]["price"]) if bids else None
    best_ask = safe_float(asks[0]["price"]) if asks else None
    spread = None
    if best_bid is not None and best_ask is not None:
        spread = best_ask - best_bid

    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "spread": spread,
        "last_trade_price": safe_float(book.get("last_trade_price"), default=None),
        "bids_top": top_levels(bids),
        "asks_top": top_levels(asks),
    }


def market_to_row(m: Dict[str, Any]) -> Dict[str, Any]:
    prices = parse_json_maybe(m.get("outcomePrices"))
    if not isinstance(prices, list):
        prices = []

    clob_token_ids = parse_clob_token_ids(m.get("clobTokenIds"))

    return {
        "id": m.get("id"),
        "slug": m.get("slug"),
        "question": m.get("question"),
        "active": m.get("active"),
        "closed": m.get("closed"),
        "archived": m.get("archived"),
        "enableOrderBook": m.get("enableOrderBook"),
        "liquidity": safe_float(m.get("liquidity")),
        "volume": safe_float(m.get("volume")),
        "volume24hr": safe_float(m.get("volume24hr")),
        "startDate": m.get("startDate"),
        "endDate": m.get("endDate"),
        "outcomePrices": prices,
        "clobTokenIds": clob_token_ids,
        "yesTokenId": clob_token_ids[0] if len(clob_token_ids) > 0 else None,
        "noTokenId": clob_token_ids[1] if len(clob_token_ids) > 1 else None,
        "raw": m,
    }


def enrich_with_books(
    client: PolymarketClient,
    rows: List[Dict[str, Any]],
    *,
    include_books: bool = True,
) -> List[Dict[str, Any]]:
    if not include_books:
        return rows

    for row in rows:
        row["yesBook"] = None
        row["noBook"] = None
        row["yesBookSummary"] = None
        row["noBookSummary"] = None

        if not row.get("enableOrderBook"):
            continue

        yes_token = row.get("yesTokenId")
        no_token = row.get("noTokenId")

        if yes_token:
            try:
                book = client.get_order_book(yes_token)
                row["yesBook"] = book
                row["yesBookSummary"] = summarize_book(book)
            except Exception as e:
                row["yesBookError"] = str(e)

        if no_token:
            try:
                book = client.get_order_book(no_token)
                row["noBook"] = book
                row["noBookSummary"] = summarize_book(book)
            except Exception as e:
                row["noBookError"] = str(e)

    return rows


def query_markets(
    client: PolymarketClient,
    *,
    tag_slug: Optional[str] = None,
    tag_id: Optional[int] = None,
    related_tags: Optional[bool] = None,
    include_books: bool = True,
    top_n: int = 10,
    sort_field: str = "volume24hr",
    descending: bool = True,
    max_pages: Optional[int] = None,
    sleep_sec: float = 0.0,
    extra_filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    filters = dict(extra_filters or {})

    filters.setdefault("closed", "false")
    filters.setdefault("active", "true")

    resolved_tag_id = client.resolve_tag_id(tag_slug=tag_slug, tag_id=tag_id)
    if resolved_tag_id is not None:
        filters["tag_id"] = resolved_tag_id
        if related_tags is not None:
            filters["related_tags"] = str(related_tags).lower()

    markets = client.list_markets_all(
        max_pages=max_pages,
        sleep_sec=sleep_sec,
        **filters,
    )

    rows = [market_to_row(m) for m in markets]

    cleaned = []
    for row in rows:
        if row.get("closed") is True:
            continue
        if row.get("archived") is True:
            continue
        if row.get("active") is False:
            continue
        cleaned.append(row)

    cleaned.sort(
        key=lambda x: safe_float(x.get(sort_field), 0.0),
        reverse=descending,
    )

    cleaned = cleaned[:top_n]
    enrich_with_books(client, cleaned, include_books=include_books)
    return cleaned


def print_market_report(rows: List[Dict[str, Any]]) -> None:
    print("=" * 120)
    print("Polymarket Query Result")
    print("=" * 120)

    for i, row in enumerate(rows, 1):
        print(f"\n{i}. {row['question']}")
        print(f" slug={row.get('slug')}")
        print(
            f" 24h=${row.get('volume24hr', 0):,.2f} | "
            f"liq=${row.get('liquidity', 0):,.2f} | "
            f"enableOrderBook={row.get('enableOrderBook')}"
        )

        prices = row.get("outcomePrices") or []
        if prices:
            try:
                pct = [round(float(x) * 100, 2) for x in prices]
                print(f" outcomePrices={pct}")
            except Exception:
                print(f" outcomePrices={prices}")

        print(f" yesTokenId={row.get('yesTokenId')}")
        print(f" noTokenId={row.get('noTokenId')}")

        if row.get("yesBookSummary"):
            s = row["yesBookSummary"]
            print(
                f" YES book: best_bid={s['best_bid']} best_ask={s['best_ask']} "
                f"spread={s['spread']} last={s['last_trade_price']}"
            )
            print(f" top bids={s['bids_top']}")
            print(f" top asks={s['asks_top']}")

        if row.get("noBookSummary"):
            s = row["noBookSummary"]
            print(
                f" NO book: best_bid={s['best_bid']} best_ask={s['best_ask']} "
                f"spread={s['spread']} last={s['last_trade_price']}"
            )
            print(f" top bids={s['bids_top']}")
            print(f" top asks={s['asks_top']}")

        if row.get("yesBookError"):
            print(f" YES book error: {row['yesBookError']}")
        if row.get("noBookError"):
            print(f" NO book error: {row['noBookError']}")

    print("\n" + "=" * 120)


def main() -> None:
    client = PolymarketClient()

    # 查询 crypto tag 下 24h 成交额前 5
    rows = query_markets(
        client,
        tag_slug="crypto",
        related_tags=True,
        include_books=False,
        top_n=5,
        sort_field="volume24hr",
        descending=True,
    )

    print_market_report(rows)


if __name__ == "__main__":
    main()
