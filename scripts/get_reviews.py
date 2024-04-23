from data import db_session
from data.reviews import Reviews
from data.users import Users

import datetime


def get_reviews(trip_id, sort=None, user=None):
    session = db_session.create_session()

    if sort is None:
        reviews_list = session.query(
            Reviews.id, Reviews.text, Reviews.title, Reviews.date, Reviews.like, Users.name, Users.surname, Reviews.user_id
        ).join(Users).filter(Reviews.trip_id == trip_id).all()
    elif sort == 'up_date':
        reviews_list = session.query(
            Reviews.id, Reviews.text, Reviews.title, Reviews.date, Reviews.like, Users.name, Users.surname, Reviews.user_id
        ).join(Users).order_by(Reviews.date).filter(Reviews.trip_id == trip_id).all()
    elif sort == 'down_date':
        reviews_list = session.query(
            Reviews.id, Reviews.text, Reviews.title, Reviews.date, Reviews.like, Users.name, Users.surname, Reviews.user_id
        ).join(Users).order_by(Reviews.date).filter(Reviews.trip_id == trip_id).all()[::-1]
    else:
        reviews_list = session.query(
            Reviews.id, Reviews.text, Reviews.title, Reviews.date, Reviews.like, Users.name, Users.surname, Reviews.user_id
        ).join(Users).order_by(Reviews.date).filter(Reviews.trip_id == trip_id, Reviews.user_id == user.id).all()

    for ind, review in enumerate(reviews_list):
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
        review = {
            'id': review[0],
            'text': review[1],
            'title': review[2],
            'date': date,
            'like': review[4],
            'user_name': review[5] + ' ' + review[6],
            'user_id': review[7]
        }

        reviews_list[ind] = review

    return reviews_list
