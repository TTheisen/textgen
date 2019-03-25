'''
Author: Thomas Theisen

Objective: Test program for postgresdb.py functionality

'''

import postgresdb
import pandas as pd

#Run: python3 -W ignore postgresdb_test.py to suppress

#Test Connection Status
# db_status = postgresdb.connection_test()
# print(db_status)


#Test Create Table
# postgresdb.create_comment_table('healthcare_stream')


#Test Batch Update
# sample_df = pd.DataFrame({'postid': 'postid', 'parent': 'parent', 'child': 'child', 
#                 'comment': 'test test test', 'level': 1, 'thread': 1, 'upvotes': 1}, index = [0])
# postgresdb.batch_update_table(sample_df)


#Test Query Table
returned_data = postgresdb.query_table('healthcare')
print(returned_data)


#Test Truncate Data
# postgresdb.delete_table_contents()
