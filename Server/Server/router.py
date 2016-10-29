from channels.routing import route

channel_routing = [
    route('websocket.receive', 'Communication.router.processRequest')
]