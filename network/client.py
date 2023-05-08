import socket
import os
import zipfile
from loguru import logger

import cfg


class ZipDir:
    def __init__(self, zip_file_name, dir_path):
        self.zip_file_name = zip_file_name
        self.dir_path = dir_path

    def zipdir(self):
        zipf = zipfile.ZipFile(self.zip_file_name, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self.dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path)
        zipf.close()


class TCPClient:
    def __init__(self, host, port):
        self.host = host  # server host
        self.port = port  # server port
        # create TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self):
        # connect to remote server
        self.server_socket.connect((self.host, self.port))
        # send protocol message
        # q means labels and frames will be sent very soon
        self.server_socket.sendall(b'r')

        # zip the frames and labels dir
        folder_to_sent = cfg.config["FOLDER_SENT"]
        zipper = ZipDir(f'{folder_to_sent}.zip', folder_to_sent)
        zipper.zipdir()

        # send the zip file to remote
        with open(f'{folder_to_sent}.zip', 'rb') as f:
            file_data = f.read()
        self.server_socket.sendall(file_data)
        # Sent Done is the end of file message for receiver
        self.server_socket.send(b"Sent Done")
        logger.info('Frames and labels are sent to remote machine')

    def receive(self):
        # connect to remote server's socket
        self.server_socket.connect((self.host, self.port))
        # send protocol message
        # b means model will be received very soon
        self.server_socket.sendall(b's')

        # model is temporarily saved as model.zip
        model_zip_file_name = cfg.config["RECEIVE_SAVE_NAME"]
        with open(f"{model_zip_file_name}.zip", 'wb') as f:
            while True:
                chunk = self.server_socket.recv(1024)
                if not chunk:
                    logger.error("Sent Done message not received!!! An error occurred")
                    break
                if chunk.endswith(b"Sent Done"):
                    chunk = chunk[:-9]
                    f.write(chunk)
                    logger.info("Successfully received the model")
                    break
                else:
                    f.write(chunk)

    def close(self):
        # Close the socket
        self.server_socket.close()
