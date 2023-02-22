import os
import re
import json
from google.oauth2 import service_account
from google.cloud import spanner

sql_file = "C://Users//Stefan//Downloads//rcn_lines.csv"

new_dialler_spanner_key = """RCN_KEY"""

def split_row(row, index):
    return row.strip().replace('"','').split(",")[index]

def perform_sql_update(transaction, sql_code):
    row_ct = transaction.execute_update(sql_code)

def get_correct_database_credentials():
    service_account_info = json.loads(new_dialler_spanner_key, strict=False)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    spanner_client = spanner.Client(project='marketingtown', credentials=credentials)
    instance = spanner_client.instance('marketing-town')
    database = instance.database('marketing-town')
    return database

def run_spanner_query(sql_code,):
        pattern = '^insert'
        is_insert = re.match(pattern, sql_code, re.IGNORECASE);
        database = get_correct_database_credentials()
        if is_insert:
            print("Running update statement")
            database.run_in_transaction(perform_sql_update, sql_code);
            return ''
        else:
            with database.snapshot() as snapshot:
                results = snapshot.execute_sql(sql_code)  
            return results

def process_statement(rows):
    code = "INSERT INTO rcn_account_names (Telephone, MembershipNumber, AccountName) VALUES "
    for row in rows:

        sql_row = '("' + split_row(row,0) + '", "' + split_row(row,1) + '", "' + split_row(row,2) + '"),'
        code = code + sql_row
    code = code[:-1]
    print("Running:")
    print(code)
    run_spanner_query(code)
    print("ran.")

def check_rows(rows):
    code = 'select Telephone from rcn_account_names where Telephone in ('
    output_rows = []
    for row in rows:
        code = code + '"' + split_row(row,0) + '",'
    code = code[:-1]
    code = code + ")"
    print("code is: " + code)
    print("checking:")
    output = run_spanner_query(code)    
    check_list = []
    for row in output:
        check_list.append(row)
    print("output: ")
    print(str(check_list))
    for row in rows:
        if [split_row(row,0)] in check_list:
            print("found match!")
            continue
        else:
           output_rows.append(row)
    return output_rows

index = 0
collection_of_rows = []
with open(sql_file) as file1:
    row_count = sum(1 for row in file1)
with open(sql_file) as file:
    print("row count is: " + str(row_count))
    for line in file:
        index += 1
        if index == 1:
            continue
        collection_of_rows.append(line)
        if index % 200 == 0 or index == row_count: 
            print("111")
            rows_to_use = check_rows(collection_of_rows)
            if len(rows_to_use) > 0:
                process_statement(rows_to_use)
            collection_of_rows = []
