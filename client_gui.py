import re
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox as mb
from tkinter import filedialog as fd
from tkinter import font
import socket
from threading import Thread
from crypto_funcs import encrypt, decrypt, check_access
from chat_color import generate_hex_color
import copy

class ConnectFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.messages = {}
        self.wrong_tries = 0
        self.self_color_in_chat = generate_hex_color()
        self.tt_canvas = tk.Canvas(self, width=420, height=100, bg='#6A5ACD')
        self.tt_canvas.create_image((350, 23), anchor='nw', image=confirm_img, tags='back_but')
        self.tt_canvas.tag_bind('back_but', '<Button-1>', self.start_chat_as_thread)
        self.tt_canvas.create_text((5, 20), anchor='nw', text='host', font='TimesNewRoman 12', fill='white')
        self.server_host_entry = tk.Entry(self.tt_canvas, width=15, bg='#4B0082', fg='white')
        self.server_host_entry.place(x=50, y=20)
        self.server_psw_entry = tk.Entry(self.tt_canvas, width=4, bg='#4B0082', fg='white')
        self.server_psw_entry.place(x=180, y=20)
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
        if self.private_key:
            self.tt_canvas.itemconfig('prvt_k', text='private key selected', fill='purple')

    def send_messages(self, event=None):
        message = self.message_ent.get()
        if re.findall(r'#[0-9A-Fa-f]{6}', message.strip()):
            self.self_color_in_chat = message.strip()
            self.message_ent.delete(0, tk.END)

        elif message.strip() == '$cc':
            self.self_color_in_chat = generate_hex_color()
            self.message_ent.delete(0, tk.END)

        elif message != '':
            message = f'{self.self_color_in_chat}$(color){self.nickname}: {message}'

            mes_to_send = ''
            self.message_ent.delete(0, tk.END)
            for i in range(len(message)):
                if i%55 == 0:
                    mes_to_send += '\n' + message[i]
                else:
                    mes_to_send += message[i]

            print(mes_to_send)
            print(len(mes_to_send))
            if mes_to_send.lower() == 'quit':
                self.client_socket.close()
                root.destroy()
            try:
                self.client_socket.sendall(encrypt(mes_to_send))

            except ValueError as e:
                print(str(e))

    def open_chat_win(self, event=None):
        self.nickname = self.nickname_ent.get()
        self.tt_canvas.destroy()
        self.server_host_entry.destroy()
        self.server_port_entry.destroy()
        self.nickname_ent.destroy()
        self.chat_canvas = tk.Canvas(self, width=600, height=800, bg='#9932CC')
        self.chat_canvas.bind("<Button-5>", self.move_text_up)
        self.chat_canvas.bind("<Button-4>", self.move_text_down)

        send_mes_frame = tk.Frame(self.chat_canvas, bd=1, bg='#9932CC', width=600, height=60)
        send_mes_frame.place(x=1, y=750)
        self.send_mes_canvas = tk.Canvas(send_mes_frame, bg='#9932CC', width=650, height=80)
        self.send_mes_canvas.place(x=-10, y=-10)
        self.message_ent = tk.Entry(send_mes_frame, width=48)
        self.message_ent.place(x=5, y=0)
        self.chat_canvas.pack(fill=tk.BOTH)


    def start_chat_as_thread(self, event):
        if (self.server_host_entry.get() and self.server_port_entry.get() and
                1 <= len(self.nickname_ent.get()) <= 10 and ' ' not in self.nickname_ent.get() and check_access()):
            Thread(target=self.start_chat, daemon=True).start()
        else:
            mb.showwarning('Warning', 'Access denied!')

    def start_chat(self):
        def new_message_processing(pre_message):
            global line_break_count
            color = pre_message[0]
            print(color)
            try:
                message = pre_message[1]
            except IndexError:
                message = pre_message[0]
            else:
                mes_y = 690

                line_break_count = 0
                for character in message:
                    if character == '\n':
                        line_break_count += 1
                if line_break_count:
                    mes_y -= line_break_count * 12 + line_break_count * 7 + 15
                else:
                    mes_y -= 15

                for tag in self.messages.keys():
                    # Получаем список идентификаторов объектов с текущим тегом
                    items = self.chat_canvas.find_withtag(tag)
                    print(items)
                    for item in items:
                        # Получаем текущие координаты элемента
                        coords = self.chat_canvas.coords(item)
                        print(coords)
                        if coords:  # Если координаты существуют
                            # Предположим, что coords содержит [x, y], обновим y-координату
                            current_y = self.messages[tag][0]  # Получаем текущее значение y
                            new_y = current_y - (690 - mes_y) - 10  # Ваше смещение по y
                            self.chat_canvas.coords(item, coords[0], new_y)  # Обновляем координаты
                            self.chat_canvas.update()
                            self.messages[tag][0] = new_y

                return mes_y, message, color

        def receive_messages():
            global line_break_count
            message_id = 0

            while True:
                received_data = self.client_socket.recv(1024)
                try:
                    pre_message = decrypt(received_data).split('$(color)')
                except ValueError:
                    mb.showerror('Error', 'Error in RSA process!')
                else:
                    try:
                        mes_y, message, color = new_message_processing(pre_message)
                    except TypeError:
                        pass
                    else:
                        current_message = self.chat_canvas.create_text((10, mes_y), anchor='nw', text=message, fill=color.strip(),
                                                                           tags=f'{message_id}')
                        message_id += 1

                        bounds = self.chat_canvas.bbox(current_message)
                        height = bounds[3] - bounds[1]
                        self.messages[str(message_id)] = [mes_y, height, line_break_count]

                        self.moved_messages = copy.deepcopy(self.messages)

                        print(received_data)
                        line_break_count = 0


        host = self.server_host_entry.get()
        port = int(self.server_port_entry.get())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((host, port))
        except socket.gaierror:
            mb.showerror('Error', 'Server is unavailable')
        except TimeoutError:
            mb.showerror('Error', 'Connection timeout')
        except ConnectionRefusedError:
            mb.showerror('Error', 'Connection refused')
        else:
            password = self.server_psw_entry.get()
            if password == '':
                password = 'null'

            self.client_socket.send(encrypt(password, pub_k='server/password_public_key.pem'))
            server_callback = decrypt(self.client_socket.recv(1024), priv_k='server/password_private_key.pem')

            if server_callback == 'Success':
                rmp = Thread(target=receive_messages, daemon=True)
                rmp.start()
                self.open_chat_win()
                self.client_socket.sendall(encrypt(f'#7FFF00$(color){self.nickname} '
                                                   f'connected with host: {socket.gethostbyname(socket.gethostname())}'))

                self.send_mes_canvas.create_image((self.message_ent.winfo_x() + self.message_ent.winfo_width() + 11, 4),
                                                  anchor='nw', image=send_img, tags='send_but')
                self.send_mes_canvas.tag_bind('send_but', '<Button-1>', self.send_messages)

            else:
                self.wrong_tries += 1
                if self.wrong_tries == 3:
                    mb.showerror('Error', 'You reached tries limit')
                    root.destroy()
                else:
                    mb.showerror('Error', 'Wrong password')

    def move_text_up(self, event=None):
        if self.message_ent.winfo_y() - int(list(self.moved_messages.values())[-1][0]) - int(list(self.moved_messages.values())[-1][1]) + 750 < 56:
            for tag in self.moved_messages.keys():
                items = self.chat_canvas.find_withtag(tag)
                print(items)
                for item in items:
                    # Получаем текущие координаты элемента
                    coords = self.chat_canvas.coords(item)
                    print(coords)
                    if coords:  # Если координаты существуют
                        # Предположим, что coords содержит [x, y], обновим y-координату
                        current_y = coords[1]  # Получаем текущее значение y
                        new_y = current_y - 50 # Ваше смещение по y
                        self.chat_canvas.coords(item, coords[0], new_y)  # Обновляем координаты
                        self.chat_canvas.update()
                        self.moved_messages[tag][0] -= 50

        print(self.messages)
        print(self.moved_messages)

    def move_text_down(self, event=None):
        if self.moved_messages['1'][0] < 0:
            for tag in self.moved_messages.keys():
                items = self.chat_canvas.find_withtag(tag)
                print(items)
                for item in items:
                    # Получаем текущие координаты элемента
                    coords = self.chat_canvas.coords(item)
                    print(coords)
                    if coords:  # Если координаты существуют
                        # Предположим, что coords содержит [x, y], обновим y-координату
                        current_y = coords[1]  # Получаем текущее значение y
                        new_y = current_y + 50 # Ваше смещение по y
                        self.chat_canvas.coords(item, coords[0], new_y)  # Обновляем координаты
                        self.chat_canvas.update()
                        self.moved_messages[tag][0] += 50

        print(self.messages)
        print(self.moved_messages)

class MainWin:
    def __init__(self, master):
        global back_img, confirm_img, send_img
        back_img = tk.PhotoImage(file='images/back36.png')
        confirm_img = tk.PhotoImage(file='images/confirm24.png')
        send_img = tk.PhotoImage(file='images/send24.png')
        image = Image.open('images/icon16.ico')  # Замените на путь к вашей иконке
        icon = ImageTk.PhotoImage(image)
        root.iconphoto(False, icon)

        menu_bar = tk.Menu(master)

        menu_font = font.Font(family='TimesNewRoman', size=8)
        file_menu = tk.Menu(menu_bar, tearoff=0, font=menu_font)
        file_menu.add_command(label='О программе...', command=self.about)
        file_menu.add_command(label='Помощь', command=self.help)
        menu_bar.add_cascade(label="Дополнительная информация", menu=file_menu, font=menu_font, command=self.about)

        # Применение меню к основному окну
        master.config(menu=menu_bar)
        master.resizable(False, False)
        master.title('RSA')

        mainframe = tk.Frame(master)
        mainframe.pack()

        ConnectFrame(mainframe)

        """except ConnectionRefusedError:
            mb.showerror('Error', 'Wrong address!')"""
    @staticmethod
    def about():
        mb.showinfo('', ""
                        "СПО с использованием асимметричного шифрования (RSA).\n"
                        "Выполнил:\n"
                        "к-т 412 уч. гр.\n"
                        "ряд. Онищенко А.")
    @staticmethod
    def help():
        mb.showinfo('', ""
                        "Поле 'host' соответствует ip адресу сервера, к которому планируется осуществить подключение.\n"
                        "Поле справа от 'host' должно содержать пароль, если он был установлен сервером.\n"
                        "Поле 'port' соответствует порту, на котором открыт socket.\n"
                        "При нажатии на надпись 'select private key file' открывается менеджер файлов для последующего "
                        "выбора приватного ключа шифрования.\n"
                        "Поле 'nick' соответствует псевдониму с использованием которого осуществляется подключение, далее "
                        "псевдоним используется для идентификации пользователя другими пользователями, это поле может "
                        "содержать от 2 до 10 символов.\n"
                        "При неправильном заполнении полей вы увидите ошибку.\n"
                        "Перед началом работы поместите файл private_key.pem и public_key.pem в директорию исполняемого "
                        "файла, если таковых нет, то создайте их с помощью скрипта rsa_key_create.py.\n"
                        "Ключи шифрования пользователей должны соответствовать друг другу, в противном случае вы увидите "
                        "соответствующую ошибку.\n"
                        "Для более надежного шифрования в режиме двух пользователей советуем использовать две пары "
                        "ключей шифрования пользователь_1 создает два ключа и передает приватный пользователю_2, "
                        "далее аналогично для пользователя_2.\nЕсли передача осуществляется не через МНИ, то советуем "
                        "использовать только защищенные каналы обмена информацией.")


root = tk.Tk()
obj = MainWin(root)
root.mainloop()