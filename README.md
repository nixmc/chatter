# Python Chatter Client

The minimalist yet fully featured Chatter API class, heavily inspired by [Python Twitter Tools](https://github.com/sixohsix/twitter/).

## Installation

Simply:

	$ easy_install chatter

Even better:

	$ pip install chatter

## Chatter API overview

See [this quickstart tutorial](http://www.salesforce.com/us/developer/docs/chatterapi/Content/quickstart.htm) from Salesforce.

## Usage

Instantiation:

    client_id = "YOUR_CHATTER_CLIENT_ID"
    client_secret = "YOUR_CHATTER_CLIENT_SECRET"
    auth = chatter.ChatterAuth(client_id, client_secret)

    instance_url = "YOUR_USER_INSTANCE_URL"
    access_token = "YOUR_USER_ACCESS_TOKEN"
    refresh_token = "YOUR_USER_REFRESH_TOKEN"

    chatter = chatter.Chatter(auth=auth, instance_url=instance_url, 
                              access_token=access_token, refresh_token=refresh_token)
            
Get authenticated user's details:

    me = chatter.users.me.get()

Note 'GET' is implied, so you can reduce the above to:

    me = chatter.users.me()

Get another user's details

    other_user = chatter.users["005E0000000FpoxIAC"].get()

Again, this can be reduced:

    other_user = chatter.users["005E0000000FpoxIAC"]()

Another way to achieve this, using the '_' magic method:

    other_user = chatter.users._("005E0000000FpoxIAC").get()

Updating the authenticated user's Chatter status:

    chatter.feeds.news.me.feed_items.post(text="Hello world!")

Occassionally it is necessary to refresh the user's access token, due to session expiration. The underlying ChatterCall class will handle this automatically, however you may wish to be notified of access token changes so you can reflect this in your user model.

It's possible to do this via the access_token_refreshed_callback, pass in  a callable, and your callback will get called with the refreshed access token.
 
e.g.

    def my_callback(access_token):
        print "New access_token", access_token
    chatter = chatter.Chatter(auth=auth, instance_url=instance_url, 
                              access_token=access_token, refresh_token=refresh_token,
                              access_token_refreshed_callback=my_callback)


The rest is hopefully self-explanatory! :)

## Feedback

Email steve.winton[at]nixonmcinnes.co.uk.
Twitter @[steveWINton](http://twitter.com/steveWINton).
