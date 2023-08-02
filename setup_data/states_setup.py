import csv
from mongo_db_setup.mongo import collection
from scraper_utils.tools import generate_id


def states():
    try:
        print('reading csv file')
        # read csv file
        file = open('setup_data/states.txt', 'r')

        print('csv file found')

        # parse csv file
        csv_reader = csv.reader(file, delimiter=',')

        # iterate through csv file
        for row in csv_reader:
            name = row[1].lower()
            abbreviation = row[0].lower()

            stateCollection = collection('states')

            # query data
            query_data = {'name': name, 'abbreviation': abbreviation}

            # check if state exists
            state = stateCollection.find_one(query_data)
            public_id = generate_id(stateCollection)

            if state:
                # generate public id
                public_id = state.get('public_id')

                if public_id == '' or public_id is None:
                    print("new public id: ", public_id)
                    stateCollection.update_one(query_data, {'$set': {'public_id': public_id}})

                continue

            stateCollection.insert_one({'name': name, 'abbreviation': abbreviation, 'public_id': public_id})
            print('state inserted')

    except FileNotFoundError:
        print('csv file not found')
