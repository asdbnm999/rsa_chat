import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
import socket
from threading import Thread
from crypto_funcs import encrypt, decrypt
from queue import Queue


class ConnectFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tt_canvas = tk.Canvas(self, width=420, height=100, bg='#6A5ACD')
        self.tt_canvas.create_image((350, 23), anchor='nw', image=confirm_img, tags='back_but')
        self.tt_canvas.tag_bind('back_but', '<Button-1>', self.start_chat_as_thread)
        self.tt_canvas.create_text((5, 20), anchor='nw', text='host', font='TimesNewRoman 12', fill='white')
        self.server_host_entry = tk.Entry(self.tt_canvas, width=15, bg='#4B0082', fg='white')
        self.server_host_entry.place(x=50, y=20)
        self.tt_canvas.create_text((230, 20), anchor='nw', text='port', font='TimesNewRoman 12', fill='white')
        self.server_port_entry = tk.Entry(self.tt_canvas, width=5, bg='#4B0082', fg='white')
        self.server_port_entry.place(x=275, y=20)
        self.tt_canvas.create_text((230, 60), anchor='nw', text='nick',
                                   font='TimesNewRoman 12', fill='white')
        self.nickname_ent = tk.Entry(self.tt_canvas, width=5, bg='#4B0082', fg='white')
        self.nickname_ent.place(x=275, y=60)
        self.tt_canvas.create_text((5, 60), anchor='nw', text='select private key file',
                                   font='TimesNewRoman 12', fill='red', tags='prvt_k')
        self.tt_canvas.tag_bind('prvt_k', '<Button-1>', self.select_private_key)

        self.server_host_entry.insert(0, 'localhost')
        self.server_port_entry.insert(0, '8888')

        self.tt_canvas.pack()
        self.pack()

    def select_private_key(self, event):
        self.private_key = fd.askopenfile()
        self.tt_canvas.itemconfig('prvt_k', text='private key selected', fill='purple')

    def send_messages(self, event=None):
        message = self.message_ent.get()
        if message != '':
            message = self.nickname + ': ' + message

            mes_to_send = str()

            for i in range(len(message)):
                if i%45 == 0:
                    mes_to_send += '\n' + message[i]
                else:
                    mes_to_send += message[i]

            print(mes_to_send)
            print(len(mes_to_send))
            self.message_ent.delete(0, tk.END)
            if mes_to_send.lower() == 'q':
                self.client_socket.close()
                root.destroy()
            self.client_socket.sendall(encrypt(mes_to_send))

    def open_chat_win(self, event=None):
        self.nickname = self.nickname_ent.get()
        self.tt_canvas.destroy()
        self.server_host_entry.destroy()
        self.server_port_entry.destroy()
        self.nickname_ent.destroy()
        self.chat_canvas = tk.Canvas(self, width=600, height=800, bg='#6A5ACD')
        self.send_but = tk.Button(self.chat_canvas, width=7, text='Send', command=self.send_messages)
        self.send_but.place(x=550, y=748)
        self.message_ent = tk.Entry(self.chat_canvas, width=48)
        self.message_ent.place(x=10, y=750)
        self.chat_canvas.pack()

    def start_chat_as_thread(self, event):
        Thread(target=self.start_chat, daemon=True).start()

    def start_chat(self):
        def receive_messages():
            message_id = 0
            messages = {}

            while True:
                received_data = self.client_socket.recv(1024)
                message = decrypt(received_data)
                mes_y = 690

                line_break_count = 0
                for character in message:
                    if character == '\n':
                        line_break_count += 1
                if line_break_count:
                    mes_y -= line_break_count*12 + line_break_count*5 + 15

                for tag in messages.keys():
                    # Получаем список идентификаторов объектов с текущим тегом
                    items = self.chat_canvas.find_withtag(tag)
                    print(items)
                    for item in items:
                        # Получаем текущие координаты элемента
                        coords = self.chat_canvas.coords(item)
                        print(coords)
                        if coords:  # Если координаты существуют
                            # Предположим, что coords содержит [x, y], обновим y-координату
                            current_y = coords[1]  # Получаем текущее значение y
                            new_y = current_y - (690 - mes_y ) - 10  # Ваше смещение по y
                            self.chat_canvas.coords(item, coords[0], new_y)  # Обновляем координаты
                            self.chat_canvas.update()
                            messages[tag][0] = new_y

                current_message = self.chat_canvas.create_text((10, mes_y), anchor='nw', text=message,
                                                               tags=f'{message_id}')
                message_id += 1

                bounds = self.chat_canvas.bbox(current_message)
                height = bounds[3] - bounds[1]
                messages[str(message_id)] = [[10, mes_y], height, line_break_count]
                print(received_data)
                line_break_count = 0

        host = self.server_host_entry.get()
        port = int(self.server_port_entry.get())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        print("Подключено к серверу. Введите 'q' для выхода.")

        rmp = Thread(target=receive_messages, daemon=True)
        rmp.start()
        self.open_chat_win()



class MainWin:
    def __init__(self, master):
        global back_img, confirm_img, send_img
        back_img = tk.PhotoImage(file='images/back36.png')
        confirm_img = tk.PhotoImage(file='images/confirm24.png')
        send_img = tk.PhotoImage(file='images/send24.png')
        mainframe = tk.Frame(master)
        mainframe.pack()

        frameList = [ConnectFrame(mainframe)]

        """except ConnectionRefusedError:
            mb.showerror('Error', 'Wrong address!')"""



root = tk.Tk()
root.resizable(False, False)
obj = MainWin(root)
root.mainloop()