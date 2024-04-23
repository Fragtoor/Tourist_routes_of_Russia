from . import db_session
from .reviews import Reviews
from flask_restful import abort, Resource, reqparse
from flask import jsonify


def abort_if_review_not_found(review_id):
    session = db_session.create_session()
    review = session.query(Reviews).get(review_id)
    if not review:
        abort(404, message=f"Review {review_id} not found")


class ReviewResource(Resource):
    def get(self, review_id):
        abort_if_review_not_found(review_id)
        session = db_session.create_session()
        review = session.query(Reviews).get(review_id)
        return jsonify(
            {'review': review.to_dict(only=('id', 'text', 'title', 'date', 'like', 'trip_id', 'user_id'))})

    def delete(self, review_id):
        abort_if_review_not_found(review_id)
        session = db_session.create_session()
        review = session.query(Reviews).get(review_id)
        session.delete(review)
        session.commit()
        return jsonify({'success': 'OK'})
