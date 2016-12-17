from app import app
from flask import Flask, render_template, redirect, request, url_for, flash, session
from models import *
import config
from functools import wraps
from flask_oauth import OAuth
from flask.ext.social import Social

app.secret_key = 'yo bappa'


GOOGLE_CLIENT_ID = '136783183654-jtdjq47utgkgh64tt8mbrfmd41i4rn3m.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'JIRIV3QeKWyNLuVgo7a1644c'
GOOGLE_OAUTH2_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

REDIRECT_URI = '/oauth2callback'

oauth = OAuth()

google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)




@app.route('/index')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login_google'))
 
    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError
 
    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login_google'))
        return res.read()
 
    return res.read()

@app.route('/google-login')
def login_google():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('login_google'))
 
 
@google.tokengetter
def get_access_token():
    return session.get('access_token')



facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='139235389897591',
    consumer_secret='56fef7209a67c9338fdbe00020fc1288',
    request_token_params={'scope': 'email'}
)



@app.route('/facebook-login')
def facebook_login():
    return facebook.authorize(
        callback=url_for(
            'facebook_authorized',
            next=request.args.get('next') or request.referrer or 
              None,
            _external=True
        ))

@app.route('/facebook-login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['facebook_oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')

    name = me.data['name']
    user =users(name,'')
    check = users.query.filter_by(username=name).first()
    # session['username'] = name
    if check == None:
    	session['username'] = name
    	db.session.add(user)
    	db.session.commit()
    	
    	print name
    	# return redirect(url_for('user',username=name))
    else:
    	session['username']=name
    	print session['username']

    return redirect(url_for('user',username=session['username']))
    # return redirect(url_for('user',username=name))
#     return 'Logged in as id=%s name=%s redirect=%s' % \
# (me.data['id'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
	return session.get('facebook_oauth_token')



@app.route("/")
def home():
    username=None
    if 'username' in session:
    	print True
        username = session['username']
        return redirect(url_for('user',username=username))
    else:
    	return render_template('base.html')
	return render_template('base.html')



def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'username' in session:
			username = session['username']
			return f(*args, **kwargs)
		else:
			return redirect(url_for('login'))
	return wrap



@app.route("/login", methods=['POST','GET'])
def login():
	error = None
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		test = users.query.filter_by(username=username).first()

		if test != None:
			if test.password == password:
				session['username'] = username
				return redirect(url_for('user',username=test.username))
	        else:
				pass

	return redirect(url_for('home'))



@app.route('/logout')
@login_required
def logout():
	session.pop('username', None)
	return redirect(url_for('home'))



@app.route("/sign-up", methods=['POST', 'GET'])
def sign_up():
	error = None
	if request.method == 'POST':
		name = request.form['username']
		pwd = request.form['password']
		user = users(name, pwd)

		check = users.query.filter_by(username=name).first()

		if check == None:
			session['username'] = name		
			db.session.add(user)
			db.session.commit()

			return redirect(url_for('user',username=session['username']))
		else:
			error = "Username Alredy Taken !! Plz take a new one"

	return render_template("base.html",error=error)



@app.route("/users/<username>")
@login_required
def user(username):
	myfeed = None
	if	username == session['username'] :
		error = None
		myfeed = show_user_post()
		feed = post.query.all()

		return render_template('user.html',username=username, myfeed=myfeed, feed=feed)
	else:
		return redirect(url_for('error404'))



@app.route("/new-post", methods=['POST', 'GET'])
@login_required
def newpost():
	# username = None
	myfeed = show_user_post()
	feed = post.query.all()
	# if username in session:
	# 	username == session['username']
	print session['username']
	if request.method == 'POST':
		posts = request.form['post']
		title = request.form['title']
		tag = request.form['tags']
		username = session['username']
		data = post(posts, title, tag, username)		

		db.session.add(data)
		db.session.commit()
		myfeed = show_user_post()
		feed = post.query.all()
	return render_template('user.html', username=session['username'], myfeed=myfeed, feed=feed)	
		# return redirect(url_for('base', username=username))

	# return render_template('user.html', username=session['username'], myfeed=myfeed, feed=feed)



def show_user_post():
		username = session['username']
		myfeed = post.query.filter_by(userid=username).first()
		return myfeed



@app.route("/search", methods=['POST', 'GET'])
@login_required
def search():
	error1=None
	if request.method == 'POST':
		title = request.form['search']

		search_title = post.query.filter_by(title=title).first()
		feed = post.query.all()
		if search_title == None:
			error1 = "No Post For this search"
			return render_template('user.html',  username=session['username'], error1=error1)

	return render_template('user.html', title=search_title.title, username=session['username'], feed=feed)
	


@app.route('/404')
def error404():
	return render_template('404.html')