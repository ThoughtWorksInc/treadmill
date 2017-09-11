"""
Treadmill IPA REST api.
"""

import flask
import flask_restplus as restplus
from flask_restplus import fields

# Disable E0611: No 'name' in module
from treadmill import webutils  # pylint: disable=E0611


# Old style classes, no init method.
#
# pylint: disable=W0232
def init(api, cors, impl):
    """Configures REST handlers for ipa resource."""

    namespace = webutils.namespace(
        api, __name__, 'IPA REST operations'
    )

    service_req_model = {
        'service': fields.String(description='Service Name'),
        'hostname': fields.String(description='Hostname'),
        'domain': fields.String(description='Domain')
    }

    service_model = api.model(
        'service', service_req_model
    )

    host_req_model = {
        'hostname': fields.String(description='Hostname'),
    }

    host_model = api.model(
        'host', host_req_model
    )

    @namespace.route('/host')
    class _Host(restplus.Resource):
        """Treadmill IPA resource"""

        @webutils.post_api(
            api,
            cors,
            req_model=host_model
        )
        def post(self):
            """Adds host to IPA."""
            return impl.create(flask.request.json)

        @webutils.delete_api(
            api,
            cors,
            req_model=host_model
        )
        def delete(self, ):
            """Deletes host from IPA."""
            return impl.delete(flask.request.json)

    @namespace.route('/service')
    class _Service(restplus.Resource):
        """Treadmill Service Allow Retrieve Keytab"""
        @webutils.post_api(
            api,
            cors,
            req_model=service_model
        )
        def post(self):
            """Whitelist host to Allowed hosts for service keytab retrieval."""
            return impl.service_add(flask.request.json)
