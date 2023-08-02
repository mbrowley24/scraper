from bs4 import BeautifulSoup
from scraper_utils.tools import proxy_request, base_url, async_proxy_request
from mongo_db_setup import mongo, collection_names
from .helper_yp_scrapper_functions import (business_name, business_url, business_phone, business_address, location_dict,
                                           check_create_business, business_city_state_info, business_category,
                                           check_create_location, check_create_zip_code)


def scrapper():
    locations = location_dict()

    for stateAbbr in locations.keys():
        offset = 0
        entries = 50

        db = mongo.get_db()
        categoryCol = db[collection_names.categories()]

        terms = categoryCol.find({})
        print(terms)

        if len(locations[stateAbbr]) == 0:
            continue

        for city in locations[stateAbbr]:

            for term in terms:
                print(term)
                search_term = term['name'].replace(' ', '+')
                params = {
                    'name': '',
                    'url': '',
                    'phone': '',
                    'address': '',
                    'city': '',
                    'state': '',
                    'zip_code': '',
                    'categories': [],
                }

                for page in range(1, 1000):

                    url = f"https://www.yellowpages.com/search?search_terms={search_term}" \
                          f"&geo_location_terms={city}%2C%20{stateAbbr}&page={page}"

                    print(url)
                    r = proxy_request(url)

                    soup = BeautifulSoup(r, 'lxml')

                    business_info = soup.find('div', {'class': 'search-results organic'})

                    if business_info:

                        business_v_card = business_info.find_all('div', {'class': 'v-card'})

                        if business_v_card:

                            for card in business_v_card:

                                params['url'] = business_url(card)

                                print('business url: ', params['url'])

                                if params['url'] is None:
                                    print("no url")
                                    continue

                                params['name'] = business_name(card).lower()
                                print('business name: ', params['name'])
                                params['phone'] = business_phone(card)

                                params['categories'] = term

                                business = check_create_business(params, term)

                                if business is None:
                                    continue

                                params['address'] = business_address(card)
                                print('business address: ', params['address'])

                                if params['address'] == '':
                                    print("no address")
                                    continue

                                location_obj = business_city_state_info(card)

                                if location_obj:
                                    location = check_create_location(params, location_obj)
                                    print(f'location created: {location["address"]}')
                    else:
                        break
