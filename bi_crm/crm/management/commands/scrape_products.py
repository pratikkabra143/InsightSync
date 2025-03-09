import http.client
import json
import re

from django.core.management.base import BaseCommand
from django.utils import timezone
from crm.models import Product

# List of ASINs to process
ASIN_LIST = [ 'B09QXCWLNS', 'B07L9FW9GF', 'B0CG13FJ5M', 'B0B296NTFV', 'B0CGCZHGW1', 'B09KBJK9LK', 'B0BYDYJLZR', 'B0C9TJ1ZW2', 'B01KK0HU3Y', 'B01HJI0FS2', 'B0D18192T2', 'B098JYT4SY', 'B0819HZPXL', 'B0CP9NSXYJ', 'B0CQRNWJM2', 'B0BG8LZNYL', 'B079Y6JZC8', 'B098K1439N', 'B01M72LILF', 'B0C9TJ1ZW2', 'B0CP9NMKCR', 'B0D95SBTM9','B0DCGC6ZV6', 'B0DCGCM6QF', 'B0DCG9J4KS', 'B0C2CTWLHZ', 'B0BJVZQ6YT', 'B0BB2H5133', 'B07LDKFM2Y', 'B09CYMRW1P', 'B0B8ZJPPML', 'B0B8MNBDS2', 'B0CJLSF2T2', 'B0CH551FC3', 'B0CGVKRNKN', 'B09YRZ734R', 'B01LYISMKO', 'B0CLHD6YQB', 'B0CQ23K1SB', 'B08PPL3ZM8', 'B08WWRJ4FM', 'B0CPBNZHDR', 'B0CYHF557D', 'B0CKRGLFQF', 'B0D7CT6PCT', 'B0DGYT5KGX', 'B0B8ZF81HJ', 'B0CR7G9V56', 'B0CZ23FJJT', 'B0D59QFJJJ', 'B084T6CK4K', 'B0CST2ML2W', 'B0CH9X8KPR', 'B08TQQBG7C', 'B0BWCVYFLC', 'B0CCM8L54V', 'B0824BZGH9', 'B07NC6LY1K', 'B0CRKLSVRL', 'B09W5LHL7G', 'B0BQMJZZNM', 'B0BKZK9JGB', 'B0DHCPZ19F', 'B0D8YJ6VFZ', 'B083C6XMKQ', 'B0BCKLM33P', 'B0C66RZQ1Z', 'B07P8SYN87', 'B0DB249WGP', 'B0B42B4C43', 'B0DKTFKCD2', 'B0CWH1NH84', 'B0D3LXD8JM', 'B0BBV83YF9', 'B07LF3PQYF', 'B0B8ZL88R5', 'B0CJLSF2T2', 'B0D25C6QP2', 'B0BR3VKC3F', 'B0BRSXGY2J', 'B0CP93MZMD', 'B0DJPJ5KXH', 'B0BYJYZGM8', 'B0CV3C2JYZ', 'B0CLVJ3JGY', 'B0CVWC3YBT', 'B0CTMQ9LST', 'B093FDQ5HK', 'B0CL2KWY66', 'B07YZ367F6', 'B07WR8GT3C', 'B09RT2Y23P', 'B0BC4N5K7D', 'B0CJLSF2T2', 'B08MD5J7Z5','B08Q824RKC', 'B07PDVRMJ9', 'B099S4TJLM', 'B0BB2H5133', 'B0BJW1KF1V', 'B0CNP9Q96Y', 'B09VT836NB', 'B0D97KFYRY', 'B0CXP9PTNR', 'B0DDQHGJLX', 'B0DFTLLS5N', 'B0CV9VWCS1', 'B08B4WJ6MK', 'B0C863H2WP', 'B0CZXWXCRG', 'B0DPG78YZB', 'B0DF69J28D', 'B09VT836NB', 'B0CVDSYCMW', 'B07DWKC8TB', 'B0D3GZPKTD', 'B0D581D417', 'B0CPQ373F5', 'B0DNWJNCXD', 'B0DQLKV19G', 'B0CR7G9V56', 'B0D98HBYMX', 'B0DP9NPN5P', 'B0CWCZBQ7V', 'B0CV93ZP8J', 'B0DSG3V4KD', 'B0D9FXRXNJ', 'B0DG97GMB5', 'B0CS9KH1Y9', 'B0BVMQQTLM', 'B09TKHNFB2', 'B0DRJDN1CZ', 'B0DP7254FC', 'B0756P63PQ', 'B0C599YQ1L', 'B0936PVCZG', 'B08SW5GMP6', 'B0DJFKLLQ4', 'B0C5R3DLSF', 'B0DNN5MZF8', 'B0CQVS991V', 'B0C42T7C2F', 'B0CKN8FFZP', 'B0CXM5DT52', 'B0DJW3PCY8', 'B0DRZV5953', 'B008XT42JU', 'B0824BZGH9', 'B0D8YM1FG4', 'B09LTYL9QH', 'B06XBXF8FB', 'B08QV81LPT', 'B07LC7LF9Y', 'B0DNWB2DQ7', 'B0D3HPCSHN', 'B0CNVL62DH', 'B0CXSH4F95', 'B0C3ZMCKZ8', 'B0D74KXZRQ', 'B0DTKF4V6X', 'B0DFTLLS5N', 'B0DRZV5953','B0DQ8MGRNX', 'B0DQ8R1DB5', 'B0DPS7FB4J', 'B07WHQRN1B', 'B0D5YCYS1G', 'B0D7VGZS69', 'B0CX59H5W7', 'B0D7VKSZGW', 'B0BY8MCQ9S', 'B0D7VKMLGD', 'B0DPS62DYH', 'B0CX58MTNN', 'B0DQ8MJYXF', 'B0DPFSJV2Z', 'B0CX59SD6C', 'B0DQ8S38R8', 'B0D7VJ72XK', 'B0BSNP46QP', 'B0BY8JZ22K', 'B0D7W9R1HM', 'B09TVV1TXL','B0D3X9275X', 'B0DCZJDYZY', 'B0D3X9P9DM', 'B0D3XBM3FR', 'B0C4DPCKDJ', 'B0CZ6TRNGT', 'B0B8YTGC23', 'B07MNNH484', 'B0D1V9PM7D', 'B0D3X9275X', 'B0C4DPCKDJ', 'B0D25MMHH2', 'B08DPLCM6T', 'B0DCZMPRXC', 'B0DBLLYXVV', 'B0D25MMHH2', 'B0CZ6QF29Y', 'B08QX1CC14', 'B0D3X9275X', 'B0BFFHGML2', 'B0CZ6PVG32', 'B07MDRGHWQ', 'B07MKFNHKG', 'B0D3DZ1SPM', 'B0CZ6QH357', 'B0CZ6V978P', 'B0DBLLXZW4', 'B0D25MMHH2', 'B0D9BYN6RJ','B0BBB8VC23', 'B09WLMD7DJ', 'B0C1Z5SJPR', 'B081LGL5QT', 'B01N54ZM9W', 'B0D5XXT373', 'B0CD4GCMZG', 'B09WYD48F1', 'B0D7MJ7P7X', 'B09XXQNVTR', 'B0DB1RRWV2', 'B0914M88KG', 'B0CJ8WKK34', 'B095T3QVDM', 'B0B6GC4HJB', 'B09JPBYQSB', 'B096BFVSFG', 'B0845PSY99', 'B0CNX9F94J', 'B0BQHSR8VP', 'B09RFVCVSD', 'B07HL3VT14', 'B0DF5WVGV2', 'B0C3XXDY1J', 'B0DGXJLCS1', 'B0CX2Z8KQM', 'B0DJ1RLB89', 'B0B51HPF5Q', 'B08PRY7ZY8', 'B0CR2VKCJ6', 'B0D3XZRZ1D', 'B0928Q5MVF', 'B0DLGZ2J3H', 'B0C58BTFZ2', 'B09ZD6D19Y', 'B0864XGSHC', 'B09RF865D4', 'B0DRKM7XH7', 'B09HCDV6JW', 'B0CVTVT79X', 'B09MFSPSP4', 'B0BVBW23PX', 'B0C4YMX5GF', 'B086631CRF', 'B0D2H9WW12', 'B09SN6R3G9', 'B0DG5P5WPQ', 'B08D3L7853', 'B0CMJDBXL9', 'B0CSKQQQ9F', 'B0DGXJKMKB', 'B00IZ95VZW', 'B01MSJNMFE', 'B08D7R8LWY', 'B091FK82FC', 'B096BDX65F', 'B0DF5WVGV2', 'B0C3XXDY1J', 'B0D73D68GD', 'B08Q5557JR', 'B0D2N6SGF3','B09D7ZDH4B', 'B0BT7RMLX9', 'B09X1JV98N', 'B09ZH7SYSB', 'B0D6KR8Z19', 'B0CS2VYXSJ', 'B0CKT95H5V', 'B0BCKLM33P', 'B0927T6DS6', 'B0BLP5S7W4', 'B0CHW9JGWY', 'B0CDSFX882', 'B0BFFXY41G', 'B09ZH7SYSB', 'B09WTK9QHM', 'B08Y5YCQ9S', 'B088MK8CPW', 'B09HSWBVVZ', 'B08DRFDV13', 'B08FYJV1PT', 'B0CXR9HF3D', 'B0BRCRKTVM', 'B0C3XW8621', 'B0BC3SKYJ9', 'B0CQXR7PQX', 'B0BS49X9DV', 'B0DJNRZKX6', 'B0D83MYR73', 'B0D7HZHGQT', 'B0BFFXY41G', 'B0BLK7Q912', 'B0CDSFX882', 'B0DP7BPV9L', 'B0CQNTS7WS', 'B0D25C6QP2', 'B0CWHB1HXM', 'B0CQMTP5CH', 'B0CDM18NS1', 'B0BCKHGZF4', 'B0DGGYS38S', 'B0DCKR8885', 'B0B6SXGSD5', 'B0BQ7FYKJ3', 'B0DHCPZ19F', 'B0BDF38CRX', 'B0DQDBTH4S', 'B07SWRC12Q', 'B0CJNV5WYX', 'B0CXX8S31B', 'B0CNXJ214M', 'B08VGMLCVF', 'B0BT22VK8Y', 'B0CQT36SJW', 'B0D7QBTL1S', 'B09D7ZDH4B', 'B07JDT2C53', 'B0DJZGG3VG', 'B0DFW9TR7G', 'B01LHNLJT4', 'B09SLV7C38', 'B0DG2ZM63D', 'B0B5WX1ZH9', 'B0C53S7H39', 'B0BKT8VL1L', 'B0DHKYJMPV', 'B0BHSBMKHM', 'B09GZK7Y6L', 'B09RP4YTW3', 'B0CHW9JGWY', 'B081X62NQD', 'B0D7HZHGQT', 'B09ZH7SYSB', 'B09RP4YTW3','B0CSKG16HJ', 'B0BNDXNDNF', 'B08WBG2GBH', 'B0C6KRGHKX', 'B09G9W3WFL', 'B0CV7DHCSL', 'B07XG4NSMM', 'B07ZVRHVJ4', 'B091Q6D4QW', 'B0B5N956P2', 'B07X91P9VZ', 'B09G9W3WFL', 'B082WVLN48', 'B08H87CXNR', 'B08L6BJNJL', 'B07NL61B2S', 'B09CR1CVW7', 'B0D8H1JBHQ', 'B09W5F6KGB', 'B08H8KD72Q', 'B0BKZK9JGB', 'B0B8RR5VQF', 'B0DH7WTKDN', 'B0C17FWR59', 'B0B77X44MX', 'B09X39XLR3', 'B0CR7G9V56', 'B098JV1SNN', 'B097PG9SBW', 'B083HL2QX3', 'B09DV6PDT9', 'B0CLDQ2GJP', 'B07NC6LY1K', 'B0BVBLQ337', 'B0BS3YY9ZQ', 'B0CH137WLD', 'B0BC47M9YL', 'B09G9W3WFL', 'B09YY2BRFD', 'B09ZLLQ3G2', 'B09F3RZCZW', 'B00ICCYIRO', 'B0BV2RPCP3', 'B0DF4WDDBC', 'B08CTJFJG9', 'B098K63RXT', 'B09K472Y76', 'B0B293BVRT', 'B0BT1YLQM5', 'B09QQDNP6P', 'B0D8JG1MDN', 'B084D16LD6', 'B09TR82NXB', 'B0D6J5LX5T', 'B099WYSG6G', 'B0BN6PCPXC', 'B0C17P9N27', 'B0C17MSK27', 'B0C8JKYVW6', 'B0BN48GPXG', 'B07FWQ9HRV', 'B091Q5H9YC', 'B0D6BT41V5', 'B0CLXWH4X1', 'B0DH53CGG8', 'B0DBJ3G3P5', 'B08CTJFJG9', 'B0D43QFC14', 'B08H87CXNR', 'B09G9W3WFL', 'B08L6BJNJL', 'B082WVLN48', 'B0DH86ZXD2','B0DTB4FP7C', 'B0DTB2XHLZ', 'B0D2KK3DW4', 'B0D4VGVSYN', 'B0D78QRYKV', 'B0D4VD11TN', 'B0C1GLVWTZ', 'B0BD5R89RQ', 'B00HFPIIOI', 'B00ISNVQMW', 'B078HLGKJW', 'B0D9NMS63L', 'B0CK6N9VDC', 'B0DC1823GZ', 'B0DFYL4635', 'B0CQ4HSR2D', 'B0BNHD7MM3', 'B000GAYQJ0', 'B099WNYHY2', 'B0BF57RN3K', 'B0D7M54GMJ', 'B0B6BPTFT5', 'B07MDGSP8F', 'B0DBZ2KZ4J', 'B0C3HB6XCN', 'B0DGLQ8KV4', 'B0CTG2N8DD', 'B07G5XQN9D', 'B07H3K85H5', 'B0CFFZR3H8', 'B01KNMEVDG', 'B08425LS13', 'B09DPZFXMQ', 'B00DUCIK7U', 'B0BJ72WZQ7', 'B099WR4WHC', 'B0CF255543', 'B0D37PHZD1', 'B0B1N3ZX7M', 'B0DM5RD6M6', 'B07CQ2DBSN', 'B07MXKMWT5', 'B01L3AZ5VE', 'B00AG37H8Y', 'B0D5LRGSCR', 'B00FZE1AZU', 'B01KNMEVDG', 'B0183NW5H6', 'B00E54TNH8', 'B0C497MSQN', 'B0DM5GVXJ9', 'B0BK85265D', 'B0CZ7LQFQL', 'B0BRKZG8GH', 'B0B5LWP12T', 'B01M5K1O7E', 'B0DGGVHMDS', 'B00ISNVM0S', 'B0C65XSTSK', 'B0CCFV4DV2', 'B08J6HRBLC', 'B00WM0CF4A', 'B0C496V772', 'B0CXXDG3LS', 'B00YS2WI7O', 'B0DT6GR65Q', 'B0D9Y7X1FD', 'B07RB6RMSN', 'B0CCFV4DV2', 'B09DPZFXMQ', 'B0CFFZR3H8', 'B0DNYXKDTN', 'B0CH8DP8Q7','B0DTB4FP7C', 'B0DTB2XHLZ', 'B0DTB3JSVV', 'B0DTB2XHLZ', 'B0DT9ZPRRB', 'B0BJ72WZQ7', 'B0BW4BFBD5', 'B0B6BPTFT5', 'B0CQLYXDXH', 'B0DM5KTM8K', 'B0DCZWZ39H', 'B0DM5RD6M6', 'B0DM5KP711', 'B0DFYL4635', 'B0DGJ917JQ', 'B0BRKZG8GH', 'B0C497MSQN', 'B0C496V772', 'B0CNW6XHP4', 'B0CXXDW4XG', 'B0CQRQK8L8', 'B0BF57RN3K', 'B0CCYPRZH6', 'B0BJ74PQK6', 'B0DM5RD6M6', 'B0D2K6JJNX', 'B0CQLYXDXH', 'B0DFLYMF79', 'B0DFYL4635', 'B0C4Q5HNMH','B09PK4XBDH', 'B0BPXQ4RX1', 'B0BPXLK2VS', 'B082BHK4D7', 'B09PR6MXH3', 'B0DCK87T14', 'B0DF5F7KXX', 'B0DSJKQXD9', 'B0BBFCG66M', 'B0DCK87T14', 'B09VDMY158', 'B08J88M4FN', 'B0BQQS5T5H', 'B09GC834XQ', 'B0BXPXWZQT', 'B0CLZY9FBS', 'B07RDJSJMZ', 'B079M6WDL8', 'B0CJV3HS9V', 'B095SWYF6M', 'B08Z332VVM', 'B0CKBW8L3M', 'B08YWZ62QZ', 'B089TKXP92', 'B08M77K5CK', 'B07SD3T8M1', 'B0DHRVCMYC', 'B0B8T1G75Q', 'B0B65BKP3R', 'B0B86LMJW8', 'B0C4YZ8621', 'B0BM4HFKHK', 'B0D7VZW3XN', 'B0DRY1XD5R', 'B0BR3VKC3F', 'B09T37S9Y5', 'B0CYTDQ3YF', 'B08RF1VL1D', 'B078WWHZ72', 'B0D59QFJJJ', 'B0BYT1DTVL', 'B0D324VJ6G', 'B0B8ZRNNYM', 'B0DMVVLMVS', 'B0BRXVT1R2', 'B09NHS9JJD', 'B0D2LLHLGP', 'B0D5Y9X4BZ', 'B0D4MCYBVT', 'B0D8W2K7C5', 'B0CGNJV2L8', 'B07BLXLY4T', 'B0D66TZYM3', 'B0DKZKLDC2', 'B0BD43W4YP', 'B0CJF4P976', 'B0CKJXGPLY', 'B0CWB37LGP', 'B0DQVHXDQJ', 'B093V8B61H', 'B0CLVDYX1S', 'B0DHSDKVX6', 'B0CJJ5PCJ7', 'B0D738FNB2', 'B09VDMY158', 'B0C5VJ1Y6K', 'B0BZT87KK4', 'B0D5Y9X4BZ', 'B09VDMY158', 'B0BYT1DTVL', 'B0BQQS5T5H', 'B0DJ8PPYWV', 'B0CTYKHDC6']

def parse_decimal_value(value):
    """
    Parses a string to a float after removing commas and extraneous characters.
    Returns None if conversion fails.
    """
    if value is None:
        return None
    # Remove any non-digit characters except for '.' and '-' (to allow for decimals and negative numbers)
    cleaned = re.sub(r"[^\d\.\-]", "", value)
    try:
        return float(cleaned)
    except Exception as e:
        return None

import http.client
import json

API_KEYS = [
    "1bc6019b8fmsh6b0d881eee73c98p19b4c3jsn8d34622f71b4",
    "390689ef64msh5a0f8d0674b5e03p18c344jsn4c78a6ef2b1c",
    "bbe73ef5aamsh0f75fe09e0f4d99p19bca7jsn7b79608943c5",
    "5b01d6362fmsh7a243a32e665950p1fb060jsn8c9f5c74cceb",
    "fec37c52bbmshafda54517f90b51p1e01f6jsn50e30e46ba72",
    "eeb1f38a98msh541cadf5cc71f02p14d873jsnff97131274e4"
]

API_HOST = "real-time-amazon-data.p.rapidapi.com"
api_key_index = 0  # Start with the first API key

def get_headers():
    return {
        'x-rapidapi-key': API_KEYS[api_key_index],
        'x-rapidapi-host': API_HOST
    }

def switch_api_key():
    global api_key_index
    if api_key_index < len(API_KEYS) - 1:
        api_key_index += 1
        print(f"Switching API key to index {api_key_index}")
    else:
        raise Exception("All API keys have exceeded their limits.")

def scrape_and_store_products(asins):
    global api_key_index

    for asin in asins:
        while True:  # Retry loop to handle API key switching
            try:
                conn = http.client.HTTPSConnection(API_HOST)
                endpoint = f"/product-details?asin={asin}&country=IN"
                conn.request("GET", endpoint, headers=get_headers())
                res = conn.getresponse()
                data = res.read()
                json_data = json.loads(data.decode("utf-8"))

                # Check for quota exceeded message
                error_message = json_data.get("message", "").lower()
                if "exceeded the monthly quota" in error_message:
                    print(f"API key {api_key_index} exceeded limit. Switching key...")
                    switch_api_key()
                    continue  # Retry with new key

                
                if json_data.get("status") == "OK":
                    product_data = json_data.get("data", {})

                    # Assume parse_decimal_value is a helper function
                    product_price = parse_decimal_value(product_data.get("product_price"))
                    original_price = parse_decimal_value(product_data.get("product_original_price"))

                    # Update or create product record
                    product, created = Product.objects.update_or_create(
                        asin=product_data.get("asin"),
                        defaults={
                            "name": product_data.get("product_title"),
                            "category": product_data.get("category", ""),
                            "price": product_price,
                            "original_price": product_data.get("product_original_price"),
                            "currency": product_data.get("currency"),
                            "country": product_data.get("country"),
                            "description": product_data.get("product_description"),
                            "product_byline": product_data.get("product_byline"),
                            "product_byline_link": product_data.get("product_byline_link"),
                            "rating": float(product_data.get("product_star_rating", 0)) if product_data.get("product_star_rating") else None,
                            "product_num_ratings": product_data.get("product_num_ratings"),
                            "product_url": product_data.get("product_url"),
                            "product_photo": product_data.get("product_photo"),
                            "product_num_offers": product_data.get("product_num_offers"),
                            "product_availability": product_data.get("product_availability"),
                            "is_best_seller": product_data.get("is_best_seller", False),
                            "is_amazon_choice": product_data.get("is_amazon_choice", False),
                            "is_prime": product_data.get("is_prime", False),
                            "climate_pledge_friendly": product_data.get("climate_pledge_friendly", False),
                            "sales_volume": product_data.get("sales_volume"),
                            "customers_say": product_data.get("customers_say"),
                            "product_information": product_data.get("product_information"),
                            "product_details": product_data.get("product_details") or {},
                            "product_photos": product_data.get("product_photos"),
                            "product_videos": product_data.get("product_videos"),
                            "video_thumbnail": product_data.get("video_thumbnail"),
                            "has_video": product_data.get("has_video", False),
                            "delivery": product_data.get("delivery"),
                            "primary_delivery_time": product_data.get("primary_delivery_time"),
                            "category_path": product_data.get("category_path"),
                            "product_variations": product_data.get("product_variations"),
                            "deal_badge": product_data.get("deal_badge"),
                            "has_aplus": product_data.get("has_aplus", False),
                            "has_brandstory": product_data.get("has_brandstory", False),
                            "more_info": product_data.get("more_info")
                        }
                    )
                    print(f"Product {asin} stored. Created: {created}")
                else:
                    print(f"Failed to fetch data for ASIN: {asin}. Response: {json_data}")
                break  # Break out of while loop and move to next ASIN
                
            except Exception as e:
                print(f"Error processing ASIN {asin}: {str(e)}")
                break  # Move to the next ASIN if an error occurs



class Command(BaseCommand):
    help = "Scrapes product data for a list of ASINs and stores/updates Product records."

    def handle(self, *args, **options):
        self.stdout.write("Starting product scraping for ASINs...")
        scrape_and_store_products(ASIN_LIST)
        self.stdout.write(self.style.SUCCESS("Product scraping completed."))
