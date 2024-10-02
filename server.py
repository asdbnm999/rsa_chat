import socket
from threading import Thread
from crypto_funcs import encrypt, decrypt

class Server:
    def __init__(self, host='127.0.0.1', port=8888):
        self.password = input('If you need to set password - type it, else press "Enter">> ')
        if self.password == '':
            self.password = 'null'
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = {}
        print(f"Server is able on {host}:{port}")

    def handle_client(self, client_socket):
        while True:
            try:
                encrypted_message = client_socket.recv(1024)
                print(encrypted_message)
                if not encrypted_message:
                    break

                # Рассылка сообщения всем подключенным клиентам
                for client in self.clients.keys():
                    client.sendall(encrypted_message)

            except Exception as e:
                print(f"Ошибка: {e}")
                break

        client_socket.close()
        print(f"Client disconnected (address {self.clients[client_socket]}). Clients: {self.clients.keys()}")
        del self.clients[client_socket]  # Удаляем клиентский сокет из списка


    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            if self.password != '':
                received_password = decrypt(client_socket.recv(2048), priv_k='server/password_private_key.pem')
                if received_password != self.password:
                    client_socket.send(encrypt('Connection refused', pub_k='server/password_public_key.pem'))
                    continue
                elif received_password == self.password:
                    client_socket.send(encrypt('Success', pub_k='server/password_public_key.pem'))

            print(f"Connected {addr}")
            self.clients[client_socket] = addr  # Добавляем клиентский сокет

            client_handler = Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
            print(self.clients)


if __name__ == "__main__":
    server = Server()
    server.start()
