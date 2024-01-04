from . import BaseTestClass
from bs4 import BeautifulSoup

class TestReviews(BaseTestClass):
    

    def test_1_get_reviews(self):
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)

    def test_2_add_review(self):
        # Login the user
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com',
            'password': '1234' 
        }, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200, 'Login failed')
        
        
        response = self.client.post('/post-review', json={
            'book_id': '1',
            'user_email': 'unai.bermudez@gmail.com',
            'rating': 5,
            'review_text': 'Test review content'
        })

        #check if we are in the read-reviews page of the correct book
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/catalogue')
        self.assertIn('token', ''.join(response.headers.values()))

        #check if the review is in the database
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        reviews = soup.find_all('div', class_='card-body d-flex flex-column')
        self.assertGreater(len(reviews), 0)
        found = False
        for review in reviews:
            if review.find('h5').text == 'unai.bermudez@gmail.com' and review.find('p', class_='card-text').text == 'Test review content':
                found = True
        self.assertTrue(found)
        
            
    def test_3_edit_review(self):
        # Login the user
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com',
            'password': '1234' 
        }, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200, 'Login failed')
        
        # Move to the read reviews page
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Get the review id
        review_id = soup.find('div', class_='card-body d-flex flex-column').find('a')['href'].split('/')[-1].split('=')[-1]

        # Edit the review
        response = self.client.post('/update-review', json={
            'id': review_id,
            'book_id': '1',
            'user_email': 'unai.bermudez@gmail.com',
            'rating': 4,
            'review_text': 'Test review content edited'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check if the review is in the database
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        reviews = soup.find_all('div', class_='card-body d-flex flex-column')
        self.assertGreater(len(reviews), 0)
        found = False
        for review in reviews:
            if review.find('h5').text == 'unai.bermudez@gmail.com' and review.find('p', class_='card-text').text == 'Test review content edited':
                found = True
        self.assertTrue(found)


    def test_4_delete_review(self):
        # Login the user
        login_response = self.client.post('/login', data={
            'email': 'unai.bermudez@gmail.com',
            'password': '1234' 
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200, 'Login failed')
        
        # Move to the read reviews page
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')

        # Get the id of the review by unai.bermudez@gmail.com and with the text 'Test review content edited'
        review_id = None
        reviews = soup.find_all('div', class_='card-body d-flex flex-column')
        for review in reviews:
            if review.find('h5').text == 'unai.bermudez@gmail.com' and review.find('p', class_='card-text').text == 'Test review content edited':
                review_id = review.find('div', class_='d-flex justify-content-between mt-2').find('a')['href'].split('=')[-1]
                break

        # Delete the review
        response = self.client.get(f"/delete-review?reviewId={review_id}", follow_redirects=True)        
        self.assertEqual(response.status_code, 200)

        # Check if the review is not in the database
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        reviews = soup.find_all('div', class_='card-body d-flex flex-column')
        self.assertGreater(len(reviews), 0)
        found = False
        for review in reviews:
            if review.find('h5').text == 'unai.bermudez@gmail.com' and review.find('p', class_='card-text').text == 'Test review content edited':
                found = True
        self.assertFalse(found)
