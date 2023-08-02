from setup_data.category_setup import categories
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    categories()
    print('categories setup complete')
