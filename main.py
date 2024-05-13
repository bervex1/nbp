import sys
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, List

class NBPApiClient:
    """Klient do obsługi API Narodowego Banku Polskiego."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url

    async def get_rates(self, start_date: str, end_date: str) -> Optional[List[dict]]:
        """Pobiera kursy wymiany walut dla danego zakresu dat."""
        url = f"{self.base_url}{start_date}/{end_date}/?format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    print(f"Brak danych dla zakresu dat {start_date} - {end_date}")
                    return None
                else:
                    raise RuntimeError(f"Błąd pobierania danych: {response.status}")

class CurrencyExchangeTool:
    """Narzędzie do pobierania kursów wymiany walut."""

    def __init__(self, api_client: NBPApiClient, max_days: int) -> None:
        self.api_client = api_client
        self.max_days = max_days

    async def get_exchange_rates(self, start_date: str, end_date: str) -> Optional[dict]:
        """Pobiera kursy wymiany walut dla danego zakresu dat."""
        tasks = [self.api_client.get_rates(start_date, end_date)]
        return await asyncio.gather(*tasks)

    async def print_exchange_rates(self, start_date: str, end_date: str) -> None:
        """Wyświetla kursy wymiany walut dla danego zakresu dat."""
        results = await self.get_exchange_rates(start_date, end_date)
        print(f"Dane dla zakresu dat {start_date} - {end_date}:")
        if results[0] is not None:
            for entry in results[0]:
                for currency in entry["rates"]:
                    if currency['code'] in ('EUR', 'USD'):
                        if currency.get("ask") is not None and currency.get("bid") is not None:
                            print(f"{currency['currency']:4} {currency['code']:3} Kurs kupna: {currency['ask']:.4f}, Kurs sprzedaży: {currency['bid']:.4f}")
                        else:
                            print(f"{currency['currency']:4} {currency['code']:3} Brak danych")
    print()

if __name__ == "__main__":
    try:
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        if days > 10:
            raise ValueError("Liczba dni nie może być większa niż 10")
        end_date = datetime.today().strftime("%Y-%m-%d")
        start_date = (datetime.today() - timedelta(days=days-1)).strftime("%Y-%m-%d")
        api_client = NBPApiClient("http://api.nbp.pl/api/exchangerates/tables/c/")
        exchange_tool = CurrencyExchangeTool(api_client, 10)
        asyncio.run(exchange_tool.print_exchange_rates(start_date, end_date))
    except (ValueError, IndexError) as e:
        print(f"Błąd: {e}. Użycie: python main.py <liczba_dni>")



