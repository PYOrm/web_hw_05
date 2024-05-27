import asyncio
import datetime
import json
import sys

import aiohttp


class PrivateBankHandler:
    max_period = 10
    period = 0
    curency_set = None
    base_url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
    receive_data = list()

    def __init__(self, period: int = 10):
        self.period = period if period < self.max_period else self.max_period
        self.curency_set = ("EUR", "USD")

    async def async_client_request(self, session: aiohttp.ClientSession, url: str):
        try:
            response = await session.get(url)
            if response.status == 200:
                return json.loads(await response.text())
        except aiohttp.ClientConnectorError:
            return None

    def next_url(self):
        today = datetime.date.today()
        for d in range(0, self.period):
            day = today - datetime.timedelta(days=d)
            yield f"{self.base_url}{day.strftime("%d.%m.%Y")}"

    def parse_response(self, data: dict):
        exchange_rate = dict()
        for row in data.get("exchangeRate"):
            if row.get("currency") in self.curency_set:
                exchange_rate[row.get("currency")] = {"sale": row.get("saleRate"), "purchase": row.get("purchaseRate")}
        return {data.get("date"): exchange_rate}

    def __str__(self):
        res = ""
        for row in self.receive_data:
            res += str(row) + "\n"
        return res

    async def run(self):
        async with aiohttp.ClientSession() as session:
            for url in self.next_url():
                get_resp = await self.async_client_request(session, url)
                pars_resp = self.parse_response(get_resp)
                self.receive_data.append(pars_resp)


def main(period):
    ut = PrivateBankHandler(period=period)
    asyncio.run(ut.run())
    print(ut)


if __name__ == "__main__":
    try:
        period = int(sys.argv[1])
        main(period)
    except ValueError as e:
        print(e)
