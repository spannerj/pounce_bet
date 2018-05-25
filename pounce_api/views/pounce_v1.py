from flask import Blueprint, Response, request, url_for
from pounce_api.extensions import db
from pounce_api.models import Pounce
from pounce_api.exceptions import ApplicationError
from flask_negotiate import consumes, produces
from datetime import datetime
# from jsonschema import validate, ValidationError, FormatChecker
import json

# This is the blueprint object that gets registered into the app in blueprints.py.
pounce_v1 = Blueprint('pounce_v1', __name__)

# JSON schema for pounce requests
# with open('pounce_api/swagger.json') as json_file:
#     swagger = json.load(json_file)

# pounce_schema = swagger["definitions"]["PounceRequest"]


# @pounce_v1.route("/pounces", methods=['GET'])
# @produces('application/json')
def getpounces():
    """Get Pounces."""
    print('get_pounces')
    results = Pounce.query.order_by(Pounce.id.desc()).paginate(per_page=10)
    pounces = []
    print('1')
    for pounce in results.items:
        pounces.append(pounce.as_dict())
    print('2')
    first = request.args.to_dict()
    first["page"] = 1

    if results.has_prev:
        prev_args = request.args.to_dict()
        prev_args["page"] = results.prev_num
        prev_url = url_for(request.endpoint, _external=True, **prev_args)
    else:
        prev_url = None

    if results.has_next:
        next_args = request.args.to_dict()
        next_args["page"] = results.next_num
        next_url = url_for(request.endpoint, _external=True, **next_args)
    else:
        next_url = None

    last = request.args.to_dict()
    last["page"] = results.pages

    links = {
        "first": url_for(request.endpoint, _external=True, **first),
        "prev": prev_url,
        "next": next_url,
        "last": url_for(request.endpoint, _external=True, **last)
    }

    if (results.page * results.per_page) > results.total:
        to = results.total
    else:
        to = (results.page * results.per_page)

    counts = {
        "total": results.total,
        "from": (results.page * results.per_page) - results.per_page + 1,
        "to": to
    }

    response = {
        "links": links,
        "counts": counts,
        "pounces": pounces
    }

    return json.dumps(response, separators=(',', ':'))
    # return Response(response=json.dumps(response, separators=(',', ':')),
    #                 mimetype='application/json',
    #                 status=200)


# @pounce_v1.route("/pounces", methods=['POST'])
# @consumes("application/json")
# @produces('application/json')
def create_pounce(pounce_request):
    """Create a new Pounce."""
    # pounce_request = request.json
    print(pounce_request)
    # Validate request against schema
    # try:
    #     validate(pounce_request, pounce_schema, format_checker=FormatChecker())
    # except ValidationError as e:
    #     raise ApplicationError(str(e), "E001", 400)

    # Create a new pounce
    placed = datetime.strptime(pounce_request["placed"], "%Y-%m-%d")

    pounce = Pounce(placed=placed,
                    rating=pounce_request["rating"],
                    bet=pounce_request["bet"],
                    sport=pounce_request["sport"],
                    pounced=pounce_request["pounced"],
                    profit=pounce_request["profit"])

    # Commit pounce to db
    db.session.add(pounce)
    db.session.commit()

    # Create new pounce response
    response = Response(response=repr(pounce),
                        mimetype='application/json',
                        status=201)

    # For newly created resources, always set the Location header to the GET request route of the new resource.
    response.headers["Location"] = "{0}/{1}".format(request.url, pounce.id)

    return response


@pounce_v1.route("/pounces/<int:pounce_id>", methods=['GET'])
@produces('application/json')
def get_pounce(pounce_id):
    """Get a Pounce for a given pounce_id."""
    pounce = Pounce.query.filter_by(id=str(pounce_id)).first()
    if not pounce:
        raise ApplicationError('Pounce not found', 'Exxx', 404)

    return Response(response=repr(pounce),
                    mimetype='application/json',
                    status=200)


@pounce_v1.route("/pounces/<int:pounce_id>", methods=['PUT'])
@consumes("application/json")
@produces('application/json')
def update_pounce(pounce_id):
    """Update a Pounce for a given pounce_id."""
    pounce_request = request.json

    # try:
    #     validate(pounce_request, pounce_schema, format_checker=FormatChecker())
    # except ValidationError as e:
    #     raise ApplicationError(str(e), "E001", 400)

    pounce = Pounce.query.filter_by(id=pounce_id).first()
    if not pounce:
        raise ApplicationError('Pounce not found', 'Exxx', 404)

    pounce.placed = pounce_request["placed"]
    pounce.rating = pounce_request["rating"]
    pounce.bet = pounce_request["bet"]
    pounce.sport = pounce_request["sport"]
    pounce.pounced = pounce_request["pounced"]
    pounce.profit = pounce_request["profit"]

    db.session.add(pounce)
    db.session.commit()

    return Response(response=repr(pounce),
                    mimetype='application/json',
                    status=200)


@pounce_v1.route("/pounces/<int:pounce_id>", methods=['DELETE'])
@produces('application/json')
def delete_pounce(pounce_id):
    """Delete a Pounce for a given pounce_id."""
    pounce = Pounce.query.filter_by(id=pounce_id).first()
    if not pounce:
        raise ApplicationError('Pounce not found', 'Exxx', 404)

    db.session.delete(pounce)
    db.session.commit()

    return Response(response=None,
                    mimetype='application/json',
                    status=204)
