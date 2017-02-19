import json
import time
import datetime
import subprocess
from models import ServerStats
from channels import Group, channel_layers
from django.db import connection
from Server.config import START_DATETIME


def login(username, password):
	return True

def send_keepalive_ping():
	Group("activeUsers").send({"text": json.dumps({"PING": "PING"})})

def get_num_active_users():
	return len(channel_layers.backends['default'].channel_layer.group_channels('activeUsers'))

def get_server_uptime():
	return datetime.datetime.now() - START_DATETIME

def get_local_disk_usage():
	total_disk_size = subprocess.check_output("df -h / | tail -1 | awk '{print $2}'", shell=True)
	used_disk_amount = subprocess.check_output("df -h / | tail -1 | awk '{print $3}'", shell=True)

	return used_disk_amount, total_disk_size

def get_total_db_rows():
	with connection.cursor() as cursor:
		cursor.execute("SELECT SUM(n_live_tup) FROM (SELECT schemaname,relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC) asdf;")
		row = cursor.fetchone()
		row_count = row[0]

	return row_count

def get_average_request_time():
	request_duration = ServerStats.objects.filter(name='request_duration')
	if request_duration:
		request_duration = request_duration[0]
		request_duration_data = json.loads(request_duration.value)
		average_request_time = float(request_duration_data['average']['value']) * 1000
	else:
		average_request_time = '<No Requests>'

	return average_request_time

def get_total_num_requests():
	request_duration = ServerStats.objects.filter(name='request_duration')
	if request_duration:
		request_duration = request_duration[0]
		request_duration_data = json.loads(request_duration.value)
		total_num_requests = request_duration_data['average']['total']
	else:
		total_num_requests = '0'

	return total_num_requests

def archive_request_duration(start_time, end_time, command):
	request_duration = ServerStats.objects.filter(name='request_duration')
	if request_duration:

		# Obtain the request_duration entry
		request_duration = request_duration[0]
		data = json.loads(request_duration.value)

		# Obtain the request average and total
		average = float(data['average']['value'])
		total = int(data['average']['total'])

		# Calculate the new average and total
		new_total = total + 1
		new_average = ((average * total) + (end_time - start_time)) / new_total
		data['average']['value'] = str(new_average)
		data['average']['total'] = str(new_total)

		# Update the stats data
		request_duration.value = json.dumps(data)
		request_duration.save()
	else:
		request_duration = ServerStats()
		request_duration.name = 'request_duration'
		request_duration.value = json.dumps({"average": {"value": str(end_time - start_time), "total": 1}})
		request_duration.save()