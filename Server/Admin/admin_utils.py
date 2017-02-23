import json
import datetime
import subprocess
from models import ServerStats, AdminUsers
from channels import Group, channel_layers
from django.db import connection
from User.userhelper import verifyPassword
from Server.config import START_DATETIME


def login(username, password):
	"""
	Attempt to authenticate the admin user
	"""
	admin = AdminUsers.objects.filter(username=username)
	if admin:
		admin = admin[0]
		return verifyPassword(password, admin.password)

	return False

def send_keepalive_ping():
	"""
	Helper function to send a ping to the client.
	Was intended to help daphne determine which socket connections have expired.
	Cleanup doesn't seem to be working well, this will likely go away.
	"""
	Group("activeUsers").send({"text": json.dumps({"PING": "PING"})})

def get_num_active_users():
	"""
	Obtain the number of websockets connected to the server
	"""
	return len(channel_layers.backends['default'].channel_layer.group_channels('activeUsers'))

def get_server_uptime():
	"""
	Obtain the amount of time the server has been up and running
	"""
	return datetime.datetime.now() - START_DATETIME

def get_local_disk_usage():
	"""
	Obtains the local disk usage for the server using the df command
	"""
	total_disk_size = subprocess.check_output("df -h / | tail -1 | awk '{print $2}'", shell=True)
	used_disk_amount = subprocess.check_output("df -h / | tail -1 | awk '{print $3}'", shell=True)

	return used_disk_amount, total_disk_size

def get_total_db_rows():
	"""
	Calculates the total number of rows in all of the tables
	"""
	with connection.cursor() as cursor:
		cursor.execute("SELECT SUM(n_live_tup) FROM (SELECT schemaname,relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC) asdf;")
		row = cursor.fetchone()
		row_count = row[0]

	return row_count

def get_all_command_perf_data():
	"""
	Obtains all of the performance data for requests
	"""
	request_duration = ServerStats.objects.filter(name='request_duration')
	if request_duration:
		request_duration = request_duration[0]
		data = json.loads(request_duration.value)
		
		commands = []
		average_data = {"value": data["average"]["value"], "total": data["average"]["total"]}
		fastest_data = {"value": float("inf"), "name": None}
		slowest_data = {"value": -1.0, "name": None}
		for cmd in data['commands']:
			total = data['commands'][cmd]['average_time']['total']
			average = data['commands'][cmd]['average_time']['value']
			fastest = data['commands'][cmd]['fastest_time']
			slowest = data['commands'][cmd]['slowest_time']
			commands.append({"name": cmd, "total": total, "average": average, "fastest": fastest, "slowest": slowest})

			if fastest < fastest_data["value"]:
				fastest_data["value"] = fastest
				fastest_data["name"] = cmd

			if slowest > slowest_data["value"]:
				slowest_data["value"] = slowest
				slowest_data["name"] = cmd

		return commands, average_data, fastest_data, slowest_data
	else:
		commands = []
		average_data = {"value": "<No Requests>", "total": 0}
		fastest_data = {"value": "<No Requests>", "name": "-"}
		slowest_data = {"value": "<No Requests>", "name": "-"}
		return commands, average_data, fastest_data, slowest_data

def _calculate_new_average(average, total, new_value):
	"""
	Helper function to re-calculate an average
	"""
	return ((average * total) + new_value) / (total + 1)

def archive_request_duration(start_time, end_time, command):
	"""
	Archive request statistics for every request to the server.
	This function should be run in a separate thread.
	"""
	request_duration = ServerStats.objects.filter(name='request_duration')
	request_time = (end_time - start_time) * 1000

	if request_duration:

		# Obtain the request_duration entry
		request_duration = request_duration[0]
		data = json.loads(request_duration.value)

		# Obtain the request average and total
		average = float(data['average']['value'])
		total = int(data['average']['total'])

		# Calculate the new average
		data['average']['value'] = _calculate_new_average(average, total, request_time)
		data['average']['total'] = total + 1

		# First time the command is getting archived
		if not command in data['commands']:
			data["commands"][command] = {}
			data["commands"][command]['fastest_time'] = request_time
			data["commands"][command]['slowest_time'] = request_time
			data["commands"][command]['average_time'] = {"value": request_time, "total": 1}

		# Command has already been archived, update its data
		else:
			# Calculate whether the request sets a fastest or slowest record for the command
			fastest_time = float(data["commands"][command]['fastest_time'])
			slowest_time = float(data["commands"][command]['slowest_time'])
			if request_time < fastest_time:
				data["commands"][command]['fastest_time'] = request_time
			elif request_time > slowest_time:
				data["commands"][command]['slowest_time'] = request_time

			# Re-calculate the average request time for the command
			average_time = float(data["commands"][command]['average_time']['value'])
			total = int(data["commands"][command]['average_time']['total'])
			data["commands"][command]['average_time']['total'] = total + 1
			data["commands"][command]['average_time']['value'] = _calculate_new_average(average_time, total, request_time)

	else:
		# Request stats don't exist, create an entry for it
		request_duration = ServerStats()
		request_duration.name = 'request_duration'

		data = {
			"average": {"value": str(request_time), "total": 1},
			"commands": {command: {"fastest_time": request_time, "slowest_time": request_time, "average_time": {"value": request_time, "total": 1}}}
		}

	# Update the stats data
	request_duration.value = json.dumps(data)
	request_duration.save()