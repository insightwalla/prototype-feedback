import sqlite3

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

   def run_query(self, query):
      self.cur.execute(query)
      self.conn.commit()
      return self.cur.fetchall()
   
if __name__ == "__main__":
   db = Database_Manager('/Users/robertoscalas/Desktop/demo_working_version/pages/reviews.db')

   db.delete_Table()
