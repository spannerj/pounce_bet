from flask import Blueprint, Response, request, url_for
from pounce_api.extensions import db
from pounce_api.models import Pounce
from pounce_api.exceptions import ApplicationError
from datetime import datetime
from pprint import pprint
# from jsonschema import validate, ValidationError, FormatChecker
import json
from collections import OrderedDict
from sqlalchemy import func, case, between

# This is the blueprint object that gets registered into the app in blueprints.py.
pounce_v1 = Blueprint('pounce_v1', __name__)


def get_data(pounced=None, sport=None):

    queries = []

    if pounced is not None:
        queries.append(Pounce.pounced == True)

    if sport is not None:
        queries.append(Pounce.sport == sport)

    pounced_profit_total = 0
    pounced_results = OrderedDict()

    mon = func.date_trunc('month', Pounce.placed)
    yea = func.date_trunc('year', Pounce.placed)

    db_results = db.session.query(mon, func.sum(Pounce.profit)) \
        .filter(*queries) \
        .group_by(yea, mon) \
        .order_by(yea, mon) \
        .all()

    for result in db_results:

        profit = '0'

        if result[1] is not None:
            profit = str(round(result[1], 2))

        if result[0].strftime("%Y") in pounced_results:
            pounced_results[result[0].strftime("%Y")][result[0].strftime("%B")] = format_profit(profit)
        else:
            pounced_results[result[0].strftime("%Y")] = OrderedDict()
            pounced_results[result[0].strftime("%Y")][result[0].strftime("%B")] = format_profit(profit)

        pounced_profit_total = pounced_profit_total + float(profit)

    pounced_results['total'] = format_profit(pounced_profit_total)

    return pounced_results


def get_ratings(sport=None):

    ratings_dict = OrderedDict()
    queries = []

    if sport is not None:
        queries.append(Pounce.sport == sport)

    rate1 = func.sum(case([(between(Pounce.rating, 0, 39), Pounce.profit), ], else_=0))
    rate2 = func.sum(case([(between(Pounce.rating, 40, 59), Pounce.profit), ], else_=0)).label("r2")
    rate3 = func.sum(case([(between(Pounce.rating, 60, 79), Pounce.profit), ], else_=0)).label("r3")
    rate4 = func.sum(case([(between(Pounce.rating, 80, 99), Pounce.profit), ], else_=0)).label("r4")
    rating_results = db.session.query(rate1, rate2, rate3, rate4).filter(*queries).all()

    # print(rating_results)
    for i, result in enumerate(rating_results[0]):
        rating_profit = str(round(result, 2))
        if i == 0:
            ratings_dict['0-39'] = format_profit(rating_profit)
        elif i == 1:
            ratings_dict['40-59'] = format_profit(rating_profit)
        elif i == 2:
            ratings_dict['60-79'] = format_profit(rating_profit)
        else:
            ratings_dict['80-99'] = format_profit(rating_profit)

    return ratings_dict


def format_profit(profit):
    return ("£" + '%0.2f' % float(profit)).replace('£-', '-£')


def build_dict(sport=None):
    result_dict = {}
    result_dict['all'] = get_data(sport=sport)
    result_dict['pounced'] = get_data(pounced=True, sport=sport)
    result_dict['rating'] = get_ratings(sport=sport)
    return result_dict


def get_reports():

    reports = {}
    reports['totals'] = build_dict()
    reports['tennis'] = build_dict('Tennis')
    reports['football'] = build_dict('Football')

    # pprint(reports)

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
