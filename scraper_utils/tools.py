import random
import string
from time import sleep
import validators
import requests
import os
import re
from urllib.parse import urlparse


def phone_number_cleaner(phone):
    phone_strip1 = phone.replace('(', '')
    phone_strip2 = phone_strip1.replace(')', '')
    phone_strip3 = phone_strip2.replace('-', '')
    phone_strip4 = phone_strip3.replace('+1', '')
    clean_phone = phone_strip4.replace(' ', '')

    return clean_phone


def generate_id(collection, iterations=30):
    chars = string.ascii_letters + string.digits

    generated_id = ''.join(random.choice(chars) for i in range(iterations))

    while collection.find_one({'public_id': generated_id}) is not None:
        generated_id = ''.join(random.choice(chars) for i in range(30))

    return generated_id


def proxy_request(url):

    return_value = ""

    payload = {'api_key': os.environ.get("SCRAPPER_API_KEY"), 'url': url, 'render': 'true'}
    headers = {
        'accept': 'application/json',
        'Content-Type': 'multipart/form-data',
    }
    while return_value == "":

        try:
            r = requests.get('http://api.scraperapi.com', headers=headers, params=payload)

            return_value = r.text
            r.close()

        except requests.exceptions.RequestException:
            sleep(1)
            print('proxy request error')

    return return_value


def async_proxy_request(url):
    json = {'apiKey': os.environ.get("SCRAPPER_API_KEY"), 'url': url, 'method': 'POST',
            'body': 'var1=value1&var2=value2', 'render': 'true'}

    r = requests.post('https://async.scraperapi.com/jobs', json=json)

    print(r.json())
    job_details = {
        'job_id': r.json()['id'],
        'statusUrl': 'https://async.scraperapi.com/jobs/35b9db39-03b7-4eeb-a87b-67a7c53a7584',
        'status': r.json()['status'],
    }

    while job_details['status'] != 'finished':

        r = requests.get(job_details['statusUrl'])
        sleep(1)
        job_details['status'] = r.json()['status']
        print(r.json())

        if job_details['status'] == 'finished':
            print('finished')
            print(r.json()['body'])

    return r


def base_url(url_string):
    print(url_string)

    url = urlparse(str(url_string))

    try:
        validators.url(url_string)
    except validators.ValidationFailure:
        return None

    domain = url.netloc
    protocol = url.scheme

    if protocol == "" or protocol is None:
        return None

    if domain == "" or domain is None:
        return None

    return f"{protocol}://{domain}"


def zip_code_check(zip_code):
    zip_code = str(zip_code)
    regex = re.compile(r'^\d{5}(?:[-\s]\d{4})?$')

    return regex.match(zip_code)


