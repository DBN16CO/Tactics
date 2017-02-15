from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.template.context_processors import csrf
from admin_utils import *



class AdminView(TemplateView):
	template_name = 'admin.html'

	def get(self, request, *args, **kwargs):
		session = request.session
		context = self.get_context_data(**kwargs)
		context.update(csrf(request))

		if 'admin' in session:
			context['admin'] = session['admin']

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
		return self.render_to_response(context)