import os
import glob
import shutil
import time
import requests
import concurrent.futures
import re
from zipfile import ZipFile
from datetime import datetime, timedelta
from pathlib import Path
import aioping
import subprocess
import logging
import json



#修改文件名且带地名
def location_based_file_name():

    directory_path = os.path.join(os.getcwd(), "directory")

    for file_name in os.listdir(directory_path):
        full_file_path = os.path.join(directory_path, file_name)
        with open(full_file_path, "r") as file:
            content = file.read()
            
            ip_port_match = re.search(r"remote\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(\d+)", content)  # 这里应该有一个 # 开头的注释符号
            if ip_port_match:  # 需要检查 ip_port_match 是否为 None
                ip = ip_port_match.group(1)
                port = ip_port_match.group(2)
                
                with open(os.path.join(os.getcwd(), "IP库.txt"), "r", encoding='utf-8', errors='ignore') as f:
                    found = False
                    for line in f:
                        if ip in line:
                            parts = line.split("-----")
                            dz = parts[1].strip()
                            found = True  # 在找到匹配的 IP 时将 found 设置为 True
                            break  # 找到匹配项就退出循环
                    
                    if not found:
                        url = "https://api.ip138.com/ip/"
                        headers = {"token": "8c67b20d60ff027014b36f32ae5f1f98"}
                        response = requests.get(url, params={"ip": ip, "datatype": "jsonp", "callback": "find"}, headers=headers)
                        if response.status_code == 200:
                            match = re.search(r'find\((.*)\)', response.text)
                            if match:
                                json_str = match.group(1)
                                data_dict = json.loads(json_str)
                                data_list = data_dict.get("data", [])
                                if len(data_list) >= 3:
                                    dz = '-'.join(data_list[:3])
                                    new_text = f'{ip}-----{dz}'
                                    with open(os.path.join(os.getcwd(), "IP库.txt"), 'a',encoding='utf-8') as a:
                                        a.write(f"{new_text}\n")  # 使用 \n 来创建新的一行

        new_filename = f"{dz}-{ip}-{port}.ovpn"  #新文件名
        new_file_path = os.path.join(directory_path, new_filename)  #新文件路径+文件名
        if new_filename != file_name:
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            os.rename(full_file_path, new_file_path)
            print(f"正在修改:{full_file_path}")

#文件分类带地名
def file_category():
    connect_path = os.path.join(os.getcwd(), "connect")
    for file_name in os.listdir(connect_path):
        parts = file_name.split("-")
        path=os.path.join(os.getcwd(), "connect",parts[0])
        if not os.path.exists(path):
            print(f"目录 {path} 不存在，正在创建...")
            os.makedirs(path)
        shutil.move(os.path.join(connect_path,file_name),path)


#connect负责多线程连接尝试
def connect():

    logging.basicConfig(level=logging.INFO)

    def get_ip_from_ovpn(file_path):
        with open(file_path, "r") as file:
            content = file.read()
            ip_match = re.search(r"remote\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", content)
            if ip_match:
                return ip_match.group(1)
        return None


    def is_pingable(ip):
        try:
            aioping.ping(ip)
            return True
        except aioping.PingError as e:
            logging.warning(f"Ping Error: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected Error: {e}")
            return False


    def process_file(file_name, directory, connect_directory):
        file_path = os.path.join(directory, file_name)
        ip = get_ip_from_ovpn(file_path)
        
        if ip:
            if is_pingable(ip):
                destination_path = os.path.join(connect_directory, file_name)
                shutil.copy(file_path, destination_path)
                logging.info(f"Success: Copied {file_name} to connect directory.")
            else:
                logging.error(f"Error: {file_name} is not reachable.")
        else:
            logging.error(f"Error: No IP found in {file_name}.")


    def main():
        directory = "directory"
        connect_directory = "connect"
        
        if not os.path.exists(connect_directory):
            os.makedirs(connect_directory)
        
        ovpn_files = [filename for filename in os.listdir(directory) if filename.endswith(".ovpn")]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(process_file, ovpn_files, [directory]*len(ovpn_files), [connect_directory]*len(ovpn_files))


    if __name__ == "__main__":
        main()

    #步骤10 尝试连接openvpn

    config_folder = "connect"
    config_files = [f for f in os.listdir(config_folder) if f.endswith(".ovpn")]

    def connect_vpn(config_file):
        try:
            log_file = config_file.replace(".ovpn", ".log")
            with open(log_file, "w") as log:
                process = subprocess.Popen(["openvpn", "--auth-nocache", "--config", os.path.join(config_folder, config_file), "--auth-user-pass", os.path.join(os.getcwd(), "zh.txt")], stdout=log, stderr=log)
            
            time.sleep(5)
            
            with open(log_file, "r") as f:
                log_content = f.read()
                if "prod.surfshark.com" in log_content:
                    return True, process, log_file
                else:
                    return False, process, log_file
        except Exception as e:
            print(f"错误: {e}")
            return False, None, log_file

    def thread_function(config_file):
        print(f"尝试连接 {config_file}")
        success, process, log_file = connect_vpn(config_file)
        
        if success:
            print("连接成功！")
        else:
            print(f"连接失败,即将删除文件 删除: {config_file}")
            os.remove(os.path.join(os.getcwd(), "connect",config_file))

        if process:
            process.terminate()

    # 使用线程池来运行
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(thread_function, config_files)

    #步骤11 删除根目录的log文件
    for log_file in glob.glob('*.log'):
        os.remove(log_file)

    #插入一个以文件地名+分类的操作
    file_category()

    #步骤13 把所有可以连接得文件打包放到ovpn内
    shutil.make_archive(os.path.join(os.getcwd(), "ovpn", (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S')+"_files"), 'zip', os.path.join(os.getcwd(),"connect"))
    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "打包可以连接得文件放到ovpn目录")

    #步骤14 清空connect目录
    shutil.rmtree(os.path.join(os.getcwd(), "connect"), ignore_errors=True)  #删除目录
    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "删除connect目录")
    os.makedirs(os.path.join(os.getcwd(), "connect"), exist_ok=True)         #新建目录   这样子代码会简便
    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "新建connect目录")


    # 等待6个小时
    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + " 等待下次循环中 " )
    time.sleep(7200)



def main():
    while True:
        try:
            # 步骤1: 排查文件

            # 定义要检查和创建的目录列表
            directories = ['back', 'connect', 'directory', 'logs', 'ovpn', 'temp']

            # 遍历目录列表，检查每个目录是否存在，如果不存在则创建
            for directory in directories:
                path = os.path.join(os.getcwd(), directory)
                if not os.path.exists(path):
                    print(f"目录 {directory} 不存在，正在创建...")
                    os.makedirs(path)
                    print(f"目录 {directory} 已创建。")
                else:
                    print(f"目录 {directory} 已存在。")

            # 步骤2: 下载文件并保存为down.zip


            headers = {
                'Referer':'https://my.shark-china.com/vpn/manual-setup/main/openvpn?restricted=&country=CN&referrer=%2Fvpn%2Fmanual-setup%2Fmain%2Fopenvpn',
                'Sec-Ch-Ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
                'Cookie':'surfshark-uuid=1c26349d-0dfc-4fa8-aac0-aa2f012cefd9; surfshark-locale=zh; cf_clearance=qngnOzmxLyi2hSK0PSOVmMzjf8N7xxcvRqCNPj4yifk-1704431053-0-2-e47d3756.7a4e0add.b37c68b6-250.0.0; surfshark-consent-state-default=a:1|m:1; _gid=GA1.2.1014671108.1704431072; _gcl_au=1.1.2042768680.1704431073; _uetsid=eab67490ab8711ee806c87617a29296f; _uetvid=eab6a460ab8711eea053a5a44c8a2759; _ssexp=1704438273; _sstk=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MDQ0MzEwNzMsImV4cCI6MTcwNDQzODI3MywidXNlcm5hbWUiOiJhYWRkMjAwMzIwMDNAc2luYS5jb20iLCJpZCI6IjhiYWQwNDI0LWQxYWEtNDUzMi04NmNkLWQ3ZmI4NDQxOGI2NiIsInQiOiJKT3paYjNNYkJoWXROMDc4dDhSUzZUSWFmSEF3eXBPNGxXUWwxTDlSYXJLZ3czalNXaUwyTzdWdjlWMk1pMWxMIn0.La8oeUy88Or7q6SGuBjgyPt6QhXy61feM8wr1l_LNmVLCnOvytCI_pVkn0d2IiUED5TA-AAzLlc3LNFvITjnUJXKPPKiEMpIQLnpvsa3t6FGcJXhHvNFk3FNEJkCvNSG63nwV3Cl3XXutnx5t7e_RLQTdPdhpGz2mhtOJqMRTHKFoBYr8RNwuphE5L7l3C-V8NHdjQUNPSFZwACx18mkZt7cZMta1B7vs7_YyFnVJyXB5KTihsnyPOynZA-8E-gswSC0jmSlFlk6hetOxrN5Og_aSdeOWB3E5oUse7hG7dqEJr2Q161-nsCbp28h5SB3t8ZaXFnhxpDIkMP-uB4xiR-jiVUoO6r21Gkjq_LPEST6X3Lnya4R7LrYLIXuN2b9bAvV2hVfPsZuX_H0S65-EQ47wdbiWMCFUNu_cipDYFHFjb64wjM8UpN5bZD8DHoNdU3-Pp39qL1ngYlO_rttcXs7BkVfhzNIYVwqG4TdQejC9bZzAmNq25jPXKGkiLqYfURWQ3smXlN7psMdhJvm7y_jMu9G4gywhrFa2DmgIMD-LCgWiUhOkfVMmgursVzmNGYc0o91RwrcHaEwnSY37Pd7Ky7Mc4HPeIetYgTDdrdfYI8iKxUP45KErin5eN98YTvuZvsd9Kpoqlq-ibtIVpdJ6KUlxcRVT_L1enlekBo; _ssrtk=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MDQ0MzEwNzMsImV4cCI6MTczNTk2NzA3MywidXNlcm5hbWUiOiJhYWRkMjAwMzIwMDNAc2luYS5jb20iLCJpZCI6IjhiYWQwNDI0LWQxYWEtNDUzMi04NmNkLWQ3ZmI4NDQxOGI2NiIsInJ0IjoiNHhMMG0rYnVNeEFTU3pGU0phcWZYYUxpcHpaU0hDVjlLamEvWEE5a0prVTd4OEpiWkJWaFdwYi9FZmtZT3JMWSJ9.DPb2FHvQMfD4RTiPLm5mHnoXGm3bkg_MPsdJqF_kIX8GESbgZ1Vzfs7njh9_8S9A_fIrvK23fNgJ2dVadUqcEv6dQjFu53TxKpCDyf4JeeEJ3Kz9xlE4tqekB1fv4KaYyDGwLMJInSsQH6XmeNf2j1wCab6QfMuK9X9c64twLJ5SyaZYVrIdi2zJTXaSKL7071IvAudBFZqQaErBZGtkZZ36cDmbmFbY6o59WTCG89zN78XRU40311wLdn6a8La6DoL6LkASXt5iZPOpKonR7W2Rrjy6r5bNJqvkZE5rczag4IFAMy7ahZujHr9VTYGU9zVi-qKkvzixzPmBkN0cW_MzhTac3y_Kmc1okN0p_vcWZ2gQMe7n5jIUyHw7h2IOhKABEj-AHDTDQA_aOF5JGNtOdkLkq-FeKEjSWpRAPmDSUVa9-AQoWHlwRwjETt8YVbc_vRZCwEFcPCFgSMPI-2HfkYWiwaFu6fu2uRlsrZ4eDsepGCh-ioGJ7mC3Dl2keO_DStX-WJ_g9eMcR6ZmNl9-iufdJKZmfzkje-Lp0nC0D_7fB21GUiziKh6cgwEGqpkS5wav3nq4LeD7VFrT0uiIMkamSZ-3-jLs1sYKzHD_S5aEES4bse-IOrokIQVczqllNcOrLL3MH5hc_Orxb6aWcBsxvpU7kcwyslTgDgA; _ssli=1; _fbp=fb.1.1704431075229.1735010498; _ga_10ZY7M4LNV=GS1.1.1704431073.1.0.1704431076.57.0.0; surfshark-screen=0; _ga=GA1.2.1025821501.1704431072; __cf_bm=jfeguJ7DoHrnkKkv4w0A.kmqrwDFdaT0v3yUTABSwNo-1704435798-1-AQ1IJcSoXEg9lvb6qco%2Fb%2F%2FGM3bM51AnOZNG%2Fm26GYQ7xMf5hCK6YWixB%2BOx%2BmXuzszl1W%2B6TVG15pvPwnAuNas%3D; _cfuvid=Kj5A1Z0dVERLFsPaoZBA.Xu7uoAABAfpJvO1EEF0WNM-1704435798711-0-604800000; __cf_bm=fqpM5Oged2fsaVdJ9f4L5hMLERi78Me25U8iSQoQG4g-1704436131-1-AYJ7D01ENRYiQEUJoavtCqdUu4KVeiyzipwaYuxCp+0FQqrWXRH+72X8BncZKa3k+H7t5ohVYa39LnKnOO+6tQc=; _gat_UA-116900630-1=1'
            }

            response = requests.get('https://my.shark-china.com/vpn/p_api/v1/server/configurations?unrestricted=1',headers=headers)
            if response.status_code == 200:
                with open('down.zip', 'wb') as file:
                    file.write(response.content)
                    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + " 从云端下载文件 ")
                    time.sleep(20)
                    # 步骤3 解压文件到temp内
                    temp_directory = 'temp'
                    with ZipFile('down.zip', 'r') as zip_ref:
                        zip_ref.extractall(temp_directory)
                        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "解压文件完毕")
                        #解压完毕以后删除文件
                        os.remove(os.path.join(os.getcwd(), 'down.zip'))
                        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "下载好得ZIP删除完毕")

                    # 步骤4: 检查和删除directory目录中的重复文件
                    for temp_file_name in os.listdir(os.path.join(os.getcwd(), "temp")):
                        for directory_file_name in os.listdir(os.path.join(os.getcwd(), "directory")):
                            if temp_file_name == directory_file_name:
                                print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + ":删除重复文件:"+os.path.join(os.getcwd(), "directory",directory_file_name))
                                os.remove(os.path.join(os.getcwd(), "directory",directory_file_name))

                    # 步骤5: 移动temp目录下的所有文件到directory目录   
                    for file in os.listdir(os.path.join(os.getcwd(), "temp")):
                        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + ":从temp目录移动文件:"+os.path.join(os.getcwd(), "temp",file),os.path.join(os.getcwd(), "directory") + "到directory")
                        shutil.move(os.path.join(os.getcwd(), "temp",file),os.path.join(os.getcwd(), "directory"))

                    # 步骤6: 清空temp目录
                    shutil.rmtree(os.path.join(os.getcwd(), "temp"), ignore_errors=True)  #删除目录
                    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "删除temp目录完成")
                    os.makedirs(os.path.join(os.getcwd(), "temp"), exist_ok=True)         #新建目录   这样子代码会简便
                    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "创建temp目录完成")  
                    
                    #插入一个给文件加地名的功能
                    location_based_file_name() 

                    # 步骤7: 打包directory目录
                    shutil.make_archive(os.path.join(os.getcwd(), "back", (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S')+"_files"), 'zip', os.path.join(os.getcwd(),"directory"))
                    print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "备份directory文件完毕")
                    connect()

################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
#################################################         以上代码为可以顺利下载,以下为使用老文件测试                  #############################################################
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
################################################################################################################################################################################
            else:
                connect()
                # 步骤8:使用aioping模块批量检测directory目录可以连通得文件并放到connect文件内
                # 设置日志

            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Restarting from Step 0...")
            continue

if __name__ == "__main__":
    main()
