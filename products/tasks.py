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
}

logger = logging.getLogger(__name__)
ua = UserAgent()
session = requests.Session()
session.headers.update({
    'User-Agent': ua.random,
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.digikala.com/',
})


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

        if not (product_data and product_data.get('id')):
            return f"Skipped {product_id}: No product data."

        brand_data = product_data.get('brand')
        category_data = product_data.get('category')
        if not (brand_data and brand_data.get('id') and category_data and category_data.get('id')):
            return f"Skipped {product_id}: Missing brand or category."

        with transaction.atomic():
            logo_url = brand_data.get('logo', {}).get('url', '')
            if logo_url:
                logo_url = logo_url[0]
            brand, _ = Brand.objects.update_or_create(
                api_id=brand_data['id'],
                defaults={'code': brand_data.get('code', ''), 'title_fa': brand_data.get('title_fa', ''), 'title_en': brand_data.get('title_en', ''), 'logo_url': logo_url}
            )
            category, _ = Category.objects.update_or_create(
                api_id=category_data['id'],
                defaults={'code': category_data.get('code', ''), 'title_fa': category_data.get('title_fa', ''), 'title_en': category_data.get('title_en', '')}
            )

            review_data = product_data.get('review', {})
            product, created = Product.objects.update_or_create(
                api_id=product_data['id'],
                defaults={
                    'title_fa': product_data.get('title_fa'),
                    'title_en': product_data.get('title_en'),
                    'brand': brand,
                    'category': category,
                    'status': product_data.get('status', 'unavailable'),
                    'rating_rate': product_data.get('rating', {}).get('rate', 0),
                    'rating_count': product_data.get('rating', {}).get('count', 0),
                    'review_description': review_data.get('description', ''),
                }
            )

            ReviewAttribute.objects.filter(product=product).delete()
            review_attrs_to_create = []
            for attr in review_data.get('attributes', []):
                # Join the list of values into a single string
                value_str = ", ".join(attr.get('values', [])).strip()
                if attr.get('title') and value_str:
                    review_attrs_to_create.append(ReviewAttribute(
                        product=product,
                        title=attr['title'],
                        value=value_str
                    ))
            if review_attrs_to_create:
                ReviewAttribute.objects.bulk_create(review_attrs_to_create)

            ProductSpecification.objects.filter(product=product).delete()
            specs_to_create = []
            for group_data in product_data.get('specifications', []):
                if not (group_title := group_data.get('title')):
                    continue
                # Get or create the specification group (e.g., 'Display')
                group, _ = SpecGroup.objects.get_or_create(title=group_title)

                for attr_data in group_data.get('attributes', []):
                    if not (attr_title := attr_data.get('title')):
                        continue
                    # Get or create the specific attribute (e.g., 'Resolution')
                    attribute, _ = SpecAttribute.objects.get_or_create(group=group, title=attr_title)
                    
                    # Join multiple values into a clean, comma-separated string
                    value_str = ", ".join(val.strip() for val in attr_data.get('values', []) if val and val.strip())
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
            main_image_url = product_data.get('images', {}).get('main', {}).get('url', [None])[0]
            for img_data in product_data.get('images', {}).get('list', []):
                if (urls := img_data.get('url')) and isinstance(urls, list) and urls:
                    images_to_create.append(ProductImage(
                        product=product, image_url=urls[0], is_main=(urls[0] == main_image_url)
                    ))
            if images_to_create:
                ProductImage.objects.bulk_create(images_to_create)


            Variant.objects.filter(product=product).delete()
            variants_to_create = []
            for variant_data in product_data.get('variants', []):
                if not (variant_id := variant_data.get('id')):
                    continue
                
                price_info = variant_data.get('price', {})
                variants_to_create.append(Variant(
                    api_id=variant_id,
                    product=product,
                    seller_name=variant_data.get('seller', {}).get('title', ''),
                    color_name=variant_data.get('color', {}).get('title', ''),
                    color_hex=variant_data.get('color', {}).get('hex_code', ''),
                    warranty_name=variant_data.get('warranty', {}).get('title_fa', ''),
                    selling_price=price_info.get('selling_price', 0) // 10,
                    rrp_price=price_info.get('rrp_price', 0) // 10,
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
def scrape_products(product_type, start_page=1, max_pages=20):
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