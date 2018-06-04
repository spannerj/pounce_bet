from flask import Blueprint, Response, request, url_for
from pounce_api.extensions import db
from pounce_api.models import Pounce
from pounce_api.exceptions import ApplicationError
from datetime import datetime
# from jsonschema import validate, ValidationError, FormatChecker
import json

from sqlalchemy import func
from sqlalchemy.sql import label

# This is the blueprint object that gets registered into the app in blueprints.py.
pounce_v1 = Blueprint('pounce_v1', __name__)


def get_reports():
    # results = Pounce.query.filter_by(func.sum(Pounce.profit)).all()
    mon = func.date_trunc('month', Pounce.placed)
    yea = func.date_trunc('year', Pounce.placed)

    all_results = db.session.query(mon, func.sum(Pounce.profit)) \
                               .group_by(yea, mon) \
                               .order_by(yea, mon) \
                               .all()

    my_results = db.session.query(mon, func.sum(Pounce.profit)) \
                               .filter(Pounce.pounced==True) \
                               .group_by(yea, mon) \
                               .order_by(yea, mon) \
                               .all()


    # results = db.session.query.filter_by(Pounce.rating>60)
    # q = db.session.query(Pounce).filter(Pounce.rating>60).first()
    # results = q.query(func.sum(Pounce.profit)).all()


    # queries = [Pounce.rating > 60]
    # queries.append(Pounce.sport=="Tennis")

    # results = db.session.query(
    #     func.sum(Pounce.profit)
    # ).filter(
    #     *queries
    #     # Pounce.rating>60
    # ).scalar()
    reports = {}
    reports['all'] = {}
    reports['mine'] = {}
    all_profit_total = 0
    my_profit_total = 0

    for result in all_results:
        if result[0].strftime("%Y") in reports['all']:
            reports['all'][result[0].strftime("%Y")][result[0].strftime("%B")] = str(round(result[1], 2))
        else:
            reports['all'][result[0].strftime("%Y")] = {}
            reports['all'][result[0].strftime("%Y")][result[0].strftime("%B")] = str(round(result[1], 2))
        all_profit_total = all_profit_total + result[1]

    reports['all']['total'] = str(round(all_profit_total, 2))

    for result in my_results:
        if result[0].strftime("%Y") in reports['mine']:
            reports['mine'][result[0].strftime("%Y")][result[0].strftime("%B")] = str(round(result[1], 2))
        else:
            reports['mine'][result[0].strftime("%Y")] = {}
            reports['mine'][result[0].strftime("%Y")][result[0].strftime("%B")] = str(round(result[1], 2))
        my_profit_total = my_profit_total + result[1]

    reports['mine']['total'] = str(round(my_profit_total, 2))

    return reports


def getpounces():
    """Get Pounces."""
    results = Pounce.query.order_by(Pounce.placed.desc()).paginate(per_page=10)
    pounces = []

    for pounce in results.items:
        pounces.append(pounce.as_dict())

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


def create_pounce(pounce_request):
    """Create a new Pounce."""

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


def get_pounce(pounce_id):
    """Get a Pounce for a given pounce_id."""
    pounce = Pounce.query.filter_by(id=str(pounce_id)).first()
    if not pounce:
        raise ApplicationError('Pounce not found', 'Exxx', 404)

    return pounce


def update_pounce(updated_pounce):
    """Update a Pounce for a given pounce_id."""

    pounce = Pounce.query.filter_by(id=updated_pounce['id']).first()
    if not pounce:
        raise ApplicationError('Pounce not found', 'Exxx', 404)

    pounce.placed = updated_pounce["placed"]
    pounce.rating = updated_pounce["rating"]
    pounce.bet = updated_pounce["bet"]
    pounce.sport = updated_pounce["sport"]
    pounce.pounced = updated_pounce["pounced"] == "True"
    pounce.profit = updated_pounce["profit"]

    db.session.add(pounce)
    db.session.commit()

    return pounce


def delete_pounce(pounce_id):
    """Delete a Pounce for a given pounce_id."""
    pounce = Pounce.query.filter_by(id=pounce_id).first()
    if not pounce:
        raise ApplicationError('Pounce not found', 'Exxx', 404)

    db.session.delete(pounce)
    db.session.commit()

    return None
