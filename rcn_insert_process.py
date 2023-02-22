import os
import re
import json
from google.oauth2 import service_account
from google.cloud import spanner

sql_file = "C://Users//Stefan//Downloads//rcn_lines.csv"

new_dialler_spanner_key = """{
  "type": "service_account",
  "project_id": "marketingtown",
  "private_key_id": "6989d61b469b3225d6b70934ce011c66edf68904",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDJ83fwvkTRzqwx\n9dIZ93XFhsxp4GSvENPA4yNT1xryeMOI3HLaIT1NfLRCmWQWFyrJiUhcZwbPctDL\nibzZhH3ibeJii1X6z8sT2AEdF0gA2X6/lnuJ1QOeujXbx8LZDo3XV9H5Z/yLqEY3\npk5ADNcv2OrEU+f2fW2iHF3R2Ij0gfNJOObPFhJK8rE13LsK7cEaiHVsxuwawohI\nPtSX3xt1ohiFqngFafLmHFS37FRB8Ko0Eq4oROFChibnPo2i/f/U6Ck+G3H77NvB\njJLbUenSa6oypoVvm5m/JoAHap2czIYBDxd5L/Lm57UmUn8B9/gLEShyBHx22yz+\n/mLTTeW7AgMBAAECggEADxr8767rqt3Ql3QRoQuXbYzloU29ejLCA/15WP4P7+8E\ngSosFRDDaxZWzVx31gcpliWEmhTCt6WY5ICK9aIpYFRjyIcviTEduYBApRJmulmK\nV35EA01Blg/Lk4Lfmiiyh1b0R7l1dGTDy8nOtI/BULzi4oh8Iz3Cg4unoNiXdeJY\ncnD3MSXaVeMlY4s7Ucg+QZLm3y6tLL+ACKDh084TNAzZdXDVYUbfGdgos453D3mh\nOVycTB1rlBbcAbK1dLTzpaq3mTV64e1AYjnGjA62KnlXBx/k6LfovzAzwAbTZ1Ts\n/J/F5ZbXfZCWUHzwNjgTB4ng/G1WwE21NCD3DBpM8QKBgQDjhwzS1WgtkUUzOMTo\nbV4kRn9wkqoLUQgEIj9eBlwCESMGQqdVi2Yv2PEquKFHuOPOXjxttxwekfA4ldbj\nmy+me/1KORndXBawvD//9/AhAn6Yap4YjFViw49vmkyVOXDPr9uen5PUct/mVTDL\n+5aU8pakt++qbRH4DuWBf6CZfQKBgQDjORBQcb0rcxk3CHIFHW1aGJi3CNMD6Yy6\nPs750pZ5RL3eplOEIQM4TueO6HZ3fgwXUYLQ9YIu7DO+3q9BMjC4QeuJRbUEGbgs\n7ZTPlKriwfS4WbBFKnbqQuDBPkt/PaK4OIMImka6r1o5FoYJV6AYOirl/uUhioub\n063CqwdhlwKBgADcafgCRrqlahWfiV83yrtoaOMMKwiP7e/WEVdRvtdjKTbE2c1B\nEcnskD0RJcsXsAT/5kqj/r8+3iHYr099Ltj6byLwxGBKEOvqSnO1hHsbf08kWCTP\noyMUil5pvxBxfzPJ/pLDF9Qd+yrr95tOAGvf3yIQcB+8+exuYf/zc7AhAoGAFBad\nbJ9BnC/G0Oi8O9uIKWj3R2dOUJA7UtPutIN7rij3qFGIHKxWfonrSuUeZB4Or5kT\nOaoa4k8bnApP8DGhwQiC7FXvVPd5Iu+2Mkvwd6+yFQJI5TSF4twaxrrdLdijJCpK\n213YVvTdwyJMo1LN4pZx6HeKhlabVSF3wTghpO0CgYANJmebAaTPqYy3Bb8hCKXn\neRyYvGiSjFJrRrcmMSDI4FBle3NL9lLx6//9u06XN1bwWVDp2JPQWekWZwgSAHer\ndgPNjPRQSfzXRhW2yue1ZkA/xY2TqUR9WriejIdFHgfl0gu2nxVQZjsi+n5V/SWf\nIsc70013Iea6BLNRadR6Qg==\n-----END PRIVATE KEY-----\n",
  "client_email": "spanner-account-eu@marketingtown.iam.gserviceaccount.com",
  "client_id": "106102359043395965791",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/spanner-account-eu%40marketingtown.iam.gserviceaccount.com"
}
"""

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
