import os
import re

def process_ovpn_directory(directory):
    def extract_ip_port(file_path):
        ip_port_list = []
        with open(file_path, 'r') as file:
            for line in file:
                match = re.search(r'remote\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(\d+)', line)
                if match:
                    ip = match.group(1)
                    port = match.group(2)
                    ip_port_list.append(f"{ip}:{port}")
        return ip_port_list

    def get_ovpn_files(directory):
        ovpn_files = []
        for file in os.listdir(directory):
            if file.endswith('.ovpn'):
                ovpn_files.append(os.path.join(directory, file))
        return ovpn_files

    ip_port_dict = {}
    ovpn_files = get_ovpn_files(directory)
    for file_path in ovpn_files:
        ip_port_list = extract_ip_port(file_path)
        for ip_port in ip_port_list:
            ip_port_dict[ip_port] = file_path
    return ip_port_dict

