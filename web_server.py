#!/usr/bin/env python3
"""Starter code for the CSE 342 TCP Web Server assignment.


Complete every numbered TODO between the ``Fill in start`` and ``Fill in end``
markers. The program takes no command-line arguments.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from socket import (
    AF_INET,
    SOCK_STREAM,
    SOL_SOCKET,
    SO_REUSEADDR,
    socket,
    timeout as SocketTimeout,
)
from urllib.parse import unquote, urlsplit


SERVER_HOST = "128.180.120.70"
SERVER_PORT = 8888
BACKLOG = 5
MAX_REQUEST_BYTES = 8192
CLIENT_TIMEOUT_SECONDS = 5.0
SERVER_DIRECTORY = Path(__file__).resolve().parent
INDEX_PAGE = SERVER_DIRECTORY / "index.html"
NOT_FOUND_PAGE = SERVER_DIRECTORY / "404.html"

# These complete HTML pages for index.html and 404.html.
INDEX_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hello World</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
"""

NOT_FOUND_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>404 Not Found</title>
</head>
<body>
    <h1>404 Not Found</h1>
    <p>The requested file could not be found.</p>
</body>
</html>
"""


def resolve_request_target(target: str) -> Path:
    """Return a safe file path inside the server program's directory."""

    url_path = unquote(urlsplit(target).path)
    if url_path in ("", "/", "/index"):
        relative_path = "index.html"
    else:
        relative_path = url_path.lstrip("/")
    requested_path = (SERVER_DIRECTORY / relative_path).resolve()
    try:
        requested_path.relative_to(SERVER_DIRECTORY)
    except ValueError as error:
        raise PermissionError("request escaped the server directory") from error
    return requested_path


def build_response(status_line: str, body: bytes, content_type: str) -> bytes:
    """Return one complete HTTP response containing the supplied body."""

    response_header = (
        f"{status_line}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Content-Type: {content_type}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii")
    return response_header + body

def main() -> None:
    """Handle one HTTP request at a time until Ctrl-C."""

    # Build both supplied HTML files before the server starts.
    INDEX_PAGE.write_bytes(INDEX_HTML)
    NOT_FOUND_PAGE.write_bytes(NOT_FOUND_HTML)

    server_socket = socket(AF_INET, SOCK_STREAM)

    # Allow the server to restart without waiting for an old TCP connection's
    # TIME_WAIT state to expire.
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # Prepare a server socket.
    # Fill in start -- TODO 1
    # Bind to (SERVER_HOST, SERVER_PORT), listen with BACKLOG, and print the
    # directory and listening URL.

    #call bind with tuple of server_host and server_port
    #call listen with backlog as argument
    server_socket.bind((SERVER_HOST,SERVER_PORT))
    server_socket.listen(BACKLOG)
    # print(f'\nserver_socket: {server_socket}')
    print(f'Directory: {SERVER_DIRECTORY}')

    # raise NotImplementedError
    # Fill in end -- TODO 1

    try:
        while True:
            print("Ready to serve...")

            # Establish the connection.
            # Fill in start -- TODO 2
            # Accept one client and save both the connected socket and address.

            #call accept with server_socket. returns the client_socket and its ip address
            #will print client every time anyone attemps to contact with server
            connection_socket, client_address = server_socket.accept()
            # print(f'\nclient: {connection_socket}, client_addy: {client_address}')



            # Fill in end -- TODO 2

            try:
                connection_socket.settimeout(CLIENT_TIMEOUT_SECONDS)

                # Receive the HTTP request.
                # Fill in start -- TODO 3
                # Repeatedly call recv until CRLF CRLF, client close, or
                # MAX_REQUEST_BYTES. Store the result as bytes in message.

                #message variable
                message=b''

                #makeshift do while loop to contoniously recieve from client. assigns data varibale w/the bytes object 
                #loop will end if the data is an empty bytes object, if the bytes objec ends with 2 crlf, 
                #or total of data+message is greater than max_request_bytes constant
                while True:
                    data = connection_socket.recv(MAX_REQUEST_BYTES)
                    # print(f'data: {data}. data[-4:]={data[-4:]}')

                    if data == b'':
                        # print('client closed')
                        break
                    elif data[-4:] == b'\r\n\r\n':
                        # print('crlf clrf')
                        message+=data
                        break
                    elif len(data+message) > MAX_REQUEST_BYTES:
                        # print('exceeded limit')
                        break
                    else:
                        message+=data
                # print(f'final message = {message}')

                # Fill in end -- TODO 3

                # Parse the request and read the requested file.
                # Fill in start -- TODO 4
                # Decode with ISO-8859-1, parse method/target/version from the
                # request line, require GET and an HTTP version, resolve target
                # with resolve_request_target, and read the file as bytes into
                # output_data.
                # Hint: use request_line = message.decode("iso-8859-1").split("\r\n", 1)[0]

                #decodes message and assigns it request_lien variable. decodes it from iso-8859-1
                #which is the http encoding. splits it by carraige return delimeter and takes first element in array
                #to get the http request
                request_line = message.decode("iso-8859-1").split("\r\n", 1)[0]
                #split up request with / as delimeter. 
                parsed = request_line.split('/')
                #method is variable which stores http request method. gets rid of all whitespace w/ replace
                method = parsed[0].replace(' ','')
                #checks method is get. if not raise value error to do 400
                if method != 'GET':
                    raise ValueError
                #target is the file. get rid of http with slicing.
                #index.html HTTP w/ slicing will be index.html
                target = parsed[1].replace(' ','')
                target = target[:-4]
                #version is the 1.1 in HTTP/1.1
                version = parsed[2].replace(' ','')
                #requested_path stores result of resolve_request_target function w/ target file passed.
                #if file does not exist will do 404 
                requested_path = resolve_request_target(target)
                #get byts object of file according to the requested_path
                output_data = requested_path.read_bytes()
                # print(f'output_data = {output_data}')

                # Fill in end -- TODO 4

                content_type = mimetypes.guess_type(requested_path.name)[0]
                if content_type is None:
                    content_type = "application/octet-stream"
                elif content_type.startswith("text/"):
                    content_type += "; charset=utf-8"

                # Send the success response.
                # Fill in start -- TODO 5
                # Construct the HTTP/1.1 200 OK header, including
                # Content-Length, Content-Type using content_type,
                # Connection: close, and the required blank line. Encode the
                # header as bytes and send it with output_data using sendall.
                
                #response stores header and bytes for body 
                #send data with sendall
                response=build_response('HTTP/1.1 200 OK', output_data, content_type)
                connection_socket.sendall(response)

                
                # Fill in end -- TODO 5

                print(f"200 {requested_path.name} | client={client_address}")

            except (FileNotFoundError, IsADirectoryError, PermissionError):
                # Send a response message for a file that cannot be served.
                # The 404 page was built from the supplied starter-code HTML.
                body = NOT_FOUND_PAGE.read_bytes()

                # Fill in start -- TODO 6
                # Construct the HTTP/1.1 404 Not Found header,
                # including Content-Length, Content-Type, Connection: close,
                # and the required blank line. Send the provided body with it.

                #start w/ putting http/1.1 and 404 as reponse code since file wasnt found
                #content_length is numbe rof bytes in body
                #content type is text/html and utf-8
                #connection is close since you dont want to keep connection open
                #final \r\n is single blank line for posix standard
                #encode it in ascii and do sendall with response_header and body
                response_header = (
                    "HTTP/1.1 404 Not Found\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("ascii")
                connection_socket.sendall(response_header + body)




                # Fill in end -- TODO 6

                print(f"404 | client={client_address}")

            except (SocketTimeout, UnicodeDecodeError, ValueError):
                body = b"<h1>400 Bad Request</h1>\n"
                response_header = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                ).encode("ascii")
                connection_socket.sendall(response_header + body)
                print(f"400 | client={client_address}")

            finally:
                # Close the client socket.
                # Fill in start -- TODO 7

                #call close() to end the connection between server and client
                connection_socket.close()



                # Fill in end -- TODO 7

    except KeyboardInterrupt:
        print("\nWeb server stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()