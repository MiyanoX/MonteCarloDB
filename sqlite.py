import sqlite3
import pandas as pd
import numpy as np
from sqlite3 import Error

path = "./simulation_results.db"
strength_table_name = "strength"
para_table_name = "para"

def create_connection():
    """ create a database connection to the SQLite database
        specified by db_file
    """
    conn = None
    try:
        conn = sqlite3.connect(path)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        

def init_para_table():
    # Project ID, Tape Length, Tape Width, Tape Thickness, Tape Angle, Specimen Length, Specimen Width, Specimen Thickness, vf, Layer Parameter, Tensile Strength

    sql_create_table = f""" CREATE TABLE IF NOT EXISTS {para_table_name} (
                                        id integer PRIMARY KEY,
                                        parameters text NOT NULL
                                    ); """

    # create a database connection
    conn = create_connection()

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_table)
        
    else:
        print("Error! cannot create the database connection.")
        
        
def init_strength_table():
    # Project ID, Tape Length, Tape Width, Tape Thickness, Tape Angle, Specimen Length, Specimen Width, Specimen Thickness, vf, Layer Parameter, Tensile Strength

    sql_create_table = f""" CREATE TABLE IF NOT EXISTS {strength_table_name} (
                                        id integer PRIMARY KEY,
                                        para_id integer,
                                        tensile_strength FLOAT
                                    ); """

    # create a database connection
    conn = create_connection()

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_table)
        
    else:
        print("Error! cannot create the database connection.")
        
        
def insert(conn, data, insert_sql):
    """
    Create a new task
    :param conn:
    :param task:
    :return:
    """

    """
    tape_shape text NOT NULL,
    tape_length FLOAT,
    tape_width FLOAT,
    tape_thickness FLOAT,
    tape_angle integer,
    specimen_length FLOAT,
    specimen_width FLOAT,
    specimen_thickness FLOAT,
    vf FLOAT,
    layer_parameter FLOAT,
    tensile_strength FLOAT
    """    
    cur = conn.cursor()
    cur.execute(insert_sql, data)
    conn.commit()
    return cur.lastrowid


def add_para_data(para):
    # create a database connection
    conn = create_connection()
    with conn:
        
        insert_sql = f''' INSERT INTO {para_table_name}(parameters)
              VALUES(?) '''
        data_id = insert(conn, para, insert_sql)

    return data_id



def add_strength_data(strength):
    # create a database connection
    conn = create_connection()
    with conn:
        
        insert_sql = f''' INSERT INTO {strength_table_name}(para_id, tensile_strength)
              VALUES(?, ?) '''
        data_id = insert(conn, strength, insert_sql)

    return data_id


def find_para_return_id(parameters):
    """
    Find a certain data in the SQLite database and return its id.
    """
    try:
        # Connect to the SQLite database
        conn = create_connection()
        c = conn.cursor()

        # SQL query to find the data
        query = f"SELECT id FROM {para_table_name} WHERE parameters = ?"
        c.execute(query, (parameters, ))

        # Fetch the result
        result = c.fetchone()
        if not result:
            return add_para_data(parameters)
        else:
            return result[0]

    except Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
            
            
def add_simulaiton_data(data):
    parameters = ', '.join(map(str, data[:-1]))
    
    para_id = find_para_return_id(parameters)
    strength_data = (para_id, data[-1])
    data_id = add_strength_data(strength_data)
        
    return data_id


def generate_random_float_normal_dist(min_value, max_value, mean=None, std_dev=None):
    """
    Generate a random float number within the specified range from a normal distribution.
    """
    if mean is None:
        mean = (min_value + max_value) / 2
    if std_dev is None:
        std_dev = (max_value - min_value) / 6  # Roughly 99.7% data within min_value and max_value

    while True:
        number = np.random.normal(mean, std_dev)
        if min_value <= number <= max_value:
            return number
        
def read_para_id_by_para(para_data):
    parameters = ', '.join(map(str, para_data))
    
    # Connect to the SQLite database
    conn = create_connection()
    
    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to select row based on ID
    query = f"SELECT * FROM {para_table_name} WHERE parameters = ?"

    # Execute the query
    cursor.execute(query, (parameters, ))

    # Fetch the data
    row = cursor.fetchone()

    # Check if the row exists and print it
    if row:
        print("Found row:", row)
    else:
        print("No row found with Parameters:", parameters)
        return None

    # Close the connection
    conn.close()
    
    return row[0]


def read_strength_by_para_id(para_id):    
    # Connect to the SQLite database
    conn = create_connection()
    
    # Create a cursor object
    cursor = conn.cursor()

    # SQL query to select row based on ID
    query = f"SELECT * FROM {strength_table_name} WHERE para_id = ?"

    # Execute the query
    cursor.execute(query, (para_id, ))

    # Fetch the data
    rows = cursor.fetchall()

    # Close the connection
    conn.close()
    
    return [row[-1] for row in rows]


def read_strengths_by_para(para_data):
    para_id = read_para_id_by_para(para_data)
    return read_strength_by_para_id(para_id)


def read_all_data():
    # Connect to the SQLite database
    conn = create_connection()

    # SQL query
    query_strength = f"SELECT * FROM {strength_table_name}"
    query_parameter = f"SELECT * FROM {para_table_name}"

    # Read the data into a DataFrame
    df_strength = pd.read_sql_query(query_strength, conn)
    df_parameter = pd.read_sql_query(query_parameter, conn)

    # Close the connection
    conn.close()

    # Now you can work with the DataFrame df
    print(df_strength.head(10))
    print(df_parameter.head(10))
    