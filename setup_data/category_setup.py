from mongo_db_setup.mongo import collection
from scraper_utils.tools import generate_id
import csv


def categories():
    try:
        print('reading csv file')

        file = open('setup_data/categories.txt', 'r')

        print('csv file found')

        csv_reader = csv.reader(file, delimiter=',')

        for row in csv_reader:
            name = row[0].lower()

            # get mongo connection to db and collection
            categoryCollection = collection('categories')
            category = categoryCollection.find_one({'name': name})

            # generate public id
            public_id = generate_id(categoryCollection)

            # check if category exists
            if category:

                current_public_id = category.get('public_id')

                # if category exists and has no public id, add public id
                if current_public_id == '' or current_public_id is None:
                    print("new public id: ", public_id)
                    categoryCollection.update_one({'name': name}, {'$set': {'public_id': public_id}})

                # continue to next iteration
                continue

            # create new category
            new_category = categoryCollection.insert_one({'name': name, 'public_id': public_id})

            print(f'category inserted: {new_category.inserted_id}')

    except FileNotFoundError:
        print('csv file not found')
