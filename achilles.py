#!/usr/bin/env python3

# import sys #lets us intract with the system runnig

#print('The first argument was: ' +sys.argv[1])  #argv ,means collection of arguments that this application was called with

import argparse
import validators
import requests
import yaml
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from bs4 import Comment

parser = argparse.ArgumentParser(description = 'The Achilles HTML Analyzer version 1.0') # a callesd to a constructor ,it takes few thigs as argument,i am just passing one arg 

parser.add_argument('-v','--version',action = 'version', version='%(prog)s 1.0') #what exactly people will pass in to trigger
parser.add_argument('url',type=str, help="The url of the HTML to analyze")
parser.add_argument('--config',help='path to configuration file')
parser.add_argument('-o','--output',help='report file path')

args = parser.parse_args()

config = {'forms': True, 'comments': True, 'password': True}


if(args.config):
	print('using confg file: ' +args.config)
	config_file = open(args.config,'r')
	config_from_file = yaml.load(config_file)
	if(config_from_file):
		
		config = {**config,**config_from_file}
	

report = ''

url = args.url

if(validators.url(url)):
	result_html = requests.get(url).text
	parsed_html = BeautifulSoup(result_html, 'html.parser')

	


	forms           = parsed_html.find_all('form')
	comments        = parsed_html.find_all(string=lambda text:isinstance(text,Comment))
	password_inputs = parsed_html.find_all('input', {'name':'password'})


	if(config['forms']):
		for form in forms:
			if((form.get('action').find('https') < 0 ) and (urlparse(url).scheme !='https')):
				report += 'form issue: Insecure form found in ' + form.get('action')  + ' document \n'


	if(config['comments']):
		for comment in comments:
			if(comment.find('key: ') > -1):
				report += 'comment issue: key is found in html comment,plese remove\n'


	if(config['password']):
		for password_input in password_inputs:
			if(password_input.get('type')!= 'password'):
				report +='Input issue:plain text password was found,please change to password input type\n'

else:
	print('please enetr a valid url')

if(report == ''):
	report += ('Nice job!your html document is secure')
else:
	header = ('Vulnarability report is as follows \n')
	header += ('====================================== \n')
	report = header + report

print(report)



if(args.output):
	f = open(args.output,'w')
	f.write(report)
	f.close
	print('report saved to '+args.output)