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

@shared_task
def scrape_assets_prices():
    """
    Scrapes price data and saves timezone-aware timestamps to the database.
    """
    headers = {
        'User-Agent': ua.random,
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://www.tgju.org/',
    }
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
        high = clean_price(details.get('h'))
        low = clean_price(details.get('l'))
        change_amount = clean_price(details.get('d'))
        timestamp_str = details.get('ts')

        if price is None or high is None or low is None or change_amount is None or not timestamp_str:
            continue
            
        try:
            # 1. Parse the string into a naive datetime object
            naive_dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            # 2. Localize the naive datetime, making it aware of the Tehran timezone
            aware_dt = tehran_tz.localize(naive_dt)
        except (ValueError, TypeError):
            # If the timestamp format is ever wrong, skip this item
            print(f"Warning: Could not parse timestamp for {symbol}: {timestamp_str}")
            continue

        asset_names = name_map.get(symbol, {})
        name_fa = asset_names.get('name_fa') or symbol.replace('_', ' ').title()
        name_en = asset_names.get('name_en') or symbol.replace('_', ' ').title()
        
        category = 'OTHER'
        if 'gold' in symbol or 'silver' in symbol: category = 'METAL'
        elif 'dollar' in symbol or 'eur' in symbol: category = 'CURRENCY'

        asset, _ = Asset.objects.get_or_create(
            symbol=symbol,
            defaults={'name_fa': name_fa, 'name_en': name_en, 'category': category}
        )

        _, log_created = AssetPriceLog.objects.get_or_create(
            asset=asset,
            timestamp=aware_dt,
            defaults={
                'price': price,
                'high': high,
                'low': low,
                'change_amount': change_amount,
                'change_percent': details.get('dp', 0),
            }
        )
        if log_created:
            new_logs_count += 1

    return f"Asset scraping finished. Created {new_logs_count} new price logs."