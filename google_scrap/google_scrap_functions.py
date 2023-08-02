from bs4 import BeautifulSoup
from mongo_db_setup import mongo, collection_names
from scraper_utils.tools import proxy_request
from .helper_functions import (page_urls, get_business_divs, website_url, address_phone, get_business_names,
                               save_businesses, cities_names)


def get_businesses():
    print('Starting scrap')

    cities = ["phoenix", "chandler", "mesa", "tucson", "albuquerque", "santa+fe"]

    businesses_cities_urls = {
        "phoenix": [],
        "chandler": [],
        "mesa": [],
        "tucson": [],
        "albuquerque": [],
        "santa+fe": []
    }

    for city in cities:

        categories = mongo.get_db()[collection_names.categories()].find({})

        for category in categories:

            print('Starting scrap')

            start_url = f"https://www.google.com/search?q={category.name}&near={city}"

            # get page source for beautiful soup
            starting_soup = proxy_request(start_url)

            # parse page with beautiful soup
            new_soup = BeautifulSoup(starting_soup, 'lxml')

            # check for more links element on search page
            to_businesses = new_soup.find('div', {"class": "iNTie"})

            # if more links element get the "a" tag element with the href to page with
            # business listings
            if to_businesses:

                link = to_businesses.find('a', {})
                # print(link.attrs['href'])
                url = f"https://www.google.com{link.attrs['href']}"

                # if href present in a tag use web driver to navigate to new page
                if link.attrs['href']:
                    businesses_cities_urls[city] = page_urls(businesses_cities_urls[city], url)

            # scrap business div containers
            business_div = get_business_divs(businesses_cities_urls)

            # Gather business names that also have websites
            business_name_with_website = get_business_names(business_div)
            save_businesses(business_name_with_website, category)


def get_locations():
    print('Starting scrap')

    for limit in range(100, 100000, 100):

        start = limit - 100

        businesses = mongo.get_db()[collection_names.businesses()].find({}).skip(start).limit(limit)

        for business in businesses:
            web_site = ''

            search_business = business.name.replace(' ', '+')
            for city in cities_names():

                url = f"https://www.google.com/search?q={search_business}+{city.name}"

                # use driver the get to the url
                r = proxy_request(url)

                # parse with beautiful soup
                soup = BeautifulSoup(r, 'lxml')

                web_site_div = soup.find("div", {"class": "IzNS7c duf-h"})

                if web_site_div:
                    web_site = website_url(web_site_div)

                address_phone_div = soup.find("div", {"class": "TzHB6b cLjAic LMRCfc"})

                if address_phone_div:
                    print("address_phone not null")
                    address_phone(address_phone_div, business, web_site)
