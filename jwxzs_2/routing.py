#-*- coding:utf-8 -*-

from channels.generic.websockets import WebsocketDemultiplexer
from channels.routing import route_class

from checkstudent.bindings import TheCheckBinding

class APIDemultiplexer(WebsocketDemultiplexer):

    consumers = {
      'thecheck': TheCheckBinding.consumer
    }

channel_routing = [
    route_class(APIDemultiplexer)
]









