#coding=utf-8
import logging
#logging.basicConfig(level=logging.DEBUG)

from spyne.application import Application
from spyne.decorator import srpc
from spyne.service import ServiceBase
from spyne.model.primitive import Integer
from spyne.model.primitive import Unicode

from spyne.model.complex import Iterable

from spyne.protocol.soap import Soap11

from spyne.server.wsgi import WsgiApplication

class HelloWorldService(ServiceBase):
    @srpc(Unicode, Integer, _returns=Iterable(Unicode))
    def say_hello(name, times):
        for i in range(times):
            yield 'Hello, %s' % name

application = Application([HelloWorldService],
    tns='spyne.examples.hello',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

if __name__ == '__main__':
        # You can use any Wsgi server. Here, we chose
        # Python's built-in wsgi server but you're not
        # supposed to use it in production.
        from wsgiref.simple_server import make_server
        print '127.0.0.1'+':'+'8000'+' server is running WSGI.......'
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
        
        logging.info("listening to http://127.0.0.1:8000")
        logging.info("wsdl is at: http://localhost:8000/?wsdl")        
        wsgi_app = WsgiApplication(application)
        server = make_server('0.0.0.0', 8000, wsgi_app)
        server.serve_forever()
        
        
        
        