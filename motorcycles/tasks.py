import requests
from decouple import config
from celery import shared_task
from django.utils import timezone
from fake_useragent import UserAgent

from .models import MotorcycleBrand, Motorcycle, MotorcyclePriceLog

ua = UserAgent()
BASE_API_URL_MOTOR = config('BASE_API_URL_MOTOR')




@shared_task
def scrape_motorcycle_prices():
    """
    Scrapes motorcycle data from the Bama API, iterates through all pages,
    and saves the data to the new motorcycle models.
    """
    HEADERS = {
        'User-Agent': ua.random,
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://bama.ir/motorcycle-price',
    }
    
    page_index = 1
    processed_count = 0
    
    while True:
        # Bama API uses pageIndex and pageSize for pagination
        params = {
            'pageIndex': page_index,
            'pageSize': 3 
        }
        
        print(f"Fetching Bama motorcycle data, page {page_index}...")
        try:
            response = requests.get(BASE_API_URL_MOTOR, headers=HEADERS, params=params)
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching Bama API: {e}")
            break

        # The main data is in the 'data' key
        brand_groups = response_data.get('data', [])

        # If the 'data' list is empty, it means we've reached the last page
        if not brand_groups:
            print("No more data found. Ending scrape.")
            break

        for brand_group in brand_groups:
            for item in brand_group.get('items', []):
                brand_fa = item.get('brand_fa')
                model_fa = item.get('model_fa')
                price = item.get('price')

                # Skip if essential data is missing
                if not all([brand_fa, model_fa, price]):
                    continue

                brand_obj, _ = MotorcycleBrand.objects.get_or_create(name=brand_fa.strip())
                
                motorcycle_obj, _ = Motorcycle.objects.get_or_create(
                    brand=brand_obj,
                    model=(model_fa or '').strip(),
                    trim=(item.get('class') or '').strip() or None,
                    production_year=item.get('model_year'),
                    defaults={
                        'origin': (item.get('manufacture_type', {}).get('display_name') or '').strip()
                    }
                )

                MotorcyclePriceLog.objects.get_or_create(
                    motorcycle=motorcycle_obj,
                    log_date=timezone.now().date(),
                    source=item.get('price_provider', 'Unknown').strip(),
                    defaults={'price': price}
                )
                processed_count += 1

        page_index += 1

    return f"Bama scraping finished. Processed {processed_count} price logs."