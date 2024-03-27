import os
import time
import re
import subprocess

class Connect_file():
    def __init__(self,FilePath):
        self.FilePath = FilePath
        self.log = ""  #保存文件log信息
        self.code = 9 #9代表未初始化  0代表连接成功  1代表连接失败
        self.hostname = "" #用来记录连接的站点
        self.port = "" #用来记录连接的端口号
        self.ip = "" #用来记录连接的IP号

    def connect(self):
        #设置需要执行得命令
        command = [
            "openvpn",
            "--auth-nocache",
            "--config",
            self.FilePath,
            "--auth-user-pass",
            os.path.join(os.getcwd(), "zh.txt")
        ]

        #创建进程
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
        process.kill()
        process.wait()
        stdout, stderr = process.communicate()
        self.log = stdout.decode('utf-8')
        if "VERIFY EKU OK" in self.log:
            #设置code状态码
            self.code = 0
            #获取IP 和 PORT
            self.GetIp()
            #获取hostname
            self.GetHostname()
        else:
            #设置code状态码
            self.code = 1

    def GetIp(self):
        for line in self.log.split('\n'):  #分割日志文件
            if "Preserving recently used remote address" in line:
                index = line.find("[AF_INET]")
                if index != -1:
                    address = line[index + len("[AF_INET]"):]
                    parts = address.split(':')
                    self.ip = parts[0]
                    self.port = parts[1]
    def GetHostname(self):
        #获取主机名
        for line in self.log.split('\n'):
            if "VERIFY OK: depth=0, " in line:
                index = line.find("CN=")
                if index != -1:
                    self.hostname = line[index + len("CN="):]
