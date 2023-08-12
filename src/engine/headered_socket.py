import socket
from socket import AddressFamily, SocketKind


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
        self.payload_length = int

    def send_headered(self, data, header_size=7):

        # construct a payload with header from bytes

        # get number of bytes json string uses
        data_size = len(data)

        print(f"sending an update with a size of {data_size}!!!!")

        # the amount of data that has been acknowledged by the client to have been sent
        # somtimes we need to resend data if the client does not acknowledge it
        # im not sure why sockets don't do this automatically
        # in my case the clients receive buffer was filling up
        sent_data = 0

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

    def recv_headered(self, header_size=7):
        
        # we arent already try to construct a message
        if len(self.constructed_data) == 0:
            try:
                header = self.recv(header_size).decode("utf-8")

            except BlockingIOError:
                print("""
                    ⠀⣞⢽⢪⢣⢣⢣⢫⡺⡵⣝⡮⣗⢷⢽⢽⢽⣮⡷⡽⣜⣜⢮⢺⣜⢷⢽⢝⡽⣝
                    ⠸⡸⠜⠕⠕⠁⢁⢇⢏⢽⢺⣪⡳⡝⣎⣏⢯⢞⡿⣟⣷⣳⢯⡷⣽⢽⢯⣳⣫⠇
                    ⠀⠀⢀⢀⢄⢬⢪⡪⡎⣆⡈⠚⠜⠕⠇⠗⠝⢕⢯⢫⣞⣯⣿⣻⡽⣏⢗⣗⠏⠀
                    ⠀⠪⡪⡪⣪⢪⢺⢸⢢⢓⢆⢤⢀⠀⠀⠀⠀⠈⢊⢞⡾⣿⡯⣏⢮⠷⠁⠀⠀⠀
                    ⠀⠀⠀⠈⠊⠆⡃⠕⢕⢇⢇⢇⢇⢇⢏⢎⢎⢆⢄⠀⢑⣽⣿⢝⠲⠉⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⡿⠂⠠⠀⡇⢇⠕⢈⣀⠀⠁⠡⠣⡣⡫⣂⣿⠯⢪⠰⠂⠀⠀⠀⠀
                    ⠀⠀⠀⠀⡦⡙⡂⢀⢤⢣⠣⡈⣾⡃⠠⠄⠀⡄⢱⣌⣶⢏⢊⠂⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⢝⡲⣜⡮⡏⢎⢌⢂⠙⠢⠐⢀⢘⢵⣽⣿⡿⠁⠁⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠨⣺⡺⡕⡕⡱⡑⡆⡕⡅⡕⡜⡼⢽⡻⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⣼⣳⣫⣾⣵⣗⡵⡱⡡⢣⢑⢕⢜⢕⡝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⣴⣿⣾⣿⣿⣿⡿⡽⡑⢌⠪⡢⡣⣣⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⡟⡾⣿⢿⢿⢵⣽⣾⣼⣘⢸⢸⣞⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠁⠇⠡⠩⡫⢿⣝⡻⡮⣒⢽⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    N O  H E A D E R S ?
                """)

                return None

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
            
            try:
                new_data = self.recv(self.payload_length - len(self.constructed_data))

            except BlockingIOError:

                print("no new data!")

                return None

            except ConnectionResetError:
                raise Disconnected("Remote socket reset connection")
            
            if header == "":
                raise Disconnected("Remote socket disconnected")
            
            self.constructed_data.extend(new_data)

        # make a copy of the constructed data before resetting it
        constructed_data = self.constructed_data.copy()
        # reset constructed data for next batch of data
        self.constructed_data = bytearray()
        # this will only return if we get all of the data
        return constructed_data

    # accept() is redefined to return PayloadSockets instead of default ones
    def accept(self):

        fd, addr = self._accept()

        # create a headered socket instead of a normal socket
        sock = HeaderedSocket(self.family, self.type, self.proto, fileno=fd)

        # blocking sockets return blocking and non blocking return non blocking
        if self.timeout == 0 or None:
            sock.settimeout(0)

        return sock, addr
    
