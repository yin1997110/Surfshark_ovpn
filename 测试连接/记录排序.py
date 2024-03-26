import os
import pandas as pd
from collections import Counter
import re

# 递归地获取所有指定文件夹及其子文件夹中的 .ovpn 文件
def retrieve_ovpn_files(dir_path):
    ovpn_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.ovpn'):
                ovpn_files.append(os.path.join(root, file))
    return ovpn_files

# 从文件内容中提取IP地址
def extract_ip(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # 指定编码为 utf-8
            contents = file.read()
            ip = re.findall(r'(?:\d{1,3}\.){3}\d{1,3}', contents)
            return ip[0] if ip else '未找到'
    except Exception as e:
        print(f"无法读取文件 {file_path}: {e}")
        return '错误'

# 路径
search_dir = os.path.join(os.getcwd())
output_file = os.path.join(os.getcwd(), "1.xlsx")

# 获取所有 .ovpn 文件
ovpn_files = retrieve_ovpn_files(search_dir)
print(f"找到 {len(ovpn_files)} 个 .ovpn 文件")

# 提取文件名和对应的IP
file_data = {}
for file_path in ovpn_files:
    file_name = os.path.basename(file_path)
    simple_name, _ = os.path.splitext(file_name)
    ip_address = extract_ip(file_path)

    # 如果文件名已经在字典里了，我们就跳过它，因为我们只记录一次
    if simple_name in file_data:
        continue

    file_data[simple_name] = ip_address

# 计算文件名的重复次数
file_name_counts = Counter(os.path.splitext(os.path.basename(fp))[0] for fp in ovpn_files)

# 准备写入Excel的数据
df_data = []
for file_name, ip in file_data.items():
    df_data.append({
        '文件名': file_name,
        'IP地址': ip,
        '重复次数': file_name_counts[file_name],
    })

# 根据“重复次数”字段排序
df_data.sort(key=lambda x: x['重复次数'], reverse=True)

# 创建DataFrame并写入Excel文件
df = pd.DataFrame(df_data)
if not df.empty:
    df.to_excel(output_file, index=False)
    print(f"数据已写入 {output_file}")
else:
    print("没有数据写入，可能是因为没有找到.ovpn文件，或者在处理这些文件时遇到问题。")
