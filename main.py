from flask import Flask
from flask import make_response, render_template, jsonify, request
from data import db_session, trip_resource
from flask_restful import Api
from data.trip import Trip
from data.district import District
import sqlalchemy
from requests import get

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '12345678оченьнадежныйпароль'
DISTRICTS = {
    'siberia': 'Сибирь',
    'far_east': 'Дальний Восток',
    'urals': 'Урал',
    'volga_region': 'Приволжье',
    'northwest': 'Северо-Запад',
    'center': 'Центральная Россия',
    'caucasus': 'Кавказ',
    'south': 'Юг'
}


@app.route('/')
def main():
    session = db_session.create_session()
    trips = session.execute(sqlalchemy.select(Trip.id, Trip.title, District.name, Trip.image).select_from(
        Trip).join(District, District.id == Trip.district).filter(Trip.fame == 'great'))

    params = {
        'title': 'Туристические маршруты по России',
        'recom_trips': trips
    }
    return render_template('main_window.html', **params)


@app.route('/districts/<string:name>')
def districts(name):
    session = db_session.create_session()
    district = session.query(District).filter(District.name == DISTRICTS[name]).first()
    id_trips = session.execute(sqlalchemy.select(District.trips).select_from(District).filter(District.name == DISTRICTS[name])).first()[0].split(', ')
    trips = []
    for id_trip in id_trips:
        trip = session.execute(sqlalchemy.select(Trip.id, Trip.title, Trip.description, District.name, Trip.image).select_from(Trip).join(District, District.id == Trip.district).filter(Trip.id == id_trip)).first()
        trips.append(trip)

    params = {
        'title': DISTRICTS[name],
        'district': district,
        'trips': trips
    }

    return render_template('district.html', **params)


@app.route('/districts/<string:district_name>/trips/<int:trip_id>')
def trips(district_name, trip_id):
    trip = get(f'http://localhost:8080/api/trip/{trip_id}').json()['trip']
    print(trip)
    params = {
        'title': trip['title'],
        'trip': trip
    }
    return render_template('trip.html', **params)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    db_session.global_init('db/journey.db')
    api.add_resource(trip_resource.TripResource, '/api/trip/<int:trip_id>')
    api.add_resource(trip_resource.TripsListResources, '/api/trips')
    app.run(port=8080, host='127.0.0.1')
