'''
list_crusher_interface.py was developed as a way to make the 'list crusher' script, developed by
Kaitlin Samocha available online.  The 'list crusher' script takes a list of de novo mutations and
a list of genes of interest and returns information regarding whether or not the de novos cited fall
in the genes of interest more than would be expected by chance.

Required local software:
	See requirements.txt

Required files:
	A 'templates' directory containing:
		list_crusher_initial.html
		list_crusherHTML.html
	A 'data' directory containing:
		betancur_asd110_list.txt
		constrained.txt
		fmrp_list_edited.txt
	exampleData.txt
	fixed_mut_prob_fs_adjdepdiv.txt
	list_crusher3_5.py
'''

from flask import Flask, request, Response, session, g, redirect, url_for, \
	abort, render_template, flash, send_from_directory, send_file
import list_crusher3_5
import tempfile
from werkzeug import secure_filename
import os
from datetime import datetime


DEBUG = True
UPLOAD_FOLDER = os.getcwd()#datasaving folder path
ALLOWED_EXTENSIONS = set(['txt'])#Currently not used allows for easy file limiting
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER#configuring file to save data

SERVER_NAME = '127.0.0.1'
SERVER_PORT = 5001

# set the secret key (keep this the same as other utilities to have cross utility logins)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def initialize():
	if 'username' in session:
		return render_template('list_crusher_initial.html')
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    	if request.form['username'] == 'ATGUuser':
        	session['username'] = request.form['username']
        	return redirect(url_for('initialize'))
        else:
        	return '''
    			<p>Incorrect Username
        		<form action="" method="post">
        		    <p><input type=text name=username>
        		    <p><input type=submit value=Login>
        		</form>
        		'''
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
        '''

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('initialize'))



def allowedFile(filename):#checks if uploaded file is of the correct type
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#This function basically handles everything
@app.route('/crushlists', methods=['POST'])
def runCrusher():
	print request.form['selectInterest']
	
	#This section gets checks and saves user files
	userData = request.files['userData']#get file from browser request
	if userData and allowedFile(userData.filename):
		dataName = secure_filename(userData.filename)
		userData.save(os.path.join(app.config['UPLOAD_FOLDER'], dataName))#save user data
	else:
		return "Your mutation list file was of an incorrect type, please change file type to .txt and try again."
	if request.form['selectInterest'] == 'choose':
		userInterest = request.files['userInterest']
		if userInterest and allowedFile(userData.filename):
			interestName = secure_filename(userInterest.filename)
			userInterest.save(os.path.join(app.config['UPLOAD_FOLDER'], interestName))#save user data
		else:
			return "Your area of interest file was of an incorrect type, please change file type to .txt and try again."
	elif request.form['selectInterest'] == 'ASD':
		interestName = 'data/betancur_asd110_list.txt'
	elif request.form['selectInterest'] == 'FMRP':
		interestName = 'data/fmrp_list_edited.txt'
	else:
		interestName = 'data/constrained_1003.txt'
	
	#Next line runs the actual file
	crushed_results = list_crusher3_5.main('fixed_mut_prob_fs_adjdepdiv.txt', dataName, interestName)
	
	#The rest of the function is just text processing
	split_crushed_results = crushed_results.split('\n')
	for num in range(0, len(split_crushed_results)):
		if ':' in split_crushed_results[num]:
			#print split_crushed_results[num]
			split_crushed_results[num] = split_crushed_results[num].split(':')
			split_crushed_results[num][0] += ':'
			if 'mutation' in split_crushed_results[num][0]:
				print 'newsection'
				splitGeneList = split_crushed_results[num][1].split(', ')
				for gene in splitGeneList:
					if split_crushed_results[num][1].count(gene) > 1:
						print split_crushed_results[num][1]
						inst = split_crushed_results[num][1].count(gene)
						split_crushed_results[num][1] = split_crushed_results[num][1].replace(gene, gene+'('+str(inst)+')', 1)
						split_crushed_results[num][1] = split_crushed_results[num][1].replace(gene+', ', '')
						print split_crushed_results[num][1]
					splitGeneList = split_crushed_results[num][1].split(', ')
			else:
				split_crushed_results[num][1] = split_crushed_results[num][1].replace(' ', '')
				scrn = split_crushed_results[num][1]
				print "SCRN "+scrn
				try:
					split_crushed_results[num][1] = str(round_to_n(float(scrn.strip()), 3))
				except ValueError:
					print scrn
	return render_template('list_crusherHTML.html', results=split_crushed_results)


def round_to_n(x, n):
    if n < 1:
        raise ValueError("number of significant digits must be >= 1")
    format = "%." + str(n-1) + "e"
    as_string = format % x
    return float(as_string)

@app.route('/exampleData')
def exampleDownload():
	exampleData = open('exampleData.txt', 'r')
	time = datetime.now()
	splitTime = str(time).rsplit('.', 1)[0]
	return send_file(exampleData, attachment_filename="ExampleInputData "+splitTime+".txt", as_attachment=True)

@app.route('/areaInterestExample')
def areaInterestExample():
	areaInterestExample = open('data/constrained_1003.txt', 'r')
	time = datetime.now()
	splitTime = str(time).rsplit('.', 1)[0]
	return send_file(areaInterestExample, attachment_filename="ExampleAreaOfInterest "+splitTime+".txt", as_attachment=True)

if __name__ == '__main__':
	app.run()