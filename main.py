import os
from typing import Literal

import httpx
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Definedge FastAPI Wrapper")

API_TOKEN = os.getenv("DEFINEDGE_API_TOKEN")
API_SECRET = os.getenv("DEFINEDGE_API_SECRET")
BASE_URL = os.getenv("DEFINEDGE_BASE_URL")
LOGIN_URL = os.getenv("DEFINEDGE_LOGIN_URL")

SESSION = {
    "api_session_key": None,
    "susertoken": None,
    "uid": None,
    "actid": None,
}


class VerifyOtpRequest(BaseModel):
    otp_token: str
    otp: str


class OrderRequest(BaseModel):
    exchange: str = "NSE"
    tradingsymbol: str
    quantity: str
    order_type: Literal["BUY", "SELL"]
    price_type: Literal["MARKET", "LIMIT", "SL-MARKET", "SL-LIMIT"] = "MARKET"
    price: str = "0"
    product_type: Literal["CNC", "INTRADAY", "NORMAL"] = "CNC"
    algo_id: str = "99999"


def auth_headers():
    if not SESSION["api_session_key"]:
        raise HTTPException(status_code=401, detail="Token not generated. Login first.")
    return {"Authorization": SESSION["api_session_key"]}


@app.get("/auth/generate-otp")
async def generate_otp():
    url = f"{LOGIN_URL}/login/{API_TOKEN}"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, headers={"api_secret": API_SECRET})

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    return res.json()


@app.post("/auth/verify-otp")
async def verify_otp(payload: VerifyOtpRequest):
    url = f"{LOGIN_URL}/token"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(
            url,
            json={
                "otp_token": payload.otp_token,
                "otp": payload.otp,
            },
        )

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    data = res.json()

    SESSION["api_session_key"] = data.get("api_session_key")
    SESSION["susertoken"] = data.get("susertoken")
    SESSION["uid"] = data.get("uid")
    SESSION["actid"] = data.get("actid")

    return {
        "message": "Login successful",
        "uid": SESSION["uid"],
        "actid": SESSION["actid"],
        "has_api_session_key": bool(SESSION["api_session_key"]),
        "has_susertoken": bool(SESSION["susertoken"]),
    }


@app.get("/quotes/{exchange}/{token}")
async def get_current_price(exchange: str, token: str):
    url = f"{BASE_URL}/quotes/{exchange}/{token}"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, headers=auth_headers())

    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    return res.json()


@app.post("/orders/place")
async def place_order(payload: OrderRequest):
    url = f"{BASE_URL}/placeorder"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(
            url,
            headers={**auth_headers(), "Content-Type": "application/json"},
            json=payload.model_dump(),
        )

    return res.json()


@app.post("/orders/buy")
async def buy_order(payload: OrderRequest):
    payload.order_type = "BUY"
    return await place_order(payload)


@app.post("/orders/sell")
async def sell_order(payload: OrderRequest):
    payload.order_type = "SELL"
    return await place_order(payload)


@app.get("/orders")
async def order_book():
    url = f"{BASE_URL}/orders"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, headers=auth_headers())

    return res.json()


@app.get("/limits")
async def limits():
    url = f"{BASE_URL}/limits"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, headers=auth_headers())

    return res.json()


@app.get("/nifty50/current-prices")
async def nifty50_current_prices():
    """
    Required file: nifty50_master.csv
    Columns needed: token, symbol, tradingsymbol, company
    """
    df = pd.read_csv("nifty50_master.csv")

    results = []

    async with httpx.AsyncClient(timeout=20) as client:
        for _, row in df.iterrows():
            token = str(row["token"])
            url = f"{BASE_URL}/quotes/NSE/{token}"

            res = await client.get(url, headers=auth_headers())

            if res.status_code == 200:
                data = res.json()
                results.append({
                    "token": token,
                    "symbol": row.get("symbol"),
                    "tradingsymbol": row.get("tradingsymbol"),
                    "company": row.get("company"),
                    "ltp": data.get("ltp"),
                    "day_open": data.get("day_open"),
                    "day_high": data.get("day_high"),
                    "day_low": data.get("day_low"),
                    "volume": data.get("volume"),
                })

    return {
        "count": len(results),
        "data": results,
    }


@app.get("/websocket-details")
async def websocket_details():
    if not SESSION["susertoken"]:
        raise HTTPException(status_code=401, detail="Login first.")

    return {
        "websocket_url": "wss://trade.definedgesecurities.com/NorenWSTRTP/",
        "connect_payload": {
            "t": "c",
            "uid": SESSION["uid"],
            "actid": SESSION["actid"],
            "source": "TRTP",
            "susertoken": SESSION["susertoken"],
        },
    }