from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.template.context_processors import csrf
from admin_utils import *
from User.models import Users


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
			ram_usage, total_ram, ram_percent = get_local_ram_usage()
			commands, average, fastest, slowest = get_all_command_perf_data()
			users = get_all_users()
			classes = get_all_classes()
			stats = get_all_stats()

			context['num_users_connected'] = get_num_active_users()
			context['uptime'] = str(get_server_uptime())
			context['used_disk_amount'] = str(used_disk_amount)
			context['total_disk_size'] = str(total_disk_size)
			context['db_row_count'] = str(get_total_db_rows())
			context['cpu_usage'] = str(get_local_cpu_usage())
			context['ram_usage'] = str(ram_usage)
			context['total_ram'] = str(total_ram)
			context['ram_percent'] = str(ram_percent)
			context['average_request_time'] = str(average["value"]) + " ms"
			context['total_num_requests'] = average["total"]
			context['slow_cmd'] = slowest["name"]
			context['slow_time'] = str(slowest["value"]) + " ms"
			context['fast_cmd'] = fastest["name"]
			context['fast_time'] = str(fastest["value"]) + " ms"
			context['commands'] = commands
			context['users'] = users
			context['classes'] = classes
			context['stats'] = stats
			context['class_stat_mapping'] = get_class_stat_mapping()
			print(str(context['class_stat_mapping']))
			context['total_registered_users'] = len(users)
			context['num_new_users'] = get_num_new_users(users)

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
				session['admin'] = username
			else:
				pass
		elif form_type == 'edit-user':
			user_id = request.POST['user_id']
			username = request.POST['username']
			email = request.POST['email']
			level = request.POST['level']
			experience = request.POST['experience']

			user = Users.objects.filter(id=user_id).first()
			if user:
				user.username = username
				user.email = email
				user.level = level
				user.experience = experience
				user.save()
		elif form_type == 'balancing':
			mapping = {}
			for identifier, val in request.POST.iteritems():
				if identifier == 'form-type':
					continue

				split = identifier.find('_')
				clazz = identifier[0:split]
				stat = identifier[split + 1:]
				
				if clazz not in mapping:
					mapping[clazz] = {}

				mapping[clazz][stat] = val

			update_class_stats(mapping)

		if 'admin' in session:
			context['admin'] = session['admin']

		context.update(csrf(request))
		return redirect('/admin')