import sqlite3
import streamlit as st
import pandas as pd

class Database_Manager:
   COLUMNS_FOR_SECTION = [
      'details', 'sentiment', 'confidence', 'menu_item',
      'overall_rating', 'food_rating', 'drink_rating',
      'service_rating', 'ambience_rating',
      'date', 'time', 'reservation_date',
      'keywords', 'drink_item', 'reservation_venue', 'label',
      'week', 'month', 'day_name', 'day_part', 'suggested_to_friend', '👍', '👎',
      'source', 'year', 'week_yr', 'month_yr', 'date_for_filter', "💡"
      ]

   COLUMNS_FOR_CREATION = [
      'Details', 'Sentiment', 'Confidence', 'Menu Item', 
      'Overall Rating','Feedback: Food Rating', 'Feedback: Drink Rating',
      'Feedback: Service Rating', 'Feedback: Ambience Rating',
      'Date Submitted', 'Reservation: Time', 'Reservation: Date',
      'Keywords', 'Drink Item', 'Reservation: Venue', 'Label: Dishoom', 
      'Week', 'Month', 'Day_Name', 'Day_Part', 'Suggested to Friend', '👍', '👎',
      'Source', 'Year', 'Week_Year', 'Month_Year', 'date_for_filter', "💡"
      ]
   
   def __init__(self, db):
      self.conn = sqlite3.connect(db)
      self.cur = self.conn.cursor()
      query = ",".join([col + ' text' for col in self.COLUMNS_FOR_SECTION])

      self.cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY, 
                        """ + query + ')')

      self.conn.commit()

   def view(self):
      '''Returns all the rows from the database'''
      self.cur.execute("SELECT * FROM reviews")
      rows = self.cur.fetchall()
      return rows
   
   def delete_all(self):
      self.cur.execute("DELETE FROM reviews")
      self.conn.commit()

   def delete_Table(self):
      self.cur.execute("DROP TABLE reviews")
      self.conn.commit()

   def insert(self, *row):
      self.cur.execute(f"INSERT INTO reviews VALUES (NULL, {','.join(['?' for i in range(len(row))])})", (row))
      self.conn.commit()
      
   def insert_multiple(self, rows):
      self.cur.executemany(f"INSERT INTO reviews VALUES (NULL, {','.join(['?' for i in range(len(self.COLUMNS_FOR_SECTION))])})", rows)
      self.conn.commit()
      # close the connection
      self.conn.close()

   def insert_multiple_with_id(self, rows):
      self.cur.executemany(f"INSERT INTO reviews VALUES ({','.join(['?' for i in range(len(self.COLUMNS_FOR_SECTION) + 1)])})", rows)
      self.conn.commit()
      # close the connection
      self.conn.close()

   def run_query(self, query):
      self.cur.execute(query)
      self.conn.commit()
      return self.cur.fetchall()
   
   def create_database_for_each_venue(self):
      # get all data 
      list_of_venue = self.run_query("SELECT DISTINCT reservation_venue FROM reviews")
      #st.write(list_of_venue)
      # get all the data for each venue
      for venue in list_of_venue:
         venue = venue[0]
         data = self.run_query(f"SELECT * FROM reviews WHERE reservation_venue = '{venue}'")
         # create a new database for each venue
         db = Database_Manager(f'pages/{venue}.db')
         db.insert_multiple_with_id(data)
         db.conn.close()
      #st.stop()

   def get_main_db_from_venue(self):
      # from each venue, get all the data
      list_of_venue = self.run_query("SELECT DISTINCT reservation_venue FROM reviews")
      # create a new database for each venue
      data = []
      for venue in list_of_venue:
         venue = venue[0]
         db = Database_Manager(f'pages/{venue}.db')
         data.append(pd.DataFrame(db.view()))
         db.conn.close()
      # insert all the data into the main database
      # transform into dataframe
      data = pd.concat(data)
      data.columns = ['idx'] + self.COLUMNS_FOR_CREATION
      #st.write(data)
      return data

   def modify_food_in_db(self, review, food):
      sql = "UPDATE reviews SET menu_item = ? WHERE details = ?"
      self.cur.execute(sql, (food, review))
      self.conn.commit()

   def modify_drink_in_db(self, review, drink):
      sql = "UPDATE reviews SET drink_item = ? WHERE details = ?"
      self.cur.execute(sql, (drink, review))
      self.conn.commit()

   def modify_label_in_db(self, review, label):
      sql = "UPDATE reviews SET label = ? WHERE details = ?"
      self.cur.execute(sql, (label, review))
      self.conn.commit()

   # last modify

   def modify_overall_rating_in_db(self, review, rating):
      sql = "UPDATE reviews SET overall_rating = ? WHERE details = ?"
      self.cur.execute(sql, (rating, review))
      self.conn.commit()

   def modify_food_rating_in_db(self, review, rating):

      sql = "UPDATE reviews SET food_rating = ? WHERE details = ?"
      self.cur.execute(sql, (rating, review))
      self.conn.commit()

   def modify_drink_rating_in_db(self, review, rating):

      sql = "UPDATE reviews SET drink_rating = ? WHERE details = ?"
      self.cur.execute(sql, (rating, review))
      self.conn.commit()

   def modify_service_rating_in_db(self, review, rating):
         
         sql = "UPDATE reviews SET service_rating = ? WHERE details = ?"
         self.cur.execute(sql, (rating, review))
         self.conn.commit()

   def modify_ambience_rating_in_db(self, review, rating):

      sql = "UPDATE reviews SET ambience_rating = ? WHERE details = ?"
      self.cur.execute(sql, (rating, review))
      self.conn.commit()

   def modify_sentiment_in_db(self, review, sentiment):
         
         sql = "UPDATE reviews SET sentiment = ? WHERE details = ?"
         self.cur.execute(sql, (sentiment, review))
         self.conn.commit()   

   def modify_thumbs_up_in_db(self, review, thumbs_up):
         
         sql = "UPDATE reviews SET 👍 = ? WHERE details = ?"
         self.cur.execute(sql, (thumbs_up, review))
         self.conn.commit()

   def modify_thumbs_down_in_db(self, review, thumbs_down):
            
            sql = "UPDATE reviews SET 👎 = ? WHERE details = ?"
            self.cur.execute(sql, (thumbs_down, review))
            self.conn.commit()   


   def modify_is_suggestion(self, review, is_suggestion):
         
         sql = "UPDATE reviews SET 💡 = ? WHERE details = ?"
         self.cur.execute(sql, (is_suggestion, review))
         self.conn.commit()







      


if __name__ == "__main__":
   db = Database_Manager('/Users/robertoscalas/Desktop/demo_working_version/pages/reviews.db')

   db.delete_Table()
