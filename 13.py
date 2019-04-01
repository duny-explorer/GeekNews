from flask_restful import reqparse, Api, Resource
from flask import Flask, jsonify, make_response, render_template, request, session
from requests import delete
from werkzeug.utils import redirect
from DBManager import *
from forms import *


api = Api(app)
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
        print(form.errors, form)
        if form.validate_on_submit():
            return redirect('/users', code=307)
        return render_template('regestration.html', form=form)


class News(Resource):
    def get(self, news_id):
        if 'username' not in session:
            return redirect('/login')
        return make_response(render_template("preview_news.html", news=DBNews.query.get(news_id)))

    def delete(self, news_id):
        db.session.delete(DBNews.query.get(news_id))
        db.session.commit()
        return jsonify({'success': 'OK'})


class NewsList(Resource):
    def get(self):
        if 'username' not in session:
            return redirect('/login')
        global news

        news = DBNews.query.all()
        form = AddNewsForm()
        return make_response(render_template("news.html", data=news, form=form, add=True, len=len(news)))

    def post(self):
        form = AddNewsForm()

        if form.validate_on_submit():
            user = DBUsers.query.get(session['user_id'])
            user.News.append(DBNews(
                title=form.title.data,
                text=form.text.data,
            ))

            db.session.commit()
            return redirect("/news")

        return make_response(render_template("news.html", data=news, form=form, add=True, len=len(news)))


class User(Resource):
    def get(self, user_id):
        user = DBUsers.query.get(user_id)
        return jsonify({'users': user})

    def delete(self, user_id):
        DBUsers.query.get(user_id).delete()
        db.session.commit()
        return jsonify({'success': 'OK'})


class UserList(Resource):
    def get(self):
        return make_response(render_template("news.html", data=DBUsers.query.all(), add=False))

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
