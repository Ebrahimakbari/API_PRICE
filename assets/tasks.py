import requests
from celery import shared_task
from fake_useragent import UserAgent
from decouple import config
from .models import Asset, AssetPriceLog
from decimal import Decimal, InvalidOperation
import pytz 
from datetime import datetime 






BASE_API_ASSETS = config('BASE_API_ASSETS')

ua = UserAgent()
def clean_price(price_str):
    """Safely cleans and converts a string to a Decimal."""
    if not isinstance(price_str, str):
        price_str = str(price_str)
    try:
        return Decimal(price_str.replace(',', ''))
    except (InvalidOperation, ValueError, TypeError):
        return None

def determine_category(symbol: str) -> str:
    """
    Analyzes the asset symbol to determine its category.
    This logic is based on patterns found in the ajax.json file.
    """
    s = symbol.lower()
    if s.startswith('seke') or s.startswith('coin') or s.startswith('rob') or s.startswith('nim'):
        return 'COIN'
    if s.startswith('crypto-') and s.endswith('-irr'):
        return 'CRYPTO_IRR'
    if s.startswith('crypto-'):
        return 'CRYPTO_USD'
    if s.endswith('-irr'): # For other cryptos like btc-irr, eth-irr
        return 'CRYPTO_IRR'
    if s.startswith('price_'):
        return 'CURRENCY_IRR'
    if 'gold' in s or 'mesghal' in s or s.startswith('geram'):
        return 'GOLD'
    if 'silver' in s or 'platinum' in s or 'palladium' in s:
        return 'METAL'
    if s.startswith('bourse') or 'dow_jones' in s or 'nasdaq' in s:
        return 'INDEX'
    if s.startswith('commodity_') or 'oil' in s:
        return 'COMMODITY'
    if '-usd-ask' in s or 'diff_' in s:
        return 'CURRENCY_FX'
    if 'ons' in s or 'aluminium' in s or 'copper' in s or 'zinc' in s:
        return 'METAL'
    return 'OTHER'

@shared_task
def scrape_assets_prices():
    """
    Scrapes price data with the new, improved categorization logic.
    """
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(BASE_API_ASSETS, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return f"Error fetching asset API: {e}"

    tehran_tz = pytz.timezone('Asia/Tehran')
    name_map = {}
    metadata_lists = data.get('last', []) + data.get('tolerance_high', []) + data.get('tolerance_low', [])
    for item in metadata_lists:
        symbol = item.get('name')
        if symbol and symbol not in name_map:
            name_map[symbol] = {
                'name_fa': item.get('title'),
                'name_en': item.get('title_en')
            }

    assets_data = data.get('current', {})
    new_logs_count = 0

    for symbol, details in assets_data.items():
        price = clean_price(details.get('p'))
        timestamp_str = details.get('ts')

        if price is None or not timestamp_str:
            continue
            
        try:
            naive_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            aware_dt = tehran_tz.localize(naive_dt)
        except (ValueError, TypeError):
            continue

        asset_names = name_map.get(symbol, {})
        name_fa = asset_names.get('name_fa') or symbol.replace('_', ' ').title()
        name_en = asset_names.get('name_en') or symbol.replace('_', ' ').title()
        
        category = determine_category(symbol)

        asset, _ = Asset.objects.get_or_create(
            symbol=symbol,
            defaults={'name_fa': name_fa, 'name_en': name_en, 'category': category}
        )

        _, log_created = AssetPriceLog.objects.get_or_create(
            asset=asset,
            timestamp=aware_dt,
            defaults={
                'price': price,
                'high': clean_price(details.get('h', 0)),
                'low': clean_price(details.get('l', 0)),
                'change_amount': clean_price(details.get('d', 0)),
                'change_percent': details.get('dp', 0),
            }
        )
        if log_created:
            new_logs_count += 1

    return f"Asset scraping finished. Created {new_logs_count} new price logs."