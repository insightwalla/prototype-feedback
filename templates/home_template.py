import streamlit as st
import pandas as pd
from utils import *
from parameters import *
from graphs import *
from database import Database_Manager
from ai_classifier import ArtificialWalla
import time


# DB connection
def fetch_data_from_db(name = 'pages/reviews.db'):
   db = Database_Manager(name)
   data = db.view()
   if len(data) == 0:
      return None
   return data

def process_direct_feedback(direct_feedback: list, df: pd.DataFrame):
   '''
   This function is used to process the direct feedback and add it to the dataframe

   ---

   params:
      direct_feedback : list of direct feedback files (it should contain only one file.xlsx)
      df: the dataframe that contains the data from the database to which we will add the direct feedback
   
   return:
      df_direct_feedback: the final dataframe with the direct feedback added
   '''
   st.write('Direct Feedback: There are emails as well')
   df_direct_feedback = pd.read_excel(direct_feedback[0])
   # change column names: CAFE == 'Reservation: Venue', 'DATE RECEIVED' == 'Date Submitted', 'FEEDBACK' == 'Feedback: Feedback', 'Source' == 'Platform'
   df_direct_feedback = df_direct_feedback.rename(columns={'CAFE': 'Reservation: Venue', 'DATE RECEIVED': 'Date Submitted', 'FEEDBACK': 'Details', 'Source': 'Platform'})
   # keep only row with "Details" not empty
   df_direct_feedback = df_direct_feedback[df_direct_feedback['Details'] != '' ]
   # add all the columns that are inside the other df
   columns_to_add = df.columns.tolist()
   for col in df_direct_feedback.columns.tolist():
      if col not in columns_to_add:
         columns_to_add.append(col)

   # add the columns that are not in the df_direct_feedback
   for col in columns_to_add:
      if col not in df_direct_feedback.columns.tolist():
         df_direct_feedback[col] = ["" for i in range(len(df_direct_feedback))]

   df_direct_feedback = df_direct_feedback[df.columns]
   # keep only the not empty Details 
   df_direct_feedback = df_direct_feedback[df_direct_feedback['Details'].astype(str) != 'nan']
   # set the same type as the df columns
   df_direct_feedback["Label: Dishoom"] = ["" for i in range(len(df_direct_feedback))]
   # transform the date into datetime

   df_direct_feedback["Date Submitted"] = df_direct_feedback["Date Submitted"].apply(lambda x: str(pd.to_datetime(x).date()))
      # get week, month and day name from the date if there is one
   df_direct_feedback["Week"] = df_direct_feedback.apply(lambda_for_week, axis=1)
   df_direct_feedback["Month"] = df_direct_feedback.apply(lambda_for_month, axis=1)
   df_direct_feedback["Day_Name"] = df_direct_feedback.apply(lambda_for_day_name, axis=1)
   df_direct_feedback["Day_Part"] = df_direct_feedback.apply(lambda_for_day_part, axis=1)
   # convert the datetime into date
   # add year
   df_direct_feedback["Year"] = df_direct_feedback["Date Submitted"].apply(lambda x: str(pd.to_datetime(x).year))
   # add the source
   df_direct_feedback["Source"] = ["Direct Feedback" for i in range(len(df_direct_feedback))]
   # add week year
   df_direct_feedback["Week_Year"] = df_direct_feedback["Week"] + "W" + df_direct_feedback["Year"]
   # add month year
   df_direct_feedback["Month_Year"] = df_direct_feedback["Month"] + "M" + df_direct_feedback["Year"]
   # set date for filter
   df_direct_feedback["date_for_filter"] = df_direct_feedback["Date Submitted"]
   # set day part 
   df_direct_feedback["Day_Part"] = df_direct_feedback["Day_Part"].apply(lambda x: get_day_part(x))
   # set the thumbs up and thumbs down 👍 👎 columns as False
   df_direct_feedback["👍"] = [False for i in range(len(df_direct_feedback))]
   df_direct_feedback["👎"] = [False for i in range(len(df_direct_feedback))]
   # set suggested for friends
   df_direct_feedback["Suggested to Friend"] = df_direct_feedback["Suggested to Friend"].apply(lambda x: 'Yes' if x == 'Yes' else 'No' if x == 'No' else 'Not Specified')
   # set same type as df columns
   df_direct_feedback["Reservation: Date"] = df_direct_feedback["Reservation: Date"].apply(lambda x: str(pd.to_datetime(x).date()) if x != "" else "")
   df_direct_feedback["Reservation: Time"] = df_direct_feedback["Reservation: Time"].apply(lambda x: str(pd.to_datetime(x).time()) if x != "" else "")
   df = pd.concat([df, df_direct_feedback], axis=0)
   return df

def create_data_from_uploaded_file():
   '''
   In this function we will create the dataframe from the uploaded file,
   preparing it for the AI model to predict the sentiment.

   '''
   # read multiple files
   files = st.file_uploader("Upload Excel", type="xlsx", accept_multiple_files=True)
   
   if files is not None:
      # 1. When received multiple files, we need to check if there is a direct feedback file
      direct_feedback = [f for f in files if f.name == 'Direct_Feedback.xlsx']
      files = [f for f in files if f.name != 'Direct_Feedback.xlsx']
      
      # 2. Read all the files and store them in a list
      dfs = [pd.read_excel(f) for f in files]

      individual_step = 100//len(dfs)
      progress_text = 'Uploading Data'
      my_bar = st.progress(0, text=progress_text)

      for i, df in enumerate(dfs):
         my_bar.progress(int((i+1) * individual_step), text=progress_text)
         # 3. Prepare the dataframes: 
         # add Reservation: Venue when empty (name of the restaurant)
         venue = df["Reservation: Venue"].unique().tolist()
         venue = [v for v in venue if str(v) != 'nan'][0]
         venue = str(venue).replace("'", "")
         df["Reservation: Venue"] = venue
         # add all the columns that we are going to use
         df["Label: Dishoom"] = ["" for i in range(len(df))]
         df['👍'] = False 
         df['👎'] = False
         df['💡'] = False    
         df['Source'] = df['Platform']
         # ADD: Week, Month, Day_Name, Day_Part, Year, Week_Year, Month_Year, date_for_filter
         # there is this sign / and the opposite \ in the date, so we need to check for both
         df["Week"] = df.apply(lambda_for_week, axis=1)
         df["Month"] = df.apply(lambda_for_month, axis=1)
         df["Day_Name"] = df.apply(lambda_for_day_name, axis=1)
         df['Day_Part'] = df.apply(lambda_for_day_part, axis=1)
         df['Year'] = df.apply(lambda x: str(pd.to_datetime(x['Date Submitted']).year) if x['Reservation: Date'] in empty else str(pd.to_datetime(x['Reservation: Date']).year), axis=1)
         df['Week_Year'] = df.apply(lambda x: x['Week'] + 'W' + x['Year'], axis=1)
         df['Month_Year'] = df.apply(lambda x: x['Month'] + 'M' + x['Year'], axis=1)
         df['date_for_filter'] = df.apply(lambda x: str(pd.to_datetime(x['Date Submitted']).date()) if x['Reservation: Date'] in empty else str(pd.to_datetime(x['Reservation: Date']).date()), axis=1)
         df['Suggested to Friend'] = df['Feedback: Recommend to Friend'].apply(lambda x: x if x == 'Yes' or x == 'No' else 'Not Specified')
      
      # concat the dfs into one
      df = pd.concat(dfs, ignore_index=True)

      # add the direct feedback file
      if len(direct_feedback) == 1:
         df = process_direct_feedback(direct_feedback, df)


      # Dividing the data into two dfs:  one with empty details and one with not empty details
      df_not_empty = df[df['Details'].astype(str) != 'nan']
      df_empty = df[df['Details'].astype(str) == 'nan']

      # drop duplicates:
      # the problem is that the details are not the same but the stripped details are the same 
      # (stripped details are the details without spaces and new lines)
      df_not_empty['Stripped_det'] = df_not_empty['Details'].apply(lambda x: x.replace(' ', '').replace('\n', '').replace('\r', '').strip())
      df_not_empty = df_not_empty.drop_duplicates(subset=['Stripped_det'])
      df_not_empty = df_not_empty.drop(columns=['Stripped_det'])

      # now we have to concat the two dfs
      df = pd.concat([df_not_empty, df_empty], ignore_index=True)
      return df
      
# main class
class FeedBackHelper:
    '''
    This class will create the main application interface
    '''
    def __init__(self, db_name):
        self.walla =  ArtificialWalla()
        self.title = 'Feedback Reviewer'
        self.db_name = db_name
        db = Database_Manager(self.db_name)

        #data = fetch_data_from_db(name=self.db_name)
        try:
          data = db.get_main_db_from_venue()
          if data is not None:
            self.df = pd.DataFrame(data, columns=['idx'] + Database_Manager.COLUMNS_FOR_CREATION)
                    
          else:
               df = create_data_from_uploaded_file()
               self.df = self.process_data(df)
               db.create_database_for_each_venue()
        except:
            df = create_data_from_uploaded_file()
            self.df = self.process_data(df)
            db.create_database_for_each_venue()


    def _preprocessing(self, data):
      '''
      Here we will do the cleaning of the data
      
      - Just filling na with empty string
      ---
      Parameters:
      
         data: pandas dataframe

      Returns:
         data: pandas dataframe
      ---
      
      '''
      data = data.fillna('')
      # add 3 
      return data

    def _classifing(self, data):
      for index, row in data.iterrows():
         sentiment, confidence, menu_items, keywords_, drinks_items = self.walla.classify_review(row['Details'])

         data.loc[index, 'Sentiment'] = sentiment
         data.loc[index, 'Confidence'] = confidence
         data.loc[index, 'Menu Item'] = ' '.join(menu_items)
         data.loc[index, 'Keywords'] = ' '.join(keywords_)
         data.loc[index, 'Drink Item'] = ' '.join(drinks_items)


      return data
   
    def process_data(self, df):
         '''
         Here we run the actual transformation of the data
         '''
         df = self._preprocessing(df)
         self.df = self._classifing(df)
         self.df = rescoring(self.df)
         save_to_db(self.df, Database_Manager.COLUMNS_FOR_CREATION, self.db_name)
         return self.df

    def plot(self):
      # fill na in reservation date with the date of the review

      final = self.to_plot
      container_keywords = st.sidebar.container()
      create_timeseries_graph(final, self.main_c)
      create_graph_keywords_as_a_whole(final, container = container_keywords)

      create_pie_chart(final)
   
      create_graph_for_source_analysis(final)

      create_graph_for_day_analysis(final)

      create_graph_for_hour_analysis(final)

      create_graph_for_week_analysis(final)

      create_graph_for_month_analysis(final)
      
      create_container_for_each_sentiment(final)


    def run(self):
      '''
      Here we will run the app

      ---
      1. Set Logo of the page
      2. Search bar
      3. Date Range for User Input
      4. Input needs to be transformed to datetime
      5. Filter the dataframe if the dates are not None
      6. Split the dataframe in two, one with review and one without reviews
      7. Rescore the dataframe without review
      8. Show the dataframe with review
      9. Save to database or delete all data from database
      10. Show all the graphs
      '''
      #1. Set Logo of the page
      st.image('pages/d.png', width=150)
      search_bar = st.text_input('Search', placeholder='Search term: "food, service, atmosphere"', key='HI')
      restaurant_container = st.sidebar.container()
      expander_filters = st.sidebar.expander('Filtering Options', expanded=False)

      # 2. Search bar
      self.main_c = st.container()

      self.main_c_1, self.main_c_2 = self.main_c.columns(2)
      
      
      if search_bar != '':
         # If the search bar is not empty, filter the dataframe
         # if search bar contains more than one word, split the words at "," and search for the ones that contains both
         if ',' in search_bar:
            search_bar = search_bar.split(',')
            # iterate over the list of words
            for word in search_bar:
               # if the word is not empty, filter the dataframe
               if word != '':
                  self.df = self.df[self.df['Details'].str.contains(word, case=False)]
         else:
            self.df = self.df[self.df['Details'].str.contains(search_bar, case=False)]

         # make sure the dataframe is not empty
         if self.df.shape[0] == 0:
            st.error('No results found. Please try again.')
            st.stop()

      # 3. Date Range for User Input
      min_date = pd.to_datetime(self.df['date_for_filter'].min())
      max_date = pd.to_datetime(self.df['date_for_filter'].max())
      try:
         start_date, end_date = expander_filters.date_input('Date Range', [min_date, max_date])
         # 5. Filter the dataframe if the dates are not None
         if start_date != None and end_date != None:
            # 4. Input needs to be transformed to datetime
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            # If both dates are not None, filter the dataframe
            self.df['date_for_filter'] = pd.to_datetime(self.df['date_for_filter'])
            self.df = self.df[(self.df['date_for_filter'] >= start_date) & (self.df['date_for_filter'] <= end_date)]
            # re-tranform to string
            self.df['date_for_filter'] = self.df['date_for_filter'].dt.strftime('%Y-%m-%d')
      except:
         st.warning('Please select a date range')
         st.stop()
      
      #6. Filter by restaurant name
      restaurant_name = restaurant_container.selectbox('Restaurant Name', ['All'] + self.df['Reservation: Venue'].unique().tolist(), index = 0)
      # PROCESSSING DATA
      if restaurant_name != 'All':
         name_choosen_db = 'pages/' + restaurant_name + '.db'
         self.df = pd.DataFrame(fetch_data_from_db(name=name_choosen_db), columns=['idx'] + Database_Manager.COLUMNS_FOR_CREATION)

      # 6.1. Split the dataframe in two, one with review and one without reviews
      self.df_with_review = self.df[self.df['Details'] != '']
      self.df_without_review = self.df[self.df['Details'] == '']

      # 7. Rescore the dataframe without review
      self.df_without_review = rescoring(self.df_without_review)

      # 7.1 Filter by keywords
      key_words = expander_filters.multiselect('Keywords', keywords, default = [])
      if key_words != []:
         self.df_with_review = self.df_with_review[self.df_with_review['Keywords'].str.contains('|'.join(key_words), case=False)]


      with st.expander(f'Empty Feedbacks: {len(self.df_without_review)}', expanded=False):
         create_graphs_no_rev(self.df_without_review)

      #7.2 Filter by Day Part
      day_parts = self.df_with_review['Day_Part'].unique().tolist()
      day_part = expander_filters.multiselect('Day Part', day_parts, default = [])
      if day_part != []:
         self.df_with_review = self.df_with_review[self.df_with_review['Day_Part'].str.contains('|'.join(day_part), case=False)]

      #7.3 Filter by Day of the week
      days_of_the_week = self.df_with_review['Day_Name'].unique().tolist()
      day_of_the_week = expander_filters.multiselect('Day of the week', days_of_the_week, default = [])
      if day_of_the_week != []:
         self.df_with_review = self.df_with_review[self.df_with_review['Day_Name'].str.contains('|'.join(day_of_the_week), case=False)]

      #7.4 Filter by Month
      months = self.df_with_review['Month'].unique().tolist()
      month = expander_filters.multiselect('Month', months, default = [])
      if month != []:
         self.df_with_review = self.df_with_review[self.df_with_review['Month'].str.contains('|'.join(month), case=False)]


      # 8. Show the dataframe with review
      # use sentiment to modify the checkbox
      self.to_plot = self.df_with_review

      #st.write(self.to_plot)


      # 9. Save to database or delete all data from database
      if start_date == min_date and end_date == max_date and search_bar == '' and month == [] and day_of_the_week == [] and day_part == [] and key_words == [] and restaurant_name != 'All':
         c1,c2 = st.sidebar.columns(2)
         
         button_delete_all = c2.button('Delete')
         button_save_all = c1.button('Save')


         if button_delete_all:
            db_single_res = Database_Manager(name_choosen_db)
            db_single_res.delete_all()
            st.info('Deleted all data from database')

         if button_save_all:
            self.to_plot = pd.concat([self.to_plot, self.df_without_review])
            #st.stop()
            save_to_db(self.to_plot, Database_Manager.COLUMNS_FOR_CREATION, name_choosen_db)

            st.success('Saved all data to database')
            # update container
            
      elif start_date == min_date and end_date == max_date and search_bar == '' and month == [] and day_of_the_week == [] and day_part == [] and key_words == [] and restaurant_name == 'All':
         button_delete_everything = st.sidebar.button('Delete All')
         if button_delete_everything:

            db_main = Database_Manager(self.db_name)
            db_main.delete_all()
            st.info('Deleted all data from database')
            venues = self.df['Reservation: Venue'].unique().tolist()
            for venue in venues:
               name_choosen_db = 'pages/' + venue + '.db'
               db_single_res = Database_Manager(name_choosen_db)
               db_single_res.delete_all()
            st.info('Deleted all data from database')

      # 10. Show all the graphs
      if len(self.df_with_review) > 0:
         self.plot()

      index_to_modify = st.number_input('Index to modify', min_value=1, max_value=len(self.df_with_review), value=1, step=1, on_change=None, key=None)


      with st.expander('Card', expanded=True):
         row = self.df_with_review.iloc[index_to_modify-1]
         date = row['date_for_filter']
         venue = row['Reservation: Venue']
         time  = row['Reservation: Time']
         suggestion = row['Suggested to Friend']
         rev = row['Details']
         is_favorite = row['👍'] == '1'
         is_not_favorite = row['👎'] == '1'
         is_suggestion = row['💡'] == '1'

         c1,c2,c3, c4 = st.columns(4)

         c1.write(f'**Venue**: {venue}')

         c2.write(f'**Date**: {date}')

         c3.write(f'**Time**: {time}')

         c4.write(f'**Suggested to Friend**: {suggestion}')

         st.write(f'{rev}')

         col1, col2, col3, col4 = st.columns(4)
         # get sentiment 
         sentiment = row['Sentiment']
         options = ['POSITIVE', 'NEGATIVE', 'neutral']
         index = options.index(sentiment)
         select_sentiment =  col1.selectbox('Sentiment', ['POSITIVE', 'NEGATIVE', 'neutral'], index = index, key = f'i_{index_to_modify}')


         select_thumbs_up = col2.checkbox('👍', value = is_favorite, key = f't_u {index_to_modify}')

         select_thumbs_down = col3.checkbox('👎', value = is_not_favorite, key = f't_d {index_to_modify}')

         select_suggestion = col4.checkbox('💡', value = is_suggestion, key = f't_s {index_to_modify}')

         columns_rating = ['Overall Rating', 'Feedback: Food Rating', 'Feedback: Drink Rating', 'Feedback: Service Rating', 'Feedback: Ambience Rating']

         columns_for_input = ['Overall', 'Food', 'Drink', 'Service', 'Ambience']
         columns_ = st.columns(len(columns_rating))


         results = []
         for i, col in enumerate(columns_rating):
            value = float(row[col])
            # transform the value into a string
            value = int(value)

            new_value = columns_[i].number_input(label=columns_for_input[i], min_value=0, max_value=10, value=value, step=1, format=None, key=f'rate{i} - {index_to_modify}')
            # add to the list
            results.append(new_value)

         # st.write(f'**Overall Rating**: {results[0]}')
         # st.write(f'**Food Rating**: {results[1]}')
         # st.write(f'**Drink Rating**: {results[2]}')
         # st.write(f'**Service Rating**: {results[3]}')
         # st.write(f'**Ambience Rating**: {results[4]}')


         # now we need to save the data to the database
         if st.button('Saving'):
               # get restaurant name
               restaurant_name = row['Reservation: Venue']
               name_choosen_db = 'pages/' + restaurant_name + '.db'
               db = Database_Manager(name_choosen_db)
               db.modify_overall_rating_in_db(rev, results[0])
               db.modify_food_rating_in_db(rev, results[1])
               db.modify_drink_rating_in_db(rev, results[2])
               db.modify_service_rating_in_db(rev, results[3])
               db.modify_ambience_rating_in_db(rev, results[4])
               db.modify_sentiment_in_db(rev, select_sentiment)

               db.modify_thumbs_up_in_db(rev, select_thumbs_up)
               db.modify_thumbs_down_in_db(rev, select_thumbs_down)

               db.modify_is_suggestion(rev, select_suggestion)

               st.success('Saved')









         





