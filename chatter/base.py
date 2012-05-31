#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json

import re

import sys

from urllib import quote

import urllib3

class ChatterAuth(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret


class ChatterCall(object):
    def __init__(self, auth, instance_url, access_token, callable_cls, 
                 uriparts, refresh_token=None, access_token_refreshed_callback=None):
        self.auth = auth
        self.instance_url = unicode(instance_url)
        self.access_token = unicode(access_token)
        self.callable_cls = callable_cls
        self.uriparts = uriparts
        self.refresh_token = unicode(refresh_token)
        self.access_token_refreshed_callback = access_token_refreshed_callback

    def __getitem__(self, k):
        return self.__getattr__(k)

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            def extend_call(arg):
                return self.callable_cls(
                    auth=self.auth, instance_url=self.instance_url, access_token=self.access_token, 
                    callable_cls=self.callable_cls, uriparts=self.uriparts + (arg.replace("_","-"),),
                    refresh_token=self.refresh_token, 
                    access_token_refreshed_callback=self.access_token_refreshed_callback)
            if k == "_":
                return extend_call
            else:
                return extend_call(k)

    def get(self, **kwargs):
        kwargs["_method"] = "GET"
        return self(**kwargs)

    def post(self, **kwargs):
        kwargs["_method"] = "POST"
        return self(**kwargs)

    def __call__(self, **kwargs):
        # Build the uri.
        uriparts = []
        for uripart in self.uriparts:
            # If this part matches a keyword argument, use the
            # supplied value otherwise, just use the part.
            uriparts.append(str(kwargs.pop(uripart, uripart)))
        uri = "/".join(uriparts)

        # Default method is 'GET'
        method = kwargs.pop("_method", "GET")

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop("id", None)
        if id:
            uri += "/%s" % (id)

        resource = self.instance_url.rstrip("/") + "/" + uri

        return self._handle_response(method, resource, fields=kwargs)

    def _refresh_access_token(self):
        """
        If the client application has a refresh token, it can use it to send a request for a new access token. 
        
        To ask for a new access token, the client application should send a POST request to https://login.instance_name/services/oauth2/token with the following query parameters:
        
            grant_type:     Value must be refresh_token for this flow.
            refresh_token:  The refresh token the client application already received. 
            client_id:      Consumer key from the remote access application definition.
            client_secret:  Consumer secret from the remote access application definition.
            format:         Expected return format. This parameter is optional. The default is json. Values are:
        
                * urlencoded
                * json
                * xml
        
        e.g.
        
            $ curl -i --form grant_type=refresh_token \
                --form refresh_token=<refresh_token> \
                --form client_id=<client_id> \
                --form client_secret=<client_secret> \
                --form format=json \
                https://na1.salesforce.com/services/oauth2/token
        """

        resource = "https://na1.salesforce.com/services/oauth2/token"
        fields = dict(grant_type="refresh_token", refresh_token=self.refresh_token,
                      client_id=self.auth.client_id, client_secret=self.auth.client_secret,
                      format="json")
        status, data = self._handle_response("POST", resource, fields=fields, 
                                             refresh_access_token=False)
        
        if "access_token" in data:
            # Update access token
            self.access_token = data["access_token"]
            
            # Notify others via callback
            if callable(self.access_token_refreshed_callback):
                self.access_token_refreshed_callback(self.access_token)
            
            # Return True, indicating access_token refresehed
            return True

        # Return False, indicating access_token not refreshed
        return False

    def _handle_response(self, method, resource, fields, headers=None, refresh_access_token=True, 
                         max_retries=2):
        http = urllib3.PoolManager()
        
        headers = headers or dict()

        retries = 1
        invalid_session_id = True
        while invalid_session_id and retries <= max_retries:
            # Need to always overwrite the Authorization header in case the access token has been
            # refreshed
            headers["Authorization"] = "OAuth %s" % self.access_token

            r = http.request(method, resource, headers=headers, fields=fields)
            data = json.loads(r.data)

            # Does the access token need to be refreshed? I.e. is the session ID invalid?
            invalid_session_id = len([
                item for item in data 
                    if "errorCode" in item and item["errorCode"] == "INVALID_SESSION_ID"]) > 0
            
            # Refresh the access token if we have an invalid session and have not yet
            # reached the max_retries limit
            if invalid_session_id and refresh_access_token and retries < max_retries:
                self._refresh_access_token()

            retries += 1

        return r.status, data

class Chatter(ChatterCall):
    """
    The minimalist yet fully featured Chatter API class.

    Heavily inspired by https://github.com/sixohsix/twitter.

    For an overview of the Chatter API visit: 
    http://www.salesforce.com/us/developer/docs/chatterapi/Content/quickstart.htm

    Examples:

            # Instantiation
            client_id = "YOUR_CHATTER_CLIENT_ID"
            client_secret = "YOUR_CHATTER_CLIENT_SECRET"
            auth = chatter.ChatterAuth(client_id, client_secret)

            instance_url = "YOUR_USER_INSTANCE_URL"
            access_token = "YOUR_USER_ACCESS_TOKEN"
            refresh_token = "YOUR_USER_REFRESH_TOKEN"

            chatter = chatter.Chatter(auth=auth, instance_url=instance_url, 
                                      access_token=access_token, refresh_token=refresh_token)
            
            # Get authenticated user's details
            me = chatter.users.me.get()

            # Note 'GET' is implied, so you can reduce the above to:
            me = chatter.users.me()

            # Get another user's details
            other_user = chatter.users["005E0000000FpoxIAC"].get()

            # Again, this can be reduced:
            other_user = chatter.users["005E0000000FpoxIAC"]()

            # Another way to achieve this, using the '_' magic method:
            other_user = chatter.users._("005E0000000FpoxIAC").get()

            # Updating the authenticated user's Chatter status:
            chatter.feeds.news.me.feed_items.post(text="Hello world!")

            # Occassionally it is necessary to refresh the user's access token, due to
            # session expiration. The underlying ChatterCall class will handle this
            # automatically, however you may wish to be notified of access token changes
            # so you can reflect this in your user model.
            # 
            # It's possible to do this via the access_token_refreshed_callback, pass in 
            # a callable, and your callback will get called with the refreshed access token.
            # 
            # e.g.
            def my_callback(access_token):
                print "New access_token", access_token
            chatter = chatter.Chatter(auth=auth, instance_url=instance_url, 
                                      access_token=access_token, refresh_token=refresh_token,
                                      access_token_refreshed_callback=my_callback)


            # The rest is hopefully self-explanatory! :)
    """
    def __init__(self, auth, instance_url, access_token, refresh_token=None, 
                 version="v24.0", access_token_refreshed_callback=None):

        uriparts = ("services", "data", version, "chatter")

        ChatterCall.__init__(
            self, auth=auth, instance_url=instance_url, access_token=access_token, 
            callable_cls=ChatterCall, refresh_token=refresh_token, uriparts=uriparts, 
            access_token_refreshed_callback=access_token_refreshed_callback)

