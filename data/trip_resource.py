from . import db_session
from .trip import Trip
from flask_restful import abort, Resource, reqparse
from flask import jsonify
from .trip_pars import parser


def abort_if_trip_not_found(trip_id):
    session = db_session.create_session()
    trip = session.query(Trip).get(trip_id)
    if not trip:
        abort(404, message=f"Trip {trip_id} not found")


class TripResource(Resource):
    def get(self, trip_id):
        abort_if_trip_not_found(trip_id)
        session = db_session.create_session()
        trip = session.query(Trip).get(trip_id)
        return jsonify({'trip':
                            trip.to_dict(only=('title', 'region', 'description', 'image'))})

    def delete(self, trip_id):
        abort_if_trip_not_found(trip_id)
        session = db_session.create_session()
        trip = session.query(Trip).get(trip_id)
        session.delete(trip)
        session.commit()
        return jsonify({'success': 'OK'})


class TripsListResources(Resource):
    def get(self):
        session = db_session.create_session()
        trips = session.query(Trip).all()
        return jsonify({'trips': [item.to_dict(
            only=('id', 'title', 'region')) for item in trips]})

    def post(self):
        args = parser.args()
        session = db_session.create_session()
        trip = Trip(
            title=args['title'],
            region=args['region'],
            description=args['description'],
            image=args['image']
        )
        session.add(trip)
        session.commit()
        return jsonify({'id': trip.id})
