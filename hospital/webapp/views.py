# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse
import MySQLdb
import base64
# Create your views here.
dbms_host = "localhost"
dbms_user = "root"
dbms_pword = "root"
dbms_db = "dbms"
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
			db.close()
			return	1
	del request.session["email"]
	del request.session["pword"]
	return 0

def login(request):
	if request.method == "POST":
		email = request.POST["email"]
		db = MySQLdb.connect(dbms_host,dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		SQL = "select password('%s')"%(request.POST["pword"])
		cursor.execute(SQL)
		pword = cursor.fetchall()[0][0]
		request.session["email"] = email
		request.session["pword"] = pword
		request.session.set_expiry(0)
		if check(request):
			return home(request)
		else:
			context = {"message":"Incorrect credentials."}
		return render(request,'webapp/login.html',context)
	else:
		return render(request,'webapp/login.html')
	

def home(request):
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	context={}
	cursor.execute("select distinct specialization from doctor")
	context['specialization'] = cursor.fetchall()
	context['specialization'] = [x[0] for x in context['specialization']]
	cursor.execute("select image from images where purpose = 'carousel'")
	context["carousel"] = cursor.fetchall()
	context["carousel"] = [ x[0] for x in context["carousel"]]
	# return HttpResponse(context["carousel"])
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"]=request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
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
		cursor.execute('show tables')
		data = cursor.fetchall()
		tables = [entry[0] for entry in data]
		message = "%s logged in!"%(request.session["name"])
		db.close()
		context["tables"] = tables
		context["message"] = message
		return render(request,'webapp/admin.html',context)
	else:
		#you need to login
		return render(request,'webapp/login.html')



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
				cursor.execute("select id,patientemail,doctoremail from appointment")
				context["appID"] = cursor.fetchall()
				context["appID"] = [ str(str(int(x[0]))+", "+str(x[1])+", "+str(x[2])) for x in context["appID"]]
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

		cursor.execute("insert into images (purpose, image) values('%s','%s')"%(request.POST["purpose"],imgenc))
		db.commit()

		context["message"] = "Data inserted!"
		context['table_name']=table
		cursor.execute("describe %s"%(table))
		context['table_details']=cursor.fetchall()
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
		context['table_name']=table
		cursor.execute("describe %s"%(table))
		context['table_details']=cursor.fetchall()
		try:
			cursor.execute(SQL)
			db.commit()
			context["message"] = "Data inserted!"
			db.close()
			return render(request,'webapp/add.html',context)
		except:
			context["message"] = "Contraints violated!"
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
	SQL = ""
	if request.method != 'POST':
		SQL= "select aadharNo, name, gender, age, phone, email, specialization from doctor"
	else:
		SQL = "select aadharNo, name, gender, age, phone, email, specialization from doctor where specialization='%s'"%(request.POST['specialization'])
	cursor.execute(SQL)
	context['data'] = cursor.fetchall()
	context["fields"]=['aadharNo', 'name', 'gender', 'age', 'phone', 'email', 'specialization']
	db.close()
	return render(request,'webapp/team.html',context)

def logout (request):
	request.session.clear()
	return home(request)

def signup(request):
	if request.method == "POST":
		s1 = "("
		s2 = "("
		for k in request.POST:
			if "csrf" not in k:
				s1+=k+","
				s2+="'"+request.POST[k]+"'"+","
		s1 = s1[:-1]
		s1 =s1+")"
		s2 = s2[:-1];
		s2 = s2+")"
		SQL = "insert into patient %s values %s"%(s1,s2)
		db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
		cursor = db.cursor()
		# return HttpResponse(SQL)
		try:
			cursor.execute(SQL)
			db.commit()
			db.close()
			request.session["name"] = request.POST["name"]
			request.session["type"] = "patient"
			request.session["email"]=request.POST["email"]
			db.close()
			return home(request)
		except:
			context={}
			context["message"]="Email-id already registered!"
			db.close()
			return render(request,'webapp/signup.html',context)


	else:
		return render(request,'webapp/signup.html')

def appointment(request):
	db = MySQLdb.connect(dbms_host,dbms_user,dbms_pword,dbms_db)
	cursor = db.cursor()
	context={}
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
			cursor.execute("insert into bill (patientID,amount,paid,date) values(%s,500,0,curdate())"%(patientID))
			db.commit()
			context["message"]="Appointment made, bill pending!"
		
			# context["message"]="Some error occured"
		db.close()
		return render(request,'webapp/appointment.html',context)
	else:
		context["message"]= "Appointment Fee - 500/-"
		db.close()
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
		# get patient id
		cursor.execute("select id from patient where email = '%s'"%(request.session["email"]))
		data =  cursor.fetchall()
		patientID =data[0][0]



		# appointment
		cursor.execute("describe appointment")
		context["appointment_details"] = cursor.fetchall()
		cursor.execute("select * from appointment where date < curdate() and patientID='%s'"%(patientID))
		context["appointment_done"] = cursor.fetchall()
		cursor.execute("select * from appointment where date >= curdate() and patientID='%s'"%(patientID))
		context["appointment_coming"]=cursor.fetchall()

		# record details
		cursor.execute("describe record")
		context["record_details"] = cursor.fetchall()
		cursor.execute("select * from record where patientID=%s"%(patientID))
		context["record"]=cursor.fetchall()

		# report details
		cursor.execute("describe report")
		context["report_details"] = cursor.fetchall()
		cursor.execute("select * from report where patientID=%s"%(patientID))
		context["report"]=cursor.fetchall()

		# bill details
		cursor.execute("describe bill")
		context["bill_details"] = cursor.fetchall()
		cursor.execute("select * from bill where patientID=%s"%(patientID))
		context["bill"]=cursor.fetchall()


		db.close()
		return render(request,'webapp/patient.html',context)
	elif request.session["type"] == "doctor":
		db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		cursor.execute("describe appointment")
		context["app_details"] = cursor.fetchall()
		cursor.execute("select id from doctor where email='%s'"%(request.session["email"]))
		data = cursor.fetchall()
		doctorID = data[0][0]
		cursor.execute("select * from appointment where doctorID='%s' and date>= curdate()"%(doctorID))
		context["app"] = cursor.fetchall()
		# return HttpResponse(app)
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
	return profile(request)

def contact(request):
	context={}
	if request.session.has_key("name") and check(request):
		context["name"]=request.session["name"]
		context["type"]=request.session["type"]
		context["email"] =request.session["email"]
	else:
		context["name"]=""
		context["type"]=""
	return render(request,'webapp/contact.html',context)

def about(request):
	context={}
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

	if request.session.has_key("name") and check(request):
		db = MySQLdb.connect(dbms_host, dbms_user, dbms_pword, dbms_db)
		cursor = db.cursor()
		if request.method =="POST":
			pass
		else:
			cursor.execute("select id from patient where email = '%s'"%(request.session["email"]))
			data =  cursor.fetchall()
			patientID =data[0][0]

			cursor.execute("describe bill")
			context["bill_details"]=cursor.fetchall()

			cursor.execute("select * from bill where patientID='%s' order by paid"%(patientID))
			data = cursor.fetchall()
			context["bill"]=data
			return render(request, 'webapp/pay.html', context)
	else:
		context["message"] = "You need to login first in order to avail this facility"
		return render(request, 'webapp/login.html',context)
	