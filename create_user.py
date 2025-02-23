vDatabase = 'DEV'

# ---- Import Modules ----
import os
import streamlit as st
import pandas as pd
import base64

# ---- Set directory ----
vPathUsers = vDatabase + '/Passwords.xlsx'

# ---- Read the Password file ----
df_Passwords = pd.read_excel(vPathUsers, sheet_name = 'Passwords')

DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")

db_config = {
    'host': 'sql7.freesqldatabase.com',
    'database': DB_LOGIN,
    'user': DB_LOGIN,
    'password': DB_PASSWORD,
    'port': 3306
}

# ---- Function to create password ----
def create_user(df_Passwords, vPathUsers):
    """Inserts a new user to the Excel"""
    Username = input("Enter username: ")
    Name = input("Enter name: ")
    Password = input("Enter password: ")

    Usernames = df_Passwords['Username'].values

    if Username in Usernames:
        print(f"Username {Username} already taken, choose another username")
    else:
        New_User = pd.DataFrame({"Username": [Username],
                         "Name": [Name],
                         "Password": [Password]})
        
        df_Passwords = pd.concat([df_Passwords, New_User], ignore_index=True)
        df_Passwords.to_excel(vPathUsers, 
                              sheet_name='Passwords',
                              index=False)
        print("User created successfully!")

# ---- Function to reset a password ----
def reset_user_password(username):
    new_password = input("Enter new password for user {}: ".format(username))

# ---- Call the function ----
create_user(df_Passwords=df_Passwords, vPathUsers=vPathUsers)