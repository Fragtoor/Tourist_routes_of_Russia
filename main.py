from flask import Flask, render_template
from data import db_session, trip_resource
from flask_restful import Api


app = Flask(__name__)
api = Api(app)


@app.route('/')
def main():
    return render_template('main_window.html', title='Туристические маршруты по России')


if __name__ == '__main__':
    db_session.global_init('db/trip.db')
    app.run(port=8080, host='127.0.0.1')
    api.add_resource(trip_resource.TripResource, '/api/trip/trip_id')
