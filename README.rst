Got it blog
===================================================
A Restful API that provide simple blogging function which contains some excellent features:

* Allow user to signing using either Facebook or Google account
* Allow user to add blog post with title and content
* Allow user to like posts from others or him-self

Dependecies
============
* Python3.6
* Flask 0.12.2
* MySQL

Installation
============

Just the basics:

    $git clone https://github.com/cuongnda/gotitblog.git
    $cd gotitblog
    $pip install -r requirements.txt


Configuration
============
If you are using autoenv you can edit .env file in the project folder to fit to your preferences. If not, you can edit these settings as you
 wish, especially the database config

    $export FLASK_APP="run.py"

    $export FLASK_DEBUG=1

    $export SECRET="some-very-long-string-of-random-characters1212"

    $export APP_SETTINGS="development"

    $export DATABASE_URL="mysql://DATABASE_USERNAME:DATABASE_PASSWORD@localhost/DATABASE_NAME"

    $export OAUTHLIB_INSECURE_TRANSPORT=1

Enter your Facebook app and Google app credential in the configration file at gotitblog/instance/config

Quickstart
==========
Once you have environment variable setting done, you can start with the product.

Database setup:

    $flask db upgrade

Starting Flask development server

    $python run.py

Now you can access the server in the browser under URL https://localhost:5000 . We used https with self-signed
 certificate here as Facebook API only allow access from HTTPS service.


REST API Description
====================

End points:

* /users : This endpoint only allow get methods, in which return all the users in the system. Login required, Finished registration required.

* /users/<user_id> :

  * GET: Return user details

  * PUT: Update an user. Atm, it only allow logged in user to edit himself

* /posts :

  * GET : Get all blog post in the system. Login required, Finished registration required.

  * POST : Adding new blog post. Login required, Finished registration required.

* /posts/<post_id>:

  * GET : Get details of single post. Login required, Finished registration required.

  * PUT :  Update a post. Login required, Finished registration required.

  * DELETE: Delete a post. Login required, Finished registration required.

* /posts/<post_id>/like:

  * POST: like a post, add current logged in user to list of user that like this post. Login required, Finished registration required.

* /facebook: This end point allow user to login using their Facebook Account. Facebook app credential must be provided.

* /google: This end point allow user to login using their Google Account. Google app credential must be provided.