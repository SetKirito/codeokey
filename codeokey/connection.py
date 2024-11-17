import socket
from logging import exception
import select
import sys
import time
from codeokey.util import flatten_parameters_to_bytestring
from codeokey.logger import *

""" @author: Aron Nieminen, Mojang AB"""


class RequestError(Exception):
    pass


class Connection:
    """Connection to a Minecraft Pi game"""
    RequestFailed = "Fail"

    def __init__(self, address, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((address, port))
        self.lastSent = ""

        # Добавляем переменные для отслеживания ошибок
        self.error_count = 0  # Счетчик ошибок
        self.error_limit = 10  # Лимит количества ошибок до закрытия соединения
        self.error_time_window = 60  # Временное окно в секундах для проверки
        self.first_error_time = None  # Время первой ошибки

    def drain(self):
        """Drains the socket of incoming data"""
        while True:
            readable, _, _ = select.select([self.socket], [], [], 0.0)
            if not readable:
                break
            data = self.socket.recv(1500)
            e = "Drained Data: <%s>\n" % data.strip()
            e += "Last Message: <%s>\n" % self.lastSent.strip()
            sys.stderr.write(e)

    def send(self, f, *data):
        """
        Sends data. Note that a trailing newline '\n' is added here

        The protocol uses CP437 encoding - https://en.wikipedia.org/wiki/Code_page_437
        which is mildly distressing as it can't encode all of Unicode.
        """
        debug("function called:" + f.decode("utf-8"), data)

        s = b"".join([f, b"(", flatten_parameters_to_bytestring(data), b")", b"\n"])
        self._send(s)

    def _send(self, s):
        """
        The actual socket interaction from self.send, extracted for easier mocking
        and testing
        """
        time.sleep(settings.SYS_SPEED)  # slow down the running speed
        self.drain()
        self.lastSent = s
        self.socket.sendall(s)

    def receive(self):
        """Receives data. Note that the trailing newline '\n' is trimmed"""
        s = self.socket.makefile("r").readline().rstrip("\n")
        #print(s)
        # Проверяем на наличие ошибки
        if s.find(Connection.RequestFailed) != -1:
            self.handle_error(s)

        return s

    def sendReceive(self, *data):
        """Sends and receive data"""
        self.send(*data)
        return self.receive()

    def handle_error(self, error_message):
        """Обработка ошибок с отслеживанием частоты и остановкой соединения"""
        current_time = time.time()

        if self.first_error_time is None:
            self.first_error_time = current_time

        # Если прошло больше времени, чем указано в окне, сбрасываем счетчик ошибок
        if current_time - self.first_error_time > self.error_time_window:
            self.error_count = 0
            self.first_error_time = current_time

        self.error_count += 1

        if self.error_count >= self.error_limit:
            self.close_connection()
            raise Exception(f"Слишком много ошибок ({self.error_count}) за короткий период. Соединение закрыто.")

        # Логируем ошибку
        exception(error_message)

    def close_connection(self):
        """Закрытие соединения при превышении числа ошибок"""
        exception("Закрытие соединения из-за превышения лимита ошибок.")
        self.socket.close()

# Пример использования:
# _connection = Connection("localhost", 4711)
# _connection.sendReceive(b"world.setBlock", 0,0,0,"stone")
