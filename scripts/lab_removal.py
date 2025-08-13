import os
import pandas as pd
from sqlalchemy import create_engine
from itertools import chain

def run_lab_removal(file_path, modified_by_function, db_username, db_password, db_name):
    # Database connection details
    #db_username = os.getenv('DB_USERNAME', 'shivam.a')
    #db_password = os.getenv('DB_PASSWORD', 'Shivam_1994')
    db_port = os.getenv('DB_PORT', '3306')
    if db_name == 'BUPA':
        db_host = os.getenv('DB_HOST', '172.20.129.12')
        db_name = os.getenv('DB_NAME', 'bupa_production_v6')
    elif db_name == 'Onebright':
        db_host = os.getenv('DB_HOST', '172.20.136.63')
        db_name = os.getenv('DB_NAME', 'onebright_live')
    elif db_name == 'Nuffield':
        db_host = os.getenv('DB_HOST', '172.20.130.107')
        db_name = os.getenv('DB_NAME', 'nuffield_live')
    elif db_name == 'Newmedica':
        db_host = os.getenv('DB_HOST', '172.20.131.33')
        db_name = os.getenv('DB_NAME', 'newmedica_live')

    connection_string = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
    try:
        engine = create_engine(connection_string)
        connection = engine.connect()
    except Exception as e:
        return f"Error connecting to database: {e}"

    if not connection:
        return "Unable to establish database connection."

    df = pd.read_excel(file_path)

    def split_and_process(column, delimiter='\n'):
        return df[column].dropna().apply(
            lambda x: [int(float(item)) for item in str(x).split(delimiter) if item.strip().replace('.', '', 1).isdigit()]
        ).tolist()

    lab_order_ids = list(chain(*split_and_process('Lab Order ID')))
    lab_set_ids = list(chain(*split_and_process('Lab Set ID')))
    lab_observation_request_ids = list(chain(*split_and_process('Lab Observation Request ID')))
    manual_order_ids = list(chain(*split_and_process('Manual Order id')))

    update_statements = []
    rollback_statements = []

    try:
        if lab_order_ids:
            for x in lab_order_ids:
                update_query = f"UPDATE {db_name}.observation_order SET status = 'C', last_modified_by = '-1000', last_modified = now(), modified_by_function = '{modified_by_function}' WHERE observation_order_id = '{int(x)}';"
                update_statements.append(update_query)
                current_columns = f"select * from observation_order where observation_order_id = '{int(x)}'"
                data1 = pd.read_sql(current_columns, engine)
                for _, row1 in data1.iterrows():
                    rollback_query = f"UPDATE {db_name}.observation_order SET status = '{row1['status']}', last_modified_by = '{row1['last_modified_by']}', last_modified = '{row1['last_modified']}', modified_by_function = '{row1['modified_by_function']}' WHERE observation_order_id = '{int(x)}';"
                    rollback_statements.append(rollback_query)
        
        if lab_set_ids:
            for x in lab_set_ids:
                update_query = f"UPDATE {db_name}.observation_set SET status = 'C', last_modified_by = '-1000', last_modified = now(), modified_by_function = '{modified_by_function}' WHERE observation_set_id = '{int(x)}';"
                update_statements.append(update_query)
                current_columns = f"select * from observation_set where observation_set_id = '{int(x)}'"
                data1 = pd.read_sql(current_columns, engine)
                for _, row1 in data1.iterrows():
                    rollback_query = f"UPDATE {db_name}.observation_set SET status = '{row1['status']}', last_modified_by = '{row1['last_modified_by']}', last_modified = '{row1['last_modified']}', modified_by_function = '{row1['modified_by_function']}' WHERE observation_set_id = '{int(x)}';"
                    rollback_statements.append(rollback_query)
        
        if lab_observation_request_ids:
            for x in lab_observation_request_ids:
                update_query = f"UPDATE {db_name}.observation_request SET status = 'C', last_modified_by = '-1000', last_modified = now(), modified_by_function = '{modified_by_function}' WHERE observation_request_id = '{int(x)}';"
                update_statements.append(update_query)
                current_columns = f"select * from observation_request where observation_request_id = '{int(x)}'"
                data1 = pd.read_sql(current_columns, engine)
                for _, row1 in data1.iterrows():
                    rollback_query = f"UPDATE {db_name}.observation_request SET status = '{row1['status']}', last_modified_by = '{row1['last_modified_by']}', last_modified = '{row1['last_modified']}', modified_by_function = '{row1['modified_by_function']}' WHERE observation_request_id = '{int(x)}';"
                    rollback_statements.append(rollback_query)
        
        if manual_order_ids:
            for x in manual_order_ids:
                update_query = f"UPDATE {db_name}.emr2_note_entry SET deleted_by_id = '-1000', deleted = now(), last_modified_by = '-1000', last_modified = now(), modified_by_function = '{modified_by_function}' WHERE emr2_note_entry_id = '{int(x)}';"
                update_statements.append(update_query)
                current_columns = f"select * from emr2_note_entry where emr2_note_entry_id = '{int(x)}'"
                data1 = pd.read_sql(current_columns, engine)
                for _, row1 in data1.iterrows():
                    rollback_query = f"UPDATE {db_name}.emr2_note_entry SET deleted_by_id = NULL, deleted = NULL, last_modified_by = '{row1['last_modified_by']}', last_modified = '{row1['last_modified']}', modified_by_function = '{row1['modified_by_function']}' WHERE emr2_note_entry_id = '{int(x)}';"
                    rollback_statements.append(rollback_query)
                
        update_statements.append('COMMIT;')
        rollback_statements.append('COMMIT;')

    except Exception as e:
        connection.close()
        return f"Error generating update/rollback statements: {e}"

    finally:
        connection.close()

    # Write update/rollback statements to files (same paths as before)
    implementation_file_path = f'C:/Users/ShivamAggarwal/OneDrive - Health Catalyst/Desktop/Scripts/BUPA/{modified_by_function}/implementation_script.sql'
    os.makedirs(os.path.dirname(implementation_file_path), exist_ok=True)
    with open(implementation_file_path, 'w') as sql_file:
        for statement in update_statements:
            sql_file.write(statement + '\n')

    rollback_file_path = f'C:/Users/ShivamAggarwal/OneDrive - Health Catalyst/Desktop/Scripts/BUPA/{modified_by_function}/rollback_script.sql'
    os.makedirs(os.path.dirname(rollback_file_path), exist_ok=True)
    with open(rollback_file_path, 'w') as sql_file:
        for statement in rollback_statements:
            sql_file.write(statement + '\n')

    return f"Scripts generated successfully at {implementation_file_path} and {rollback_file_path}"