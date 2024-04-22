import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, List

class NBPApiClient:
    """Klient do obsługi API Narodowego Banku Polskiego."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def get_rates(self, date: str) -> Optional[List[dict]]:
        """Pobiera kursy wymiany walut dla danego dnia."""
        url = f"{self.base_url}{date}?format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    print(f"Brak danych dla dnia {date}")
                    return None
                else:
                    raise RuntimeError(f"Błąd pobierania danych: {response.status}")

class CurrencyExchangeTool:
    """Narzędzie do pobierania kursów wymiany walut."""

    def __init__(self, api_client: NBPApiClient, max_days: int) -> None:
        self.api_client = api_client
        self.max_days = max_days

    async def get_exchange_rates(self, days: int) -> Optional[dict]:
        """Pobiera kursy wymiany walut z ostatnich kilku dni."""
        today = datetime.today()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, min(days, self.max_days) + 1)]
        tasks = [self.api_client.get_rates(date) for date in dates]
        return await asyncio.gather(*tasks)

    async def print_exchange_rates(self, days: int) -> None:
        """Wyświetla kursy wymiany walut."""
        results = await self.get_exchange_rates(days)
        for i, result in enumerate(results, 1):
            print(f"Dane z dnia {datetime.today() - timedelta(days=i)}:")
            if result is not None:
                for entry in result:
                    for currency in entry["rates"]:
                        if currency["code"] in ["EUR", "USD"]:
                            print(f"{currency['currency']:4} {currency['code']:3} {currency['mid']:.4f}")
            print()

if __name__ == "__main__":
    try:
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        if days > 10:
            raise ValueError("Liczba dni nie może być większa niż 10")
        api_client = NBPApiClient("https://api.nbp.pl/api/exchangerates/tables/a/")
        exchange_tool = CurrencyExchangeTool(api_client, 10)
        asyncio.run(exchange_tool.print_exchange_rates(days))
    except (ValueError, IndexError) as e:
        print(f"Błąd: {e}. Użycie: python main.py <liczba_dni>")
