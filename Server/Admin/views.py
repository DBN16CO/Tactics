from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.template.context_processors import csrf
from models import ServerStats
from admin_utils import *


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

			send_keepalive_ping()
			used_disk_amount, total_disk_size = get_local_disk_usage()
			slow_cmd, slow_time = get_slowest_command()
			fast_cmd, fast_time = get_fastest_command()

			context['num_users_connected'] = get_num_active_users()
			context['uptime'] = str(get_server_uptime())
			context['used_disk_amount'] = str(used_disk_amount)
			context['total_disk_size'] = str(total_disk_size)
			context['db_row_count'] = str(get_total_db_rows())
			context['average_request_time'] = str(get_average_request_time()) + " ms"
			context['total_num_requests'] = get_total_num_requests()
			context['slow_cmd'] = slow_cmd
			context['slow_time'] = str(slow_time) + " ms"
			context['fast_cmd'] = fast_cmd
			context['fast_time'] = str(fast_time) + " ms"

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