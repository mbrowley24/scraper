from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, CollectionInvalid
import os


def get_db(db_name='scraper'):
    print('connecting to db')

    # mongo db connection connection string in env file
    client = MongoClient(os.environ['MONGO_URL'])

    try:
        client.admin.command('ping')
        print('MongoDB connection: Success')

    except ConnectionFailure:
        print('Connection failed')

    return client[db_name]


def collection(collection_name):
    db = get_db()

    return db[collection_name]
