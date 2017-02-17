import json
import datetime
import subprocess
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.template.context_processors import csrf
from django.db import connection
from channels import Group, channel_layers
from admin_utils import *
from Server.config import START_DATETIME



class AdminView(TemplateView):
	template_name = 'admin.html'

	def get(self, request, *args, **kwargs):
		session = request.session
		context = self.get_context_data(**kwargs)
		context.update(csrf(request))

		if 'logout' in request.GET:
			del session['admin']
			return redirect('/admin')

		if 'admin' in session:
			context['admin'] = session['admin']

			Group("activeUsers").send({"text": json.dumps({"PING": "PING"})})
			num_users_connected = len(channel_layers.backends['default'].channel_layer.group_channels('activeUsers'))
			uptime = datetime.datetime.now() - START_DATETIME

			total_disk_size = subprocess.check_output("df -h / | tail -1 | awk '{print $2}'", shell=True)
			used_disk_amount = subprocess.check_output("df -h / | tail -1 | awk '{print $3}'", shell=True)
			
			with connection.cursor() as cursor:
				cursor.execute("SELECT SUM(n_live_tup) FROM (SELECT schemaname,relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC) asdf;")
				row = cursor.fetchone()
				row_count = row[0]

			context['num_users_connected'] = num_users_connected
			context['uptime'] = str(uptime)
			context['used_disk_amount'] = str(used_disk_amount)
			context['total_disk_size'] = str(total_disk_size)
			context['db_row_count'] = str(row_count)

		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		session = request.session
		context = self.get_context_data(**kwargs)
		
		form_type = request.POST['form-type']

		if form_type == 'login':
			username = request.POST['username']
			password = request.POST['password']

			success = login(username, password)
			if success:
				print("Login Success")
				session['admin'] = username
			else:
				print("Login Failed")

		if 'admin' in session:
			context['admin'] = session['admin']

		context.update(csrf(request))
		return redirect('/admin')