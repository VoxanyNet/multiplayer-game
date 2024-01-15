import socket
from socket import AddressFamily, SocketKind
from typing import Optional


class InvalidHeader(Exception):
    pass


class Disconnected(Exception):
    pass


class PayloadTooLarge(Exception):
    pass


# a socket that has the ability to add headers
class HeaderedSocket(socket.socket):

    def __init__(self, family: AddressFamily | int = -1, type: SocketKind | int = -1, proto: int = -1, fileno: int | None = None) -> None:
        super().__init__(family, type, proto, fileno)

        self.constructed_data = bytearray()
        self.payload_length = int()

    def send_headered(self, data, header_size=7):

        # construct a payload with header from bytes

        # get number of bytes json string uses
        data_size = len(data)

        # if the number used to represent the length of the payload is over 7 characters we cant trasmit it
        if len(str(data_size)) > header_size:
            raise PayloadTooLarge(f"Payload header cannot be more than {header_size} characters")

        # create header containing payload size - this header must always be the same size: 7 characters
        # header contains the number of bytes that the json payload is
        # if the number of bytes requires less than 7 characters to represent, we use leading zeros
        header = f"{(header_size - len(str(data_size))) * '0'}{data_size}"  # 7 - len(str(payload_size_string)) fills in unused digits with 0s

        header_bytes = bytes(header, "utf-8")

        # final payload with header and data
        headered_data = header_bytes + data

        self.sendall(headered_data)

    def recv_headered(self, header_size=7) -> bytes:
        """
        Attempt to construct complete message
        If didn't receive the whole message yet, returns None
        """
        
        # if self.constructed data is 0, that means we should be expecting a new header
        if len(self.constructed_data) == 0:
            try:
                header = self.recv(header_size).decode("utf-8")

            except BlockingIOError:
                # nothing in the socket buffer
                raise BlockingIOError()

            except ConnectionResetError:
                raise Disconnected("Remote socket reset connection")

            if header == "":
                raise Disconnected("Remote socket disconnected")

            try:
                # replace the old payload length with the new one
                self.payload_length = int(header)

            except ValueError:
    
                raise InvalidHeader(f"Sender sent header {header}, which is invalid")


        while len(self.constructed_data) != self.payload_length:
            # read from buffer until we get a complete message
            
            try:
                # read {self.payload_length} number of bytes from the socket buffer minus what we have already read
                new_data = self.recv(self.payload_length - len(self.constructed_data))

            except BlockingIOError:
                # we reached the end of the buffer, so the user will need to invoke recv_headered again to receive the entire message

                raise BlockingIOError()

            except ConnectionResetError:
                raise Disconnected("Remote socket reset connection")
            
            if new_data == "":
                raise Disconnected("Remote socket disconnected")
            
            # save the newly read data
            self.constructed_data.extend(new_data)

        # make a copy of the constructed data before resetting it
        constructed_data = self.constructed_data.copy()
        # reset constructed data for next batch of data
        self.constructed_data = bytearray()
        # this will only return if we get all of the data
        return bytes(constructed_data)

    # accept() is redefined to return PayloadSockets instead of default ones
    def accept(self):

        fd, addr = self._accept()

        # create a headered socket instead of a normal socket
        sock = HeaderedSocket(self.family, self.type, self.proto, fileno=fd)

        # blocking sockets return blocking and non blocking return non blocking
        if self.timeout == 0 or None:
            sock.settimeout(0)

        return sock, addr
    
