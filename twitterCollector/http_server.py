from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from api import Api

# TODO validate against PEP8 standard

'''
This class represents very simplified server.
It delegates client's requested actions to be executed server-side.
To make this happen, it waits and process received JSON RPC (Remote Procedure Call)
It allows to execute methods present only within Api class(see api.py)
Available methods are stored inside dictionary, called dispatcher
'''
class Server(object):

    # TODO Werkzeug's authors says that watchdog is more efficient than 'stat'(but default)
    # More about reloaders: http://werkzeug.pocoo.org/docs/0.12/serving/#reloader
    def __init__(self, hostname='localhost', port=4000, reloader_type='stat'):
        self.hostname = hostname
        self.port = port

    '''
    Starts the server
    '''
    def run(self):
        run_simple(self.hostname, self.port, self.application, reloader_type='watchdog')

    '''
    Method responsible for responding to received request
    Technically you can add custom method to dispatcher, like: dispatcher["add"] = lambda a, b: a + b
    But it is highly unwanted, every remote-callable should be inside Api class(see api.py)
    '''
    @Request.application
    def application(self, request):
        response = JSONRPCResponseManager.handle(request.data, dispatcher)
        print(request.data)
        return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    rpc_server = Server(hostname='localhost', port=4000)
    rpc_server.run()