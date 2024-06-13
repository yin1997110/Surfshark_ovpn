## 简介

surfshark在中国地区经常无法使用,这是一个可以自动扫描目前可用节点的脚本,需要使用linux系统使用.
他会自动下载官方最新的脚本到 directory目录内以供使用

## 目录详情

* directory 目录保存着所有surfshark的openvpn配置文档 ovpn 记录着目前可用的节点 他不是实时更新的 而且中国GWF很复杂 每个地区可用节点可能都不大一样
  zh.txt 文件随便写一个数据即可 第一行为账号 第二行为密码 不要使用自己的账号 因为频繁连接会导致封号 back 目录弃用 pycache 目录弃用

* directory 目录保存着所有surfshark的openvpn配置文档

* ovpn 记录着目前可用的节点 他不是实时更新的 而且中国GWF很复杂 每个地区可用节点可能都不大一样

* zh.txt 文件随便写一个数据即可 第一行为账号 第二行为密码 不要使用自己的账号 因为频繁连接会导致封号

* back 目录弃用

* pycache 目录弃用

`使用 python connect.py 进行使用`

## 需要环境和模块

1. 需要安装软件  `python3(含以上)` `openvpn`
2. python需要安装的模块
   1. ZipFile
   2. os
   3. datatime
   4. shutil
   5. re
   6. time
   7. subprocess
   8. requests