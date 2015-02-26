import json, requests
from datetime import datetime
from flask import Blueprint, render_template, flash, request, redirect, url_for, Response, current_app
from flask.ext.login import login_user, logout_user, login_required

from memex import cache
from memex.forms import LoginForm
from memex.models import User

main = Blueprint('main', __name__)


@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('facetview.html',
                           title='MEMEX FacetView',
                           current_year=datetime.now().year)


@main.route('/ceos_gcmd')
@cache.cached(timeout=1000)
def home_ceos_gcmd():
    return render_template('facetview-ceos_gcmd.html',
                           title='CEOS-GCMD Instruments FacetView',
                           current_year=datetime.now().year)


@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # For demonstration purposes the password in stored insecurely
        user = User.query.filter_by(username=form.username.data,
                                    password=form.password.data).first()

        if user:
            login_user(user)

            flash("Logged in successfully.", "success")
            return redirect(request.args.get("next") or url_for(".home"))
        else:
            flash("Login failed.", "danger")

    return render_template("login.html", form=form)


@main.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for(".home"))


@main.route("/restricted")
@login_required
def restricted():
    return "You can only see this if you are logged in!", 200


@main.route("/query", methods=['GET'])
def query():
    # get callback, source
    callback = request.args.get('callback')
    source = request.args.get('source')

    # query
    es_url = current_app.config['ELASTICSEARCH_URL']
    es_index = current_app.config['MEMEX_ELASTICSEARCH_INDEX']
    #current_app.logger.debug("ES query for query(): %s" % json.dumps(json.loads(source), indent=2))
    r = requests.post('%s/%s/_search' % (es_url, es_index), data=source.encode('utf-8'))
    result = r.json()
    if r.status_code != 200:
        current_app.logger.debug("Failed to query ES. Got status code %d:\n%s" %
                                 (r.status_code, json.dumps(result, indent=2)))
    r.raise_for_status()
    #current_app.logger.debug("result: %s" % pformat(r.json()))

    # return only one url
    for hit in result['hits']['hits']:
        # emulate result format from ElasticSearch <1.0
        #current_app.logger.debug("hit: %s" % pformat(hit))
        if '_source' in hit: hit.setdefault('fields', {}).update(hit['_source'])
        hit['fields']['_type'] = hit['_type']

    # return JSONP
    return Response('%s(%s)' % (callback, json.dumps(result)),
                    mimetype="application/javascript")


@main.route("/query_ceos_gcmd", methods=['GET'])
def query_ceos_gcmd():
    # get callback, source
    callback = request.args.get('callback')
    source = request.args.get('source')

    # query
    es_url = current_app.config['ELASTICSEARCH_URL']
    es_index = current_app.config['CEOS_GCMD_ELASTICSEARCH_INDEX']
    #current_app.logger.debug("ES query for query(): %s" % json.dumps(json.loads(source), indent=2))
    r = requests.post('%s/%s/_search' % (es_url, es_index), data=source)
    result = r.json()
    if r.status_code != 200:
        current_app.logger.debug("Failed to query ES. Got status code %d:\n%s" %
                                 (r.status_code, json.dumps(result, indent=2)))
    r.raise_for_status()
    #current_app.logger.debug("result: %s" % pformat(r.json()))

    # return only one url
    for hit in result['hits']['hits']:
        # emulate result format from ElasticSearch <1.0
        #current_app.logger.debug("hit: %s" % pformat(hit))
        if '_source' in hit: hit.setdefault('fields', {}).update(hit['_source'])
        hit['fields']['_type'] = hit['_type']

    # return JSONP
    return Response('%s(%s)' % (callback, json.dumps(result)),
                    mimetype="application/javascript")
