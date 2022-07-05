import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_question(request, results):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [r.format() for r in results]
    current = questions[start:end]

    return current


def get_quize_question(Category, previous_questions):
    return Question.query.filter(
        Question.category == Category.id,
        Question.id.notin_(previous_questions)).order_by(
        Question.id).first()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type, Authorization")
        response.headers.add(
            "Access-Control-Allow-Headers",
            "GET,POST,PATCH,PUT,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories", methods=['GET'])
    def get_category():
        all = Category.query.all()

        dict_c = {}

        for c in all:
            dict_c[c.id] = c.type

        return jsonify({"categories": dict_c})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.



    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=['GET'])
    def get():
        all_q = Question.query.all()
        current_q = paginate_question(request, all_q)

        if len(current_q) == 0:
            abort(404)

        all_c = Category.query.all()

        dict_c = {}

        for c in all_c:
            dict_c[c.id] = c.type

        current_c = Category.query.filter(Category.id == 1).one_or_none()
        f_c = current_c.format()

        return jsonify({"questions": current_q, "total_questions": len(
            Question.query.all()), "categories": dict_c, "current_category": f_c['type']})

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete(id):
        q = Question.query.filter(Question.id == id).one_or_none()
        if q is None:
            abort(422)
        q.delete()
        return jsonify({'statusCode': 200, "id": id})

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def add():
        data = request.get_json()
        n_question = data.get('question', None)
        n_answer = data.get('answer', None)
        n_difficulty = data.get('difficulty', None)
        n_category = data.get('category', None)
        cat = Question(
            question=n_question,
            answer=n_answer,
            difficulty=n_difficulty,
            category=n_category)
        cat.insert()
        return jsonify({'status': 201})

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/search', methods=['POST'])
    def search():
        data = request.get_json()
        term = data.get('searchTerm', None)
        all_q = Question.query.filter(
            Question.question.ilike(f'%{term}%')).all()

        formated_q = [q.format() for q in all_q]

        if len(formated_q) == 0:
            abort(404)

        current_c = Category.query.filter(Category.id == 1).one_or_none()

        return jsonify({"questions": formated_q,
                        "totalQuestions": len(Question.query.all()),
                        "currentCategory": current_c.format()['type']})

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def find(id):
        all = Question.query.filter(Question.category == id).all()

        formated_q = [q.format() for q in all]

        if len(formated_q) == 0:
            abort(404)

        current_c = Category.query.filter(Category.id == id).one_or_none()

        return jsonify({"questions": formated_q,
                        "totalQuestions": len(Question.query.all()),
                        "currentCategory": current_c.format()['type']})

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        quiz_category = data.get('quiz_category', None)
        is_all = False

        # print(previous_questions)

        if quiz_category['id'] == 0:
            cat = Category.query.all()
            is_all = True
        else:
            cat = Category.query.filter(
                Category.type == quiz_category['type']).one_or_none()

        if cat is None:
            abort(404)

        if not is_all:
            question = get_quize_question(cat, previous_questions)
        else:
            for c in cat:
                question = get_quize_question(c, previous_questions)
                if question is not None:
                    break
                elif len(previous_questions) < 5:
                    continue

        if question is None:
            return jsonify(
                {'previous_questions': [1, 2, 3, 4, 5], 'question': None})

        formated_q = question.format()

        return jsonify({'question': formated_q})

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
