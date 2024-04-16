import datetime
import os
from dotenv import load_dotenv
from requests import get

from flask import Flask, request
from flask import render_template, redirect

from flask_login import LoginManager, login_required, logout_user, current_user, login_user

from flask_restful import Api
from sqlalchemy import case

from data import db_session, trip_resource
from data.reviews import Reviews
from data.trip import Trip
from data.district import District
from data.users import Users
from data.des_settlements import DesSettlements

import sqlalchemy

from scripts.parser_news import get_news

from forms.register_form import RegisterForm
from forms.login_form import LoginForm


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
        'news': news
    }
    return render_template('index.html', **params)


@app.route('/districts/<int:district_id>')
def districts(district_id):
    session = db_session.create_session()
    district = session.query(District).filter(District.id == district_id).first()
    id_trips = session.execute(
        sqlalchemy.select(District.trips).select_from(District).filter(District.id == district_id)
    ).first()[0].split(', ')

    list_trips = []
    for id_trip in id_trips:
        trip = session.execute(
            sqlalchemy.select(
                Trip.id, Trip.title, Trip.description, District.id, Trip.image, Trip.fame
            ).select_from(Trip).join(District, District.id == Trip.district).filter(Trip.id == id_trip)
        ).first()
        data_trips = {
            'id': trip[0],
            'title': trip[1],
            'description': trip[2],
            'district_id': trip[3],
            'image': trip[4],
            'fame': trip[5]
        }
        list_trips.append(data_trips)
    params = {
        'title': district.name,
        'district': district,
        'trips': list_trips
    }

    return render_template('district.html', **params)


@app.route('/districts/<int:district_id>/trips/<int:trip_id>', methods=['GET', 'POST'])
def trips(district_id, trip_id):
    if request.method == 'GET':
        session = db_session.create_session()
        trip = get(f'http://localhost:8080/api/trip/{trip_id}').json()['trip']
        trip['settlements'] = trip['settlements'].split(', ')
        descriptions = []
        for ind_des in trip['des_settlements'].split(', '):
            description = session.execute(
                sqlalchemy.select(
                    DesSettlements.description, DesSettlements.image
                ).select_from(DesSettlements).filter(ind_des == DesSettlements.id)
            ).first()
            descriptions.append(description)

        district = session.execute(
            sqlalchemy.select(District.id, District.name).select_from(District).filter(District.id == district_id)
        ).first()
        reviews_list = session.execute(
            sqlalchemy.select(
                Reviews.text, Reviews.title, Reviews.like, Reviews.date, Users.name, Users.surname, Users.id
            ).select_from(Reviews).join(Users, Reviews.user_id == Users.id).filter(Reviews.trip_id == Trip.id).order_by(
                Reviews.date
            )
        ).all()
        dict_reviews = []
        for review in reviews_list[::-1]:
            delta = datetime.datetime.now() - review[3]
            days = delta.days

            if days <= 30:
                if days == 0:
                    date = 'Сегодня'
                elif days % 10 == 1:
                    date = f'{days} день назад'
                elif days % 10 < 5:
                    date = f'{days} дня назад'
                else:
                    date = f'{days} дней назад'
            elif days < 365:
                months = days // 30
                if months == 1:
                    date = '1 месяц назад'
                elif months < 5:
                    date = f'{months} месяца назад'
                else:
                    date = f'{months} месяцев назад'
            else:
                date = 'Более года назад'
            data = {
                'text': review[0],
                'title': review[1],
                'user_name': review[4] + ' ' + review[5],
                'user_id': review[6],
                'date': date,
                'like': review[2]
            }
            dict_reviews.append(data)

        params = {
            'district': district,
            'title': trip['title'],
            'trip': trip,
            'reviews': dict_reviews,
            'descriptions': descriptions
        }
        return render_template('trip.html', **params)
    else:
        session = db_session.create_session()
        dataGet = request.get_json(force=True)

        date = datetime.datetime.strptime(dataGet['date'], '%Y-%m-%d %H:%M:%S')

        review = Reviews(
            title=dataGet['title'],
            text=dataGet['text'],
            trip_id=trip_id,
            user_id=current_user.id,
            date=date,
            like=dataGet['button']
        )

        session.add(review)
        session.commit()
        return redirect(f'/districts/{district_id}/trips/{trip_id}')


@app.route('/districts/<int:district_id>/trips/<int:trip_id>/reviews/')
def reviews(district_id, trip_id):
    session = db_session.create_session()
    district_name = session.query(District.name).filter(District.id == district_id).first()[0]
    trip_title = session.query(Trip.title).filter(Trip.id == trip_id).first()[0]
    reviews_list = session.execute(
        sqlalchemy.select(
            Reviews.text, Reviews.title, Reviews.like, Reviews.date, Users.name, Users.surname, Users.id
        ).select_from(Reviews).join(Users, Reviews.user_id == Users.id).filter(Reviews.trip_id == Trip.id).order_by(
            Reviews.date
        )
    ).all()
    dict_reviews = []
    for review in reviews_list[::-1]:
        delta = datetime.datetime.now() - review[3]
        days = delta.days

        if days <= 30:
            if days == 0:
                date = 'Сегодня'
            elif days % 10 == 1:
                date = f'{days} день назад'
            elif days % 10 < 5:
                date = f'{days} дня назад'
            else:
                date = f'{days} дней назад'
        elif days < 365:
            months = days // 30
            if months == 1:
                date = '1 месяц назад'
            elif months < 5:
                date = f'{months} месяца назад'
            else:
                date = f'{months} месяцев назад'
        else:
            date = 'Более года назад'
        data = {
            'text': review[0],
            'title': review[1],
            'user_name': review[4] + ' ' + review[5],
            'user_id': review[6],
            'date': date,
            'like': review[2]
        }
        dict_reviews.append(data)

    params = {
        'district_id': district_id,
        'trip_id': trip_id,
        'title': 'Отзывы, ' + trip_title + ', ' + district_name,
        'district_name': district_name,
        'trip_title': trip_title,
        'reviews': dict_reviews
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
            return redirect("/")
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


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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
    api.add_resource(trip_resource.TripsListResources, '/api/trips')
    app.run(port=8080, host='127.0.0.1')


# DISTRICTS = {
#     'siberia': 'Сибирь',
#     'far_east': 'Дальний Восток',
#     'urals': 'Урал',
#     'volga_region': 'Приволжье',
#     'northwest': 'Северо-Запад',
#     'center': 'Центральная Россия',
#     'caucasus': 'Кавказ',
#     'south': 'Юг'
# }

# def send_confirmation_email(email):
#     # Уникальный код
#     confirmation_code = ''.join(random.choices([str(i) for i in range(10)], k=6))
#     app_password = 'ngbm icyj phop jjlj'
#     smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
#     smtpserver.ehlo()
#     smtpserver.login("alexandersivkov228@gmail.com", app_password)
#     from_mail = "alexandersivkov228@gmail.com"
#     text = f'Code: {confirmation_code}'
#     smtpserver.sendmail(from_mail, email, text)
#     smtpserver.close()
#
#     return confirmation_code