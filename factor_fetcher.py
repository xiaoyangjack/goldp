# -*- coding: utf-8 -*-
"""
宏观与关联因子采集（真实数据源，经 akshare）

与黄金（人民币计价）常见相关的日频或可对齐因子：
- 美元指数 DXY：美元强弱，与金价常呈一定反向（非绝对）
- 离岸人民币 USD/CNH：影响人民币标价黄金的汇率项
- 上金所 Ag99.99：金银比、白银工业属性参照
- Shibor 隔夜：国内短端利率与流动性
- 上证综指：国内风险资产情绪（与黄金关系不稳定，作参考）

输出：与主数据按交易日左对齐合并后的宽表，便于回测/特征工程。
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

import pandas as pd
from loguru import logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak

    AK_AVAILABLE = True
except ImportError:
    AK_AVAILABLE = False


def _resolve_path(p: str) -> str:
    if not p:
        return p
    if os.path.isabs(p):
        return p
    return os.path.join(BASE_DIR, p)


def _try_fetch(name: str, fn, *args, **kwargs) -> Optional[pd.DataFrame]:
    try:
        df = fn(*args, **kwargs)
        if df is None or df.empty:
            logger.warning(f"[factors] {name}: 空数据")
            return None
        return df
    except Exception as e:
        logger.error(f"[factors] {name} 获取失败: {e}")
        return None


def fetch_dxy() -> Optional[pd.DataFrame]:
    """东方财富 美元指数 日行情"""
    df = _try_fetch("dxy", ak.index_global_hist_em, symbol="美元指数")
    if df is None:
        return None
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["日期"], errors="coerce").dt.normalize(),
            "dxy_close": pd.to_numeric(df["最新价"], errors="coerce"),
        }
    )
    return out.dropna(subset=["date"]).drop_duplicates("date", keep="last")


def fetch_usdcnh() -> Optional[pd.DataFrame]:
    """东方财富 USD/CNH 日行情"""
    df = _try_fetch("usdcnh", ak.forex_hist_em, symbol="USDCNH")
    if df is None:
        return None
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["日期"], errors="coerce").dt.normalize(),
            "usdcnh_close": pd.to_numeric(df["最新价"], errors="coerce"),
        }
    )
    return out.dropna(subset=["date"]).drop_duplicates("date", keep="last")


def fetch_ag99() -> Optional[pd.DataFrame]:
    """上金所 Ag99.99 现货历史（元/千克与 SGE 一致）"""
    df = _try_fetch("ag99", ak.spot_hist_sge, symbol="Ag99.99")
    if df is None:
        return None
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"], errors="coerce").dt.normalize(),
            "ag99_close": pd.to_numeric(df["close"], errors="coerce"),
        }
    )
    return out.dropna(subset=["date"]).drop_duplicates("date", keep="last")


def fetch_shibor_overnight() -> Optional[pd.DataFrame]:
    """Shibor 隔夜（%）"""
    df = _try_fetch(
        "shibor_overnight",
        ak.rate_interbank,
        market="上海银行同业拆借市场",
        symbol="Shibor人民币",
        indicator="隔夜",
    )
    if df is None:
        return None
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["报告日"], errors="coerce").dt.normalize(),
            "shibor_overnight": pd.to_numeric(df["利率"], errors="coerce"),
        }
    )
    return out.dropna(subset=["date"]).drop_duplicates("date", keep="last")


def fetch_sse_index() -> Optional[pd.DataFrame]:
    """上证综指 sh000001 日收盘"""
    df = _try_fetch(
        "sse",
        ak.stock_zh_index_daily_em,
        symbol="sh000001",
        start_date="19900101",
        end_date="20500101",
    )
    if df is None:
        return None
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"], errors="coerce").dt.normalize(),
            "sse_close": pd.to_numeric(df["close"], errors="coerce"),
        }
    )
    return out.dropna(subset=["date"]).drop_duplicates("date", keep="last")


def build_merged_panel(
    gold_csv_path: Optional[str] = None,
    out_csv_path: Optional[str] = None,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    以黄金主数据日期为轴，左连接各因子；非交易日因子向前填充（仅填充缺口，不跨太久可后续加限制）。
    返回 (panel_df, meta_errors)
    """
    gold_csv_path = _resolve_path(gold_csv_path or os.getenv("DATA_PATH", "data/gold_au9999_verified.csv"))
    if not os.path.exists(gold_csv_path):
        alt = _resolve_path("data/gold_au9999_with_atr.csv")
        if os.path.exists(alt):
            gold_csv_path = alt
        else:
            raise FileNotFoundError(f"未找到黄金数据: {gold_csv_path}")

    gold = pd.read_csv(gold_csv_path)
    if "date" not in gold.columns or "close" not in gold.columns:
        raise ValueError("黄金数据需包含 date, close")
    gold["date"] = pd.to_datetime(gold["date"], errors="coerce").dt.normalize()
    gold = gold.sort_values("date").drop_duplicates("date", keep="last")
    panel = gold[["date", "close"]].rename(columns={"close": "gold_close"})

    meta: Dict[str, str] = {}
    if not AK_AVAILABLE:
        meta["akshare"] = "未安装 akshare，无法拉取因子"
        return panel, meta

    parts: List[pd.DataFrame] = []
    for label, fn in [
        ("dxy", fetch_dxy),
        ("usdcnh", fetch_usdcnh),
        ("ag99", fetch_ag99),
        ("shibor", fetch_shibor_overnight),
        ("sse", fetch_sse_index),
    ]:
        sub = fn()
        if sub is not None:
            parts.append(sub)
        else:
            meta[label] = "获取失败或为空"

    merged = panel
    for sub in parts:
        merged = merged.merge(sub, on="date", how="left")

    factor_cols = [c for c in merged.columns if c not in ("date", "gold_close")]
    merged = merged.sort_values("date")
    merged[factor_cols] = merged[factor_cols].ffill()

    # Au 现货多为元/克；Ag99.99 上金所为 元/千克 → 换算为可比“元/克”后再算金银比
    if "ag99_close" in merged.columns:
        ag_per_g = merged["ag99_close"].astype(float) / 1000.0
        merged["gold_silver_ratio"] = merged["gold_close"] / ag_per_g.replace(0, float("nan"))

    out_csv_path = _resolve_path(out_csv_path or "data/macro_factors_merged.csv")
    os.makedirs(os.path.dirname(out_csv_path), exist_ok=True)
    merged.to_csv(out_csv_path, index=False, encoding="utf-8")
    logger.info(f"[factors] 已写入 {out_csv_path}，行数={len(merged)}")
    meta["output_path"] = out_csv_path
    return merged, meta


def load_merged_panel(path: Optional[str] = None) -> Optional[pd.DataFrame]:
    p = _resolve_path(path or "data/macro_factors_merged.csv")
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    return df
