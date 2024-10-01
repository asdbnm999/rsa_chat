import socket
from threading import Thread


class Server:
    def __init__(self, host='127.0.0.1', port=8888):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.clients = []
        print(f"Сервер запущен на {host}:{port}")

    def handle_client(self, client_socket):
        while True:
            try:
                encrypted_message = client_socket.recv(1024)
                if not encrypted_message:
                    break

                # Рассылка сообщения всем подключенным клиентам
                for client in self.clients:
                    client.sendall(encrypted_message)

            except Exception as e:
                print(f"Ошибка: {e}")
                break

        client_socket.close()
        self.clients.remove(client_socket)  # Удаляем клиентский сокет из списка
        print(f"Клиент отключен. Текущие клиенты: {self.clients}")

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Подключен к {addr}")
            self.clients.append(client_socket)  # Добавляем клиентский сокет

            client_handler = Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()
            print(self.clients)


if __name__ == "__main__":
    server = Server()
    server.start()
