#  coding: utf-8 
import socketserver

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        '''
        Handle receiving/processing a request and send a response
        '''
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        request_line, request_headers = self.process_request(self.data)
        request_line_values = request_line.strip().split(" ")
        method, filename = request_line_values[0], request_line_values[1]
        response = self.process_response(method, filename)
        self.request.sendall(response)

    def process_request(self, data):
        '''
        Decode and process the HTTP request string

        Parameters:
            String: The binary HTTP request string
        Returns:
            Tuple(string, dict): the request line and a dictionary of the request headers
        '''
        data = data.decode('utf-8').split('\r\n')
        if data == ['']:
            return None
        request_line = data[0]
        request_headers = {}
        for header in data[1:]:
            # Ignore anything that is not a key value pair
            if len(header) == 2:
                key, value = header.split(': ')
                request_headers[key] = value
        return request_line, request_headers

        
    def process_response(self, method, filename):
        '''
        Process the valid response based on the request's method and filename

        Parameters:
            (string)method: method of the request
            (string)filename: filename of the request
        Returns:
            The binary response string
        '''
        if method == 'GET':
            if filename[-1] != '/':
                response = f'HTTP/1.1 301 Moved Permanently\r\nLocation: http://127.0.0.1:8080{filename}/'
                return bytearray(response, 'utf-8')
            else:
                try:
                    filename = self.parse_filename(filename)
                    f = open(f'www{filename[:-1]}', 'r')
                    content_type = self.get_content_type(filename)
                    response = f'HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n{f.read()}'
                    f.close()
                    return bytearray(response, 'utf-8')
                except:
                    response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nError 404 Page Not Found'
                    return bytearray(response, 'utf-8')
        else:
            return bytearray('HTTP/1.1 405 Method Not Allowed', 'utf-8')

    def parse_filename(self, filename):
        '''
        Parse the filename from the request to return proper file paths

        Parameters:
            string: filename from the request line
        Returns:
            string: the file path
        '''
        if filename == '/' or (not filename.endswith('.css/') and not filename.endswith('.html/')):
            return filename + 'index.html/'
        else:
            return filename

    def get_content_type(self, filename):
        '''
        Returns the correct mime-type for the file

        Parameters:
            string: filename from the request
        Returns:
            string: the mime-type
        '''
        if filename.endswith('.html/'):
            return 'text/html'
        elif filename.endswith('.css/'):
            return 'text/css'
        else:
            return None
    
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
