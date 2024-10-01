import socket
from threading import Thread
from crypto_funcs import encrypt, decrypt


class Client:
    def __init__(self, host='127.0.0.1', port=8881):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        print("Подключено к серверу. Введите 'q' для выхода.")

    def send_messages(self):
        while True:
            message = input('>> ')
            if message.lower() == 'q':
                break
            self.client_socket.sendall(encrypt(message))

    def receive_messages(self, output_queue):
        while True:
            received_data = self.client_socket.recv(1024)
            output_queue.put(decrypt(received_data))

    def start(self):
        smp = Thread(target=self.send_messages, daemon=True)
        rmp = Thread(target=self.receive_messages, daemon=True)

        smp.start()
        rmp.start()
        smp.join()
        self.client_socket.close()

"""if __name__ == "__main__":
    client = Client()
    client.start()"""
