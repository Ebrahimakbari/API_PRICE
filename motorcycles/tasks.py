import requests
from celery import shared_task
from django.utils import timezone
from fake_useragent import UserAgent
from decouple import config
from .models import MotorcycleBrand, Motorcycle, MotorcyclePriceLog

ua = UserAgent()
BASE_API_URL_MOTOR = config('BASE_API_URL_MOTOR')




@shared_task
def scrape_motorcycle_prices():
    """
    Scrapes motorcycle data from the Bama API, using the updated model structure
    with both Persian and English fields.
    """
    HEADERS = {
        'User-Agent': ua.random,
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://bama.ir/motorcycle-price',
    }
    
    page_index = 1
    processed_count = 0
    
    while True:
        params = {'pageIndex': page_index, 'pageSize': 3}
        
        print(f"Fetching Bama motorcycle data, page {page_index}...")
        try:
            response = requests.get(BASE_API_URL_MOTOR, headers=HEADERS, params=params)
            response.raise_for_status()
            response_data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching Bama API: {e}")
            break

        brand_groups = response_data.get('data', [])
        if not brand_groups:
            print("No more data found. Ending scrape.")
            break

        for item in [i for brand in brand_groups for i in brand.get('items', [])]:
            brand_fa = item.get('brand_fa')
            brand_en = item.get('brand') # The english slug from API
            model_fa = item.get('model_fa')
            model_en = item.get('model') # The english slug from API
            price = item.get('price')

            if not all([brand_fa, model_fa, price]):
                continue
            
            # Use 'defaults' to add English name only when creating a new brand
            brand_obj, _ = MotorcycleBrand.objects.get_or_create(
                name_fa=(brand_fa or '').strip(),
                defaults={'name_en_slug': (brand_en or '').strip()}
            )
            
            motorcycle_obj, _ = Motorcycle.objects.get_or_create(
                brand=brand_obj,
                model_fa=(model_fa or '').strip(),
                trim_fa=(item.get('class') or '').strip() or None,
                production_year=item.get('model_year'),
                # Use defaults to add English model slug and origin on creation
                defaults={
                    'model_en_slug': (model_en or '').strip(),
                    'origin': (item.get('manufacture_type', {}).get('display_name') or '').strip()
                }
            )

            MotorcyclePriceLog.objects.get_or_create(
                motorcycle=motorcycle_obj,
                log_date=timezone.now().date(),
                source=(item.get('price_provider') or 'Unknown').strip(),
                defaults={'price': price}
            )
            processed_count += 1

        page_index += 1

    return f"Bama scraping finished. Processed {processed_count} price logs."