import requests
from celery import shared_task
from django.db import transaction, IntegrityError
import logging
from decouple import config
from fake_useragent import UserAgent
from .models import Product, Brand, Category, ProductImage, ProductSpecification, Variant, ReviewAttribute, SpecGroup, SpecAttribute




LIST_API_URL_MOBILE = config('LIST_API_URL_MOBILE')
LIST_API_URL_PC = config('LIST_API_URL_PC')
DETAIL_API_URL_MOBILE = config('DETAIL_API_URL_MOBILE')
DETAIL_API_URL_PC = config('DETAIL_API_URL_PC')


SCRAPE_CONFIG = {
    'mobile': {
        'list_url': config('LIST_API_URL_MOBILE'),
        'detail_url': config('DETAIL_API_URL_MOBILE'),
    },
    'pc': {
        'list_url': config('LIST_API_URL_PC'),
        'detail_url': config('DETAIL_API_URL_PC'),
    },
    'console': {
        'list_url': config('LIST_API_URL_CONSOLE'),
        'detail_url': config('DETAIL_API_URL_CONSOLE'),
    }
}

logger = logging.getLogger(__name__)
ua = UserAgent()
session = requests.Session()
session.headers.update({
    'User-Agent': ua.random,
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.digikala.com/',
})


def safe_get(data, *keys, default=''):
    """
    Safely get nested values from dict/list structures.
    
    Args:
        data: The data structure to get value from
        *keys: Keys/indices to traverse (e.g., 'rating', 'rate')
        default: Default value if path doesn't exist
    
    Returns:
        The value at the path or default if not found
    """
    if not data:
        return default
        
    current = data
    for key in keys:
        try:
            if isinstance(current, (list, tuple)):
                # Handle list indices or get first element if key is not an integer
                current = current[key] if isinstance(key, int) else current[0]
            elif isinstance(current, dict):
                current = current.get(key, default)
            else:
                return default
                
            if current is None:
                return default
                
        except (IndexError, KeyError, TypeError):
            return default
            
    return current



@shared_task
def fetch_and_save_product_details(product_id, product_type):
    """
    Fetches and saves focused product information, leveraging bulk operations and relational models.
    """
    url = SCRAPE_CONFIG[product_type]['detail_url'].format(product_id=product_id)
    logger.info(f"Processing product ID: {product_id}")
    
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()
        data = response.json().get('data', {})
        product_data = data.get('product')

        if not (product_data and safe_get(product_data, 'id')):
            return f"Skipped {product_id}: No product data."

        brand_data = safe_get(product_data, 'brand')
        category_data = safe_get(product_data, 'category')
        if not (brand_data and safe_get(brand_data, 'id') and category_data and safe_get(category_data, 'id')):
            return f"Skipped {product_id}: Missing brand or category."

        with transaction.atomic():
            brand, _ = Brand.objects.update_or_create(
                api_id=safe_get(brand_data, 'id'),
                defaults={
                    'code': safe_get(brand_data, 'code'),
                    'title_fa': safe_get(brand_data, 'title_fa'),
                    'title_en': safe_get(brand_data, 'title_en'),
                    'logo_url': safe_get(brand_data, 'logo', 'url', 0)
                }
            )
            
            category, _ = Category.objects.update_or_create(
                api_id=safe_get(category_data, 'id'),
                defaults={
                    'code': safe_get(category_data, 'code'),
                    'title_fa': safe_get(category_data, 'title_fa'),
                    'title_en': safe_get(category_data, 'title_en')
                }
            )

            product, created = Product.objects.update_or_create(
                api_id=safe_get(product_data, 'id'),
                defaults={
                    'title_fa': safe_get(product_data, 'title_fa'),
                    'title_en': safe_get(product_data, 'title_en'),
                    'brand': brand,
                    'category': category,
                    'status': safe_get(product_data, 'status', default='unavailable'),
                    'rating_rate': safe_get(product_data, 'rating', 'rate', default=0),
                    'rating_count': safe_get(product_data, 'rating', 'count', default=0),
                    'review_description': safe_get(product_data, 'review', 'description'),
                }
            )

            ReviewAttribute.objects.filter(product=product).delete()
            review_attrs_to_create = []
            for attr in safe_get(product_data, 'review', 'attributes', default=[]):
                value_str = ", ".join(safe_get(attr, 'values', default=[])).strip()
                if safe_get(attr, 'title') and value_str:
                    review_attrs_to_create.append(ReviewAttribute(
                        product=product,
                        title=safe_get(attr, 'title'),
                        value=value_str
                    ))
            if review_attrs_to_create:
                ReviewAttribute.objects.bulk_create(review_attrs_to_create)

            ProductSpecification.objects.filter(product=product).delete()
            specs_to_create = []
            for group_data in safe_get(product_data, 'specifications', default=[]):
                group_title = safe_get(group_data, 'title')
                if not group_title:
                    continue
                group, _ = SpecGroup.objects.get_or_create(title=group_title)

                for attr_data in safe_get(group_data, 'attributes', default=[]):
                    attr_title = safe_get(attr_data, 'title')
                    if not attr_title:
                        continue
                    attribute, _ = SpecAttribute.objects.get_or_create(
                        group=group, 
                        title=attr_title
                    )
                    
                    value_str = ", ".join(
                        val.strip() 
                        for val in safe_get(attr_data, 'values', default=[]) 
                        if val and val.strip()
                    )
                    if value_str:
                        specs_to_create.append(ProductSpecification(
                            product=product,
                            attribute=attribute,
                            value=value_str
                        ))
            if specs_to_create:
                ProductSpecification.objects.bulk_create(specs_to_create)

            ProductImage.objects.filter(product=product).delete()
            images_to_create = []
            main_image_url = safe_get(product_data, 'images', 'main', 'url', 0)
            for img_data in safe_get(product_data, 'images', 'list', default=[]):
                urls = safe_get(img_data, 'url')
                if urls and isinstance(urls, list) and urls:
                    images_to_create.append(ProductImage(
                        product=product, 
                        image_url=urls[0], 
                        is_main=(urls[0] == main_image_url)
                    ))
            if images_to_create:
                ProductImage.objects.bulk_create(images_to_create)

            Variant.objects.filter(product=product).delete()
            variants_to_create = []
            for variant_data in safe_get(product_data, 'variants', default=[]):
                variant_id = safe_get(variant_data, 'id')
                if not variant_id:
                    continue
                
                price_info = safe_get(variant_data, 'price', default={})
                variants_to_create.append(Variant(
                    api_id=variant_id,
                    product=product,
                    seller_name=safe_get(variant_data, 'seller', 'title'),
                    color_name=safe_get(variant_data, 'color', 'title'),
                    color_hex=safe_get(variant_data, 'color', 'hex_code'),
                    warranty_name=safe_get(variant_data, 'warranty', 'title_fa'),
                    selling_price=safe_get(price_info, 'selling_price', default=0) // 10,
                    rrp_price=safe_get(price_info, 'rrp_price', default=0) // 10,
                ))
            if variants_to_create:
                Variant.objects.bulk_create(variants_to_create)

        status_msg = "Created" if created else "Updated"
        logger.info(f"Successfully {status_msg} product ID: {product_id}")
        return f"Success: {status_msg} {product_id}"

    except IntegrityError as e:
        logger.error(f"Database integrity error for product ID {product_id}: {e}. Skipping.")
        return f"Failed {product_id}: IntegrityError"
    except Exception as e:
        logger.exception(f"CRITICAL UNEXPECTED ERROR for product ID {product_id}: {e}")


@shared_task
def scrape_products(product_type, start_page=1, max_pages=30):
    """Scrape products from the API and save them to the database."""
    logger.info(f"Starting product scrape from page {start_page} for {max_pages} pages.")
    processed_count = 0
    for page_num in range(start_page, start_page + max_pages):
        try:
            url = SCRAPE_CONFIG[product_type]['list_url'].format(page=page_num)
            response = session.get(url, timeout=15)
            response.raise_for_status()
            api_data = response.json().get('data', {})
            products = api_data.get('products', [])
            if not products:
                logger.info(f"No more products found on page {page_num}. Stopping scrape.")
                break

            for product in products:
                product_id = product.get('id')
                if product_id and not Product.objects.filter(api_id=product_id).exists():
                    fetch_and_save_product_details.delay(product_id, product_type=product_type)
                    processed_count += 1

            logger.info(f"Queued tasks for {len([p for p in products if p.get('id')])} new products from page {page_num}.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error on page {page_num}: {e}")
            continue
        except Exception as e:
            logger.exception(f"An unexpected error on page {page_num}: {e}")
            continue

    logger.info(f"Product scraping task finished. Queued {processed_count} new products.")
    return f"Scraping completed: {processed_count} products queued."


@shared_task
def run_all_products_scrape():
    """
    A master task that initiates scraping for all configured product types.
    This is ideal for scheduling with Celery Beat.
    """
    logger.info("Starting scrapes for all configured product types.")
    for product_type in SCRAPE_CONFIG.keys():
        if SCRAPE_CONFIG[product_type]['list_url']: # Only run if URL is configured
            scrape_products.delay(product_type=product_type)
        else:
            logger.warning(f"Skipping scrape for '{product_type}': LIST_API_URL not configured.")
    return "All scrape tasks have been queued."