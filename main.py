import argparse
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('depends')
sys.path.append(os.path.join('depends', 'waitress'))
import bottle
from bottle import hook, redirect, request, route
import waitress

root_path = None
def full_path(path):
    return os.path.abspath(os.path.join(root_path, path))

def list_path(path):
    for f in os.listdir(path):
        fullpath = full_path(f)
        if not os.path.isfile(fullpath):
            continue
        yield f

@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')

@route('/')
def s_root():
    redirect('/list')

@route('/list')
def s_list():
    for chunk in s_list_path('.'):
        yield chunk

@route('/list/<path:path>')
def s_list_path(path):
    if os.path.isdir(full_path(path)):
        yield '<ul>'
        for f in list_path(root_path):
            yield '<li><a href="/list/{0}">{0}</a></li>'.format(f)
        yield '</ul>'
    else:
        pass

class Adapter(bottle.WaitressServer):
    def run(self, handler):
        waitress.serve(handler, host=self.host, port=self.port, threads=self.options['threads'])

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('root', help='Root path')
parser.add_argument("--help", action="help", help="show this help message and exit")
parser.add_argument('-h', '--host', help='Host', default='0.0.0.0')
parser.add_argument('-p', '--port', type=int, help='Port', default=8000)
parser.add_argument('-t', '--threads', type=int, help='Number of threads', default=6)

if __name__ == '__main__':
    args = parser.parse_args()
    root_path = args.root
    app = bottle.app()
    app.run(server=Adapter(host=args.host, port=args.port, threads=args.threads))
