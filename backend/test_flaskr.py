import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}@{}/{}".format(
            'postgres:Server!123', 'localhost:5433', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
            "question": "Which module helps interact with DBMS in Python",
            "answer": "Flask-SQLAlchemy",
            "difficulty": 1,
            "category": 1
        }

        self.search_term = {
            "searchTerm": "Africa"
        }

        self.search_term_404 = {
            "searchTerm": "Henoke"
        }

        self.quizze = {
            "previous_questions": [20, 21],
            'quiz_category': {"type": "Science"}
        }

        self.quizze_404 = {
            "previous_questions": [20, 21],
            'quiz_category': {"type": "Sciencee"}
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_404_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        if(len(data) == 0):
            self.assertEqual(res.status_code, 404)

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])

    def test_404_get_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        res = self.client().delete('/questions/20')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 20).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['id'], 20)
        self.assertEqual(question, None)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_post_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(data['status'], 201)

    def test_405_post_question(self):
        res = self.client().post('/questions/56', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method Not Allowed')

    def test_search_questions(self):
        res = self.client().post('/search', json=self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])

    def test_404_search_questions(self):
        res = self.client().post('/search', json=self.search_term_404)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_question_by_category(self):
        res = self.client().get('categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_404_get_question_by_category(self):
        res = self.client().get('categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_quezze(self):
        res = self.client().post('/quizzes', json=self.quizze)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_404_get_quezze(self):
        res = self.client().post('/quizzes', json=self.quizze_404)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
