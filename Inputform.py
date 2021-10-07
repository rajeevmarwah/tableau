from flask import Flask, render_template,request,redirect,url_for, session,flash,Markup
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
import requests
from configparser import ConfigParser
import xml.etree.ElementTree as ET
import os.path
from wtforms.validators import DataRequired
from wtforms import ValidationError
import flask
import sys

api_version = 3.12
xmlns = {'t': 'http://tableau.com/api'}

app = flask.Flask(__name__)
app.config['SECRET_KEY']='Admin123'
#Inheriting FlaskForm imported earlier
class InfoForm(FlaskForm):
     projectname = StringField('Enter the name of the project',validators=[DataRequired()])
     projectdescription = StringField('Enter the description for the project',validators=[DataRequired()])
     submit = SubmitField('Create Project')
     

     

@app.route('/',methods=['GET','POST'])
def index():
    #Initial value to be false
    projectname = False
    projectdescription = False
    form = InfoForm()
   
    if request.method == "POST":
        projectname=request.form.get("projectname")
        projectdescription=request.form.get("projectdescription")
        projectbuild=createproject(projectname, projectdescription)
        print(projectbuild)
        errormessage=str(projectbuild.status_code)
        print(errormessage)
        print(projectbuild.status_code)
        if projectbuild.status_code == 201:
            message = Markup("Success : Project "+ projectname + " has been created")
            
            
            flash(message)
            
        elif projectbuild.status_code == 409:
            message = Markup("Error : Project "+ projectname + " with the name already exists, Please provide a different name")
            flash(message)
        else:
            message = Markup("Error : Project "+ projectname + " can not be created Error Code="+ errormessage)
            flash(message)
    return render_template('Inputform.html', form=form ,projectname=projectname,projectdescription=projectdescription)
    
            
    
def signIn():
    #inputpath='C:/Users/Rajeev/Documents/Tableau/Tableau code'
	#propertiesfile=os.path.join(inputpath,'config.properties')
	#configfile = ConfigParser()
	#configfile.read(propertiesfile)
	#Reading the credentials, url and site name from config file
	#username=configfile.get('tableau', 'username)
    username='rajeevmarwah15@gmail.com'
	#password=configfile.get('tableau', 'password')
    password='Office@15'
    server_url='https://prod-useast-b.online.tableau.com'
    server_url_sign_in= server_url + "/api/{0}/auth/signin".format(api_version)
    site='Learningtableau'
    print(server_url)

	#server_url=configfile.get('tableau', 'server_url')
	#site=configfile.get('tableau', 'site')
    #Forming the request body with the parent element tsRequest
    input_data=ET.Element('tsRequest')
	#Forming the request body for the child element
    input_credentials=ET.SubElement(input_data,'credentials', name=username,password=password)
	#Forming the next request for the child element along with credentials and parent element
	#this is all in XML format
    ET.SubElement(input_credentials,'site', contentUrl=site)
    input=ET.tostring(input_data)	
	#Body has been formed.Signing in
    input_signin=requests.post(server_url_sign_in, data=input,verify=False)
	#print(input_signin)
    server_response = input_signin.text.encode('ascii', errors="backslashreplace").decode('utf-8')
    get_output=ET.fromstring(server_response)
	#fromstring has 2 method find and get. find get the first child element and get the name.
	#Get the authentication token
    auth_token=get_output.find('t:credentials',xmlns).get('token')
	#Get the site id
    site_id=get_output.find('.//t:site', xmlns).get('id')
	#Return the auth token and site id
    return(auth_token, site_id)
    


def createproject(projectname,projectdescription):
  
    print(projectname)
    auth_token,site_id=signIn()
    print(auth_token)
    print(site_id)
    inputpath='C:/Users/Rajeev/Documents/Tableau\Tableau code'
    propertiesfile=os.path.join(inputpath,'config.properties')
    configfile = ConfigParser() 
    configfile.read(propertiesfile)
	#Reading the credentials, url and site name from config file
    print("In project")
    server_url='https://prod-useast-b.online.tableau.com'
    print(server_url)
    url_createproject= server_url + "/api/{0}/sites/{1}/projects".format(api_version,site_id)
    print(url_createproject)
    input_project=ET.Element('tsRequest')
    print(input_project)
    print(projectname)
    print(projectdescription)
    input_body=ET.SubElement(input_project,'project', name=projectname,description=projectdescription,contentPermissions="LockedtoProject")
    print(input_body)
    input_data=ET.tostring(input_project)
    projectbuild=requests.post(url_createproject,data=input_data,headers = {'x-tableau-auth':auth_token,'Accept':'application/json'}, verify = False )
    print(projectbuild)
    return(projectbuild)   
   

def executestatus(projectbuild,statuscode):
    print("In status block")
    print(statuscode)
    if projectbuild == statuscode:
        status_code = flask.Response(status=success)
        return status_code
        form = InfoForm()
        
        #session['form.projectname.data'] = ''
        #session['form.projectdescription.data']= ''
            
        return redirect(url_for("thankyou"))
        
    else:
        return render_template('projectsuccess.html')

@app.route('/thankyou')
def thankyou():
    return render_template('projectsuccess.html')

if __name__== '__main__':
    app.run()
    