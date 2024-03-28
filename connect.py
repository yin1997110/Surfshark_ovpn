from zipfile import ZipFile
import DownFile
import os
import getconfinfo
from datetime import datetime, timedelta
import shutil
import ConnectConf
from concurrent.futures import ThreadPoolExecutor
import re
import time


class spider():
    def __init__(self):
        self.confdirs = os.path.join(os.getcwd(),"directory")  #主配置文档目录
        self.temp_directory = os.path.join(os.getcwd(), "temp")  #设置临时缓存目录
        self.directoryconf = {}
        self.tempconf = {}
    def run(self):
        #第一步 文件下载
        downfile = DownFile.DownConfig()
        downfile.run()
        if downfile.code == 0: #判断一下有没有下载成功  做冗余处理
            #解压文件
            #判断一下目录是否存在
            if os.path.isdir(self.temp_directory):
                pass
            else:
                os.mkdir(self.temp_directory)

            #解压文件
            with ZipFile(downfile.filepath, 'r') as zip_ref:
                zip_ref.extractall(self.temp_directory)  #解压到这个位置
                print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "解压文件完毕")

            self.FileComparison()  #对比文件并且新增到主配置目录

        else:
            print("从云端下载文件失败")

        #不管下载成功还是失败 都要执行链接Openvpn的操作
        ovpn_files = [os.path.join(self.confdirs, file_name) for file_name in os.listdir(self.confdirs) if
                      file_name.endswith('.ovpn')]
        results = []
        with ThreadPoolExecutor(max_workers=50) as executor:
            for file_path in ovpn_files:
                con = ConnectConf.Connect_file(file_path)
                con.connect()
                if con.code == 0:
                    #修改名字
                    self.xgfilename(con.FilePath, con.hostname, con.ip, con.port)
                else:
                    print(f"{con.FilePath}:链接失败")

    def xgfilename(self,path,hostname,ip,port):
        #定义国家和城市
        Countries = {'AC': '阿森松岛', 'AD': '安道尔', 'AE': '阿拉伯联合酋长国', 'AF': '阿富汗', 'AG': '安提瓜和巴布达',
                     'AI': '安圭拉', 'AL': '阿尔巴尼亚', 'AM': '亚美尼亚', 'AN': '荷属安的列斯群岛', 'AO': '安哥拉',
                     'AQ': '南极洲', 'AR': '阿根廷', 'AS': '美属萨摩亚', 'AT': '奥地利', 'AU': '澳大利亚',
                     'AW': '阿鲁巴', 'AX': '奥兰群岛', 'AZ': '阿塞拜疆', 'BA': '波斯尼亚和黑塞哥维那', 'BB': '巴巴多斯',
                     'BD': '孟加拉国', 'BE': '比利时', 'BF': '布基纳法索', 'BG': '保加利亚', 'BH': '巴林',
                     'BI': '布隆迪', 'BJ': '贝宁', 'BL': '圣巴泰勒米', 'BM': '百慕大', 'BN': '文莱', 'BO': '玻利维亚',
                     'BQ': '荷兰加勒比区', 'BR': '巴西', 'BS': '巴哈马', 'BT': '不丹', 'BV': '布韦岛', 'BW': '博茨瓦纳',
                     'BY': '白俄罗斯', 'BZ': '伯利兹', 'CA': '加拿大', 'CC': '科科斯（基林）群岛', 'CD': '刚果（金）',
                     'CF': '中非共和国', 'CG': '刚果 - 布拉柴维尔', 'CH': '瑞士', 'CI': '科特迪瓦', 'CK': '库克群岛',
                     'CL': '智利', 'CM': '喀麦隆', 'CN': '中国', 'CO': '哥伦比亚', 'CP': '克利珀顿岛',
                     'CR': '哥斯达黎加', 'CU': '古巴', 'CV': '佛得角', 'CW': '库拉索', 'CX': '圣诞岛', 'CY': '塞浦路斯',
                     'CZ': '捷克共和国', 'DE': '德国', 'DG': '迪戈加西亚岛', 'DJ': '吉布提', 'DK': '丹麦',
                     'DM': '多米尼克', 'DO': '多米尼加共和国', 'DZ': '阿尔及利亚', 'EA': '休达和梅利利亚',
                     'EC': '厄瓜多尔', 'EE': '爱沙尼亚', 'EG': '埃及', 'EH': '西撒哈拉', 'ER': '厄立特里亚',
                     'ES': '西班牙', 'ET': '埃塞俄比亚', 'EU': '欧盟', 'FI': '芬兰', 'FJ': '斐济', 'FK': '福克兰群岛',
                     'FM': '密克罗尼西亚', 'FO': '法罗群岛', 'FR': '法国', 'GA': '加蓬', 'GB': '英国', 'GD': '格林纳达',
                     'GE': '格鲁吉亚', 'GF': '法属圭亚那', 'GG': '根西岛', 'GH': '加纳', 'GI': '直布罗陀',
                     'GL': '格陵兰', 'GM': '冈比亚', 'GN': '几内亚', 'GP': '瓜德罗普', 'GQ': '赤道几内亚', 'GR': '希腊',
                     'GS': '南乔治亚岛和南桑威奇群岛', 'GT': '危地马拉', 'GU': '关岛', 'GW': '几内亚比绍',
                     'GY': '圭亚那', 'HK': '香港', 'HM': '赫德和麦克唐纳群岛', 'HN': '洪都拉斯', 'HR': '克罗地亚',
                     'HT': '海地', 'HU': '匈牙利', 'IC': '加纳利群岛', 'ID': '印度尼西亚', 'IE': '爱尔兰',
                     'IL': '以色列', 'IM': '马恩岛', 'IN': '印度', 'IO': '英属印度洋领地', 'IQ': '伊拉克', 'IR': '伊朗',
                     'IS': '冰岛', 'IT': '意大利', 'JE': '泽西岛', 'JM': '牙买加', 'JO': '约旦', 'JP': '日本',
                     'KE': '肯尼亚', 'KG': '吉尔吉斯斯坦', 'KH': '柬埔寨', 'KI': '基里巴斯', 'KM': '科摩罗',
                     'KN': '圣基茨和尼维斯', 'KP': '朝鲜', 'KR': '韩国', 'KW': '科威特', 'KY': '开曼群岛',
                     'KZ': '哈萨克斯坦', 'LA': '老挝', 'LB': '黎巴嫩', 'LC': '圣卢西亚', 'LI': '列支敦士登',
                     'LK': '斯里兰卡', 'LR': '利比里亚', 'LS': '莱索托', 'LT': '立陶宛', 'LU': '卢森堡',
                     'LV': '拉脱维亚', 'LY': '利比亚', 'MA': '摩洛哥', 'MC': '摩纳哥', 'MD': '摩尔多瓦',
                     'ME': '黑山共和国', 'MF': '圣马丁岛', 'MG': '马达加斯加', 'MH': '马绍尔群岛', 'MK': '北马其顿',
                     'ML': '马里', 'MM': '缅甸', 'MN': '蒙古', 'MO': '中国澳门特别行政区', 'MP': '北马里亚纳群岛',
                     'MQ': '马提尼克', 'MR': '毛里塔尼亚', 'MS': '蒙特塞拉特', 'MT': '马耳他', 'MU': '毛里求斯',
                     'MV': '马尔代夫', 'MW': '马拉维', 'MX': '墨西哥', 'MY': '马来西亚', 'MZ': '莫桑比克',
                     'NA': '纳米比亚', 'NC': '新喀里多尼亚', 'NE': '尼日尔', 'NF': '诺福克岛', 'NG': '尼日利亚',
                     'NI': '尼加拉瓜', 'NL': '荷兰', 'NO': '挪威', 'NP': '尼泊尔', 'NR': '瑙鲁', 'NU': '纽埃',
                     'NZ': '新西兰', 'OM': '阿曼', 'PA': '巴拿马', 'PE': '秘鲁', 'PF': '法属波利尼西亚',
                     'PG': '巴布亚新几内亚', 'PH': '菲律宾', 'PK': '巴基斯坦', 'PL': '波兰',
                     'PM': '圣皮埃尔和密克隆群岛', 'PN': '皮特凯恩群岛', 'PR': '波多黎各', 'PS': '巴勒斯坦领土',
                     'PT': '葡萄牙', 'PW': '帕劳', 'PY': '巴拉圭', 'QA': '卡塔尔', 'QO': '大洋洲边远群岛',
                     'RE': '留尼汪', 'RO': '罗马尼亚', 'RS': '塞尔维亚', 'RU': '俄罗斯', 'RW': '卢旺达',
                     'SA': '沙特阿拉伯', 'SB': '所罗门群岛', 'SC': '塞舌尔', 'SD': '苏丹', 'SE': '瑞典', 'SG': '新加坡',
                     'SH': '圣赫勒拿', 'SI': '斯洛文尼亚', 'SJ': '斯瓦巴特和扬马延群岛', 'SK': '斯洛伐克',
                     'SL': '塞拉利昂', 'SM': '圣马力诺', 'SN': '塞内加尔', 'SO': '索马里', 'SR': '苏里南',
                     'SS': '南苏丹', 'ST': '圣多美和普林西比', 'SV': '萨尔瓦多', 'SX': '圣马丁岛', 'SY': '叙利亚',
                     'SZ': '斯威士兰', 'TA': '特里斯坦-达库尼亚群岛', 'TC': '特克斯和凯科斯群岛', 'TD': '乍得',
                     'TF': '法属南部领地', 'TG': '多哥', 'TH': '泰国', 'TJ': '塔吉克斯坦', 'TK': '托克劳',
                     'TL': '东帝汶', 'TM': '土库曼斯坦', 'TN': '突尼斯', 'TO': '汤加', 'TR': '土耳其',
                     'TT': '特立尼达和多巴哥', 'TV': '图瓦卢', 'TW': '台湾', 'TZ': '坦桑尼亚', 'UA': '乌克兰',
                     'UG': '乌干达', 'UM': '美国本土外小岛屿', 'US': '美国', 'UY': '乌拉圭', 'UZ': '乌兹别克斯坦',
                     'VA': '梵蒂冈', 'VC': '圣文森特和格林纳丁斯', 'VE': '委内瑞拉', 'VG': '英属维京群岛',
                     'VI': '美属维京群岛', 'VN': '越南', 'VU': '瓦努阿图', 'WF': '瓦利斯和富图纳群岛', 'WS': '萨摩亚',
                     'XK': '科索沃', 'YE': '也门', 'YT': '马约特', 'ZA': '南非', 'ZM': '赞比亚', 'ZW': '津巴布韦'}
        Cities = {'TIR': '地拉那', 'BUE': '布宜诺斯艾利斯', 'PER': '珀斯', 'ADE': '阿德莱德', 'MEL': '墨尔本',
                  'SYD': '悉尼', 'VIE': '维也纳', 'BRU': '布鲁塞尔', 'SAO': '圣保罗', 'SOF': '索非亚',
                  'MON': '蒙特利尔', 'TOR': '多伦多', 'VAN': '温哥华', 'SAN': '旧金山', 'ZAG': '萨格勒布',
                  'NIC': '尼科西亚', 'PRA': '布拉格', 'COP': '哥本哈根', 'TAL': '塔林', 'HEL': '赫尔辛基',
                  'PAR': '巴黎', 'LON': '伦敦', 'FRA': '法兰克福', 'ATH': '雅典', 'HON': '香港', 'SIN': '新加坡',
                  'BUD': '布达佩斯', 'REY': '雷克雅未克', 'MUM': '孟买', 'IND': '印多尔', 'JAK': '雅加达',
                  'DUB': '迪拜', 'MIL': '米兰', 'ROM': '罗马', 'TOK': '东京', 'RIG': '里加', 'AUC': '奥克兰',
                  'KUA': '吉隆坡', 'CHI': '芝加哥', 'AMS': '阿姆斯特丹', 'NEW': '纽约', 'OSL': '奥斯陆',
                  'GDA': '格但斯克', 'WAR': '华沙', 'LOU': '路易斯维尔', 'BUC': '布加勒斯特', 'MOS': '莫斯科',
                  'BEL': '贝尔格莱德', 'BRA': '布拉迪斯拉发', 'LJU': '卢布尔雅那', 'JOH': '约翰内斯堡', 'SEO': '首尔',
                  'MAD': '马德里', 'STO': '斯德哥尔摩', 'ZUR': '苏黎世', 'TAI': '台中市', 'BAN': '曼谷',
                  'BUR': '布尔萨', 'KYI': '基辅', 'MAN': '马纳萨斯', 'DAL': '达拉斯', 'BUF': '布法罗', 'DEN': '丹佛',
                  'OKL': '俄克拉何马城', 'SEA': '西雅图', 'ATL': '亚特兰大', 'LAS': '拉斯维加斯', 'PHO': '菲尼克斯',
                  'MIA': '迈阿密', 'LOS': '洛杉矶', 'HOC': '胡志明市', 'LUX': '卢森堡', 'KAN': '堪萨斯城',
                  'BAR': '巴塞罗那', 'DET': '底特律', 'CHA': '夏洛特', 'TAM': '坦帕', 'HOU': '休斯敦', 'CHE': '金奈',
                  'GLA': '格拉斯哥', 'SAL': '盐湖城', 'POR': '波尔图', 'BRI': '布里斯班', 'BEN': '本德',
                  'ORL': '奥兰多', 'LAT': '莱瑟姆', 'BOS': '波士顿', 'SAR': '萨拉热窝', 'MAR': '马赛', 'BER': '柏林',
                  'VAL': '巴伦西亚', 'BOR': '波尔多', 'LIS': '里斯本', 'ASH': '阿什伯恩', 'ANT': '安特卫普'}

        #找出国家和城市代码
        groups = hostname.split("-")
        country_code = groups[0].upper()
        city_code = groups[1].upper()
        if country_code in Countries:
            country_name = Countries[country_code]   #找出国家
        else:
            country_name = "未知国家"

        if city_code in Cities:
            city_name = Cities[city_code]            #找出城市
        else:
            city_name = "未知城市"

        #设置新得文件名
        #新名字以  国家---城市---IP---端口.ovpn
        new_name = f"{country_name}---{city_name}---{ip}-{port}.ovpn"

        #给文件改名
        new_file_path = os.path.join(self.confdirs,new_name)  #新文件得地址
        os.rename(path, new_file_path)  #修改文件名字

        #判断目录是否存在
        ovpnpath = os.path.join(os.getcwd(),"ovpn")
        if not os.path.exists(ovpnpath):
            print(f"目录 ovpn 不存在，正在创建...")
            os.makedirs(ovpnpath)

        #检测目标目录是否存在
        country_path = os.path.join(ovpnpath,country_name)
        city_path = os.path.join(country_path, city_name)
        if not os.path.exists(ovpnpath):
            print("国家名目录不存在 正在创建...")
            os.makedirs(country_path)
            if not os.path.exists(city_path):
                print("城市名目录不存在 正在创建...")
                os.makedirs(city_path)
                # 拷贝文件到目标目录
                ovpn_file_path = os.path.join(city_path, new_name)
                shutil.copyfile(new_file_path, ovpn_file_path)

    def FileComparison(self):
        #获取directory目录所有配置文档的IP和端口
        self.directoryconf = getconfinfo.process_ovpn_directory(self.confdirs)
        #此时保存格式为 "IP:端口":"文件地址"


        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + f"获取{len(self.directoryconf)}个配置项!")
        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "开始对比文件")


        #获取temp目录所有配置文档的IP和端口
        self.tempconf = getconfinfo.process_ovpn_directory(self.temp_directory)

        #进行对比
        for temp_ip_port, temp_file_path in self.tempconf.items():   #开始循环temp内得ip和端口
            for direct_ip_port, direct_file_path in self.directoryconf.items():   #然后循环所有主文件得地址和端口
                if temp_ip_port == direct_ip_port:   #如果找到相匹配项
                    os.remove(direct_file_path)     #删除主文件得匹配项
                    print("删除:" + direct_file_path)


        #把整个time目录内的文件都拷贝到directory目录
        #遇到新的问题 文件名一样IP不一样
        for file in os.listdir(self.temp_directory):
            path_file = os.path.join(os.getcwd(), "temp", file)  #源文件
            ip = ""
            port = ""
            #获取IP和port来定义新得文件名
            with open(path_file, "r") as file:
                content = file.read()
                ip_port_match = re.search(r"remote\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\s+(\d+)", content)  #获取IP和port
                if ip_port_match:
                    ip = ip_port_match.group(1)
                    port = ip_port_match.group(2)

            #定义新的文件名
            new_name = f"{ip}---{port}--{str(int(time.time()))}.ovpn"
            os.rename(path_file,os.path.join(os.getcwd(), "temp",new_name))
            source_path = os.path.join(os.getcwd(), "temp", new_name)
            destination_path = os.path.join(os.getcwd(), "directory", new_name)

            print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + ":从temp目录移动文件:" + source_path +"到"+ destination_path)

            if os.path.exists(destination_path):
                os.remove(destination_path)  # 如果目标路径已存在，则删除它

            shutil.move(source_path, destination_path)   #复制文件内容



        # 删除目录
        shutil.rmtree(self.temp_directory, ignore_errors=True)  # 删除目录
        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "删除temp目录完成")
        os.makedirs(self.temp_directory, exist_ok=True)  # 新建目录   这样子代码会简便
        print((datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d-%H-%M-%S') + "创建temp目录完成")


a = spider()
a.run()
