# import necessary libraries
import logging  # logging module for logging events
import joblib  # module for loading and saving models
import mysql.connector  # module for connecting to a MySQL database
from colorama import init, Fore, Style, Back  # module for colored terminal output
from prettytable import PrettyTable  # module for displaying tabular data in a visually appealing ASCII table
from humanize import intword  # module for displaying numbers in a more human-readable format

# import modules created by the developer
import analyse_data
import fetch_data
import db_initialize

# configure logging
logging.basicConfig(filename='pcp.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')


# define a function to connect to the MySQL database
def connect_to_database():
    global cursor, cnx  # global variables to be used throughout the program
    try:
        # create a connection to the database and get a cursor object
        cnx = mysql.connector.connect(user='whsnow', password='', host='127.0.0.1', database='pcp')
        cursor = cnx.cursor()
        logging.info('( main ): connected to database and made cursor')  # log the success of the connection
    except Exception as e:
        logging.error(f'( main ): Error connecting to database: {e}')  # log any errors that occur


# initialize colorama
init()


# define a function to display the main menu of options
def show_menu():
    menu = """ 
1. Custom Car
2. Select Car
3. Update Data
0. Initialize program
Type 'exit' to close
"""
    print(Fore.CYAN + menu + Back.BLACK + Style.RESET_ALL)


# define a function to display the list of available car names and ids
def show_car_name():
    cursor.execute('SELECT * FROM car_name_id')
    colmuns = [desc[0] for desc in cursor.description]  # get the column names
    rows = cursor.fetchall()  # fetch all the rows
    table = PrettyTable(colmuns)  # create a table object with the column names
    for row in rows:
        table.add_row(row)  # add each row to the table
    print(table)  # display the table


# define a function to get the name of a car given its id
def get_car_name(car_id):
    cursor.execute(f'SELECT model, company FROM car_name_id WHERE car_id={car_id}')  # execute an SQL query
    rows = cursor.fetchone()  # fetch one row
    return rows  # return the model and company names


# define a function to get the predicted price of a car
def get_data(car_id):
    """
    Takes a car id as input and prompts the user to enter the mileage, year, and transmission of the car to predict its price.
    Uses the car_id to fetch the model and company of the car from the database.
    Uses the mileage to determine whether to use the trained model for zero mileage or non-zero mileage cars.
    If zero mileage, checks if a trained model is available for zero mileage for the car, otherwise uses the trained model for non-zero mileage with 0 mileage input.
    If non-zero mileage, uses the trained model for non-zero mileage with the entered mileage.
    Predicts the price using the loaded model and prints it to the console.
    """
    mileage = input(Fore.GREEN + "[+] Mileage: " + Style.RESET_ALL)
    year = input(Fore.GREEN + "[+] Year: " + Style.RESET_ALL)
    transmission = int(input(Fore.GREEN + "[+] Transmission( 1. Manual, 2. Automatic ): " + Style.RESET_ALL)) - 1
    print(Fore.MAGENTA + "[-] Predicting the car price..." + Style.RESET_ALL)
    model, company = get_car_name(car_id)  # get the model and company names
    if int(mileage) == 0:
        try:
            loaded_model = joblib.load(f'trees/0_mile/{car_id}.joblib')  # load a model specific to 0 mileage
            price = loaded_model.predict([[car_id, year, transmission]])  # predict the price with the loaded model
        except:
            print(
                Fore.RED + f'[!] We still have no data for "0 milage" {model} {company} and using stock car data:\n' + Style.RESET_ALL)
            loaded_model = joblib.load(f'trees/1_mile/{car_id}.joblib')
            price = loaded_model.predict([[car_id, year, transmission, 0]])
    else:
        loaded_model = joblib.load(f'trees/1_mile/{car_id}.joblib')
        price = loaded_model.predict([[car_id, year, transmission, mileage]])
    price = intword(price)
    print(
        Fore.YELLOW + f"\n[*] Predicted price for '{company} {model}' is: {price} $"
        + Style.RESET_ALL
    )


# The main function of the program
def main():
    # Connect to the database
    connect_to_database()

    # Display a welcome message to the user
    print('   ===(Welcome to Car Price Prediction System)===')

    # Loop continuously until the user chooses to exit
    while True:
        # Show the main menu to the user
        show_menu()

        # Get the user's input for which option to choose
        usr_inp = input(Fore.GREEN + "[+] Enter your option: " + Style.RESET_ALL)

        # If the user chooses option 1, enter Custom Car mode
        if usr_inp == '1':
            print(Fore.YELLOW + '[*] Custom Car mode' + Style.RESET_ALL)

            # Get the user's input for the car's company and model
            company = input(Fore.GREEN + "[+] Company: " + Style.RESET_ALL)
            model = input(Fore.GREEN + "[+] Model: " + Style.RESET_ALL)

            # Use the database to find the car's ID
            cursor.execute(
                f"SELECT car_id FROM pcp.car_name_id WHERE model='{model}' AND company='{company}'")
            car_id = cursor.fetchone()[0]

            # Get the car's data and predict its price
            get_data(car_id)

        # If the user chooses option 2, enter Select Car mode
        elif usr_inp == '2':
            print(Fore.YELLOW + '[*] Select Car mode' + Style.RESET_ALL)

            # Show a list of available cars to the user
            show_car_name()

            # Get the user's input for which car to choose
            car_id = input(Fore.GREEN + "[+] Please enter your car id: " + Style.RESET_ALL)

            # Get the selected car's data and predict its price
            get_data(car_id)

        # If the user chooses option 3, enter Update Data mode
        elif usr_inp == '3':
            print(Fore.YELLOW + '[*] Update Data mode' + Style.RESET_ALL)

            # Fetch the latest data from the website and update the database
            print(Fore.MAGENTA + '[-] Start fetch_data' + Style.RESET_ALL)
            fetch_data.main()

            # Analyze the data and create prediction models for each car
            print(Fore.MAGENTA + '[-] Start analyse_data' + Style.RESET_ALL)
            analyse_data.main()

            # Notify the user that the data has been updated
            print(Fore.YELLOW + '[*] fetch and analyse data finished' + Style.RESET_ALL)

        # If the user chooses option 0, initialize the program
        elif usr_inp == '0':
            print(Fore.YELLOW + '[*] Initialize Program mode' + Style.RESET_ALL)

            # Create the database tables and import initial data
            db_initialize.main()

        # If the user chooses to exit, break out of the loop and end the program
        elif usr_inp == 'exit':
            print(Fore.LIGHTRED_EX + '[3>] GoodBye :)')
            break

        # If the user chooses an invalid option, notify them and show the menu again
        else:
            print(Fore.RED + '[-] Enter correct option')

        # Add a separator between the end of one action and the start of another
        print('\n==========================')


# Check if the current file is being run as the main program
if __name__ == '__main__':
    # Call the main function to start the program
    main()
