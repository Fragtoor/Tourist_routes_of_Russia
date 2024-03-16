from flask import Flask
from flask import make_response, render_template, jsonify
from data import db_session, trip_resource
from flask_restful import Api
from requests import get

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '12345678оченьнадежныйпароль'


@app.route('/')
def main():
    trips = get('http://localhost:8080/api/trips').json()['trips']

    params = {
        'title': 'Туристические маршруты по России',
        'trips': trips
    }
    return render_template('main_window.html', **params)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    db_session.global_init('db/trip.db')

    api.add_resource(trip_resource.TripResource, '/api/trip/<int:trip_id>')
    api.add_resource(trip_resource.TripsListResources, '/api/trips')
    app.run(port=8080, host='127.0.0.1')
