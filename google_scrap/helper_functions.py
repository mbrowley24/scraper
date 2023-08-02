import pytz

from scraper_utils.tools import proxy_request, base_url, phone_number_cleaner, generate_id
from mongo_db_setup import mongo, collection_names
from bs4 import BeautifulSoup
import datetime


def check_url_in_list(urls, url):
    add_item = True

    # check if item is in the list
    for item in urls:

        # if item in the list change add item to False and break for loop
        if item == url:
            add_item = False
            break

    if add_item:
        urls.append(url)

    return urls


def page_urls(urls, url):
    urls = check_url_in_list(urls, url)

    source_page = proxy_request(url)

    # parse page with beautiful soup
    page_soup = BeautifulSoup(source_page, 'lxml')

    # locate a tag with class identifier to gather the first ten
    # search pages
    links = page_soup.find_all("a", {"class": 'fl'})

    for link in links:
        url = f"https://www.google.com{link['href']}"

        urls = check_url_in_list(urls, url)

    return urls


def get_business_names(divs):
    if divs is None:
        return None

    business_names_and_web_sites = []

    for div in divs:

        name_div = div.find('div', {"class": "dbg0pd"})

        if not name_div:
            continue

        name_span = name_div.find('span', {})
        name = name_span.text

        try:

            url = div.find('a', {"class": "yYlJEf Q7PwXb L48Cpd brKmxb"})

            website = base_url(url['href'])

            if website:
                business_names_and_web_sites.append({'name': name, 'website': website})

        except AttributeError:

            continue

    return business_names_and_web_sites


def save_businesses(businesses, category):
    db = mongo.get_db()
    businessCol = db[collection_names.businesses()]

    for business in businesses:
        business_entity = businessCol.find_one({'website': business['website']})

        if business_entity:
            print('business already in db')
            continue

        public_id = generate_id(businessCol)
        business = businessCol.insert_one(
            {"name": business['name'], "web_site": business['website'], "categories": [category],
             "public_id": public_id, "created_at": datetime.datetime.now(pytz.utc),
             "updated_at": datetime.now(pytz.utc)})

        print('business saved', business.inserted_id)


def get_business_divs(urls):
    return_list = []

    for url in urls:

        # use driver the get to the url
        r = proxy_request(url)

        # parse with beautiful soup
        soup = BeautifulSoup(r, 'lxml')

        divs = soup.find_all("div", {"class": "VkpGBb"})

        if not divs:
            continue

        for div in divs:
            return_list.append(div)

    return return_list


def website_url(web_site_div):
    web_site = ''

    web_link = web_site_div.find('a', {"class": "ab_button"})

    if web_link:
        print('web_link')
        print(web_link)
        try:
            web_site = web_link.attrs['href']

        except KeyError:
            print('key error')

    return web_site


def cities_names():
    city_list = ['phoenix', 'tucson', 'mesa', 'chandler', 'scottsdale', 'glendale', 'gilbert',
                 'tempe', 'albuquerque', 'las+cruses', 'rio+rancho', 'santa+fe', 'las+cruses']


def address_phone(div, business, web_site):
    clean_phone = ''
    phone_span = div.find("span", {"class": "LrzXr zdqRlf kno-fv"})

    business_web_sites = ''

    if web_site != '#':
        business_web_sites = web_site

    try:

        phone = phone_span.find('span', {}).text

    except AttributeError:

        phone = ''

    if phone != '':
        clean_phone = phone_number_cleaner(phone)

    address_div = div.find("div", {"class": "UDZeY OTFaAf"})

    try:
        location_container = address_div.find("span", {"class": "LrzXr"})
        location_text = location_container.text
        location = location_class(location_text)
    except AttributeError:
        return

    if location is None:
        return

    try:
        print('current location')
        Location.objects.get(
            address=location.address,
            business=business,
            phone=clean_phone,
            city=location.city,
            state=location.state,
            zip_code=location.zip_code,
        )

    except Location.DoesNotExist:
        print('new location')
        Location.objects.create(
            address=location.address,
            business=business,
            phone=clean_phone,
            city=location.city,
            state=location.state,
            zip_code=location.zip_code,
            web_site=business_web_sites
        )

    if business.web_site == '' and web_site != '':
        print('website')
        print(web_site)
        business.web_site = base_url(web_site)

    business.updated_at = datetime.datetime.now()
    business.save()
