import logging

def pingAuthentication(data):
	if "session_username" in data:
		return {"PONG_AUTH": "PONG_AUTH"}
	else:
		return {"Ruh Roh": "How did we get this far??"}