import requests
from celery import shared_task
from fake_useragent import UserAgent
from decouple import config
from .models import Asset, AssetPriceLog
from decimal import Decimal, InvalidOperation
import pytz 
from datetime import datetime 





STATIC_NAME_MAP = {
    "price_dollar_rl": {"name_fa": "دلار", "name_en": "US Dollar (Market)"},
    "price_eur": {"name_fa": "یورو", "name_en": "Euro (Market)"},
    "price_aed": {"name_fa": "درهم امارات", "name_en": "UAE Dirham (Market)"},
    "price_gbp": {"name_fa": "پوند انگلیس", "name_en": "British Pound (Market)"},
    "price_try": {"name_fa": "لیر ترکیه", "name_en": "Turkish Lira (Market)"},
    "price_chf": {"name_fa": "فرانک سوئیس", "name_en": "Swiss Franc (Market)"},
    "price_cny": {"name_fa": "یوان چین", "name_en": "Chinese Yuan (Market)"},
    "price_jpy": {"name_fa": "ین ژاپن (100 ین)", "name_en": "JPY"},
    "price_krw": {"name_fa": "وون کره جنوبی", "name_en": "KRW"},
    "price_cad": {"name_fa": "دلار کانادا", "name_en": "CAD"},
    "price_aud": {"name_fa": "دلار استرالیا", "name_en": "AUD"},
    "price_nzd": {"name_fa": "دلار نیوزیلند", "name_en": "NZD"},
    "price_sgd": {"name_fa": "دلار سنگاپور", "name_en": "SGD"},
    "price_inr": {"name_fa": "روپیه هند", "name_en": "INR"},
    "price_pkr": {"name_fa": "روپیه پاکستان", "name_en": "PKR"},
    "price_iqd": {"name_fa": "دینار عراق", "name_en": "IQD"},
    "price_syp": {"name_fa": "پوند سوریه", "name_en": "SYP"},
    "price_afn": {"name_fa": "افغانی", "name_en": "AFN"},
    "price_dkk": {"name_fa": "کرون دانمارک", "name_en": "DKK"},
    "price_sek": {"name_fa": "کرون سوئد", "name_en": "SEK"},
    "price_nok": {"name_fa": "کرون نروژ", "name_en": "NOK"},
    "price_sar": {"name_fa": "ریال عربستان", "name_en": "SAR"},
    "price_qar": {"name_fa": "ریال قطر", "name_en": "QAR"},
    "price_omr": {"name_fa": "ریال عمان", "name_en": "OMR"},
    "price_kwd": {"name_fa": "دینار کویت", "name_en": "KWD"},
    "price_bhd": {"name_fa": "دینار بحرین", "name_en": "BHD"},
    "price_myr": {"name_fa": "رینگیت مالزی", "name_en": "MYR"},
    "price_thb": {"name_fa": "بات تایلند", "name_en": "THB"},
    "price_hkd": {"name_fa": "دلار هنگ کنگ", "name_en": "HKD"},
    "price_rub": {"name_fa": "روبل روسیه", "name_en": "RUB"},
    "price_azn": {"name_fa": "منات آذربایجان", "name_en": "AZN"},
    "price_amd": {"name_fa": "درام ارمنستان", "name_en": "AMD"},
    "price_gel": {"name_fa": "لاری گرجستان", "name_en": "GEL"},
    "price_kgs": {"name_fa": "سوم قرقیزستان", "name_en": "KGS"},
    "price_tjs": {"name_fa": "سامانی تاجیکستان", "name_en": "TJS"},
    "price_tmt": {"name_fa": "منات ترکمنستان", "name_en": "TMT"},
    "price_all": {"name_fa": "لک آلبانی", "name_en": "ALL"},
    "price_bbd": {"name_fa": "دلار باربادوس", "name_en": "BBD"},
    "price_bdt": {"name_fa": "تاکا بنگلادش", "name_en": "BDT"},
    "price_bgn": {"name_fa": "لو بلغارستان", "name_en": "BGN"},
    "price_bif": {"name_fa": "فرانک بوروندی", "name_en": "BIF"},
    "price_bnd": {"name_fa": "دلار برونئی", "name_en": "BND"},
    "price_bsd": {"name_fa": "دلار باهاماس", "name_en": "BSD"},
    "price_bwp": {"name_fa": "پوله بوتسوانا", "name_en": "BWP"},
    "price_byn": {"name_fa": "روبل بلاروس", "name_en": "BYN"},
    "price_bzd": {"name_fa": "دلار بلیز", "name_en": "BZD"},
    "price_cup": {"name_fa": "پزوی کوبا", "name_en": "CUP"},
    "price_czk": {"name_fa": "کرون چک", "name_en": "CZK"},
    "price_djf": {"name_fa": "فرانک جیبوتی", "name_en": "DJF"},
    "price_dop": {"name_fa": "پزوی دومنیکن", "name_en": "DOP"},
    "price_dzd": {"name_fa": "دینار الجزایر", "name_en": "DZD"},
    "price_etb": {"name_fa": "بیر اتیوپی", "name_en": "ETB"},
    "price_gnf": {"name_fa": "فرانک گینه", "name_en": "GNF"},
    "price_gtq": {"name_fa": "کوئزال گواتمالا", "name_en": "GTQ"},
    "price_gyd": {"name_fa": "دلار گویان", "name_en": "GYD"},
    "price_hnl": {"name_fa": "لمپیرا هندوراس", "name_en": "HNL"},
    "price_hrk": {"name_fa": "کونا کرواسی", "name_en": "HRK"},
    "price_htg": {"name_fa": "گورد هائیتی", "name_en": "HTG"},
    "price_isk": {"name_fa": "کرون ایسلند", "name_en": "ISK"},
    "price_jmd": {"name_fa": "دلار جامائیکا", "name_en": "JMD"},
    "price_kes": {"name_fa": "شیلینگ کنیا", "name_en": "KES"},
    "price_khr": {"name_fa": "ریل کامبوج", "name_en": "KHR"},
    "price_kmf": {"name_fa": "فرانک کومور", "name_en": "KMF"},
    "price_kzt": {"name_fa": "تنگه قزاقستان", "name_en": "KZT"},
    "price_lak": {"name_fa": "کیپ لائوس", "name_en": "LAK"},
    "price_lbp": {"name_fa": "پوند لبنان", "name_en": "LBP"},
    "price_lkr": {"name_fa": "روپیه سریلانکا", "name_en": "LKR"},
    "price_lrd": {"name_fa": "دلار لیبریا", "name_en": "LRD"},
    "price_lsl": {"name_fa": "لاتی لسوتو", "name_en": "LSL"},
    "price_lyd": {"name_fa": "دینار لیبی", "name_en": "LYD"},
    "price_mad": {"name_fa": "درهم مراکش", "name_en": "MAD"},
    "price_mdl": {"name_fa": "لئو مولداوی", "name_en": "MDL"},
    "price_mga": {"name_fa": "آریاری ماداگاسکار", "name_en": "MGA"},
    "price_mkd": {"name_fa": "دینار مقدونیه", "name_en": "MKD"},
    "price_mmk": {"name_fa": "کیات میانمار", "name_en": "MMK"},
    "price_mxn": {"name_fa": "پزو مکزیک", "name_en": "MXN"},
    "price_mzn": {"name_fa": "متیکال موزامبیک", "name_en": "MZN"},
    "price_nad": {"name_fa": "دلار نامیبیا", "name_en": "NAD"},
    "price_ngn": {"name_fa": "نایرا نیجریه", "name_en": "NGN"},
    "price_nio": {"name_fa": "کوردوبا نیکاراگوئه", "name_en": "NIO"},
    "price_npr": {"name_fa": "روپیه نپال", "name_en": "NPR"},
    "price_pen": {"name_fa": "سول پرو", "name_en": "PEN"},
    "price_pab": {"name_fa": "بالبوآ پاناما", "name_en": "PAB"},
    "price_php": {"name_fa": "پزوی فیلیپین", "name_en": "PHP"},
    "price_pgk": {"name_fa": "کینا پاپوآ گینه نو", "name_en": "PGK"},
    "price_pln": {"name_fa": "زووتی لهستان", "name_en": "PLN"},
    "price_pyg": {"name_fa": "گوارانی پاراگوئه", "name_en": "PYG"},
    "price_ron": {"name_fa": "لئو رومانی", "name_en": "RON"},
    "price_rsd": {"name_fa": "دینار صربستان", "name_en": "RSD"},
    "price_rwf": {"name_fa": "فرانک رواندا", "name_en": "RWF"},
    "price_scr": {"name_fa": "روپیه سیشل", "name_en": "SCR"},
    "price_sdg": {"name_fa": "پوند سودان", "name_en": "SDG"},
    "price_shp": {"name_fa": "پوند سنت هلنا", "name_en": "SHP"},
    "price_sll": {"name_fa": "لئون سیرالئون", "name_en": "SLL"},
    "price_sos": {"name_fa": "شیلینگ سومالی", "name_en": "SOS"},
    "price_std": {"name_fa": "دوبرا سائوتومه و پرینسیپ", "name_en": "STD"},
    "price_svc": {"name_fa": "کلون السالوادور", "name_en": "SVC"},
    "price_szl": {"name_fa": "لیلانگنی اسواتینی", "name_en": "SZL"},
    "price_tnd": {"name_fa": "دینار تونس", "name_en": "TND"},
    "price_ttd": {"name_fa": "دلار ترینیداد و توبago", "name_en": "TTD"},
    "price_twd": {"name_fa": "دلار تایوان", "name_en": "TWD"},
    "price_tzs": {"name_fa": "شیلینگ تانزانیا", "name_en": "TZS"},
    "price_uah": {"name_fa": "حریوانا اوکراین", "name_en": "UAH"},
    "price_ugx": {"name_fa": "شیلینگ اوگاندا", "name_en": "UGX"},
    "price_uyu": {"name_fa": "پزو اروگوئه", "name_en": "UYU"},
    "price_uzs": {"name_fa": "سوم ازبکستان", "name_en": "UZS"},
    "price_vef": {"name_fa": "بولیوار ونزوئلا", "name_en": "VEF"},
    "price_vnd": {"name_fa": "دونگ ویتنام", "name_en": "VND"},
    "price_vuv": {"name_fa": "واتو وانواتو", "name_en": "VUV"},
    "price_xaf": {"name_fa": "فرانک آفریقای مرکزی", "name_en": "XAF"},
    "price_xcd": {"name_fa": "دلار کارائیب شرقی", "name_en": "XCD"},
    "price_xof": {"name_fa": "فرانک آفریقای غربی", "name_en": "XOF"},
    "price_xpf": {"name_fa": "فرانک CFP", "name_en": "XPF"},
    "price_yer": {"name_fa": "ریال یمن", "name_en": "YER"},
    "price_zar": {"name_fa": "رند آفریقای جنوبی", "name_en": "ZAR"},
    "price_zmw": {"name_fa": "کوچا زامبیا", "name_en": "ZMW"},
    "price_dubai_dollar": {"name_fa": "دلار دبی", "name_en": "Dubai Dollar"},
    "price_eur_ex": {"name_fa": "یورو (صرافی)", "name_en": "EUR Ex"},

    # --- FX Rates (Updated with your overrides) ---
    "usd-try-ask": {"name_fa": "دلار / لیر", "name_en": "USD/TRY"},
    "usd-sek-ask": {"name_fa": "دلار / کرون سوئد", "name_en": "USD/SEK"},
    "usd-sar-ask": {"name_fa": "دلار / ریال عربستان", "name_en": "USD/SAR"},
    "usd-nzd-ask": {"name_fa": "دلار / دلار نیوزیلند", "name_en": "USD/NZD"},
    "usd-krw-ask": {"name_fa": "دلار / وون کره", "name_en": "USD/KRW"},
    "usd-jpy-ask": {"name_fa": "دلار / ین ژاپن", "name_en": "USD/JPY"},
    "usd-cny-ask": {"name_fa": "دلار / یوان چین", "name_en": "USD/CNY"},
    "usd-chf-ask": {"name_fa": "دلار / فرانک سوئیس", "name_en": "USD/CHF"},
    "usd-cad-ask": {"name_fa": "دلار / دلار کانادا", "name_en": "USD/CAD"},
    "usd_afn_bid": {"name_fa": "افغانی / دلار", "name_en": "AFN/USD"},
    "afn_usd_bid": {"name_fa": "افغانی / دلار", "name_en": "AFN/USD"},
    "afghan_usd": {"name_fa": "افغانی به دلار", "name_en": "Afghan USD"},

    # --- Metals (Updated with your overrides) ---
    "zinc": {"name_fa": "روی", "name_en": "Zinc"},
    "base_global_zinc": {"name_fa": "روی جهانی", "name_en": "Global Zinc"},
    "base_global_copper": {"name_fa": "مس جهانی", "name_en": "Global Copper"},
    "base_global_lead": {"name_fa": "سرب جهانی", "name_en": "Global Lead"},
    "base_global_nickel": {"name_fa": "نیکل جهانی", "name_en": "Global Nickel"},
    "base_global_tin": {"name_fa": "قلع جهانی", "name_en": "Global Tin"},
    "aluminium": {"name_fa": "آلومینیوم", "name_en": "Aluminium"},
    "base-us-aluminum": {"name_fa": "آلومینیوم آمریکا", "name_en": "US Aluminum"},
    "cobalt": {"name_fa": "کبالت", "name_en": "Cobalt"},
    "base-us-steel-coil": {"name_fa": "فولاد", "name_en": "US Steel Coil"},
    "base-us-iron-ore": {"name_fa": "سنگ آهن آمریکا", "name_en": "US Iron Ore"},
    "base-us-copper": {"name_fa": "مس آمریکا", "name_en": "US Copper"},
    "base-us-zinc": {"name_fa": "روی آمریکا", "name_en": "US Zinc"},
    "base-us-uranium": {"name_fa": "اورانیوم", "name_en": "Uranium"},
    "tgju_gold_irg18": {"name_fa": "طلای ۱۸ عیار", "name_en": "18K Gold"},
    "silver_999": {"name_fa": "گرم نقره ۹۹۹", "name_en": "999 Silver Gram"},
    "silver_925": {"name_fa": "نقره ۹۲۵", "name_en": "925 Silver"},
    "silver": {"name_fa": "نقره", "name_en": "Silver"},
    "geram18": {"name_fa": "طلای 18 عیار / 750", "name_en": "Gold 18k / 750"},
    "geram24": {"name_fa": "طلای ۲۴ عیار", "name_en": "Gold 24k"},
    "mesghal": {"name_fa": "مثقال طلا", "name_en": "Gold Mesghal"},
    "gold_mini_size": {"name_fa": "طلای دست دوم", "name_en": "Used Gold"},
    "gold_global": {"name_fa": "انس طلا", "name_en": "Gold Ounce"},
    "ons": {"name_fa": "انس طلا", "name_en": "Gold Ounce"},
    "platinum": {"name_fa": "انس پلاتین", "name_en": "Platinum Ounce"},
    "palladium": {"name_fa": "انس پالادیوم", "name_en": "Palladium Ounce"},

    # --- Coins (Updated with your overrides) ---
    "sekee": {"name_fa": "سکه امامی", "name_en": "Emami Coin"},
    "sekeb": {"name_fa": "سکه بهار آزادی", "name_en": "Bahar Azadi Coin"},
    "nim": {"name_fa": "نیم سکه", "name_en": "Half Coin"},
    "rob": {"name_fa": "ربع سکه", "name_en": "Quarter Coin"},
    "gerami": {"name_fa": "سکه گرمی", "name_en": "Gram Coin"},
    "sekee_real": {"name_fa": "سکه امامی واقعی", "name_en": "Emami Real"},
    "sekee_down": {"name_fa": "تمام سکه (قبل 86)", "name_en": "Old Full Coin (pre-1997)"},
    "nim_down": {"name_fa": "نیم سکه (قبل 86)", "name_en": "Old Half Coin (pre-1997)"},
    "rob_down": {"name_fa": "ربع سکه (قبل 86)", "name_en": "Old Quarter Coin (pre-1997)"},
    "sekee_dollar": {"name_fa": "سکه امامی دلاری", "name_en": "Emami Dollar Coin"},
    "sekee_buy": {"name_fa": "خرید سکه امامی", "name_en": "Emami Buy Coin"},
    "sekeb_buy": {"name_fa": "خرید سکه بهار آزادی", "name_en": "Bahar Azadi Buy Coin"},
    "coin_blubber": {"name_fa": "حباب سکه امامی", "name_en": "Emami Coin Bubble"},
    "sekeb_blubber": {"name_fa": "حباب سکه بهار آزادی", "name_en": "Bahar Azadi Coin Bubble"},
    "rob_blubber": {"name_fa": "حباب ربع سکه", "name_en": "Quarter Coin Bubble"},
    "gerami_blubber": {"name_fa": "حباب سکه گرمی", "name_en": "Gram Coin Bubble"},
    "retail_sekee": {"name_fa": "سکه امامی / تک فروشی", "name_en": "Emami Coin Retail"},
    "retail_sekeb": {"name_fa": "سکه بهار آزادی / تک فروشی", "name_en": "Bahar Azadi Coin Retail"},
    "retail_rob": {"name_fa": "ربع سکه / تک فروشی", "name_en": "Quarter Coin Retail"},
    "retail_nim": {"name_fa": "نیم سکه / تک فروشی", "name_en": "Half Coin Retail"},
    "retail_gerami": {"name_fa": "سکه گرمی / تک فروشی", "name_en": "Gram Coin Retail"},
    "rob_buy": {"name_fa": "خرید ربع سکه", "name_en": "Quarter Buy Coin"},
    "سکه-پارسیان-۰-۱۰۰": {"name_fa": "سکه پارسیان ۰/۱۰۰", "name_en": "Parsian Coin 0.100g"},
    "سکه-پارسیان-۰-۲۰۰": {"name_fa": "سکه پارسیان ۰/۲۰۰", "name_en": "Parsian Coin 0.200g"},
    "سکه-پارسیان-۰-۳۰۰": {"name_fa": "سکه پارسیان ۰/۳۰۰", "name_en": "Parsian Coin 0.300g"},
    "سکه-پارسیان-۰-۴۰۰": {"name_fa": "سکه پارسیان ۰/۴۰۰", "name_en": "Parsian Coin 0.400g"},
    "سکه-پارسیان-۰-۵۰۰": {"name_fa": "سکه پارسیان ۰/۵۰۰", "name_en": "Parsian Coin 0.500g"},
    "سکه-پارسیان-۰-۶۰۰": {"name_fa": "سکه پارسیان ۰/۶۰۰", "name_en": "Parsian Coin 0.600g"},
    "سکه-پارسیان-۰-۷۰۰": {"name_fa": "سکه پارسیان ۰/۷۰۰", "name_en": "Parsian Coin 0.700g"},
    "سکه-پارسیان-۰-۸۰۰": {"name_fa": "سکه پارسیان ۰/۸۰۰", "name_en": "Parsian Coin 0.800g"},
    "سکه-پارسیان-۰-۹۰۰": {"name_fa": "سکه پارسیان ۰/۹۰۰", "name_en": "Parsian Coin 0.900g"},
    "سکه-پارسیان-۱-۰۰۰": {"name_fa": "سکه پارسیان ۱/۰۰۰", "name_en": "Parsian Coin 1.000g"},

    # --- Crypto (Updated with your overrides) ---
    "xrp-irr": {"name_fa": "ریپل", "name_en": "XRP"},
    "xlm-irr": {"name_fa": "استلار", "name_en": "XLM"},
    "usdt-irr": {"name_fa": "تتر", "name_en": "USDT"},
    "btc-irr": {"name_fa": "بیت کوین", "name_en": "BTC"},
    "eth-irr": {"name_fa": "اتریوم", "name_en": "ETH"},
    "price_etc": {"name_fa": "اتریوم کلاسیک", "name_en": "ETC"},
    "price_eos": {"name_fa": "ایوس", "name_en": "EOS"},
    "price_omg": {"name_fa": "امگ", "name_en": "OMG"},
    "price_gnt": {"name_fa": "گینت", "name_en": "GNT"},
    "crypto-bitcoin": {"name_fa": "بیت کوین", "name_en": "Bitcoin"},
    "crypto-ethereum": {"name_fa": "اتریوم", "name_en": "Ethereum"},
    "crypto-tether": {"name_fa": "تتر", "name_en": "Tether"},
    "crypto-ripple": {"name_fa": "ریپل", "name_en": "Ripple"},
    "crypto-dogecoin": {"name_fa": "دوج کوین", "name_en": "Dogecoin"},
    "crypto-shiba-inu": {"name_fa": "شیبا اینو", "name_en": "Shiba Inu"},
    "crypto-cardano": {"name_fa": "کاردانو", "name_en": "Cardano"},
    "crypto-solana": {"name_fa": "سولانا", "name_en": "Solana"},
    "crypto-tron": {"name_fa": "ترون", "name_en": "Tron"},

    # --- Commodities (Updated with your overrides) ---
    "commodity_london_coffee": {"name_fa": "قهوه لندن", "name_en": "London Coffee"},
    "commodity_lumber": {"name_fa": "الوار", "name_en": "Lumber"},
    "commodity_us_sugar_no11": {"name_fa": "شکر", "name_en": "US Sugar"},
    "commodity_us_cotton_no_2": {"name_fa": "پنبه", "name_en": "US Cotton"},
    "commodity_rough_rice": {"name_fa": "برنج خشن", "name_en": "Rough Rice"},
    "commodity_oats": {"name_fa": "جو دوسر", "name_en": "Oats"},
    "commodity_live_cattle": {"name_fa": "گوشت گاو", "name_en": "Live Cattle"},
    "commodity_feed_cattle": {"name_fa": "فیدر گاو", "name_en": "Feeder Cattle"},
    "commodity_us_coffee_c": {"name_fa": "قهوه آمریکا", "name_en": "US Coffee C"},
    "commodity_us_cocoa": {"name_fa": "کاکائو آمریکا", "name_en": "US Cocoa"},

    # --- Indices and Ratios (Updated with your overrides) ---
    "bourse": {"name_fa": "شاخص کل بورس", "name_en": "Tehran Stock Market Index"},
    "bourse_stoxx-600": {"name_fa": "شاخص استاکس 600", "name_en": "Stoxx 600"},
    "bourse_singapore": {"name_fa": "شاخص سنگاپور", "name_en": "Singapore Index"},
    "bourse_nikkei-225": {"name_fa": "نیکی 225", "name_en": "Nikkei 225"},
    "bourse_globaldow": {"name_fa": "داوجونز جهانی", "name_en": "Global Dow"},
    "bourse_asia-dow": {"name_fa": "داوجونز آسیا", "name_en": "Asia Dow"},
    "dow_jones_us": {"name_fa": "داوجونز", "name_en": "Dow Jones"},
    "nasdaq_us": {"name_fa": "ناسداک", "name_en": "Nasdaq"},
    "s_p_500_us": {"name_fa": "اس اند پی 500", "name_en": "S&P 500"},
    "ratio_xau": {"name_fa": "نسبت طلا", "name_en": "Gold Ratio"},
    "ratio_sp500": {"name_fa": "نسبت اس اند پی", "name_en": "S&P Ratio"},
    "ratio_silver": {"name_fa": "نسبت نقره", "name_en": "Silver Ratio"},
    "ratio_platinum": {"name_fa": "نسبت پلاتین", "name_en": "Platinum Ratio"},
    "ratio_palladium": {"name_fa": "نسبت پالادیوم", "name_en": "Palladium Ratio"},
    "ratio_hui": {"name_fa": "نسبت HUI", "name_en": "HUI Ratio"},
    "ratio_dija": {"name_fa": "نسبت داوجونز", "name_en": "DJIA Ratio"},
    "ratio_crudeoil": {"name_fa": "نسبت نفت خام", "name_en": "Crude Oil Ratio"},

    # --- Other Specifics from JSON (Updated with your overrides) ---
    "yemen@kwd-sell": {"name_fa": "یمن به دینار کویت (فروش)", "name_en": "Yemen KWD Sell"},
    "coin_future": {"name_fa": "آتی سکه", "name_en": "Coin Future"},
    "coin_checkout": {"name_fa": "چک اوت سکه", "name_en": "Coin Checkout"},
    "price_dubai_dollar": {"name_fa": "دلار دبی", "name_en": "Dubai Dollar"},

    # --- Futures & Certificates (Updated with your overrides) ---
    "fu01": {"name_fa": "شمش طلای خام تحویل 20 آبان 04", "name_en": "Raw Gold Futures (Nov 2025)"},
    "fu02": {"name_fa": "شمش طلای خام تحویل 28 بهمن 04", "name_en": "Raw Gold Futures (Feb 2026)"},
    "gc51": {"name_fa": "صندوق طلای آلتون", "name_en": "Alton Gold Fund"},
    "go01": {"name_fa": "گواهی سپرده شمش طلا", "name_en": "Gold Bar Certificate"},
    "go02": {"name_fa": "گواهی سپرده سکه طلا", "name_en": "Gold Coin Certificate"},
    "go03": {"name_fa": "گواهی سپرده شمش نقره", "name_en": "Silver Bar Certificate"},
    "in01": {"name_fa": "شاخص صندوق‌های طلا", "name_en": "Gold Funds Index"},
}

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


def determine_category(symbol: str, name_en: str) -> str:
    """
    Analyzes both the asset symbol and its English name to determine the
    most accurate category.
    """
    s = symbol.lower()
    n = name_en.lower() if name_en else ""

    if "fund" in n or "certificate" in n:
        return 'INDEX'
    if "coin" in n and "crypto" not in n:
        return 'COIN'
    if "futures" in n or "options" in n:
        return 'DERIVATIVES'

    if s.startswith('seke') or s.startswith('rob') or s.startswith('nim') or s.startswith('gerami'):
        return 'COIN'
    if 'crypto-' in s and s.endswith('-irr'):
        return 'CRYPTO_IRR'
    if s.startswith('crypto-'):
        return 'CRYPTO_USD'
    if s.endswith('-irr'):
        return 'CRYPTO_IRR'
    if s.startswith(('sana_', 'nima_', 'transfer_', 'bank_', 'ice_')):
        return 'CURRENCY_IRR'
    if s.startswith('price_'):
        return 'CURRENCY_IRR'
    if 'gold' in n or 'gold' in s or 'mesghal' in s or s.startswith('geram'):
        return 'GOLD'
    if 'silver' in n or 'platinum' in n or 'palladium' in n:
        return 'METAL'
    if s.startswith('bourse') or 'dow_jones' in s or 'nasdaq' in s or 's&p 500' in s:
        return 'INDEX'
    if 'commodity_' in s or 'oil' in s or 'lumber' in n or 'coffee' in n:
        return 'COMMODITY'
    if '-ask' in s or '-bid' in s or 'diff_' in s:
        return 'CURRENCY_FX'
    if 'ons' in s or 'aluminium' in s or 'copper' in s or 'zinc' in s or s.startswith('base_'):
        return 'METAL'
    
    return 'OTHER'




@shared_task
def scrape_assets_prices():
    """
    Scrapes price data using the static name map for higher quality data.
    """
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(BASE_API_ASSETS, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return f"Error fetching asset API: {e}"

    tehran_tz = pytz.timezone('Asia/Tehran')
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

        # --- UPDATED LOGIC: Use the static map ---
        asset_info = STATIC_NAME_MAP.get(symbol, {})
        name_fa = asset_info.get('name_fa') or symbol.replace('_', ' ').title()
        name_en = asset_info.get('name_en') or symbol.replace('_', ' ').title()
        
        category = determine_category(symbol, name_en)

        # Use update_or_create to keep names and categories fresh
        asset, _ = Asset.objects.update_or_create(
            symbol=symbol,
            defaults={
                'name_fa': name_fa,
                'name_en': name_en,
                'category': category
            }
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