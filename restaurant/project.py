"""
This module is the main project for P4 of the udacity FSND Item Catalog
"""
import os
import random
import string
import json
import httplib2
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from werkzeug.utils import secure_filename

# DATA VIZ DEPENDENCIES
from sqlalchemy import func
from sqlalchemy.sql import label

# TODO: add image uploads to the web page to add addtional
# funcitonality to the site

__author__ = "Harry Staley <staleyh@gmail.com>"
__version__ = "1.0"

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DB_SESSION = sessionmaker(bind=engine)
session = DB_SESSION()

# IMAGE UPLOAD HANDLING
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = '/static/images/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Route that will process the file upload
# @app.route('/upload', methods=['POST'])

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)


# DATA VIZUALIZATIONS
@app.route('/dashboard')
def dashboard():
    """ gets the json data and renders the dashboard """
    labels = []
    for course in session.query(label('name', MenuItem.course)
                                ).group_by(MenuItem.course).all():
        labels.append(str(course.name))
    print labels
    values = []
    for course in session.query(label('value', func.count(MenuItem.course))
                                ).group_by(MenuItem.course).all():
        values.append(course.value)
    print values
    return render_template('dashboard.html', labels=labels, values=values)


# JSON REQUEST HANDLERS
@app.route('/dashboard/JSON/')
@app.route('/dashboard/json/')
def course_json():
    """ gets the course data for bar chart and pushes it into a json """
    courses = session.query(label('name', MenuItem.course),
                            label('count', func.count(MenuItem.course))
                            ).group_by(MenuItem.course).all()
    return jsonify(courses=courses)


@app.route('/restaurant/JSON/')
@app.route('/restaurant/json/')
def restaurnts_json():
    """ handler to provide a list of restaurants in the form of a json """
    restaurants = session.query(Restaurant).all()
    return jsonify(RestData=[rest.serialize for rest in restaurants])


@app.route('/restaurant/<int:restaurant_id>/JSON/')
@app.route('/restaurant/<int:restaurant_id>/json/')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON/')
@app.route('/restaurant/<int:restaurant_id>/menu/json/')
def menu_json(restaurant_id):
    """ handler to provide a json for the list of items on a menu. """
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id
                                              ).all()
    return jsonify(MenuItems=[item.serialize for item in items])


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/JSON/')
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/json/')
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/json/')
def item_json(restaurant_id, menu_id):
    """ handler to provide json for an individual item """
    item = session.query(MenuItem).filter_by(id=menu_id
                                             ).one()
    return jsonify(MenuItem=item.serialize)


# MAIN HANDLERS
@app.route('/')
@app.route('/restaurant/')
def get_restaurants():
    """
    Get all of the restaurants in the database and display them in a web page.
    """
    restaurants = session.query(Restaurant).all()
    # if the userid is in the login session pass it to the template.
    try:
        user_id = login_session['user_id']
    except KeyError:
        user_id = None
    return render_template('restaurants.html', restaurants=restaurants,
                           user_id=user_id)


@app.route('/login/')
def get_login():
    """
    Creates a state token and store it in a session for later retrieval to
    guard against cross site forgerty.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits
                                  ) for x in xrange(32))
    login_session['state'] = state
    print "LOGIN STATE: " + state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """
    Handles authentication and authorization for facebook
    authentication.
    """
    # state token validation
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'
                                            ), 401)
        response.headers['content-type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received: %s" % access_token

    # exchange client token for server token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?grant_type='
           'fb_exchange_token&client_id=%s&client_secret=%s&'
           'fb_exchange_token=%s'
           % (app_id, app_secret, access_token))
    http_ = httplib2.Http()
    result = http_.request(url, 'GET')[1]

    # use token to get info from fb api
    # userinfo_url = 'https://graph.facebook.com/v2.4/me'

    # Strip expire tag from access token
    token = result.split('&')[0]
    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in
    # our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    http_ = httplib2.Http()
    result = http_.request(url, 'GET')[1]
    print "url sent for API access: %s" % url
    print "API JSON result: %s" % result

    data = json.loads(result)

    # populate login session
    login_session['username'] = data['name']
    print login_session['username']
    login_session['email'] = data['email']
    print login_session['email']
    login_session['facebook_id'] = data['id']
    print login_session['facebook_id']
    login_session['provider'] = 'facebook'
    print login_session['provider']
    # get user profile pic
    url = ('https://graph.facebook.com/v2.4/me/picture?%s'
           '&redirect=0&height=200&width=200' % token)
    http_ = httplib2.Http()
    result = http_.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # if the user exists get their user id otherwise create new user
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    # store the user id in the login session
    login_session['user_id'] = user_id
    # display welcome message for user
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'
    output += ' height: 300px;'
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def fbdisconnect():
    """ Log out of facebook """
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']
    url = ('https://graph.facebook.com/%s/'
           'permissions?access_token=%s'
           % (facebook_id, access_token))
    http_ = httplib2.Http()
    result = http_.request(url, 'DELETE')[1]
    return 'You have logged out.'


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ handles authentication and authorization for google authentication """
    # state token validation
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'
                                            ), 401)
        response.headers['content-type'] = 'application/json'
        return response
    code = request.data
    try:
        # try to upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # exchanges the code for oauth credentials
        credentials = oauth_flow.step2_exchange(code)
    # if a flow exchange error exists dump to json and return error msg
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    http_ = httplib2.Http()
    result = json.loads(http_.request(url, 'GET')[1])
    # If an error exists in the access token info, abort operation.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify current app level access token validity.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # if stored credentials exist and user ids match respond that user is
    # already logged in
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get google user data json
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # access user data json for display
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # if the user exists get their user id otherwise create new user
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    # store the user id in the login session
    login_session['user_id'] = user_id
    # display welcome message for user
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'
    output += ' height: 300px;'
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def gdisconnect():
    """ handles the log out functions of the google acccount """
    # gets and displays the acccess token data in the console
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: ' + login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'
                                            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # gets the url to revoke the access token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    # gets the result of the url and displays it in the concole
    result = h.request(url, 'GET')[0]
    print result['status']
    # if the result status is confirmed then delete all session
    # data otherwise send error to jsaon
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    """ Handles the disconnection of all accounts """
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have been successfully logged out.')
        return redirect(url_for('get_restaurants'))
    else:
        flash('You never logged in.')
        return redirect(url_for('get_restaurants'))


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def get_menu(restaurant_id):
    """ This method gets all of the menu items for the selected restaurant """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id
                                              ).all()
    # if the userid is in the login session pass it to the template.
    try:
        user_id = login_session['user_id']
    except KeyError:
        user_id = None
    return render_template('menu.html', restaurant=restaurant,
                           items=items, user_id=user_id)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def new_restaurant():
    """ method to add a new restaurant """
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            newRestaurant = Restaurant(name=request.form['name'],
                                       address=request.form['address'],
                                       city=request.form['city'],
                                       state=request.form['state'],
                                       zip_code=request.form['zip_code'],
                                       phone=request.form['phone'],
                                       user_id=login_session['user_id'])
            session.add(newRestaurant)
            session.commit()
            flash(str(newRestaurant.name) + " restaurant created.")
            return redirect(url_for('get_restaurants'))
        else:
            return render_template('newrestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    """ method to edit a restaurant """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        # if the logged in user is the restaurant owner allow them to edit
        if restaurant.user_id == login_session['user_id']:
            if request.method == 'POST':
                if request.form['name']:
                    restaurant.name = request.form['name']
                    restaurant.address = rresequest.form['address']
                    restaurant.city = request.form['city']
                    restaurant.state = request.form['state']
                    restaurant.zip_code = request.form['zip_code']
                    restaurant.phone = request.form['phone']
                    session.add(restaurant)
                    session.commit()
                    flash(str(restaurant.name) + " restaurant updated.")
                return redirect(url_for('get_restaurants'))
            else:
                return render_template('editrestaurant.html',
                                       restaurant=restaurant)
        else:
            flash("Athentication Error: you are not the owner.")
            return redirect(url_for('get_restaurants'))


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    """ method to delete a restaurant """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        # if the logged in user is the restaurant owner allow them to delete
        if restaurant.user_id == login_session['user_id']:
            items = session.query(MenuItem
                                  ).filter_by(restaurant_id=restaurant.id
                                              ).all()
            if request.method == 'POST':
                session.delete(restaurant)
                session.commit()
                flash(str(restaurant.name) + " restaurant deleted.")
                return redirect(url_for('get_restaurants'))
            else:
                return render_template('deleterestaurant.html',
                                       restaurant=restaurant)
        else:
            flash("Athentication Error: you are not the owner.")
            return redirect(url_for('get_restaurants'))


@app.route('/restaurant/<int:restaurant_id>/newitem', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    """ method to add a new menu item to the menu """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        # if the logged in user is the restaurant owner allow them to add items
        if restaurant.user_id == login_session['user_id']:
            if request.method == 'POST':
                newItem = MenuItem(name=request.form['name'],
                                   course=request.form['course'],
                                   picture_url=request.form['picture_url'],
                                   alt_text=request.form['alt_text'],
                                   description=request.form['description'],
                                   price=request.form['price'],
                                   user_id=restaurant.user_id,
                                   restaurant_id=restaurant_id)
                session.add(newItem)
                session.commit()
                flash(str(newItem.name) + " menu item created.")
                return redirect(url_for('get_menu',
                                        restaurant_id=restaurant_id))
            else:
                return render_template('newmenuitem.html',
                                       restaurant=restaurant)
        else:
            flash("Athentication Error: you are not the owner.")
            return redirect(url_for('get_manu',
                                    restaurant_id=restaurant_id))


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    """ method to edit a menu item """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        # if the logged in user is the restaurant owner allow them to edit
        if restaurant.user_id == login_session['user_id']:
            item = session.query(MenuItem).filter_by(id=int(menu_id)
                                                     ).one()
            if request.method == 'POST':
                editItem = item
                if request.form['name']:
                    editItem.name = request.form['name']
                    editItem.course = request.form['course']
                    editItem.picture_url = request.form['picture_url'],
                    editItem.alt_text = request.form['alt_text'],
                    editItem.description = request.form['description']
                    editItem.price = request.form['price']
                    session.add(editItem)
                    session.commit()
                    flash(str(item.name) + " updated.")
                return redirect(url_for('get_menu',
                                        restaurant_id=restaurant_id))
            else:
                return render_template('editmenuitem.html',
                                       restaurant=restaurant,
                                       item=item)
        else:
            flash("Athentication Error: you are not the owner.")
            return redirect(url_for('get_manu',
                                    restaurant_id=restaurant_id))


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    """ method to delete the menu item """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        # if the logged in user is the restaurant owner allow item deletion
        if restaurant.user_id == login_session['user_id']:
            item = session.query(MenuItem).filter_by(id=int(menu_id)
                                                     ).one()
            if request.method == 'POST':
                session.delete(item)
                session.commit()
                flash("Menu item deleted.")
                return redirect(url_for('get_menu',
                                        restaurant_id=restaurant_id))
            else:
                return render_template('deletemenuitem.html',
                                       restaurant=restaurant,
                                       item=item)
        else:
            flash("Athentication Error: you are not the owner.")
            return redirect(url_for('get_manu',
                                    restaurant_id=restaurant_id))


def get_user_id(email):
    """ queries the User table for user id based on user email """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_user_info(user_id):
    """
    queries the User table based on user id for the rest of the
    user info such as email, picture, ect.
    """
    user = session.query(User).filter_by(user_id=user_id).one()
    if user:
        return user
    else:
        return None


def create_user(login_session):
    """
    creates a new user and commits it to the database and then
    once created returns the user id of the newly created user.
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
