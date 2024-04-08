from flask import Flask
from flask import make_response, render_template, jsonify, request
from data import db_session, trip_resource
from flask_restful import Api
from data.trip import Trip
from data.district import District
from data.des_settlements import DesSettlements
import sqlalchemy
from requests import get
from scripts.parser_news import get_news

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '12345678оченьнадежныйпароль'
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


@app.route('/')
def main():
    session = db_session.create_session()
    trips = session.execute(sqlalchemy.select(Trip.id, Trip.title, District.id, District.name, Trip.image).select_from(
        Trip).join(District, District.id == Trip.district).filter(Trip.fame == 'great'))
    news = get_news(count=6)

    params = {
        'title': 'Туристические маршруты по России',
        'recom_trips': trips,
        'news': news
    }
    return render_template('index.html', **params)


@app.route('/districts/<int:district_id>')
def districts(district_id):
    session = db_session.create_session()
    district = session.query(District).filter(District.id == district_id).first()
    id_trips = session.execute(sqlalchemy.select(District.trips).select_from(District).filter(District.id == district_id)).first()[0].split(', ')
    trips = []
    for id_trip in id_trips:
        trip = session.execute(sqlalchemy.select(Trip.id, Trip.title, Trip.description, District.id, Trip.image).select_from(Trip).join(District, District.id == Trip.district).filter(Trip.id == id_trip)).first()
        trips.append(trip)
    params = {
        'title': district.name,
        'district': district,
        'trips': trips
    }

    return render_template('district.html', **params)


@app.route('/districts/<int:district_id>/trips/<int:trip_id>')
def trips(district_id, trip_id):
    session = db_session.create_session()
    trip = get(f'http://localhost:8080/api/trip/{trip_id}').json()['trip']
    trip['settlements'] = trip['settlements'].split(', ')
    descriptions = []
    for ind_des in trip['des_settlements'].split(', '):
        description = session.execute(sqlalchemy.select(DesSettlements.description, DesSettlements.image).select_from(DesSettlements).filter(ind_des == DesSettlements.id)).first()
        descriptions.append(description)

    params = {
        'district_id': district_id,
        'title': trip['title'],
        'trip': trip,
        'descriptions': descriptions
    }
    return render_template('trip.html', **params)


@app.errorhandler(400)
def bad_request(_):
    return render_template('error.html', title='Ошибка')


@app.errorhandler(404)
def bad_request(_):
    return render_template('error.html', title='Ошибка')


if __name__ == '__main__':
    db_session.global_init('db/journey.db')
    api.add_resource(trip_resource.TripResource, '/api/trip/<int:trip_id>')
    api.add_resource(trip_resource.TripsListResources, '/api/trips')
    app.run(port=8080, host='127.0.0.1')
