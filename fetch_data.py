# importing required modules
import logging  # for logging errors and events
from bs4 import BeautifulSoup  # for parsing HTML
from datetime import datetime  # for generating timestamp
import requests  # for making HTTP requests
import json  # for working with JSON data
import mysql.connector  # for connecting to MySQL database


# defining a function that deletes commas from a string and converts it to an integer
def comma_deleter(str: str):
    try:
        str = str.replace(",", "")
    except:
        pass
    return int(str)


# defining the main function
def main():
    # establish the database connection
    try:
        logging.info('( fetch_data ): start fetching data')
        try:
            # connect to the database
            cnx = mysql.connector.connect(user='whsnow', password='', host='127.0.0.1', database='pcp')
            cursor = cnx.cursor()
            logging.info('( fetch_data ): connected to database and made cursor')
        except Exception as e:
            # log error if connection fails
            logging.error(f'( fetch_data ): Error connecting to database: {e}')

        # check if table already exists
        # generate the table name using current date and time
        table_name = f"scan_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        exists_query = f"SELECT 1 FROM {table_name} LIMIT 1"
        try:
            cursor.execute(exists_query)
            logging.info(f"Table {table_name} already exists. Aborting...")
            return
        except:
            pass

        # create the table
        # defining the structure of the table
        create_query = (
            f"CREATE TABLE {table_name} "
            "(id INTEGER PRIMARY KEY AUTO_INCREMENT,company TEXT, model TEXT, year TEXT, mileage BIGINT,transmission TEXT, price BIGINT, location TEXT)"
        )
        try:
            # executing the query to create a new table in the database
            cursor.execute(create_query)
            logging.info(f"Table {table_name} created successfully")
        except Exception as e:
            logging.error(f"( fetch_data ): Error creating table: {e}")
            return

        add_car_data_query = (
            f"INSERT INTO {table_name} "
            "(company, model, year, mileage, transmission, price, location) "
            "VALUES (%s, %s,%s,%s,%s,%s,%s)"
        )

        errorlog = ""

        logging.info("( fetch_data ): start scanning")
        for i, _ in enumerate(range(1, 21)):
            url = f"https://bama.ir/cad/api/search?priced=1&pageIndex={i}"

            try:
                # send GET request to the website and extract data
                page = requests.get(url)
                soup = BeautifulSoup(page.text, "html.parser")
                data = json.loads(soup.get_text())
                ads = data["data"]["ads"]
            except Exception as e:
                # log error if fetching data fails
                logging.error(f"( fetch_data ): Error fetching data from page {i}: {e}")
                continue

            for ad in ads:
                try:
                    # extract relevant car details from the JSON data
                    company, model = ad["detail"]["title"].split("، ")
                    year = ad["detail"]["year"]
                    transmission = ad["detail"]["transmission"]
                    price = comma_deleter(ad["price"]["price"])
                    location = ad["detail"]["location"].split(" / ")[0]

                    if ad["detail"]["mileage"] == "کارکرد صفر":
                        mileage = 0
                    elif ad["detail"]["mileage"].split(" ")[0] != "کارکرده":
                        mileage = comma_deleter(ad["detail"]["mileage"].split(" ")[0])

                    cursor.execute(
                        add_car_data_query,
                        (company, model, year, mileage, transmission, price, location)
                    )
                    cnx.commit()

                except Exception as e:
                    errorlog += ("( fetch_data ): Error : " + str(e) + '\n')
                    logging.error(f"( fetch_data ): Error adding car data to database: {e}")

            logging.info(f"( fetch_data ): page {i} loaded...")
        logging.info('( fetch_data ): scan finished successfully')

    except Exception as e:
        logging.error(f"( fetch_data ): Error connecting to database: {e}")
        return


if __name__ == "__main__":
    main()