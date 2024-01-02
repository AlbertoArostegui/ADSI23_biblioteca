from .Connection import Connection
from .Author import Author

db = Connection()

class Review:
	def __init__(self, id, book_id, user_email, date_time, rating, review_text):
		self.id = id
		self.book_id = book_id
		self.user_email = user_email
		self.date_time = date_time
		self.rating = rating
		self.review_text = review_text
		