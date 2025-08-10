from __future__ import annotations

import os
from typing import Any, Dict, List, Sequence

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Config por env (com defaults)
YAHOO_BASE_URL = os.getenv("YAHOO_BASE_URL", "https://query1.finance.yahoo.com")
YAHOO_TIMEOUT_SECONDS = float(os.getenv("YAHOO_TIMEOUT_SECONDS", "8"))
YAHOO_RETRIES = int(os.getenv("YAHOO_RETRIES", "3"))
YAHOO_BACKOFF_MULTIPLIER = float(os.getenv("YAHOO_BACKOFF_MULTIPLIER", "0.8"))
YAHOO_BACKOFF_MIN = float(os.getenv("YAHOO_BACKOFF_MIN", "0.5"))
YAHOO_BACKOFF_MAX = float(os.getenv("YAHOO_BACKOFF_MAX", "4.0"))


class YahooError(RuntimeError):
    """Erro de integração Yahoo Finance."""


def _symbols_to_str(symbols: Sequence[str]) -> str:
    """Normaliza e junta símbolos (AAPL,MSFT,...)"""
    unique = {s.strip().upper() for s in symbols if s and s.strip()}
    return ",".join(sorted(unique))


class YahooClient:
    """Cliente async p/ Yahoo Finance (search + quotes) com retry/backoff."""

    def __init__(self, timeout: float | None = None, base_url: str | None = None):
        self._timeout = timeout or YAHOO_TIMEOUT_SECONDS
        self._base_url = base_url or YAHOO_BASE_URL
        self._client = httpx.AsyncClient(  # HTTP/2 reduz latência
            base_url=self._base_url,
            http2=True,
            timeout=self._timeout,
            headers={
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (compatible; DK-AnkaTech/1.0)",
            },
        )

    async def aclose(self):
        await self._client.aclose()

    @retry(
        reraise=True,
        stop=stop_after_attempt(YAHOO_RETRIES),
        wait=wait_exponential(
            multiplier=YAHOO_BACKOFF_MULTIPLIER, min=YAHOO_BACKOFF_MIN, max=YAHOO_BACKOFF_MAX
        ),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def search(self, query: str, quotes_count: int = 10) -> List[Dict[str, Any]]:
        """Busca por texto e retorna itens sanitizados (symbol, names, exch*, typeDisp)."""
        if not query or not query.strip():
            return []

        params = {"q": query.strip(), "quotesCount": quotes_count, "newsCount": 0}
        try:
            r = await self._client.get("/v1/finance/search", params=params)
            r.raise_for_status()
            data = r.json() or {}
            quotes = data.get("quotes") or []
            sanitized: List[Dict[str, Any]] = []
            for item in quotes:
                sym = (item.get("symbol") or "").strip()
                if not sym:
                    continue
                sanitized.append(
                    {
                        "symbol": sym.upper(),
                        "shortname": item.get("shortname"),
                        "longname": item.get("longname"),
                        "exch": item.get("exch"),
                        "exchDisp": item.get("exchDisp"),
                        "typeDisp": item.get("typeDisp"),
                    }
                )
            return sanitized
        except httpx.HTTPError as e:
            raise YahooError(f"Yahoo search failed: {e}") from e

    @retry(
        reraise=True,
        stop=stop_after_attempt(YAHOO_RETRIES),
        wait=wait_exponential(
            multiplier=YAHOO_BACKOFF_MULTIPLIER, min=YAHOO_BACKOFF_MIN, max=YAHOO_BACKOFF_MAX
        ),
        retry=retry_if_exception_type(httpx.HTTPError),
    )
    async def quotes(self, symbols: Sequence[str]) -> Dict[str, Dict[str, Any]]:
        """Cotações para múltiplos símbolos. Chave do dict = símbolo UPPER."""
        if not symbols:
            return {}

        params = {"symbols": _symbols_to_str(symbols)}
        if not params["symbols"]:
            return {}

        try:
            r = await self._client.get("/v7/finance/quote", params=params)
            r.raise_for_status()
            payload = r.json() or {}
            result_raw = (payload.get("quoteResponse") or {}).get("result") or []
            out: Dict[str, Dict[str, Any]] = {}
            for q in result_raw:
                sym = (q.get("symbol") or "").strip().upper()
                if not sym:
                    continue
                out[sym] = q
            return out
        except httpx.HTTPError as e:
            raise YahooError(f"Yahoo quotes failed: {e}") from e


# DI (singleton) p/ FastAPI
_yahoo_singleton: YahooClient | None = None

async def get_yahoo() -> YahooClient:
    """Retorna instância singleton do YahooClient."""
    global _yahoo_singleton
    if _yahoo_singleton is None:
        _yahoo_singleton = YahooClient()
    return _yahoo_singleton

async def close_yahoo_client():
    """Fecha httpx.AsyncClient no shutdown."""
    global _yahoo_singleton
    if _yahoo_singleton is not None:
        await _yahoo_singleton.aclose()
        _yahoo_singleton = None
