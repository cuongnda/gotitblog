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

.. code-block:: bash
    $git clone https://github.com/cuongnda/gotitblog.git
    $cd gotitblog
    $pip install -r requirements.txt


Configuration
============
If you are using autoenv you can take edit .env file in the project folder. If not, you can edit these settings as you
 wish, especially the database config
.. code-block:: bash
    $export FLASK_APP="run.py"
    $export FLASK_DEBUG=1
    $export SECRET="some-very-long-string-of-random-characters1212"
    $export APP_SETTINGS="development"
    $export DATABASE_URL="mysql://DATABASE_USERNAME:DATABASE_PASSWORD@localhost/DATABASE_NAME"
    $export OAUTHLIB_INSECURE_TRANSPORT=1


Quickstart
==========
