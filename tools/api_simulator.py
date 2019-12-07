# rest_api_simulator.py, Copyright (c) 2019 Holitics/Phenome Project, Nicholas Saparoff

# Original Implementation

import time, datetime, os, importlib, argparse
import socket, sys, json
from importlib import reload

from http.server import BaseHTTPRequestHandler, HTTPServer
from phenome_core.core.base.basethread import BaseThread

_SIM_DATA = None
_MSGS_RECEIVED = []
_SERVER_TYPE = "HTTP"


class HttpServer(BaseHTTPRequestHandler):

    def do_HEAD(self):
        return

    def do_GET(self):

        # Process possible REST request
        self.respond(self.path)

        return

    def do_POST(self):

        # Process possible JSON RPC request
        request = self.rfile.read(int(self.headers["Content-Length"])).decode()
        self.respond(request)

        return

    def respond(self, request):

        global _SIM_DATA, _MSGS_RECEIVED, _SERVER_TYPE

        content = None
        content_type = "text/html"
        data = None
        status_code = 200

        if _SERVER_TYPE == 'UDP_SERVER':
            # special case, just return the messages received
            content = json.dumps(_MSGS_RECEIVED)
            content_type = "application/json"
        else:

            # get the data by path
            try:
                data = _SIM_DATA.routes[request]
            except Exception as ex:
                print(ex)

            if data is None:
                status_code = 404
                content = "No mapping for request in Simulator Data"
            else:

                #print("route:" + self.path + "  -  DATA = " + content)

                # is data TXT/HTML or JSON?
                if isinstance(data, dict):
                    content = json.dumps(data)
                    content_type = "application/json"
                elif "{" in data:
                    # the json must be in string version already
                    content_type = "application/json"
                else:
                    content = data

        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

        return


class APISimulator(BaseThread):

    def __init__(self):

        super(APISimulator, self).__init__()

        # init defaults
        self.is_json_rpc = False
        self.is_udp_server = False
        self.listening = False
        self.socket = None
        self.server = None
        self.hostname = '127.0.0.1'
        self.port = 80
        self.last_request = None
        self.last_response = None
        self.filename = None

    def __build_arg_parser(self):

        parser = argparse.ArgumentParser(
            description="API Simulator, Copyright 2019 Phenome Project",
            prog='api_simulator',
            epilog="Happy Simulating!")
        parser.add_argument('-port', nargs="?", help='HTTP PORT to listen on', default=80, type=int)
        parser.add_argument('-file', nargs="?", help='Routes file to load', default='sim_data.py', type=str)
        parser.add_argument('-type', nargs="?", help='Type of server (HTTP, JSON_RPC, UDP_SERVER)', default='HTTP', type=str)

        return parser

    def get_last_query(self):
        return self.last_request

    def get_last_response(self):
        return self.last_response

    def stop(self):

        # output the message
        self.__output_message("API SIMULATOR STOPPING")

        self.listening = False

        if self.socket is not None:

            try:
                if self.is_udp_server:
                    closing_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                else:
                    closing_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                closing_socket.connect(('0.0.0.0', int(self.port)))
                closing_socket.shutdown(1)
                closing_socket.close()
                closing_socket = None
                if self.socket:
                    self.socket.close()
                    self.socket = None
            except Exception as ex:
                print(ex)

        else:
            try:
                if self.server != None:
                    # shutdown the server
                    self.server.shutdown()
                    self.server.server_close()
            except Exception as ex:
                print(ex)

        try:
            # stop the BaseThread!!
            super(APISimulator, self).stop()
        except Exception as ex:
            print(ex)

    def _load_simulator_data(self):

        success = False
        global _SIM_DATA

        try:

            abs_path = os.path.dirname(self.filename)
            data_filename = os.path.basename(self.filename).lower()

            if ".py" in data_filename:
                data_filename = data_filename.replace(".py", "")

            # add the path to the import path
            sys.path.append(abs_path)

            if _SIM_DATA is not None:
                try:
                    if _SIM_DATA.routes is not None:
                        # get the classname
                        data_classname = _SIM_DATA.__name__
                        # clear the current routes
                        _SIM_DATA.routes = None
                        # delete the class from the list of loaded modules
                        if data_classname in sys.modules:
                            del sys.modules[data_classname]
                except:
                    pass

            # load the SIM data from the module
            _SIM_DATA = importlib.import_module(data_filename)

            if _SIM_DATA.routes is not None and _SIM_DATA.routes is None:
                # seems we tried to reload the same module. force a reload
                reload(_SIM_DATA)

            success = True

        except Exception as ex:
            print("Problem loading simulator datafile '{}', exception = '{}'".format(data_filename, ex))

        return success

    def setup(self, passed_args):

        global _SIM_DATA, _SERVER_TYPE

        # build a parser
        parser = self.__build_arg_parser()

        # parse the args
        if passed_args is not None:
            args = parser.parse_args(passed_args)
        else:
            # will take sys.argv by default
            args = parser.parse_args()

        if args.port:
            self.port = args.port

        if args.file and (not args.file == 'None'):
            self.filename = args.file
            self._load_simulator_data()

        if args.type:
            self.is_json_rpc = (args.type == 'JSON_RPC')
            self.is_udp_server = (args.type == 'UDP_SERVER')
            _SERVER_TYPE = args.type

        # listen for sigterm signals and call stop if heard
        # signal.signal(signal.SIGTERM, self.stop)

    def __output_message(self, message):

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print("---------- {} ON PORT {} at {} ----------".format(message, self.port, st))

    def listen_udp(self):

        HOST = ''
        PORT = int(self.port)
        BUFFSIZE = 1024

        global _MSGS_RECEIVED

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print ('UDP SOCKET CREATED')

        try:

            self.socket.bind((HOST, PORT))
            self.listening = True

            self.__output_message("UDP SERVER LISTENING")

            # Listen for incoming datagrams

            while self.listening:

                bytes_from = self.socket.recvfrom(BUFFSIZE)
                message = bytes_from[0]
                address = bytes_from[1]

                self.last_request = message

                # add to messages
                _MSGS_RECEIVED.append(message)

                self.__output_message("UDP Message '{}' from '{}'".format(message, address))

                if self.listening is False:
                    break

        except socket.error as err:
            if self.listening:
                print ('UDP SOCKET ERROR={} MSG={}'.format(str(err.errno), str(err.strerror)))

        print('UDP SOCKET CLOSED')

    def listen_rpc(self):

        global _SIM_DATA, _MSGS_RECEIVED

        if _SIM_DATA is None:
            print("No Simulator DATA was loaded. Exiting.")
            return

        HOST = ''
        PORT = int(self.port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print ('RPC SOCKET CREATED')

        try:

            self.socket.bind((HOST, PORT))
            self.socket.listen(5)

            self.listening = True

            self.__output_message('RPC SOCKET LISTENING')

            while self.listening:

                payload = "{'status' : 'NO_DATA'}"

                try:
                    conn, addr = self.socket.accept()
                except:
                    pass

                if self.listening is False:
                    break

                request_bytes = conn.recv(4096)
                command = request_bytes.decode()

                self.last_request = command

                # add to messages
                _MSGS_RECEIVED.append(command)

                if "GET" and "HTTP/1" in command:
                    command = command.split('\r\n')[0].split(" ")[1]
                    payload = "\0"

                print('RPC SOCKET RECEIVED COMMAND {} FROM {}'.format(command, addr))

                try:
                    # get the payload
                    payload = _SIM_DATA.routes[command]
                except Exception as ex:
                    print(ex)

                try:
                    # now send response and 0 byte terminator
                    conn.sendall(bytes(json.dumps(payload), 'utf-8'))
                    conn.close()
                except Exception as ex:
                    print(ex)

        except socket.error as err:
            if self.listening:
                print ('RPC SOCKET ERROR={} MSG={}'.format(str(err.errno), str(err.strerror)))

        print('RPC SOCKET CLOSED')

    def listen_http(self):

        global _SIM_DATA

        if _SIM_DATA is not None:

            try:
                # create the server on the port
                self.server = HTTPServer((self.hostname, int(self.port)), HttpServer)
                self.server.timeout = 5
                self.listening = True
                self.__output_message("API SIMULATOR LISTENING")

                # really start listening
                self.server.serve_forever()
            except KeyboardInterrupt:
                pass

            # stop
            self.stop()

        else:
            if _SIM_DATA is None:
                print("No Simulator DATA was loaded. Exiting.")
            else:
                print("No HTTP Server could be created. Exiting.")

    def run(self):

        if self.is_json_rpc:
            self.listen_rpc()
        elif self.is_udp_server:
            self.listen_udp()
        else:
            self.listen_http()

if __name__ == '__main__':

    ####### MAIN PROGRAM STARTS HERE #######

    simulator = APISimulator()
    simulator.setup(None)
    simulator.start()