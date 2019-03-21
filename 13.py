from flask_restful import reqparse, Api, Resource
from flask import Flask, jsonify, make_response, render_template, request, session
from requests import delete
from werkzeug.utils import redirect
from DBManager import *
from forms import *


app = Flask(__name__)
api = Api(app)
db = DB()
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PROPAGATE_EXCEPTIONS'] = True

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)

parser_put = reqparse.RequestParser()
parser_put.add_argument('part', required=True)
parser_put.add_argument('text', required=True)

parser_new_user = reqparse.RequestParser()
parser_new_user.add_argument('login', required=True)
parser_new_user.add_argument('password', required=True)


class Error404(Exception):
    pass


@app.errorhandler(404)
def not_found(error):
    return make_response(render_template("error404.html"), 404)


@app.errorhandler(Error404)
def not_found(error):
    return make_response(render_template("error404.html"), 404)


def abort_if_news_not_found(news_id, data_base):
    if not data_base.get(news_id):
        print(89)
        raise Error404


@app.route('/delete_news/<int:news_id>')
def delete_news(news_id):
    delete('http://localhost:8080/news/{}'.format(news_id))
    return redirect("/news")


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "GET":
        return render_template('login.html', form=form)
    elif request.method == "POST":
        user_name = form.username.data
        password = form.password.data
        exists = UserModel(db.get_connection()).exists(user_name, password)

        if exists[0]:
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect("/news")
        else:
            return redirect("/login")


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/add_user', methods=["POST", "GET"])
def add_user():
    form = RegistrationForm()
    if request.method == "GET":
        return render_template('regestration.html', form=form)
    elif request.method == "POST":
        return redirect('/users', code=307)


class News(Resource):
    def get(self, news_id):
        if 'username' not in session:
            return redirect('/login')
        news = NewsModel(db.get_connection())
        abort_if_news_not_found(news_id, news)
        return make_response(render_template("preview_news.html", news=news.get(news_id)))

    def delete(self, news_id):
        news = NewsModel(db.get_connection())
        abort_if_news_not_found(news_id, news)
        news.delete(news_id)
        return jsonify({'success': 'OK'})
    
    def put(self, news_id):
        news = NewsModel(db.get_connection())
        abort_if_news_not_found(news_id, news)
        args = parser_put.parse_args()
        news.update(news_id, args['part'], args['text'])
        return jsonify({'success': 'OK'})


class NewsList(Resource):
    def get(self):
        if 'username' not in session:
            return redirect('/login')
        global news
        news = NewsModel(db.get_connection()).get_all(int(session["user_id"]))
        form = AddNewsForm()
        return make_response(render_template("13.html", data=news, form=form, add=True))

    def post(self):
        #  args = parser.parse_args()
        form = AddNewsForm()

        if form.validate_on_submit():
            NewsModel(db.get_connection()).insert(form.title.data, form.text.data, session['user_id'])
            return redirect("/news")

        return make_response(render_template("13.html", data=news, form=form, add=True))


class User(Resource):
    def get(self, user_id):
        user = UserModel(db.get_connection())
        abort_if_news_not_found(user_id, user)
        return jsonify({'users': user.get(user_id)})

    def delete(self, user_id):
        user = UserModel(db.get_connection())
        abort_if_news_not_found(user_id, user)
        user.delete(user_id)
        return jsonify({'success': 'OK'})
    
    def put(self, user_id):
        user = UserModel(db.get_connection())
        abort_if_news_not_found(user_id, user)
        args = parser_put.parse_args()
        user.update(user_id, args['part'], args['text'])
        return jsonify({'success': 'OK'})


class UserList(Resource):
    def get(self):
        user = UserModel(db.get_connection()).get_all()
        return make_response(render_template("13.html", data=user, add=False))

    def post(self):
        form = RegistrationForm()
        user_name = form.username.data
        password = form.password.data
        exists = UserModel(db.get_connection()).exists(user_name, password)

        if exists[0]:
            return "Такой пользователь уже сущесвует"
        else:
            UserModel(db.get_connection()).insert(user_name, password)
            session['username'] = user_name
            session['user_id'] = UserModel(db.get_connection()).exists(user_name, password)[1]
            return redirect("/news")


if __name__ == '__main__':
    api.add_resource(NewsList, '/', '/news')
    api.add_resource(News, '/news/<int:news_id>')
    api.add_resource(UserList, '/users')
    api.add_resource(User, '/users/<int:user_id>')
    app.register_error_handler(404, not_found)
    app.run(port=8080, host='127.0.0.1')
