import logging
import mysql.connector
from sklearn.tree import DecisionTreeClassifier
import joblib

tables = list()


def connect_to_database():
    global cursor, cnx
    try:
        # Connect to database
        cnx = mysql.connector.connect(user='whsnow', password='', host='127.0.0.1', database='pcp')
        # Create cursor object
        cursor = cnx.cursor()
        logging.info('( analyse_data ): connected to database and made cursor')
    except Exception as e:
        logging.error(f'( analyse_data ): Error connecting to database: {e}')


def get_scans():
    try:
        # Execute SHOW TABLES query
        cursor.execute("SHOW tables")
        # Fetch all table names
        results = cursor.fetchall()
        for result in results:
            # Add table names that contain "scan" to a list
            if result[0].decode().find('scan') != -1:
                tables.append(result[0].decode())
    except Exception as e:
        print(e)
    # Return the list of table names
    return tables


def delete_empty_tables():
    for table in tables:
        # Get number of rows in the table
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        # If the table is empty, delete it
        if count == 0:
            cursor.execute(f"DROP TABLE {table}")
    # Commit changes to the database
    cnx.commit()


def get_model_company_car_data(scan_name):
    # Get car model and company name from the given table
    cursor.execute(f"SELECT model, company FROM {scan_name}")
    return cursor.fetchall()


def get_car_data(scan_name):
    # Get car data (price, year, mileage, and transmission) from the given table
    cursor.execute(f"SELECT price, year, mileage, transmission FROM {scan_name}")
    return cursor.fetchall()


def insert_car_data(car_model, car_company):
    # Insert car data (model and company) into the car_name_id table
    add_query = ("INSERT IGNORE INTO car_name_id "
                 "(model, company) "
                 "VALUES (%s, %s)")
    values = (car_model, car_company)
    cursor.execute(add_query, values)
    cnx.commit()


def clean_duplicate_processed_data():
    try:
        # Delete duplicate rows from the proccesed_data table
        cursor.execute("""DELETE t1 FROM proccesed_data t1 INNER JOIN proccesed_data t2 WHERE t1.id > 
        t2.id AND t1.car_id = t2.car_id AND t1.mileage = t2.mileage AND t1.price = t2.price AND t1.year = t2.year AND 
        t1.transmission = t2.transmission""")
    except Exception as e:
        logging.error(f'( analyse_data ): Error  deleting duplicate data: {e}')
    # Commit changes to the database
    cnx.commit()
    # Drop the id column from the proccesed_data table
    cursor.execute("ALTER TABLE proccesed_data DROP COLUMN id")
    # Commit changes to the database
    cnx.commit()
    # Add a new id column to the proccesed_data table
    cursor.execute("ALTER TABLE proccesed_data ADD COLUMN id INTEGER PRIMARY KEY AUTO_INCREMENT FIRST")
    # Commit changes to the database
    cnx.commit()


def clean_duplicate_car_id_data():
    # Delete rows with duplicate car_id values and keep only the first occurrence
    cursor.execute("""DELETE t1 FROM car_name_id t1 INNER JOIN car_name_id t2 WHERE t1.car_id > 
    t2.car_id AND t1.model = t2.model AND t1.company = t2.company""")
    cnx.commit()

    # Remove the old car_id column
    cursor.execute("ALTER TABLE car_name_id DROP COLUMN car_id")
    cnx.commit()

    # Add a new car_id column with AUTO_INCREMENT and make it the primary key
    cursor.execute("ALTER TABLE car_name_id ADD COLUMN car_id INTEGER PRIMARY KEY AUTO_INCREMENT FIRST")
    cnx.commit()


def match_car_id():
    logging.info("( analyse_data ): get scanned table names")
    # Get the list of scanned tables
    get_scans()

    logging.info("( analyse_data ): start inserting data in 'car_name_id' table")
    # Iterate over each scanned table and insert its car model and company into the 'car_name_id' table
    for scanned_table in tables:
        for car_model, car_company in get_model_company_car_data(scanned_table):
            insert_car_data(car_model, car_company)

    logging.info("( analyse_data ): clear and specify car_name_id")
    # Clean up the 'car_name_id' table by removing duplicates and setting the primary key
    clean_duplicate_car_id_data()


def match_data():
    logging.info('( analyse_data ): start match_car_id_scan_table and clean duplicate data')
    # Iterate over each scanned table and match its car data with the car ids in the 'car_name_id' table
    for scanned_table in tables:
        match_car_id_scan_table(scanned_table)


def match_car_id_scan_table(scan_name):
    try:
        # Match the car data in the scanned table with the car ids in the 'car_name_id' table
        sql = """
            INSERT INTO proccesed_data 
                (car_id, price, year, mileage, transmission)
            SELECT 
                car_name_id.car_id, 
                {0}.price,
                {0}.year,
                {0}.mileage,
                CASE
                    WHEN {0}.transmission = 'دنده ای' THEN 0 
                    WHEN {0}.transmission = 'اتوماتیک' THEN 1
                    ELSE NULL 
                END AS transmission
            FROM 
                {0} LEFT JOIN car_name_id ON {0}.model = car_name_id.model AND {0}.company = car_name_id.company
            ORDER BY 
                car_name_id.car_id
        """.format(scan_name)
        cursor.execute(sql)
        cnx.commit()

    except Exception as e:
        logging.error(f'( analyse_data ): Error match_car_id_scan_table: {e}')

    # Clean up the processed data table by removing duplicates and setting the primary key
    clean_duplicate_processed_data()


def make_decision_trees():
    # Get the maximum row from the processed_data table
    cursor.execute("SELECT MAX(id) FROM proccesed_data")
    max_row = cursor.fetchone()[0]

    # Start creating decision trees
    logging.info('( analyse_data ): start creating decision trees')
    for car_id in range(1, max_row):
        # Get data for the current car id from processed_data table
        cursor.execute(
            f"SELECT car_id,year,transmission,mileage,price FROM proccesed_data WHERE car_id={car_id}")
        results = cursor.fetchall()

        # For each result, create a decision tree and save it to the corresponding directory
        for result in results:
            model = DecisionTreeClassifier()
            x_train = []
            y_train = []

            # If mileage is not zero, add all columns to x_train and price to y_train
            if result[3] != 0:
                x_train.append(list(result[:-1]))
                y_train.append(result[-1])
                model.fit(x_train, y_train)

                try:
                    # Save the decision tree to the corresponding directory based on mileage
                    joblib.dump(model, f'trees/1_mile/{car_id}.joblib')
                except Exception as e:
                    logging.error(f'( analyse_data ): Error for dump tree data: {e}')

            # If mileage is zero, add all columns except mileage to x_train and price to y_train
            else:
                x_train.append(list(result[:-2]))
                y_train.append(result[-1])
                model.fit(x_train, y_train)

                try:
                    # Save the decision tree to the corresponding directory based on mileage
                    joblib.dump(model, f'trees/0_mile/{car_id}.joblib')
                except Exception as e:
                    logging.error('( analyse_data ): Error save decision_tree:' + e)


def main():
    logging.info('( analyse_data ): start analyse data')
    connect_to_database()
    match_car_id()
    match_data()
    make_decision_trees()
    delete_empty_tables()
    logging.info('( analyse_data ): analyse finished successfully')


if __name__ == '__main__':
    main()
