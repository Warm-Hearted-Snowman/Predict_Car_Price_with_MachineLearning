import mysql.connector  # Importing the module to connect to a MySQL database
import logging  # Importing the logging module to write log messages to a file
from colorama import init, Fore, Style, Back  # Importing the colorama module to colorize console output
from pathlib import Path  # Importing the pathlib module to handle file paths
from os import makedirs, path  # Importing the os module to create directories


def make_dir(dir_name: str):
    # This function creates a directory if it doesn't exist
    project_path = Path().parent.resolve()
    directory_name = dir_name
    directory_path = path.join(project_path, directory_name)
    try:
        makedirs(directory_path, exist_ok=True)
        logging.info(
            f"( initialize ): Directory {directory_path} created successfully")  # Logging that the directory was created
    except Exception as e:
        logging.error(f"( initialize ): Error creating directory {directory_path}: {str(e)}")
        print(
            Fore.RED + f'[!] Error : Already {dir_name} created')  # Printing an error message if the directory already exists


def main():
    init()  # Initializing the colorama module
    try:
        cnx = mysql.connector.connect(user='whsnow', password='', host='127.0.0.1')  # Connecting to the MySQL database
        cursor = cnx.cursor()  # Creating a cursor object to execute SQL queries
        logging.info(
            '( initialize ): connected to database for create database and made cursor')  # Logging that the connection was successful
    except Exception as e:
        logging.error(
            f'( initialize ): Error connecting to database: {e}')  # Logging an error message if the connection failed

    try:
        cursor.execute("CREATE DATABASE pcp")  # Creating a new database
    except Exception as e:
        logging.error(
            f'( initialize ): Error creating database: {e}')  # Logging an error message if the database creation failed
        print(
            Fore.RED + '[!] Error : Already database created')  # Printing an error message if the database already exists

    try:
        cnx.commit()  # Committing the changes to the database
    except Exception as e:
        logging.error(f'( initialize ): Error commit database: {e}')  # Logging an error message if the commit failed

    cursor.close()  # Closing the cursor object
    cnx.close()  # Closing the database connection

    try:
        cnx = mysql.connector.connect(user='whsnow', password='', host='127.0.0.1',
                                      database='pcp')  # Connecting to the pcp database
        cursor = cnx.cursor()  # Creating a new cursor object
        logging.info(
            '( initialize ): connected to database for creating tables and made cursor')  # Logging that the connection was successful
    except Exception as e:
        logging.error(
            f'( initialize ): Error connecting to database: {e}')  # Logging an error message if the connection failed

    try:
        cursor.execute(
            "CREATE TABLE car_name_id ( car_id INTEGER primary key AUTO_INCREMENT, model TEXT, company TEXT)")  # Creating a new table
    except Exception as e:
        logging.error(
            f'( initialize ): Error creating tables: {e}')  # Logging an error message if the table creation failed
        print(Fore.RED + '[!] Error : Already tables created')  # Printing an error message if the table already exists

    try:
        cursor.execute(
            'CREATE TABLE proccesed_data (id INTEGER primary key AUTO_INCREMENT, car_id INTEGER, price BIGINT, year INTEGER, mileage bigint, transmission int(1))')
    except Exception as e:
        logging.error(f'( initialize ): Error creating tables: {e}')
        print(Fore.RED + '[!] Error : Already tables created')
    try:
        cnx.commit()
    except Exception as e:
        logging.error(f'( initialize ): Error commit database: {e}')
    cursor.close()
    cnx.close()

    make_dir('trees/1_mile')
    make_dir('trees/0_mile')

    print(Fore.MAGENTA + '[-] Program initialize finished' + Style.RESET_ALL)


if __name__ == '__main__':
    main()
