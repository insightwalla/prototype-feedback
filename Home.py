'''
To run the script:

streamlit run Home.py
'''
import streamlit as st
from login_script import login
from templates.home_template import FeedBackHelper

st.set_page_config(
   page_title='Feedback Reviewer',
   page_icon=':smile:',
   layout='wide',
   initial_sidebar_state='auto'
   )

def main_debug(name_db: str,section = ''):
    try:
        app = FeedBackHelper(name_db)
        app.run()
    except Exception as error:
        st.warning(error)
        raise error

def main_prod(name_db: str, section = ''):
    '''
    Main function to run the app
    This wont display the error message
    '''
    try:
        app = FeedBackHelper(name_db)
        app.run()
    except:
        st.info('Add some reviews by dragging and dropping the file')

# Main Loop
if __name__ == "__main__":
    DEBUG = True
    CONFIG_FILE = "config.yaml"
    MAIN = main_debug if DEBUG else main_prod
    login(render_func=MAIN,
          config_file=CONFIG_FILE)