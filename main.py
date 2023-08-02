from dotenv import load_dotenv
from yellow_pages import yp_scrapper_functions as yp
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def scraper():
    load_dotenv()
    yp.scrapper()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    scraper()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
