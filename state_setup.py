from setup_data.states_setup import states
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()
    states()
    print('states setup complete')
