import gspread
from google.oauth2.service_account import Credentials
# from pprint import pprint <- NOT USED IN FINAL DEPLOYMENT

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("love_sandwiches")

# Code to check API works
# sales = SHEET.worksheet("sales")

# data = sales.get_all_values()

# print(data)


def get_sales_data():
    """
    Get sales figures input from the user
    """
    while True:
        print("Please enter sales data from the last market.")
        print("Data should be six numbers, serparated by commas.")
        print("Example: 10,20,30,40,50,60\n")

        # newline char necessary on input for deployment mock terminal
        data_str = input("Enter your data here:\n")
        # print(f"The data provided is {data_str}")

        # Returns the values provided as a list with the split method
        sales_data = data_str.split(",")
        # print(sales_data)
        """
        If this if statement is returned 'True' from the try statement
        completing successfully, then it will break out of the while
        loop to get sales data.
        """
        if validate_data(sales_data):
            print("Data is valid!")
            break

    return sales_data


def validate_data(values):
    """
    Inside the try, converts all string values into integers.
    Raises ValueError if strings cannot be donverted into int,
    or if there aren't exactly 6 values.
    """
    # print(values)
    try:
        [int(value) for value in values]
        if len(values) != 6:
            raise ValueError(
                f"Exactly 6 values required, you provided {len(values)}"
            )
    except ValueError as e:
        # '{e}' refers to the custom ValueError message above
        print(f"Invalid data: {e}, please try again.\n")
        # This function returns 'False' when failing to validate so that
        # the while loop of the does not break out and continues running
        return False

    # This returns 'True' to the if statement of the get_sales_data
    # function's while loop, so that it may end on successful completion
    return True


# The following two functions are commented out. They have been
# refactored from two functions into one, by passing arguments to
# specify which data and worksheets are to be used and updated,
# respectively

# def update_sales_worksheet(data):
#     """
#     Update sales worksheet, add new row with the list data provided.
#     """
#     print("Updating sales worksheet...\n")
#     sales_worksheet = SHEET.worksheet("sales")
#     sales_worksheet.append_row(data)
#     print("Sales worksheet updated successfully.\n")


# def update_surplus_worksheet(surplus_list):
#     """
#     Update surplus worksheet. Adds a new row to the surplus worksheet,
#     using the newest surplus data which is assigned in the main
#     function.
#     """
#     print("Updating surplus worksheet...\n")
#     surplus_worksheet = SHEET.worksheet("surplus")
#     surplus_worksheet.append_row(surplus_list)
#     print("Surplus worksheet updated successfully.\n")


def update_worksheet(data, worksheet):
    """
    This function used the data provided to the data arg to update the
    worksheet specified by the worksheet arg. This is a refactoring of
    two separate functions that updated the sales and surplus worksheets
    individually. The worksheet arg is to be provided as a string.
    """
    print(f"Updating {worksheet} worksheet...\n")
    worksheet_to_update = SHEET.worksheet(worksheet)
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully.\n")


def calculate_surplus_data(sales_row):
    """
    Compare sales with stock and calculate the surplus for each item
    type.

    The surplus is defined as the sales figure subtracted from the
    stock:
    - +ve surplus indicates waste
    - -ve surplus indicates extra stock made after selling out
    """
    print("Calculating surplus data...\n")
    # Define stock variable to calculate surplus, using worksheet
    # method of the SHEET constant, which selects the 'stock' worksheet.
    # Furthermore, the gspread method to get all values of the cells is
    # used in defining the var
    stock = SHEET.worksheet("stock").get_all_values()
    # pretty-print (built-in) installed at top. Formats the list of
    # lists to a more readable, table-like structure
    # pprint(stock)
    # Create a var for the last row of the stock sheet
    # (this is actually a list slice and I didn't realize!)
    # stock_row expression wrapped in int() so that calculations may be
    # performed to work out the surplus <- DIDN'T WORK!
    # New list comprehension created, specifying int data type
    stock_row = stock[-1]
    stock_row_ints = [int(x) for x in stock_row]
    print(stock_row_ints)
    # print(stock_row)
    print(f"stock row: {stock_row}")
    print(f"sales row: {sales_row}")

    """
    zip() method used to iterate through two lists at the same time!
    Declare the singular placeholder vars, separated by commas 'in'
    zip(list1, list2):

    Creates a var 'surplus' to store the result of the stock minus sales
    Empty list declared above the for loop so that the results of the
    zipped iterations can be appended to it.

    int() method wraps the stock var in the for loop. This makes the
    integer list comprehension strategy obsolete as it converts each
    string of the stock_row list to an int as it is iterated.
    """
    surplus_data = []
    for stock, sales in zip(stock_row, sales_row):
        surplus = int(stock) - sales
        surplus_data.append(surplus)

    return surplus_data


def get_last_5_entries_sales():
    """
    Collect columns of data from the sales worksheet, collecting the
    last 5 entries for each sandwich and returns the data as a list of
    lists.

    col_values() method from gspread allows us to access the data in
    columns, as opposed to rows.

    Empty list and for loop created to store the values from each list.
    Note that the index of the spreadsheet columns starts from 1, not 0.
    The ind var is created in the for loop and runs 6 times,
    representing the 6 columns or types of sandwiches.
    """
    sales = SHEET.worksheet("sales")
    # column = sales.col_values(3)
    # pprint(column)
    columns = []
    for ind in range(1, 7):
        # create a var to access the column for each index of the loop
        column = sales.col_values(ind)
        # append, starting at -5, then onwards (colon: nothing)
        columns.append(column[-5:])
    # pprint(columns)

    return columns


def calculate_stock_data(data):
    """
    Calculate the average stock for each item type, adding 10%
    """
    print("Calculating stock data...\n")
    new_stock_data = []
    # for loop to calculate the average of last 5 sales for each
    # sandwich type
    # For each 'column' in the 'last 5 entries sales'...
    for column in data:
        # create new list comprehension of ints
        int_column = [int(num) for num in column]
        # now we have this list in ints, use built-in sum() function to
        # add the values of the int_column and divide by its length
        avg = sum(int_column) / len(int_column)
        # print(avg)
        # Add 10% to the average
        stock_plus_10_percent = avg * 1.1
        # append these values to the empty list at the top of the
        # function, as a rounded int
        new_stock_data.append(round(stock_plus_10_percent))

    return new_stock_data


def main():
    """
    Run all program functions
    """
    # This var is the result of calling the function specified and will
    # hold its return value
    data = get_sales_data()
    # New var from list comprehension to convert the 'data' list to
    # integers
    sales_data = [int(num) for num in data]
    # print(sales_data)
    # update_sales_worksheet(sales_data) <- OBSOLETE FUNCTION; see below
    update_worksheet(sales_data, "sales")
    # Pass the sales_data to the calculate surplus function
    # Assign the return value of the function to the var that called it
    new_surplus_data = calculate_surplus_data(sales_data)
    print(new_surplus_data)
    # Call the function to update the surplus worksheet, using the new
    # surplus var defined above
    # update_surplus_worksheet(new_surplus_data) <- OBSOLETE FUNCTION
    update_worksheet(new_surplus_data, "surplus")
    # var to hold the list containing the list of lists for the last 5
    # sales of each sandwich type
    sales_columns = get_last_5_entries_sales()
    # Call the calculate stock data function, passing it the last 5
    # sales. This then performs some calculations to return the average
    # week's sales, plus 10 percent. The result of this is stored in
    # this var
    stock_to_prep = calculate_stock_data(sales_columns)
    # print(stock_to_prep)
    update_worksheet(stock_to_prep, "stock")


# This print statement is the first thing the user sees on program start
print("Welcome to Love Sandwiches Data Automation\n")
# Function call to start the program
main()
