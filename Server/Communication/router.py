def processRequest(message):
	request = message.content['text']
	print 'Received: ' + request
	message.reply_channel.send({
		'text': request,
	})