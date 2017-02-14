from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.template.context_processors import csrf

# Create your views here.

class AdminView(TemplateView):
	template_name = 'admin.html'

	def get(self, request, *args, **kwargs):
		context = self.get_context_data(**kwargs)
		context.update(csrf(request))
		return self.render_to_response(context)