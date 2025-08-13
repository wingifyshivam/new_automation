import os
import pandas as pd
from sqlalchemy import create_engine, text
from itertools import chain
import urllib.parse

def remove_card_details(patient_id, modified_by_function):
    # Database connection details
    db_username = os.getenv('DB_USERNAME', 'shivam.a')
    db_password = os.getenv('DB_PASSWORD', 'Shivam_1994')
    db_host = os.getenv('DB_HOST', '172.20.129.12')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'bupa_production_v6')

    # Connection string for MySQL
    connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    #print(f"Connecting to database: {db_name}")

    # Create a database connection
    try:
        engine = create_engine(connection_string)
        connection = engine.connect()
        #print("Database connection successful.")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        connection = None


    if connection:
        #patient_id = 2893034
        #modified_by_function = 'LUMEON-50506'
        query = f"select * from payment where patient_id = '{patient_id}' and card_pan IS NOT NULL"
        data = pd.read_sql(query, engine)

        # Initialize the rollback script string
        implementation_script = []
        rollback_script = []

        # Iterate over each row in the dataframe to construct the SQL UPDATE statements
        try:
            for _, row in data.iterrows():
                implementation_query = f"UPDATE {db_name}.payment SET card_scheme = NULL, card_pan = NULL, card_expires = NULL, last_modified_by = '-1000', last_modified = now(), modified_by_function = '{modified_by_function}' WHERE payment_id = '{row['payment_id']}';"
                implementation_script.append(implementation_query)
                rollback_query = f"UPDATE {db_name}.payment SET card_scheme = '{row['card_scheme']}', card_pan = '{row['card_pan']}', card_expires = '{row['card_expires']}', last_modified_by = '{row['last_modified_by']}', last_modified = '{row['last_modified']}', modified_by_function = '{row['modified_by_function']}' WHERE payment_id = '{row['payment_id']}';"
                rollback_script.append(rollback_query)
            implementation_script.append('COMMIT;')
            rollback_script.append('COMMIT;')
        
        except Exception as e:
            print(f"Error generating update/rollback statements")

        finally:
            connection.close()    

        # Optionally, write the rollback script to a file
        implementation_file_path = 'C:/Users/ShivamAggarwal/OneDrive - Health Catalyst/Desktop/Scripts/BUPA/{}/implementation_script.sql'.format(modified_by_function)
        os.makedirs(os.path.dirname(implementation_file_path), exist_ok=True)
        with open(implementation_file_path, 'w') as sql_file:
            for statement in implementation_script:
                sql_file.write(statement + '\n')
        rollback_file_path = 'C:/Users/ShivamAggarwal/OneDrive - Health Catalyst/Desktop/Scripts/BUPA/{}/rollback_script.sql'.format(modified_by_function)
        os.makedirs(os.path.dirname(rollback_file_path), exist_ok=True)
        with open(rollback_file_path, 'w') as sql_file:
            for statement in rollback_script:
                sql_file.write(statement + '\n')
        
        return f"Scripts generated successfully at {implementation_file_path} and {rollback_file_path}"

    else:
        print("Unable to establish database connection.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python removal_card.py <patient_id> <modifier_name>")
        sys.exit(1)
    
    patient_id = sys.argv[1]
    modifier_name = sys.argv[2]

    result = remove_card_details(patient_id, modifier_name)
    print(result)  # <---- MAKE SURE THIS LINE EXISTS