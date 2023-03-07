"""
 * @file        bddScript.py
 * @brief       Contains the functions specific to the bdd's management
 * @author      Jules Gauthier
 * @version     0.1
 * @date        2023
"""

from sshtunnel import SSHTunnelForwarder
import base64
import paramiko
import io
import pymysql
import pandas as pd
import mysql.connector 

ssh_host = '3.89.81.43'
ssh_username = 'ec2-user'
with open('./be-ec2keypair.pem', 'rb') as key:
    SSH_KEY_BLOB = base64.b64encode(key.read())
    
SSH_KEY_BLOB_DECODED = base64.b64decode(SSH_KEY_BLOB)
SSH_KEY = SSH_KEY_BLOB_DECODED.decode('utf-8')
pkey = paramiko.RSAKey.from_private_key(io.StringIO(SSH_KEY))


"""
* @brief Open an SSH tunnel and connect using a username and password.        
    :param verbose: Set to True to show logging    
    :return tunnel: Global SSH tunnel connection    
"""   
def open_ssh_tunnel(): 
    try:
        global server        
        server = SSHTunnelForwarder(
            (ssh_host),
            ssh_username=ssh_username,
            ssh_pkey=pkey,
            remote_bind_address=('newdatabase-be.ckagegrkprl8.us-east-1.rds.amazonaws.com', 3306)
        )
        server.start()
    except BaseException as e:
        print('Problem with-->',e)
    finally:
        if server:
            print('Server started')
  
    
"""
* @brief Connect to a MySQL server using the SSH tunnel connection        
    :return connection: Global MySQL database connection   
"""   
def mysql_connect():
    try:
        global connection        
        connection = mysql.connector.connect(
            database="robot-db",
            host='127.0.0.1',
            user="admin",
            password="Byuqutrg31!",
            auth_plugin="mysql_native_password",
            port=server.local_bind_port)
    except BaseException as e:
        print('Problem with-->',e)
    finally:
        if server:
            print('Connection to MySQL database established')
          
            
"""
* @brief Runs a given SQL query via the global database connection.        
    :param sql: MySQL query    
"""  
def get_query(sql):  
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
    
     
    
"""
* @brief Runs a given SQL query via the global database connection.        
    :param sql: MySQL query    
"""  
def push_query(sql):  
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
  
    
"""
* @brief Closes the MySQL database connection.    
""" 
def mysql_disconnect():   
    connection.close()
    
    
"""
* @brief Closes the SSH tunnel connection.    
"""      
def close_ssh_tunnel():
    server.close
    

