import requests
from celery import shared_task
from django.utils import timezone
from fake_useragent import UserAgent


from .models import Brand, Vehicle, PriceLog
from decouple import config


ua = UserAgent()

HEADERS = {
    'User-Agent': ua.random,
    'accept': 'application/json, text/plain, */*',
    'referer': 'https://khodro45.com/pricing/',
}

BASE_API_URL_CAR = config('BASE_API_URL_CAR')

@shared_task
def scrape_car_prices():
    """
    This Celery task scrapes car data from the khodro45 API,
    iterates through all pages, and saves the data to the database.
    """
    page_url = BASE_API_URL_CAR 
    vehicles_processed_count = 0

    while page_url:
        print(f"Fetching data from: {page_url}")
        try:
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching API: {e}")
            break

        # Extract the main list of car groups from the 'results' key
        car_groups = data.get('results', [])

        for car_group in car_groups:
            for daily_car in car_group.get('dailycars', []):
                
                props = daily_car.get('car_properties', {})
                brand_name = props.get('brand', {}).get('title')
                model_name = props.get('model', {}).get('title')
                trim_name = props.get('trim', {}).get('title')
                year = props.get('year', {}).get('title')
                option = props.get('option', {}).get('title')
                price = daily_car.get('price')

                # If essential data is missing, skip this record
                if not all([brand_name, model_name, trim_name, year, price]):
                    continue

                # 1. Get or create the Brand
                brand_obj, _ = Brand.objects.get_or_create(name=brand_name.strip())

                # 2. Get or create the Vehicle using all its unique properties
                vehicle_obj, vehicle_created = Vehicle.objects.get_or_create(
                    brand=brand_obj,
                    name=model_name.strip(),
                    trim=trim_name.strip(),
                    production_year=int(year),
                    specifications=option.strip()
                )
                if vehicle_created:
                    print(f"Created new vehicle: {vehicle_obj}")

                # 3. Log the price for today
                _, price_log_created = PriceLog.objects.get_or_create(
                    vehicle=vehicle_obj,
                    log_date=timezone.now().date(),
                    defaults={'price': price} 
                )

                if price_log_created:
                    vehicles_processed_count += 1
                    print(f"Logged new price for {vehicle_obj}: {price}")

        page_url = data.get('next')

    return f"Scraping finished. Processed {vehicles_processed_count} new price logs."