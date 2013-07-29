from flask import Flask, request, Response, session, g, redirect, url_for, \
	abort, render_template, flash, send_from_directory, send_file
import list_crusher3_5
import tempfile
from werkzeug import secure_filename
import os

DEBUG = True
UPLOAD_FOLDER = os.getcwd()#datasaving folder path
ALLOWED_EXTENSIONS = set(['txt'])#Currently not used allows for easy file limiting
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER#configuring file to save data

@app.route('/')
def initialize():
	return render_template('list_crusher_initial.html')

def allowedFile(filename):#checks if uploaded file is of the correct type
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/crushlists', methods=['POST'])
def runCrusher():
	userData = request.files['userData']#get file from browser request
	userInterest = request.files['userInterest']
	if userData and allowedFile(userData.filename):
		dataName = secure_filename(userData.filename)
		userData.save(os.path.join(app.config['UPLOAD_FOLDER'], dataName))#save user data
	else:
		return "Your mutation list file was of an incorrect type, please change file type to .txt and try again."
	if userInterest and allowedFile(userData.filename):
		interestName = secure_filename(userInterest.filename)
		userInterest.save(os.path.join(app.config['UPLOAD_FOLDER'], interestName))#save user data
	else:
		return "Your area of interest file was of an incorrect type, please change file type to .txt and try again."
	crushed_results = list_crusher3_5.main('fixed_mut_prob_fs_adjdepdiv.txt', dataName, interestName)
	split_crushed_results = crushed_results.split('\n')
	'''for line in split_crushed_results:
		if ':' in line:
			print line
			line = line.split(':')
			line[0] = '<b>'+line[0]
			line[0] += ':</b>'
			line = line[0]+line[1]
			print line
		line = '<pre><p style="padding: 0px;">'+line+'</p></pre>'
		'''
	for num in range(0, len(split_crushed_results)):
		if ':' in split_crushed_results[num]:
			print split_crushed_results[num]
			split_crushed_results[num] = split_crushed_results[num].split(':')
			#split_crushed_results[num][0] = '<b>'+split_crushed_results[num][0]
			#split_crushed_results[num][0] += ':</b>'
			#split_crushed_results[num] = split_crushed_results[num][0]+split_crushed_results[num][1]
			split_crushed_results[num][0] += ':'
			print split_crushed_results[num]
		#split_crushed_results[num] = '<pre><p style="padding: 0px;">'+split_crushed_results[num]+'</p></pre>'
	print split_crushed_results
	return render_template('list_crusherHTML.html', results=split_crushed_results)

@app.route('/exampleData')
def exampleDownload():
	exampleData = open('exampleData.txt', 'r')
	return send_file(exampleData, attachment_filename="ExampleInputData.txt", as_attachment=True)
#python list_crusher3_5.py fixed_mut_prob_fs_adjdepdiv.txt examplefile.txt fmrp_list_edited.txt -p

@app.route('/areaInterestExample')
def areaInterestExample():
	areaInterestExample = open('fmrp_list_edited.txt', 'r')
	return send_file(areaInterestExample, attachment_filename="ExampleAreaOfInterest", as_attachment=True)

if __name__ == '__main__':
	app.run()