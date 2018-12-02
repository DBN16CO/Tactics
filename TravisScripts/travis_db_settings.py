DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tactics',
        'USER': 'postgres',
        'PASSWORD': 'abc12345',
        'HOST': 'localhost',
        'PORT': '',
    }
}

CHANNEL_LAYERS = {
    'default': {
        #'BACKEND': 'asgiref.inmemory.ChannelLayer',
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("localhost", 6379)],
        },
        'ROUTING': 'Server.router.channel_routing',
    },
}