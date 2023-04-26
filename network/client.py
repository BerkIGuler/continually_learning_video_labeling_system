import socket
import os
import zipfile
import tarfile


class TarDir:
    def __init__(self, tar_file_name, dir_path):
        self.tar_file_name = tar_file_name
        self.dir_path = dir_path

    def tardir(self):
        with tarfile.open(self.tar_file_name, "w:gz") as tar:
            tar.add(self.dir_path, arcname=os.path.basename(self.dir_path))


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


def _receive(file_name, client_socket):
    with open(file_name, 'wb') as f:
        while True:
            chunk = client_socket.recv(10240)
            if not chunk:
                print("receive done")
                break
            if chunk.endswith(b"Sent Done"):
                chunk = chunk[:-9]
                f.write(chunk)
                break
            else:
                f.write(chunk)
        print("Finish")


def _send(file_name, client_socket):
    with open(file_name, 'rb') as f:
        file_data = f.read()
    client_socket.sendall(file_data)
    client_socket.send(b"Sent Done")
    print('File sent to server')


class TCPClient:
    def __init__(self, host, port):
        self.host = host  # server host
        self.port = port  # server port
        # create TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, folder_path):
        self.server_socket.connect((self.host, self.port))
        self.server_socket.sendall(b'q')
        zip_file_name = f'{folder_path}.zip'
        zipper = ZipDir(zip_file_name, folder_path)
        zipper.zipdir()
        _send(zip_file_name, self.server_socket)

    def receive(self, folder_path):
        self.server_socket.connect((self.host, self.port))
        self.server_socket.sendall(b'm')
        receive_file_name = 'receive_file.zip'
        _receive(receive_file_name, self.server_socket)

    def close(self):
        # Close the server socket
        self.server_socket.close()
