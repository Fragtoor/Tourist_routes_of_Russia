from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('district', required=True)
parser.add_argument('settlements', required=True)
parser.add_argument('fame', required=True)
parser.add_argument('route', required=True)
parser.add_argument('des_settlements', required=True)
parser.add_argument('description', required=True)
parser.add_argument('image', required=True)
