from django.shortcuts import render
from django.http import JsonResponse
import json

# Create your views here.

def attack(request, game_id):
	if request.method != 'PUT':
		raise Exception("NO PUT")

	info = json.loads(request.body)

	if not info:
		raise Exception("NO JSON")

	print info['target']

	return JsonResponse({"Success": True, "Magic": 22})