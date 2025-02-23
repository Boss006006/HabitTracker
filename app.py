# ---- Set general settings ----
vEnv = 'PRD/'

#region ---- Import  Libraries ---- 
import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.dates import DateFormatter

#endregion

#region ---- Setup Streamlit Config ----
st.set_page_config(
        page_title = 'TEST'
    ,   layout = 'wide'
)
st.title('Your Health and Habit tracker')
#endregion

#region ---- Authentication ----

# Read the Excel with the passwords

vFilepathPasswords = vEnv + 'Passwords.xlsx'
df_Passwords = pd.read_excel(vFilepathPasswords, sheet_name='Passwords')
#df_Passwords.set_index('Username', inplace=True)

# Create a form with a unique key

# Initialize session states
if 'login_status' not in st.session_state:
    st.session_state['login_status'] = 0

if 'primary_login' not in st.session_state:
    st.session_state['primary_login'] = 1

if 'name_user' not in st.session_state:
    st.session_state['name_user'] = None

# Logout functionality
if st.session_state['login_status'] == 1:
    with st.sidebar:
        logout_button = st.button('Logout')
        if logout_button:
            st.session_state['login_status'] = 0
            st.session_state['primary_login'] = 0
            st.rerun()

# Display logout message
if st.session_state['primary_login'] == 0:
    st.info('You are succesfully logged out')
    
    homescreen_button = st.button('Go To the login Page')
    if homescreen_button:
        st.session_state['login_status'] = 0
        st.session_state['primary_login'] = 1
        st.rerun()

# Login form
if st.session_state.get('login_status', 0) == 0 and st.session_state.get('primary_login', 1) == 1:
    with st.form(key='Login'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        # Check if username exists in the DataFrame
        if username in df_Passwords['Username'].values:
            user_row = df_Passwords[df_Passwords['Username'] == username]
            stored_password = user_row.iloc[0]['Password']
            st.session_state['name_user'] = user_row.iloc[0]['Name']

            
            if password == stored_password:
                st.session_state['login_status'] = 1
                st.session_state['primary_login'] = 1
                st.success('Login Successful')
                time.sleep(2)
                st.rerun()
            else:
                st.warning('Username or Password incorrect')
        else:
            st.warning('Username or Password incorrect')
  
# Main app functionality
if st.session_state['login_status'] == 1:

#endregion 

    #region ---- Load the data ----
    vUser = st.session_state['name_user'] + '/'
    vFilepathData = vEnv + vUser + 'Data.xlsx'

    df_stats = pd.read_excel(vFilepathData, sheet_name='Data')
    df_stats['Date'] = pd.to_datetime(df_stats['Date']).dt.date

    #endregion

    #region ---- Setup Homepage ----
    with st.sidebar:
        option_menu = st.radio(label='option menu',
                               options=['Home', 'New Habit', 'Scores', 'Statistics']
                               )
  
    if option_menu == 'Home':
        name = st.session_state['name_user']
        st.write('---')
        st.subheader(f'Welcome {name} to your personal Health and Habit tracker')

    #endregion

    #region ---- Habits ----
    if option_menu == 'New Habit':
        st.write('---')
        st.subheader('Welcome to your personal Health and Habit tracker')

        col1, col2 = st.columns(2)

        with col1.form(key='new_habit', clear_on_submit=True):
            new_col = st.text_input('Enter habit: ')

            submit_button = st.form_submit_button(label='Add Habit')

            if submit_button:
                if new_col in df_stats.columns:
                    st.warning('This habit already exists')        
                else:
                    df_stats[new_col] = None
                    st.success(f'New habit **{new_col}** added')

                    df_stats.to_excel(vFilepathData, sheet_name='Data', index=False)
                    df_stats = pd.read_excel(vFilepathData, sheet_name='Data')

        with col2.form(key='remove_habit', clear_on_submit=True):
            columns = list(df_stats.columns)
            columns.remove('Date')

            remove_column=st.selectbox(options=columns, label='Select Habit')

            submit_button = st.form_submit_button(label='Remove Habit')

            if submit_button:
                df_stats.drop(columns=[remove_column], inplace=True)

                st.write(remove_column)

                df_stats.to_excel(vFilepathData, sheet_name='Data', index=False)
                df_stats = pd.read_excel(vFilepathData, sheet_name='Data')
                st.success(f'Column **{remove_column}** removed.')
                time.sleep(2)
                st.rerun()
    
    #endregion

    #region ---- Today ----
    if option_menu == 'Scores':
        st.write('---')
        st.subheader('Welcome to your personal Health and Habit tracker')

        today = datetime.today()
        selected_day = st.date_input("Select Date:", value=today, max_value=today)

        df_today = df_stats[df_stats['Date'] == selected_day]

        if not df_today.empty:
            update_values = {}
            for column in df_today.columns:
                if column != 'Date':
                    current_value = df_today.iloc[0][column]
                    if pd.isna(current_value):
                        current_value = None
                    try:
                        choice_index = ['Good', 'Medium', 'Bad', None].index(current_value)
                    except ValueError:
                        choice_index = 2  

                    update_values[column] = st.radio(f'**{column}**', 
                                                    options=['Good', 'Medium', 'Bad', None],
                                                    index=choice_index)
                    
            if st.button('Update Habits'):
                for column in update_values:
                    df_stats.loc[df_stats['Date'] == selected_day, column] = update_values[column]
                
                df_stats.to_excel(vFilepathData, 
                                  index=False,
                                  sheet_name='Data')
                st.success("Habits updated successfully!")
        else:
            st.error("No data found for the selected date.")

    #endregion

    #region ---- Statistics ----
    if option_menu == 'Statistics':
        st.write('---')
        st.subheader('Welcome to your personal Health and Habit tracker')

        today = datetime.today()
        begin_date_default = today - timedelta(days=6)

        col1, col2 = st.columns(2)

        begin_date = col1.date_input("Begin date", value=begin_date_default, max_value=today)
        end_date = col2.date_input("End date", value=today, max_value=today)
        
        st.write('---')

        df_stats['Date'] = pd.to_datetime(df_stats['Date'])

        df_stats_f = df_stats[(df_stats['Date'] >= pd.to_datetime(begin_date)) 
                           & (df_stats['Date'] <= pd.to_datetime(end_date))]
        
        value_map = {None: 0, 'Bad': 1, 'Medium': 2, 'Good': 3}

        for col in df_stats_f.columns[1:]:  # Skip 'Date' column
            df_stats_f[col] = df_stats_f[col].map(value_map)

        # Ensure 'Date' is in the correct datetime format
        df_stats_f['Date'] = pd.to_datetime(df_stats_f['Date'])

        # Transpose the DataFrame for the desired axis orientation
        df_stats_fT = df_stats_f.set_index('Date').T  

        # Define the colors for the values
        color_map = ListedColormap(['red', 'orange', 'green'])  # Red, Orange, Green for 1, 2, 3
        norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5], color_map.N)  # Define the boundaries that map values to colors

        # Assuming df_stats_fT is your DataFrame transposed and set up correctly
        plt.figure(figsize=(10, 5))
        ax = sns.heatmap(df_stats_fT, annot=False, cmap=color_map, norm=norm,
                        linewidths=2.5, cbar=False)
        plt.title('Daily Habit Tracker')
        plt.xlabel('')

        # Customizing the color bar to show what each color represents
        colorbar = ax.collections[0].colorbar
        #colorbar.set_ticklabels(['Bad', 'Medium', 'Good'])  # Optionally customize with your labels

        # Formatting the x-axis labels as dates
        ax.set_xticklabels([date.strftime('%Y-%m-%d') for date in df_stats_fT.columns])
        ax.set_facecolor('lightblue')

        plt.xticks(rotation=45)  
        plt.yticks(rotation=45)

        # Show the plot in Streamlit
        st.pyplot(plt, transparent=True)

    #endregion

