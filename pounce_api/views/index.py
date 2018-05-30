from flask import Blueprint, request, redirect, url_for, render_template
import json
from pounce_api.views.pounce_v1 import getpounces, create_pounce, get_pounce, update_pounce, delete_pounce

# This is the blueprint object that gets registered into the app in blueprints.py.
index = Blueprint('index', __name__)


@index.route("/", methods=['GET'])
def index_page():
    args = request.args.to_dict()

    if 'page' in args:
        page = '?page=' + args['page']
        curr_page = args['page']
    else:
        curr_page = '1'
        page = ''

    response = getpounces()

    pounces = json.loads(response)

    if pounces['links']['prev'] is None:
        prev = None
    else:
        prev = pounces['links']['prev'].replace("v1/pounces", "")

    if pounces['links']['next'] is None:
        next = None
    else:
        next = pounces['links']['next'].replace("v1/pounces", "")

    first = pounces['links']['first'].replace("v1/pounces", "")
    last = pounces['links']['last'].replace("v1/pounces", "")

    return render_template('index.html', **locals())


@index.route("/add-pounce", methods=['GET', 'POST'])
def new_pounce():
    if request.method == 'GET':
        return render_template('add_pounce.html')
    else:
        fd = request.form.to_dict()

        create_pounce(fd)
        return redirect(url_for('index.index_page'))


@index.route("/edit-pounce", methods=['GET', 'POST'])
def edit_pounce():
    args = request.args.to_dict()

    if request.method == 'GET':
        pounce = get_pounce(args['id'])
        return render_template('edit_pounce.html', pounce=pounce)
    else:
        fd = request.form.to_dict()
        fd['id'] = args['id']
        update_pounce(fd)
        return redirect(url_for('index.index_page'))


@index.route('/delete-pounce', methods=['POST'])
def remove_pounce():
    args = request.form.to_dict()

    delete_pounce(args['id'])
    return redirect(url_for('index.index_page'))
