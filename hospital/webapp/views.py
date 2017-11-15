# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
import MySQLdb
import base64
from django.shortcuts import render,redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
import hashlib
# Create your views here.
dbms_host = "shivam7.mysql.pythonanywhere-services.com"
dbms_user = "shivam7"
dbms_pword = "Sd08051995"
dbms_db = "shivam7$dbms"
limitOfPatients = 2

def check(request):
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor  = db.cursor()
	tables = ["admins","doctor","patient"]
	email = request.session["email"]
	pword  = request.session["pword"]
	for tb in tables:
		SQL = "select name from %s where email='%s' and password='%s'"%(tb,email,pword)
		cursor.execute(SQL)
		data = cursor.fetchall()
		if len(data)!=0:
			request.session["name"] = data[0][0]
			request.session["type"] = tb
			cursor.close()
			db.close()
			return	1
	request.session.clear()
	cursor.close()
	db.close()
	return 0

def login(request):
	if request.method == "POST":
		email = request.POST["email"]
		db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		context={}
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		SQL = "select password('%s')"%(request.POST["pword"])
		cursor.execute(SQL)
		pword = cursor.fetchall()[0][0]
		request.session["email"] = email
		request.session["pword"] = pword
		request.session.set_expiry(0)
		cursor.close()
		db.close()
		if check(request):
			return home(request)
		else:
			context = {"message":"Incorrect credentials."}
		return render(request,'webapp/login.html',context)
	else:
		db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		context={}
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		cursor.close()
		db.close()
		return render(request,'webapp/login.html',context)


def home(request):
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	cursor.execute("select distinct specialization from doctor")
	context['specialization'] = cursor.fetchall()
	context['specialization'] = [x[0] for x in context['specialization']]
	cursor.execute("select image from images where purpose = 'carousel'")
	context["carousel"] = cursor.fetchall()
	context["carousel"] = [ x[0] for x in context["carousel"]]

	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]


	# return HttpResponse(context["carousel"])
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"]=request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	cursor.close()
	db.close()
	return render(request,'webapp/home.html',context)

def admin(request):
	context = {}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
	else:
		context["name"]=""
		context["type"]=""
	if request.session.has_key("name") and request.session.has_key("type") and request.session["type"] == "admins":
		#logged in
		db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
		cursor = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		cursor.execute('show tables')
		data = cursor.fetchall()
		tables = [entry[0] for entry in data]
		message = "%s logged in!"%(request.session["name"])
		cursor.close()
		db.close()
		context["tables"] = tables
		context["message"] = message
		return render(request,'webapp/admin.html',context)
	else:
		db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		context={}
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		cursor.close()
		db.close()
		return render(request,'webapp/login.html',context)



def alterdb(request):
	context = {}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
	else:
		context["name"]=""
		context["type"]=""

	q1 = request.POST['method']
	tb = request.POST['table']
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	if q1== "Add":
		context['table_name']=tb
		SQL = "describe %s"%(tb)
		cursor.execute(SQL)
		context['table_details']=cursor.fetchall()
		# if any of the attributes contain patient, any of them contain doctor
		for field in context['table_details']:
			if "patientID" in field:
				cursor.execute("select id,aadharNo,name from patient")
				context["patientID"] = cursor.fetchall()
				context["patientID"] = [ str(str(int(x[0]))+", "+str(x[1])+", "+str(x[2]))for x in context["patientID"]]
		for field in context['table_details']:
			if "doctorID" in field:
				cursor.execute("select id,aadharNo,name from doctor")
				context["doctorID"] = cursor.fetchall()
				context["doctorID"] = [ str(str(int(x[0]))+", "+str(x[1])+", "+str(x[2])) for x in context["doctorID"]]
		for field in context['table_details']:
			if "appID" in field:
				cursor.execute("select a.id, d.name, p.name from appointment a, doctor d, patient p where a.doctorID = d.id and a.patientID=p.id")
				context["appID"] = cursor.fetchall()
				context["appID"] = [ str(str(int(x[0]))+", "+str(x[1])+", "+str(x[2])) for x in context["appID"]]
		cursor.close()
		db.close()
		return render(request,'webapp/add.html',context)
	elif q1=="View/Delete":
		context['table_name'] = tb
		SQL = "select * from %s"%(tb)
		cursor.execute(SQL)
		context['table_details']=cursor.fetchall()
		SQL = "describe %s"%(tb)
		cursor.execute(SQL)
		data = cursor.fetchall()
		data= [x[0] for x in data]
		context['table_field'] = data
		cursor.close()
		db.close()
		return render(request,'webapp/delete.html',context)

def add(request):
	context = {}
	if request.session.has_key("name"):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
	else:
		context["name"]=""
		context["type"]=""

	table = request.POST['table']
	if table=="images":
		img = request.FILES["image"]
		x = img.read()
		imgenc = base64.encodestring(x)
		db  = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		cursor.execute("insert into images (purpose, image) values('%s','%s')"%(request.POST["purpose"],imgenc))
		db.commit()

		context["message"] = "Data inserted!"
		context['table_name']=table
		cursor.execute("describe %s"%(table))
		context['table_details']=cursor.fetchall()
		cursor.close()
		db.close()
		return render(request,'webapp/add.html',context)
	else:

		l1 = []
		l2 = []
		for x in request.POST:
			if 'csrf' not in x and 'submit' not in x and 'table' not in x:
				y = request.POST[x]
				if x=="patientID":
					y = y.split(",")[0]
				elif x=="doctorID":
					y = y.split(",")[0]
				l1.append(str(x))
				if x=="password":
					l2.append("password('"+str(y)+"')")
				else:
					l2.append("'"+str(y)+"'")
		s1 = "("+",".join([i for i in l1])+")"
		s2 = "values(" + ",".join([i for i in l2])+")"
		SQL = "insert into "+table+s1+" "+s2;
		# return HttpResponse(SQL);
		db=MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
		cursor = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		context['table_name']=table
		cursor.execute("describe %s"%(table))
		context['table_details']=cursor.fetchall()
		try:
			cursor.execute(SQL)
			db.commit()
			context["message"] = "Data inserted!"
			cursor.close()
			db.close()
			return render(request,'webapp/add.html',context)
		except:
			context["message"] = "Contraints violated!"
			cursor.close()
			db.close()
			return render(request,'webapp/add.html',context)
def delete(request):
	context={}
	if request.session.has_key("name"):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
	else:
		context["name"]=""
		context["type"]=""

	l = request.POST.getlist("id")
	field = request.POST["field"]
	table = request.POST["table"]
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	s=""
	for val in l:
		if field != 'id':
			SQL = "delete from %s where %s=%s"%(table,field,"'"+str(val)+"'")
		else:
			SQL = "delete from %s where %s=%s"%(table,field,val)
		cursor.execute(SQL)
	db.commit()
	context['table_name'] = table
	SQL = "select * from %s"%(table)
	cursor.execute(SQL)
	context['table_details']=cursor.fetchall()
	SQL = "describe %s"%(table)
	cursor.execute(SQL)
	data = cursor.fetchall()
	data= [x[0] for x in data]
	context['table_field'] = data
	context['message'] = 'Deleted Successfully!'
	cursor.close()
	db.close()
	return render(request,'webapp/delete.html',context)

def team (request):
	context={}
	if request.session.has_key("name"):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
	else:
		context["name"]=""
		context["type"]=""

	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	SQL = ""
	if request.method != 'POST':
		SQL= "select aadharNo, name, gender, age, phone, email, specialization from doctor"
	else:
		SQL = "select aadharNo, name, gender, age, phone, email, specialization from doctor where specialization='%s'"%(request.POST['specialization'])
	cursor.execute(SQL)
	context['data'] = cursor.fetchall()
	context["fields"]=['aadharNo', 'name', 'gender', 'age', 'phone', 'email', 'specialization']
	cursor.close()
	db.close()
	return render(request,'webapp/team.html',context)

def logout (request):
	request.session.clear()
	return home(request)

def verifymail(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	if request.method == 'POST':
		email_id=request.POST.get('email')
		if email_id:
			current_site = get_current_site(request)
			message = render_to_string('acc_active_email.html', {
			    'domain':current_site.domain,
			    'uid': urlsafe_base64_encode(force_bytes(email_id)),
			    'token': account_activation_token.make_token(email_id),
			})
			mail_subject = 'Activate your account.'
			to_email = email_id
			email = EmailMessage(mail_subject, message, to=[to_email])



			try:

				email.send()
				context["message"]="Email sent! Verify your email-id."
				cursor.close()
				db.close()
				return render(request,'webapp/verifymail.html',context)
			except:
				context["message"]="Network issue"
				cursor.close()
				db.close()
				return render(request,'webapp/verifymail.html',context)
	else:
		# render form to input email id to verifymail
		return render(request,'webapp/verifymail.html',context)


def activate(request, uidb64,token):
	# if request.session.has_key('user_id'):
	# 	rollno=request.session.get('user_id')
	# 	return render(request,'blog/homee.html',{'user_id':rollno,'messagee':'Logout from current account to activate other account!!'})
	# else:

	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	cursor.close()
	db.close()


	uid = force_text(urlsafe_base64_decode(uidb64))
	uid=uid.encode('utf-8')
	if uid and account_activation_token.check_token(uid, token):
		context["email"]=uid
		return render(request,'webapp/signup.html',context)
	else:
		context["message"]="Activate your account"
		return render(request,'webapp/verifymail.html',context)



def signup(request):
	if request.method == "POST":
		s1 = "("
		s2 = "("
		for k in request.POST:
			if "csrf" not in k:
				if k=="password":
					s1+=k+","
					s2+="password('"+request.POST[k]+"'),"
				else:
					s1+=k+","
					s2+="'"+request.POST[k]+"'"+","
		s1 = s1[:-1]
		s1 =s1+")"
		s2 = s2[:-1];
		s2 = s2+")"

		db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
		cursor = db.cursor()
		context={}
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		SQL = "select password('%s')"%(request.POST["password"])
		cursor.execute(SQL)
		pword = cursor.fetchall()[0][0]
		SQL = "insert into patient %s values %s"%(s1,s2)
		try:
			cursor.execute(SQL)
			db.commit()
			cursor.close()
			db.close()
			request.session["name"] = request.POST["name"]
			request.session["type"] = "patient"
			request.session["email"]=request.POST["email"]
			request.session["pword"] = pword
			return home(request)
		except:
			cursor.close()
			db.close()
			context["message"]="Email-id already registered!"
			return render(request,'webapp/signup.html',context)
	else:

		db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		context={}
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		cursor.close()
		db.close()
		return render(request,'webapp/verifymail.html',context)

def appointment(request):
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	cursor.execute("select distinct specialization from doctor")
	context["specialization"] = cursor.fetchall()
	context["specialization"] = [x[0] for x in context["specialization"]]
	data = []
	for sp in context["specialization"]:
		lt = [sp]
		cursor.execute("select  name,id from doctor where specialization='%s'"%(sp))
		lt.extend(cursor.fetchall())
		data.append(lt)
		# return HttpResponse(lt)
	context['data'] = data
	if request.method == "POST":
		doctorID = request.POST["doctorID"]
		specialization = request.POST["specialization"]
		date = request.POST["date"]
		db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
		cursor = db.cursor()

		# return HttpResponse("select id from patient where email = '%s'"%(request.session["email"]))
		cursor.execute("select id from patient where email = '%s'"%(request.session["email"]))
		data =  cursor.fetchall()
		patientID =data[0][0]



		# return HttpResponse("select count(id) from appointment where doctorID = '%s' and date = '%s'"%(doctorID,date))
		cursor.execute("select count(id) from appointment where doctorID = '%s' and date = '%s'"%(doctorID,date))
		data = cursor.fetchall()
		q = data[0][0]
		if q >= limitOfPatients:
			context["message"]="No slots available on chosen date, choose a different date!"
			return render(request,'webapp/appointment.html',context)
		else:
			cursor.execute("insert into appointment (doctorID, patientID, date) value('%s','%s','%s')"%(doctorID,patientID,date))
			db.commit()
			# cursor.execute("select id from appointment where ")
			cursor.execute("insert into bill (appID,amount,paid,date) values(last_insert_id(),500,0,curdate())")
			db.commit()
			context["message"]="Appointment made, bill pending!"

			# context["message"]="Some error occured"
		cursor.close()
		db.close()
		return render(request,'webapp/appointment.html',context)
	else:
		context["message"]= "Appointment Fee - 500/-"
		return render(request,'webapp/appointment.html',context)

def profile(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	if request.session["type"] == "patient":
		db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
		cursor  = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		# get patient id
		cursor.execute("select id from patient where email = '%s'"%(request.session["email"]))
		data =  cursor.fetchall()
		patientID =data[0][0]



		# appointment
		cursor.execute("describe appointment")
		context["appointment_details"] = cursor.fetchall()
		cursor.execute("select a.id, d.name, a.date from appointment a, doctor d where a.doctorID=d.id and a.date < curdate() and a.patientID='%s'"%(patientID))
		context["appointment_done"] = cursor.fetchall()
		cursor.execute("select a.id, d.name, a.date from appointment a, doctor d where a.doctorID=d.id and a.date >= curdate() and a.patientID='%s'"%(patientID))
		context["appointment_coming"]=cursor.fetchall()

		# record details
		cursor.execute("describe record")
		context["record_details"] = cursor.fetchall()
		cursor.execute("select r.appID, d.name, a.date, r.remarks from record r, appointment a, doctor d where r.appID= a.id and a.doctorID=d.id and a.patientID=%s"%(patientID))
		context["record"]=cursor.fetchall()

		# report details
# 		cursor.execute("describe report")
# 		context["report_details"] = cursor.fetchall()
# 		cursor.execute("select * from report where patientID=%s"%(patientID))
# 		context["report"]=cursor.fetchall()

		# bill details
		cursor.execute("describe bill")
		context["bill_details"] = cursor.fetchall()
		cursor.execute("select b.id, b.appID, b.amount, b.paid, b.date from bill b, appointment a where b.appID=a.id and a.patientID=%s"%(patientID))
		context["bill"]=cursor.fetchall()


		cursor.close()
		db.close()
		return render(request,'webapp/patient.html',context)
	elif request.session["type"] == "doctor":
		db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		cursor.execute("describe appointment")
		context["app_details"] = cursor.fetchall()
		cursor.execute("select id from doctor where email='%s'"%(request.session["email"]))
		data = cursor.fetchall()
		doctorID = data[0][0]
		cursor.execute("select a.id, p.name, a.date, a.patientID from appointment a, patient p where a.patientID=p.id and a.doctorID='%s' and a.date>= curdate()"%(doctorID))
		context["app"] = cursor.fetchall()
		cursor.close()
		db.close()
		return render(request,'webapp/doctor.html',context)

def exp(request):
	return render(request,"webapp/exp.html")

def delapp(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
	cursor = db.cursor()
	cursor.execute("delete from appointment where id='%s'"%(request.POST["del"]))
	db.commit()
	cursor.close()
	db.close()
	return profile(request)

def contact(request):
	db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	cursor.close()
	db.close()
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	return render(request,'webapp/contact.html',context)

def about(request):
	db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	cursor.close()
	db.close()
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	return render(request,'webapp/about.html',context)

def pay(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""

	if request.session.has_key("name") and check(request) and request.session["type"]=="patient":
		db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		if request.method =="POST":
			cursor.close()
			db.close()
			pass
		else:
			cursor.execute("select id from patient where email = '%s'"%(request.session["email"]))
			data =  cursor.fetchall()
			patientID =data[0][0]

			cursor.execute("describe bill")
			context["bill_details"]=cursor.fetchall()

			cursor.execute("select b.id, b.appID, b.amount, b.paid, b.date from bill b, appointment a where b.appID=a.id and a.patientID=%s"%(patientID))
			data = cursor.fetchall()
			context["bill"]=data
			cursor.close()
			db.close()
			return render(request, 'webapp/pay.html', context)
	else:
		db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		cursor.execute("select image from images where purpose like 'logo'")
		context["logo"] = cursor.fetchall()
		context["logo"] = [ x[0] for x in context["logo"]]
		context["message"] = "You need to login (as a patient) first in order to avail this facility"
		cursor.close()
		db.close()
		return render(request, 'webapp/login.html',context)


def recordPayment(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
	cursor = db.cursor()
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	if request.method=="POST":
		cursor.execute("update bill set paid=amount where id='%s'"%(request.POST["id"]))
		db.commit()
		cursor.close()
		db.close()
		return admin(request)
	else:
		cursor.execute("select b.id, b.appID, p.name, b.amount - b.paid, b.date from bill b, appointment a, patient p where b.appID=a.id and a.patientID=p.id")
		data = cursor.fetchall()
		context["bill"]= data
		cursor.close()
		db.close()
		return render(request,'webapp/recordPayment.html',context)


def searchPatient(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
	cursor = db.cursor()
	cursor.execute("select image from images where purpose like 'logo'")
	context["logo"] = cursor.fetchall()
	context["logo"] = [ x[0] for x in context["logo"]]
	if request.method == "POST":
	    pid = request.POST["id"]
	    cursor.execute("select r.appID, r.remarks, a.date from record r, appointment a where r.appID=a.id and a.patientID='%s'"%(pid))
	    context["record"]=cursor.fetchall()
	    return render(request,'webapp/showPatient.html',context)

