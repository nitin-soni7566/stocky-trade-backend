import csv
import io
import zipfile

import httpx
from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instrument import Instrument

MASTER_URLS = {
    "nsecash": "https://app.definedgesecurities.com/public/nsecash.zip",
    "nsefno": "https://app.definedgesecurities.com/public/nsefno.zip",
    "allmaster": "https://app.definedgesecurities.com/public/allmaster.zip",
}


async def download_master_file(db: AsyncSession, master: str = "nsecash") -> dict:
    url = MASTER_URLS.get(master)
    if not url:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported master file")

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(url)
    response.raise_for_status()

    count = 0
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        for name in archive.namelist():
            if not name.lower().endswith((".csv", ".txt")):
                continue
            with archive.open(name) as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8", errors="ignore")
                reader = csv.DictReader(text)
                for row in reader:
                    record = _instrument_from_row(row)
                    if not record["token"]:
                        continue
                    stmt = insert(Instrument).values(**record)
                    stmt = stmt.on_conflict_do_update(
                        constraint="uq_instruments_exchange_token",
                        set_={
                            "symbol": stmt.excluded.symbol,
                            "tradingsymbol": stmt.excluded.tradingsymbol,
                            "name": stmt.excluded.name,
                            "instrument_type": stmt.excluded.instrument_type,
                            "lot_size": stmt.excluded.lot_size,
                        },
                    )
                    await db.execute(stmt)
                    count += 1
    await db.commit()
    return {"master": master, "imported": count}


async def search_instruments(db: AsyncSession, query: str, limit: int = 25) -> list[Instrument]:
    pattern = f"%{query}%"
    result = await db.execute(
        select(Instrument)
        .where(
            or_(
                Instrument.symbol.ilike(pattern),
                Instrument.tradingsymbol.ilike(pattern),
                Instrument.name.ilike(pattern),
                Instrument.token == query,
            )
        )
        .order_by(Instrument.exchange, Instrument.tradingsymbol)
        .limit(limit)
    )
    return list(result.scalars().all())


def _instrument_from_row(row: dict) -> dict:
    normalized = {str(key).strip().lower(): value for key, value in row.items() if key is not None}
    token = _pick(normalized, "token", "instrument_token", "security_token")
    exchange = _pick(normalized, "exchange", "exch", "segment") or "NSE"
    lot_size = _pick(normalized, "lot_size", "lotsize", "lot")
    return {
        "exchange": str(exchange).upper(),
        "token": str(token).strip() if token else "",
        "symbol": _pick(normalized, "symbol", "symname"),
        "tradingsymbol": _pick(normalized, "tradingsymbol", "trading_symbol", "symbol"),
        "name": _pick(normalized, "company", "name", "description"),
        "instrument_type": _pick(normalized, "instrument_type", "insttype", "series"),
        "lot_size": int(lot_size) if str(lot_size or "").isdigit() else None,
    }


def _pick(row: dict, *keys: str):
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value).strip()
    return None
