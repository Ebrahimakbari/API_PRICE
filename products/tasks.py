import requests
from celery import shared_task
from django.db import transaction, IntegrityError
import logging
from decouple import config
from fake_useragent import UserAgent
from .models import PriceHistory, Product, Brand, Category, ProductImage, ProductSpecification, Variant, ReviewAttribute, SpecGroup, SpecAttribute


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
    },
    'headphone': {
        'list_url': config('LIST_API_URL_HEADPHONE'),
        'detail_url': config('DETAIL_API_URL_HEADPHONE'),
    },
    'gadget': {
        'list_url': config('LIST_API_URL_GADGET'),
        'detail_url': config('DETAIL_API_URL_GADGET'),
    },
    'personal': {
        'list_url': config('LIST_API_URL_PERSONAL'),
        'detail_url': config('DETAIL_API_URL_PERSONAL'),
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
    """Fetches details, updates product, and tracks price history."""
    url = SCRAPE_CONFIG[product_type]['detail_url'].format(
        product_id=product_id)
    logger.info(f"Processing product ID: {product_id}")
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()
        product_data = safe_get(response.json(), 'data', 'product')

        if not (product_data and safe_get(product_data, 'id')):
            return f"Skipped {product_id}: No product data."

        brand_data = safe_get(product_data, 'brand')
        category_data = safe_get(product_data, 'category')
        if not (safe_get(brand_data, 'id') and safe_get(category_data, 'id')):
            return f"Skipped {product_id}: Missing brand or category ID."

        with transaction.atomic():
            brand, _ = Brand.objects.update_or_create(
                api_id=safe_get(brand_data, 'id'),
                defaults={
                    'code': safe_get(brand_data, 'code', default=''),
                    'title_fa': safe_get(brand_data, 'title_fa', default=''),
                    'title_en': safe_get(brand_data, 'title_en', default=''),
                    'logo_url': safe_get(brand_data, 'logo', 'url', 0, default='')
                }
            )
            category, _ = Category.objects.update_or_create(
                api_id=safe_get(category_data, 'id'),
                defaults={
                    'code': safe_get(category_data, 'code', default=''),
                    'title_fa': safe_get(category_data, 'title_fa', default=''),
                    'title_en': safe_get(category_data, 'title_en', default='')
                }
            )
            product, created = Product.objects.update_or_create(
                api_id=safe_get(product_data, 'id'),
                defaults={
                    'title_fa': safe_get(product_data, 'title_fa', default=''),
                    'title_en': safe_get(product_data, 'title_en', default=''),
                    'brand': brand,
                    'category': category,
                    'status': safe_get(product_data, 'status', default='unavailable'),
                    'rating_rate': safe_get(product_data, 'rating', 'rate', default=0),
                    'rating_count': safe_get(product_data, 'rating', 'count', default=0),
                    'review_description': safe_get(product_data, 'review', 'description', default=''),
                }
            )

            # --- Sync Variants and Price History ---
            variants_from_api = safe_get(product_data, 'variants', default=[])
            api_variant_ids = {v['id']
                            for v in variants_from_api if v.get('id')}
            history_to_create = []

            for data in variants_from_api:
                if not (variant_id := safe_get(data, 'id')):
                    continue
                price_info = safe_get(data, 'price', default={})
                new_price = (
                    safe_get(price_info, 'selling_price', default=0) or 0) // 10
                new_rrp = (
                    safe_get(price_info, 'rrp_price', default=0) or 0) // 10

                variant, _ = Variant.objects.update_or_create(
                    api_id=variant_id, product=product,
                    defaults={
                        'seller_name': safe_get(data, 'seller', 'title', default=''),
                        'color_name': safe_get(data, 'color', 'title', default=''),
                        'color_hex': safe_get(data, 'color', 'hex_code', default=''),
                        'warranty_name': safe_get(data, 'warranty', 'title_fa', default=''),
                        'selling_price': new_price, 'rrp_price': new_rrp
                    }
                )
                latest_history = PriceHistory.objects.filter(
                    variant=variant).first()
                if not latest_history or latest_history.selling_price != new_price:
                    history_to_create.append(PriceHistory(
                        variant=variant, selling_price=new_price, rrp_price=new_rrp))

            if history_to_create:
                PriceHistory.objects.bulk_create(history_to_create)

            Variant.objects.filter(product=product).exclude(
                api_id__in=api_variant_ids).delete()

            # --- Sync other related data ---
            ReviewAttribute.objects.filter(product=product).delete()
            review_attrs_to_create = [
                ReviewAttribute(product=product, title=safe_get(
                    attr, 'title'), value=", ".join(safe_get(attr, 'values', default=[])).strip())
                for attr in safe_get(
                    product_data,
                    'review',
                    'attributes',
                    default=[]
                    ) if safe_get(attr, 'title')
            ]
            if review_attrs_to_create:
                ReviewAttribute.objects.bulk_create(review_attrs_to_create)

            ProductSpecification.objects.filter(product=product).delete()
            specs_to_create = []
            for group_data in safe_get(product_data, 'specifications', default=[]):
                if not (group_title := safe_get(group_data, 'title')):
                    continue
                group, _ = SpecGroup.objects.get_or_create(title=group_title)
                for attr_data in safe_get(group_data, 'attributes', default=[]):
                    if not (attr_title := safe_get(attr_data, 'title')):
                        continue
                    attribute, _ = SpecAttribute.objects.get_or_create(
                        group=group, title=attr_title)
                    value_str = ", ".join(v.strip() for v in safe_get(
                        attr_data, 'values', default=[]) if v and v.strip())
                    if value_str:
                        specs_to_create.append(ProductSpecification(
                            product=product, attribute=attribute, value=value_str))
            if specs_to_create:
                ProductSpecification.objects.bulk_create(specs_to_create)

            ProductImage.objects.filter(product=product).delete()
            main_image_url = safe_get(product_data, 'images', 'main', 'url', 0)
            images_to_create = [
                ProductImage(product=product, image_url=url,
                            is_main=(url == main_image_url))
                for img_data in safe_get(
                    product_data,
                    'images',
                    'list',
                    default=[]) if (url := safe_get(img_data, 'url', 0)
                                    )
            ]
            if images_to_create:
                ProductImage.objects.bulk_create(images_to_create)

        logger.info(
            f"Successfully {'created' if created else 'updated'} product ID: {product_id}")
        return f"Success: {'Created' if created else 'Updated'} {product_id}"

    except IntegrityError as e:
        logger.error(f"DB integrity error for {product_id}: {e}.")
        return f"Failed {product_id}: IntegrityError"


@shared_task
def scrape_products(product_type, start_page=1, max_pages=10):
    """Scrape products from the API and save them to the database."""
    logger.info(
        f"Starting '{product_type}' scrape from page {start_page} for {max_pages} pages.")
    queued_count = 0
    for page_num in range(start_page, start_page + max_pages):
        try:
            url = SCRAPE_CONFIG[product_type]['list_url'].format(page=page_num)
            response = session.get(url, timeout=15)
            response.raise_for_status()
            products = safe_get(response.json(), 'data',
                                'products', default=[])

            if not products:
                logger.info(
                    f"No more products on page {page_num} for '{product_type}'. Stopping scrape.")
                break

            for product_item in products:
                # The 'if not exists' check is removed to ensure every product gets updated.
                if product_id := product_item.get('id'):
                    fetch_and_save_product_details.delay(
                        product_id, product_type)
                    queued_count += 1

            logger.info(
                f"Queued {queued_count} detail tasks from page {page_num}.")
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Network error on page {page_num} for '{product_type}': {e}")
        except Exception as e:
            logger.exception(
                f"Unexpected error on page {page_num} for '{product_type}': {e}")

    logger.info(
        f"'{product_type}' scrape finished. Total tasks queued: {queued_count}.")
    return f"Scraping completed for '{product_type}': {queued_count} tasks queued."


@shared_task
def run_all_products_scrape():
    """
    A master task that initiates scraping for all configured product types.
    This is ideal for scheduling with Celery Beat.
    """
    logger.info("Starting scrapes for all configured product types.")
    for product_type in SCRAPE_CONFIG.keys():
        if SCRAPE_CONFIG[product_type]['list_url']:  # Only run if URL is configured
            scrape_products.delay(product_type=product_type)
        else:
            logger.warning(
                f"Skipping scrape for '{product_type}': LIST_API_URL not configured.")
    return "All scrape tasks have been queued."
