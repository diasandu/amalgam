# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
import os

# create the application object
app = Flask(__name__)

# Setup secret key
app.secret_key = 'my precious'

# login required decorator
def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("You need to login first.")
			return redirect(url_for('login'))		
	return wrap


# use decorators to link the function to a url
@app.route('/')
def index():
	return render_template('index.html')  # render a template


@app.route('/welcome')
def welcome():
	return render_template('welcome.html')  # render a template


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid Credentials. Please try again.'
		else:
			session['logged_in'] = True
			flash('You were just logged in!')
			return redirect(url_for('home'))
	return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in', None)
	flash('You were just logged out!')
	return redirect(url_for('index'))
	

@app.route('/home')
@login_required
def home():
	return render_template('home.html')
	

@app.route('/sitemap')
@login_required
def sitemap():
	return render_template('sitemap.html')


@app.route('/sitemap_analyze', methods=['GET', 'POST'])
@login_required
def sitemap_analyze():
	import subprocess
	
	#sys.path.append('./foo/bar/mock-0.3.1')
	
	#check parameter
	if not request.form['address']:
		flash('No address.')
		return redirect(url_for('sitemap'))
		
	
	#Extraction
	current_folder = os.path.dirname(os.path.abspath(__file__))
	#print("Current folder %s" % current_folder)

	script_path = os.path.abspath(current_folder + '/pieces/sitemap-visualization-tool/extract_urls.py')
	#print("Script path %s" % script_path)


	address = request.form['address']
	result = subprocess.run(["python3", script_path, '--url', address, '--not_index'], stdout=subprocess.PIPE, text=True, input="")
	#print(result.stdout)


	#Categorization
	script_path = os.path.abspath(current_folder + '/pieces/sitemap-visualization-tool/categorize_urls.py')
	result = subprocess.run(["python3", script_path], stdout=subprocess.PIPE, text=True, input="")
	#print(result.stdout)


	#Visualize
	script_path = os.path.abspath(current_folder + '/pieces/sitemap-visualization-tool/visualize_urls.py')
	result = subprocess.run(["python3", script_path, '--output-format', 'png', '--size', '"40"'], stdout=subprocess.PIPE, text=True, input="")
	#print(result.stdout)
	
	#TODO: This is lame
	#copy image to /static
	from shutil import copyfile
	filename = 'sitemap_graph_3_layer.png'
	srcfile = current_folder + '/' + filename
	destinationfile = current_folder + '/static/' + filename
	copyfile(srcfile, destinationfile)

	
	#render image
	return redirect(url_for('sitemap_result'))
	

@app.route('/sitemap_result', methods=['GET', 'POST'])
@login_required
def sitemap_result():
	return render_template('sitemap_result.html')


@app.route('/status', methods=['GET', 'POST'])
@login_required
def status():
	status = []
	
	#Home folder
	from os.path import expanduser	
	home = expanduser("~")	
	status.append({'key':'Home folder', 'value':home})	
	
	#Python version
	import sys
	status.append({'key':'Python version', 'value':sys.version})	
		
	#Current folder	
	status.append({'key':'Current folder', 'value':os.path.dirname(__file__)})	

	#Graphviz dependency
	from shutil import which
	status.append({'key':'Graphviz present', 'value': which('dot') is not None})	
	
	return render_template('status.html', status=status)




# start the server with the 'run()' method
if __name__ == '__main__':
	app.debug = True
	app.run()