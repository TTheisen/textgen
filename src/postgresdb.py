'''
Author: Thomas Theisen

Objective: Provide functionality related to postgres

'''

# Python Modules
#-----------------------------------------------------------------------------#
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import os
import sys

# Interal Modules
#-----------------------------------------------------------------------------#
import credentials

# Create table
#-----------------------------------------------------------------------------#

DB_USER = credentials.configuration['DatabaseCredentials']['USER']
DB_PASS = credentials.configuration['DatabaseCredentials']['PASSWORD']
DB_HOST = credentials.configuration['DatabaseCredentials']['HOST']
DB_NAME = credentials.configuration['DatabaseCredentials']['DBNAME']
DB_PORT = credentials.configuration['DatabaseCredentials']['PORT']
DB_TYPE = 'postgresql'
DB_DRIVER = 'psycopg2'
POOL_SIZE = 50


def connection_test():
    conn = None
    connectionStatus = False
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                        user=DB_USER, password=DB_PASS)
        connectionStatus = True
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    finally:
        if conn is not None:
            conn.close()
        return connectionStatus


def create_comment_table(tablename):
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                        user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        sql = "CREATE TABLE {} (postid varchar(10) not null, parent VARCHAR(10) not null, \
                child VARCHAR(10) not null, author VARCHAR(50) not null, comment text not null, \
                level integer not null, thread integer not null, upvotes integer not null)".format(tablename)
        # cur.execute(sql)
        print(sql)
        print('Successfully created table')
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    finally:
        if conn:
            conn.close()


def batch_update_table(table, df):
    conn = None
    try:
        SQLALCHEMY_DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (DB_TYPE, DB_DRIVER, DB_USER,
                                                                DB_PASS, DB_HOST, DB_PORT, DB_NAME)
        ENGINE = create_engine(SQLALCHEMY_DATABASE_URI,
                               pool_size=POOL_SIZE, max_overflow=0)
        df.to_sql(table, ENGINE, if_exists='append', index=False)
        print('Batch Update Complete')
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1)
    finally:
        if conn is not None:
            conn.close()


def query_table(table):
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                        user=DB_USER, password=DB_PASS)
        cur = conn.cursor()
        sql = "SELECT * FROM {}".format(table)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        labels = ['postid', 'parent', 'child',
            'comment', 'level', 'thread', 'upvotes']
        df = pd.DataFrame.from_records(rows, columns=labels)
        return df
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def delete_table_contents():
    conn = None
    try:
        conn = psycopg2.connect(host = DB_HOST, database = DB_NAME,
                        user = DB_USER, password = DB_PASS)
        cur = conn.cursor()
        sql = "TRUNCATE comments"
        cur.execute(sql)
        print('Truncated data from comments table')
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:

        if conn is not None:
            conn.close()
