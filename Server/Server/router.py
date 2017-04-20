from channels.routing import route
from Communication.router import *

channel_routing = [
	route('websocket.connect', connect),
	route('websocket.disconnect', disconnect),
	route('websocket.receive', processRequest)
]