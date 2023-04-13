# Car Price Prediction System

This is a Python application for predicting the price of a car based on its mileage, year, and transmission using
machine learning algorithms. The application uses a MySQL database to store and retrieve car data, and it also fetches
and analyzes new car data from external sources.

## Features

* Custom Car mode: allows users to input the details of a specific car and get a predicted price
* Select Car mode: displays a list of all available cars in the database and allows the user to select one to get a
  predicted price
* Update Data mode: fetches new car data from external sources, analyzes it, and updates the MySQL database with the new
  data
* Initialize Program mode: initializes the MySQL database with the necessary tables and data

## Installation

1. Clone the repository:

```
git clone https://github.com/Warm-Hearted-Snowman/Predict_Car_Price_with_MachineLearning
```

2. Install the required dependencies:

```
pip install -r requirements.txt
```

3. Create a MySQL database and configure the connection in the main.py file.

4. Run the program:

```
python main.py
```

## Usage

Upon running the program, the user will be presented with a menu of options:

1. Custom Car: allows the user to input the details of a specific car and get a predicted price
2. Select Car: displays a list of all available cars in the database and allows the user to select one to get a
   predicted price
3. Update Data: fetches new car data from external sources, analyzes it, and updates the MySQL database with the new
   data
4. Initialize Program: initializes the MySQL database with the necessary tables and data

The user can select an option by entering the corresponding number. If the user selects Custom Car mode, they will be
prompted to input the details of the car. If the user selects Select Car mode, they will be presented with a table of
all available cars in the database and prompted to enter the ID of the car they wish to predict the price for.

If the user selects Update Data mode, the program will fetch new car data from external sources, analyze it, and update
the MySQL database with the new data. This may take several minutes to complete.

If the user selects Initialize Program mode, the program will initialize the MySQL database with the necessary tables
and data.

## Screen shots


<p align="center">
  <img src=https://i.imgur.com/b7JXSMT.png>
  <img src=https://i.imgur.com/Cr1GOFk.png>
  <img src=https://i.imgur.com/Yvj9Fd2.png>
  <img src=https://i.imgur.com/0nbzSuC.png>
  <img src=https://i.imgur.com/9ccbypl.png>
</p>


## License

This project is licensed under the MIT License - see the LICENSE file for details.




