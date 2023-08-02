from bs4 import BeautifulSoup
from scraper_utils.tools import proxy_request, base_url, phone_number_cleaner, generate_id, zip_code_check
from urllib.parse import urlparse
from mongo_db_setup import mongo, collection_names
from datetime import datetime
import pytz
import validators


def business_name(card):
    return_string = ""

    info = card.find('div', {'class': 'info-section info-primary'})

    if info:
        name = info.find('a', {'class': 'business-name'})

        if name:

            return_string = name.text.strip().lower()

            if len(return_string) > 255:
                return_string = return_string[:255]

    return return_string


def business_url(card):
    return_string = ""
    info = card.find('div', {'class': 'info-section info-primary'})

    if info:
        website = card.find('a', {'class': 'track-visit-website'})

        if website:
            web_site_url = website.attrs['href']
            return_string = web_site_url.lower()

    return return_string


def business_phone(card):
    return_string = ""

    info = card.find('div', {'class': 'info-section info-secondary'})

    if info:

        phone = info.find('div', {'class': 'phones phone primary'})

        if phone:
            char = ['(', ')', '-', ' ']
            phone = phone.text.strip()

            for c in char:
                phone = phone.replace(c, '')

            return_string = phone

    return return_string


def business_address(card):
    return_string = ""

    info = card.find('div', {'class': 'info-section info-secondary'})

    if info:
        address = info.find('div', {'class': 'street-address'})

        if address:
            return_string = address.text.strip().lower()

        else:
            return_string

    return return_string


def business_city_state_info(card):
    return_dict = {
        'city': '',
        'state': '',
        'zip_code': '',
    }

    db = mongo.get_db()
    stateCol = db[collection_names.states()]
    info = card.find('div', {'class': 'info-section info-secondary'})

    if info:
        locality = info.find('div', {'class': 'locality'})

        if locality:
            locality_string = locality.text
            locality_string = locality_string.replace(',', '')
            locality_string = locality_string.split(' ')

            return_dict['city'] = locality_string[0].lower()
            return_dict['state'] = locality_string[1].lower()
            return_dict['zip_code'] = locality_string[2].lower()

            state = stateCol.find_one({'abbreviation': return_dict['state']})

            if state is None:
                print("state not found")
                return_dict['state'] = ''

            if zip_code_check(return_dict['zip_code']) is None:
                print("zip code invalid")
                return_dict['zip_code'] = ''

    if return_dict['city'] == '':
        return None
    if return_dict['state'] == '':
        return None
    if return_dict['zip_code'] == '':
        return None

    return return_dict


def business_category(card):
    return_list = []

    info = card.find('div', {'class': 'info-section info-secondary'})

    if info:
        categories = info.find('div', {'class': 'categories'})

        if categories:
            for category in categories.find_all('a'):
                return_list.append(category.text.strip().lower())

    return return_list


def check_create_zip_code(params):
    if params['zip_code'] == '':
        return None
    if params['state'] == '':
        return None
    if params['city'] == '':
        return None

    return_dict = {
        'zip_code': None,
        'city': None,
        'state': None,
    }

    return return_dict


def check_create_business(params, term):
    return_business = None

    try:
        validators.url(params['url'])

    except validators.ValidationError:

        return None

    print("params: ", params['url'])
    web_site = base_url(params['url'])

    print("web_site: ", web_site)

    db = mongo.get_db()

    businessCol = db[collection_names.businesses()]

    business = businessCol.find_one({'web_site': web_site})

    if business:

        return_business = businessCol.update_one({'web_site': web_site},
                                                 {'$addToSet': {'categories': term},
                                                  '$set': {'updated_at': datetime.now(pytz.utc)}})
    else:
        public_id = generate_id(businessCol)
        return_business = businessCol.insert_one({'name': params['name'], 'web_site': web_site, 'public_id': public_id,
                                                  'categories': [term], 'updated_at': datetime.now(pytz.utc),
                                                  'created_at': datetime.now(pytz.utc)})
    return return_business


def check_create_location(params, location_obj):
    # get mongo db client
    db = mongo.get_db()

    # get location collection
    locationCol = db[collection_names.locations()]
    businessCol = db[collection_names.businesses()]
    web_site = base_url(params['url'])

    # get business object
    business = businessCol.find_one({'web_site': web_site})

    # get location street address to lower case
    address = params['address'].lower()

    # clean number of format
    phone = phone_number_cleaner(params['phone'])

    location_query = {'address': address, 'city': location_obj['city'], 'state': location_obj['state'],
                      'zip_code': location_obj['zip_code'], 'phone': phone, 'business': business['_id']}

    location = locationCol.find_one(location_query)

    if location is None:
        public_id = generate_id(locationCol)
        locationCol.insert_one({'address': address, 'city': location_obj['city'], 'state': location_obj['state'],
                                'zip_code': location_obj['zip_code'], 'phone': phone, 'public_id': public_id,
                                'business': business['_id'],
                                'updated_at': datetime.now(pytz.utc),
                                'created_at': datetime.now(pytz.utc)})

    return locationCol.find_one(location_query)


def check_page_url(new_url, urls):
    returnValue = True

    for url in urls:

        if url == new_url:
            returnValue = False
            break

    print(returnValue)
    return returnValue


def page_url_list(soup, urls):
    pagination = soup.find('div', {'class': 'pagination'})

    if pagination:
        pages = pagination.find_all('a')

        if pages:
            for page in pages:
                if page.attrs['href']:
                    add_url = check_page_url(page.attrs['href'], urls)

                    if add_url:
                        new_url = f"https://www.yellowpages.com{page.attrs['href']}"
                        print(new_url)
                        urls.append(new_url)

    else:
        return urls

    return urls


def location_dict():
    locations = {
        'az': ['phoenix', 'tucson', 'mesa', 'chandler', 'scottsdale', 'glendale', 'gilbert', 'tempe', ],
        'nm': ['albuquerque', 'las+cruses', 'rio+rancho', 'santa+fe'],
    }

    return locations
