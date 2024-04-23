import datetime
import os
from dotenv import load_dotenv
from requests import get, delete

from flask import Flask, request, session
from flask import render_template, redirect

from flask_login import LoginManager, login_required, logout_user, current_user, login_user

from flask_restful import Api

from data import db_session, trip_resource, review_resource
from data.reviews import Reviews
from data.trip import Trip
from data.district import District
from data.users import Users
from data.des_settlements import DesSettlements

import sqlalchemy

from scripts.parser_news import get_news
from scripts.get_reviews import get_reviews
from scripts.validate_password import validate_on_password

from forms.register_form import RegisterForm
from forms.login_form import LoginForm

from waitress import serve

app = Flask(__name__)
api = Api(app)

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main():
    session = db_session.create_session()
    trips = session.execute(sqlalchemy.select(Trip.id, Trip.title, District.id, District.name, Trip.image).select_from(
        Trip).join(District, District.id == Trip.district).filter(Trip.fame == 'great'))
    dict_trips = []
    for trip in trips:
        dict_trip = {
            'id': trip[0],
            'title': trip[1],
            'district_id': trip[2],
            'district_name': trip[3],
            'image': trip[4]
        }
        dict_trips.append(dict_trip)

    news = get_news(count=6)
    params = {
        'title': 'Туристические маршруты по России',
        'recom_trips': dict_trips,
        'news': news,
    }
    return render_template('index.html', **params)


@app.route('/districts/<int:district_id>', methods=['GET', 'POST'])
def districts(district_id):
    if request.method == 'GET':
        session = db_session.create_session()
        district = session.query(District).filter(District.id == district_id).first()
        list_trips = get(f'http://localhost:8080/api/trips/{district_id}').json()['trips']
        params = {
            'title': district.name,
            'district': district,
            'trips': list_trips,
        }

        return render_template('district.html', **params)
    elif request.method == 'POST':
        search_trip = request.form.get('search_trip')
        session = db_session.create_session()
        list_trips = session.query(Trip).filter(Trip.title.like(f'%{search_trip.strip()}%')).all()
        district = session.query(District).filter(District.id == district_id).first()
        params = {
            'title': district.name,
            'district': district,
            'trips': list_trips,
            'search_trip': search_trip
        }

        return render_template('district.html', **params)


@app.route('/districts/<int:district_id>/trips/<int:trip_id>', methods=['GET', 'POST', 'DELETE'])
def trips(district_id, trip_id):
    if request.method == 'GET':
        session = db_session.create_session()
        trip = get(f'http://localhost:8080/api/trip/{trip_id}').json()['trip']
        trip['settlements'] = trip['settlements'].split(', ')
        trip['des_settlements'] = trip['des_settlements'].split(', ')
        descriptions = []
        for ind_des in trip['des_settlements']:
            description = session.execute(
                sqlalchemy.select(
                    DesSettlements.description, DesSettlements.image
                ).select_from(DesSettlements).filter(ind_des == DesSettlements.id)
            ).first()
            descriptions.append(description)

        district = session.query(District).get(district_id)
        reviews_list = get_reviews(trip_id)

        params = {
            'district': district,
            'title': trip['title'],
            'trip': trip,
            'reviews': reviews_list,
            'descriptions': descriptions,
        }
        return render_template('trip.html', **params)
    elif request.method == 'POST':
        session = db_session.create_session()
        data_get = request.get_json(force=True)

        date = datetime.datetime.strptime(data_get['date'], '%Y-%m-%d %H:%M:%S')

        review = Reviews(
            title=data_get['title'],
            text=data_get['text'],
            trip_id=trip_id,
            user_id=current_user.id,
            date=date,
            like=data_get['button']
        )

        session.add(review)
        session.commit()
        return redirect(f'/districts/{district_id}/trips/{trip_id}')
    elif request.method == 'DELETE':
        data_get = request.get_json(force=True)
        delete(f'http://localhost:8080/api/review/{data_get["id"]}')
        return redirect('/')


@app.route('/districts/<int:district_id>/trips/<int:trip_id>/reviews/', methods=['GET', 'POST'])
def reviews(district_id, trip_id):
    if request.method == 'GET':
        session = db_session.create_session()
        district_name = session.query(District.name).filter(District.id == district_id).first()[0]
        trip_title = session.query(Trip.title).filter(Trip.id == trip_id).first()[0]
        reviews_list = get_reviews(trip_id)

        params = {
            'district_id': district_id,
            'trip_id': trip_id,
            'title': 'Отзывы, ' + trip_title + ', ' + district_name,
            'district_name': district_name,
            'trip_title': trip_title,
            'reviews': reviews_list,
        }
        return render_template('reviews.html', **params)
    elif request.method == 'POST':
        selected_value = request.args.get('selectedValue')
        session = db_session.create_session()
        district_name = session.query(District.name).filter(District.id == district_id).first()[0]
        trip_title = session.query(Trip.title).filter(Trip.id == trip_id).first()[0]
        if selected_value == 'up_date':
            reviews_list = get_reviews(trip_id, 'up_date')
        elif selected_value == 'down_date':
            reviews_list = get_reviews(trip_id, 'down_date')
        elif selected_value == 'your_reviews':
            reviews_list = get_reviews(trip_id, 'your_reviews', current_user)
        else:
            reviews_list = get_reviews(trip_id)

        params = {
            'district_id': district_id,
            'trip_id': trip_id,
            'title': 'Отзывы, ' + trip_title + ', ' + district_name,
            'district_name': district_name,
            'trip_title': trip_title,
            'reviews': reviews_list,
        }
        return render_template('reviews.html', **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # Перенаправление на предыдущую страницу
            if 'previous_url' in session:
                previous_url = session['previous_url']
                session.pop('previous_url', None)
                return redirect(previous_url)
            return redirect('/')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")

        validate = validate_on_password(form.password.data)
        if validate['message'] != 'OK':
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message=validate['message'])

        session = db_session.create_session()
        user = Users(
            name=form.name.data,
            surname=form.surname.data,
            login=form.login.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)


@app.before_request
def before_request():
    if request.endpoint not in ('login', 'logout', 'static', 'register'):
        session['previous_url'] = request.path


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # Перенаправление на предыдущую страницу
    if 'previous_url' in session:
        previous_url = session['previous_url']
        session.pop('previous_url', None)
        return redirect(previous_url)
    return redirect('/')


@app.errorhandler(400)
def bad_request(_):
    return render_template('error.html', message="Похоже какие-то неполадки", title='Ошибка')


@app.errorhandler(404)
def bad_request(_):
    return render_template('error.html', message="Страница не найдена", title='Ошибка')


@app.errorhandler(500)
def bad_request(_):
    return render_template('error.html', message="Мы уже работаем над проблемой", title='Ошибка')


if __name__ == '__main__':
    db_session.global_init('db/journey.db')
    api.add_resource(trip_resource.TripResource, '/api/trip/<int:trip_id>')
    api.add_resource(review_resource.ReviewResource, '/api/review/<int:review_id>')
    api.add_resource(trip_resource.TripsListResources, '/api/trips/<int:district_id>')
    serve(app, host='127.0.0.1', port=8080)
