from datetime import datetime, timedelta, timezone
from decimal import Decimal

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


class DefinedgeClient:
    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        access_token: str | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = settings.trading_base_url.rstrip("/")
        self.login_url = settings.auth_base_url.rstrip("/")
        self.data_url = settings.definedge_data_base_url.rstrip("/")
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token

    def _auth_headers(self, api_session_key: str | None = None) -> dict[str, str]:
        token = api_session_key or self.access_token
        if not token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Broker access token is missing")
        return {"Authorization": token}

    async def request_otp(self, api_token: str | None = None, api_secret: str | None = None) -> dict:
        self.api_key = api_token or self.api_key
        self.api_secret = api_secret or self.api_secret
        return await self.generate_otp()

    async def generate_otp(self) -> dict:
        if not self.api_key:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Broker API key is missing")
        if not self.api_secret:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Broker API secret is missing")
        if not self.login_url:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DEFINEDGE_LOGIN_URL is missing")

        url = f"{self.login_url}/login/{self.api_key}"
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                url,
                headers={"api_secret": self.api_secret},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    async def verify_otp(self, otp_token: str, otp: str) -> tuple[str, datetime | None, dict]:
        if not self.login_url:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DEFINEDGE_LOGIN_URL is missing")

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.login_url}/token",
                headers={"Content-Type": "application/json"},
                json={"otp_token": otp_token, "otp": otp},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        token = data.get("api_session_key") or data.get("access_token") or data.get("token") or data.get("susertoken")
        if not token:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Definedge token was not returned")

        expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
        return token, expires_at, data

    async def get_profile(self) -> dict:
        if not self.base_url:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DEFINEDGE_BASE_URL is missing")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}/profile", headers=self._auth_headers())
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def get_quotes(self, exchange: str, token: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/quotes/{exchange.upper()}/{token}",
                headers=self._auth_headers(),
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def get_security_info(self, exchange: str, token: str) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/securityinfo/{exchange.upper()}/{token}",
                headers=self._auth_headers(),
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def get_history(self, segment: str, token: str, timeframe: str, from_date: str, to_date: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.data_url}/history/{segment}/{token}/{timeframe}/{from_date}/{to_date}",
                headers=self._auth_headers(),
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def get_orders(self, api_session_key: str | None = None) -> dict:
        return await self._get_account_resource("/orders", api_session_key)

    async def get_single_order(self, api_session_key: str | None, order_id: str) -> dict:
        return await self._get_account_resource(f"/order/{order_id}", api_session_key)

    async def get_trades(self, api_session_key: str | None = None) -> dict:
        return await self._get_account_resource("/trades", api_session_key)

    async def get_positions(self, api_session_key: str | None = None) -> dict:
        return await self._get_account_resource("/positions", api_session_key)

    async def get_holdings(self, api_session_key: str | None = None) -> dict:
        return await self._get_account_resource("/holdings", api_session_key)

    async def get_limits(self, api_session_key: str | None = None) -> dict:
        return await self._get_account_resource("/limits", api_session_key)

    async def get_margin(self, api_session_key: str | None, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/margin",
                headers=self._auth_headers(api_session_key),
                json=payload,
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def _get_account_resource(self, path: str, api_session_key: str | None = None) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}{path}", headers=self._auth_headers(api_session_key))
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def get_nifty50_stocks(self) -> list[dict]:
        return [
            {"symbol": "ADANIENT", "name": "Adani Enterprises"},
            {"symbol": "ADANIPORTS", "name": "Adani Ports and SEZ"},
            {"symbol": "APOLLOHOSP", "name": "Apollo Hospitals"},
            {"symbol": "ASIANPAINT", "name": "Asian Paints"},
            {"symbol": "AXISBANK", "name": "Axis Bank"},
            {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto"},
            {"symbol": "BAJFINANCE", "name": "Bajaj Finance"},
            {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv"},
            {"symbol": "BEL", "name": "Bharat Electronics"},
            {"symbol": "BHARTIARTL", "name": "Bharti Airtel"},
            {"symbol": "CIPLA", "name": "Cipla"},
            {"symbol": "COALINDIA", "name": "Coal India"},
            {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories"},
            {"symbol": "EICHERMOT", "name": "Eicher Motors"},
            {"symbol": "ETERNAL", "name": "Eternal"},
            {"symbol": "GRASIM", "name": "Grasim Industries"},
            {"symbol": "HCLTECH", "name": "HCL Technologies"},
            {"symbol": "HDFCBANK", "name": "HDFC Bank"},
            {"symbol": "HDFCLIFE", "name": "HDFC Life Insurance"},
            {"symbol": "HINDALCO", "name": "Hindalco Industries"},
            {"symbol": "HINDUNILVR", "name": "Hindustan Unilever"},
            {"symbol": "ICICIBANK", "name": "ICICI Bank"},
            {"symbol": "INDIGO", "name": "InterGlobe Aviation"},
            {"symbol": "INFY", "name": "Infosys"},
            {"symbol": "ITC", "name": "ITC"},
            {"symbol": "JIOFIN", "name": "Jio Financial Services"},
            {"symbol": "JSWSTEEL", "name": "JSW Steel"},
            {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank"},
            {"symbol": "LT", "name": "Larsen and Toubro"},
            {"symbol": "M&M", "name": "Mahindra and Mahindra"},
            {"symbol": "MARUTI", "name": "Maruti Suzuki"},
            {"symbol": "MAXHEALTH", "name": "Max Healthcare Institute"},
            {"symbol": "NESTLEIND", "name": "Nestle India"},
            {"symbol": "NTPC", "name": "NTPC"},
            {"symbol": "ONGC", "name": "ONGC"},
            {"symbol": "POWERGRID", "name": "Power Grid Corporation"},
            {"symbol": "RELIANCE", "name": "Reliance Industries"},
            {"symbol": "SBILIFE", "name": "SBI Life Insurance"},
            {"symbol": "SHRIRAMFIN", "name": "Shriram Finance"},
            {"symbol": "SBIN", "name": "State Bank of India"},
            {"symbol": "SUNPHARMA", "name": "Sun Pharma"},
            {"symbol": "TCS", "name": "Tata Consultancy Services"},
            {"symbol": "TATACONSUM", "name": "Tata Consumer Products"},
            {"symbol": "TMPV", "name": "Tata Motors Passenger Vehicles"},
            {"symbol": "TATASTEEL", "name": "Tata Steel"},
            {"symbol": "TECHM", "name": "Tech Mahindra"},
            {"symbol": "TITAN", "name": "Titan Company"},
            {"symbol": "TRENT", "name": "Trent"},
            {"symbol": "ULTRACEMCO", "name": "UltraTech Cement"},
            {"symbol": "WIPRO", "name": "Wipro"},
        ]

    async def get_ltp(self, symbol: str) -> tuple[Decimal, dict]:
        if not self.base_url:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DEFINEDGE_BASE_URL is missing")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}/quotes/NSE/{symbol.upper()}", headers=self._auth_headers())
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        value = data.get("ltp") or data.get("last_price") or data.get("price")
        if value is None:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Definedge LTP was not returned")
        return Decimal(str(value)), data

    async def place_order(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/placeorder", payload, api_session_key)

    async def modify_order(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/modify", payload, api_session_key)

    async def cancel_order(self, order_id: str, api_session_key: str | None = None) -> dict:
        if not get_settings().enable_live_trading:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Live trading is disabled for Phase 1")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{self.base_url}/cancel/{order_id}",
                headers=self._auth_headers(api_session_key),
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def slice_order(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/sliceorder", payload, api_session_key)

    async def product_conversion(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/productconversion", payload, api_session_key)

    async def gtt_place_order(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/gttplaceorder", payload, api_session_key)

    async def gtt_orders(self, api_session_key: str | None = None) -> dict:
        return await self._get_account_resource("/gttorders", api_session_key)

    async def gtt_modify(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/gttmodify", payload, api_session_key)

    async def gtt_cancel(self, alert_id: str, api_session_key: str | None = None) -> dict:
        return await self._live_get(f"/gttcancel/{alert_id}", api_session_key)

    async def oco_place_order(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/ocoplaceorder", payload, api_session_key)

    async def oco_modify(self, payload: dict, api_session_key: str | None = None) -> dict:
        return await self._live_post("/ocomodify", payload, api_session_key)

    async def oco_cancel(self, alert_id: str, api_session_key: str | None = None) -> dict:
        return await self._live_get(f"/ococancel/{alert_id}", api_session_key)

    async def _live_post(self, path: str, payload: dict, api_session_key: str | None = None) -> dict:
        if not get_settings().enable_live_trading:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Live trading is disabled for Phase 1")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                headers=self._auth_headers(api_session_key),
                json=payload,
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()

    async def _live_get(self, path: str, api_session_key: str | None = None) -> dict:
        if not get_settings().enable_live_trading:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Live trading is disabled for Phase 1")
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(f"{self.base_url}{path}", headers=self._auth_headers(api_session_key))
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
