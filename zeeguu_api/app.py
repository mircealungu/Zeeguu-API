# -*- coding: utf8 -*-
from .cross_domain_app import CrossDomainApp
from zeeguu.util.configuration import load_configuration_or_abort
from flask_cors import CORS, cross_origin
from flask import Flask

# *** Creating and starting the App *** #
app = Flask("Zeeguu-API")
CORS(app)

load_configuration_or_abort(app, 'ZEEGUU_API_CONFIG',
                            ['SQLALCHEMY_DATABASE_URI', 'HOST', 'DEBUG', 'SECRET_KEY', 'MAX_SESSION'])


# The zeeguu.model  module relies on an app being injected from outside
# ----------------------------------------------------------------------
import zeeguu
zeeguu.app = app
import zeeguu.model
assert zeeguu.model
# -----------------

from .api import api
app.register_blueprint(api)

try:
    import dashboard
    dashboard.config.from_file(None)

    # dashboard can benefit from a way of associating a request with a user id
    def get_user_id():
        import flask
        print ("trying to get the flask.g.user.id")
        try:
            session_id = int(flask.request.args['session'])
        except:
            print ("cound not find the session in the request")
            return 1
        from zeeguu.model import Session
        session = Session.find_for_id(session_id)
        print ("found session object")

        user_id = session.user.id
        print ("got user id = " + str(user_id))
        return user_id


    dashboard.config.get_group_by = get_user_id
    dashboard.bind(app=app)
except Exception as e:
    print ("could not start the dashboard, but will continue anyway")
    print (str(e))
    raise e

