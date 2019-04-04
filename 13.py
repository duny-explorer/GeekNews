import random

import post as post
from flask_restful import Api, Resource, reqparse
from flask import jsonify, make_response, render_template, request, session
from requests import delete, post
from werkzeug.utils import redirect
from DBManager import *
from forms import *
from flask_bootstrap import Bootstrap


api = Api(app)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PROPAGATE_EXCEPTIONS'] = True

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('text', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('theme', required=True)


class Error404(Exception):
    pass


@app.errorhandler(404)
def not_found(error):
    return make_response(render_template("error404.html"), 404)


@app.errorhandler(Error404)
def not_found(error):
    return make_response(render_template("error404.html"), 404)


def abort_if_not_found(data_base, item_id) :
    if not data_base.query.get(item_id):
        raise Error404


@app.route('/delete_news/<int:news_id>')
def delete_news(news_id):
    delete('http://localhost:8080/news/{}'.format(news_id))
    return redirect("/news")


@app.route('/add_news', methods=["GET", "POST"])
def add_news():
    form = AddNewsForm()
    if request.method == "GET":
        return render_template('add_news.html', form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            post("http://localhost:8080/news", json={"title": form.title.data,
                                                     "text": form.text.data,
                                                     "user_id": session["user_id"],
                                                     "theme": form.theme.data})

            return redirect("/news")

        return render_template('add_news.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "GET":
        return render_template('login.html', form=form)
    elif request.method == "POST":
        user_name = form.username.data
        password = form.password.data
        user = DBUsers.query.filter_by(username=user_name, password=password).first()

        if not (user is None):
            session['username'] = user_name
            session['user_id'] = user.id
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
        if form.validate_on_submit():
            return redirect('/users', code=307)
        return render_template('regestration.html', form=form)


class News(Resource):
    def get(self, news_id):
        abort_if_not_found(DBNews, news_id)
        form = AddComments()

        if 'username' not in session:
            return redirect('/login')

        return make_response(render_template("preview_news.html", news=DBNews.query.get(news_id), form=form,
                             comments=Comments.query.filter_by(news_id=news_id).all()))

    def delete(self, news_id):
        abort_if_not_found(DBNews, news_id)
        db.session.delete(DBNews.query.get(news_id))
        db.session.commit()
        return jsonify({'success': 'OK'})

    def post(self, news_id):
        abort_if_not_found(DBNews, news_id)
        form = AddComments()
        if form.validate_on_submit():
            user = DBUsers.query.get(session['user_id'])
            comment = Comments(text=form.text.data, news_id=news_id)

            user.News1.append(comment)

            db.session.commit()
            return make_response(render_template("preview_news.html", news=DBNews.query.get(news_id), form=form),
                                 comments=Comments.query.filter_by(news_id=news_id).all())

        return make_response(render_template("preview_news.html", news=DBNews.query.get(news_id), form=form),
                             comments=Comments.query.filter_by(news_id=news_id).all())


class NewsList(Resource):
    def get(self):
        if 'username' not in session:
            return redirect('/login')
        global news

        news = DBNews.query.all()
        science_news = random.choice(DBNews.query.filter_by(theme="Наука").all())
        game_news = random.choice(DBNews.query.filter_by(theme="Игры").all())
        technology_news = random.choice(DBNews.query.filter_by(theme="Технологии").all())
        return make_response(render_template("news.html", data=news, len=len(news), science_news=science_news.id,
                             game_news=game_news.id, technology_news=technology_news.id))

    def post(self):
        args = parser.parse_args()
        user = DBUsers.query.get(args["user_id"])
        user.News.append(DBNews(
                title=args["title"],
                text=args["text"],
                theme=args["theme"]
            ))

        db.session.commit()
        return True


class User(Resource):
    def get(self, user_id):
        user = DBUsers.query.get(user_id)
        return make_response(render_template("preview_users.html", user=user))

    def delete(self, user_id):
        DBUsers.query.get(user_id).delete()
        db.session.commit()
        return jsonify({'success': 'OK'})


class UserList(Resource):
    def get(self):
        return make_response(render_template("users.html", data=DBUsers.query.all()))

    def post(self):
        form = RegistrationForm()
        username = form.username.data
        db.session.add(DBUsers(
                username=username,
                password=form.password.data,
                name=form.name.data,
                email=form.email.data,
                surname=form.surname.data,
        ))

        db.session.commit()
        session["username"] = username
        session["user_id"] = DBUsers.query.filter_by(username=username).first().id

        return redirect("/news")


if __name__ == '__main__':
    api.add_resource(NewsList, '/', '/news')
    api.add_resource(News, '/news/<int:news_id>')
    api.add_resource(UserList, '/users')
    api.add_resource(User, '/users/<int:user_id>')
    app.register_error_handler(404, not_found)
    app.run(port=8080, host='127.0.0.1')
