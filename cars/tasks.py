import requests
from celery import shared_task
from django.utils import timezone
from fake_useragent import UserAgent
from decouple import config
from .models import Brand, Vehicle, PriceLog

ua = UserAgent()
BASE_API_URL_CAR = config('BASE_API_URL_CAR')



@shared_task
def scrape_car_prices():
    """
    Scrapes car data from the Khodro45 API, using the updated model structure
    with both Persian and English fields.
    """
    HEADERS = {
        'User-Agent': ua.random,
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://khodro45.com/pricing/',
    }
    
    page_url = BASE_API_URL_CAR
    vehicles_processed_count = 0

    while page_url:
        print(f"Fetching car data from: {page_url}")
        try:
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching API: {e}")
            break

        car_groups = data.get('results', [])
        for car_group in car_groups:
            for daily_car in car_group.get('dailycars', []):
                
                props = daily_car.get('car_properties', {})
                brand_props = props.get('brand', {})
                brand_fa = brand_props.get('title')
                brand_en = brand_props.get('title_en')
                model_props = props.get('model', {})
                model_fa = model_props.get('title')
                model_en = model_props.get('title_en')
                trim_props = props.get('trim', {})
                trim_fa = trim_props.get('title')
                trim_en = trim_props.get('title_en')
                year = props.get('year', {}).get('title')
                option_fa = props.get('option', {}).get('title')
                price = daily_car.get('price')

                # Skip record if essential data is missing
                if not all([brand_fa, model_fa, trim_fa, year, price]):
                    continue

                # Use 'defaults' to add the English name only when creating a new brand
                brand_obj, _ = Brand.objects.get_or_create(
                    name_fa=(brand_fa or '').strip(),
                    defaults={'name_en': (brand_en or '').strip()}
                )

                # Use 'defaults' to add English details on vehicle creation
                vehicle_obj, _ = Vehicle.objects.get_or_create(
                    brand=brand_obj,
                    model_fa=(model_fa or '').strip(),
                    trim_fa=(trim_fa or '').strip(),
                    production_year=int(year),
                    specifications_fa=(option_fa or '').strip(),
                    defaults={
                        'model_en': (model_en or '').strip(),
                        'trim_en': (trim_en or '').strip(),
                    }
                )

                _, price_log_created = PriceLog.objects.get_or_create(
                    vehicle=vehicle_obj,
                    log_date=timezone.now().date(),
                    defaults={'price': price} 
                )
                if price_log_created:
                    vehicles_processed_count += 1

        page_url = data.get('next')

    return f"Car scraping finished. Processed {vehicles_processed_count} new price logs."