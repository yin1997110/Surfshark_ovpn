import os
import requests

class DownConfig():
    def __init__(self):
        self.Cwd = os.path.join(os.getcwd(),"downconfig")  #获取当前目录
        self.headers = {
            'Referer': 'https://my.shark-china.com/vpn/manual-setup/main/openvpn?restricted=&country=CN&referrer=%2Fvpn%2Fmanual-setup%2Fmain%2Fopenvpn',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Cookie': 'surfshark-uuid=1c26349d-0dfc-4fa8-aac0-aa2f012cefd9; surfshark-locale=zh; cf_clearance=qngnOzmxLyi2hSK0PSOVmMzjf8N7xxcvRqCNPj4yifk-1704431053-0-2-e47d3756.7a4e0add.b37c68b6-250.0.0; surfshark-consent-state-default=a:1|m:1; _gid=GA1.2.1014671108.1704431072; _gcl_au=1.1.2042768680.1704431073; _uetsid=eab67490ab8711ee806c87617a29296f; _uetvid=eab6a460ab8711eea053a5a44c8a2759; _ssexp=1704438273; _sstk=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MDQ0MzEwNzMsImV4cCI6MTcwNDQzODI3MywidXNlcm5hbWUiOiJhYWRkMjAwMzIwMDNAc2luYS5jb20iLCJpZCI6IjhiYWQwNDI0LWQxYWEtNDUzMi04NmNkLWQ3ZmI4NDQxOGI2NiIsInQiOiJKT3paYjNNYkJoWXROMDc4dDhSUzZUSWFmSEF3eXBPNGxXUWwxTDlSYXJLZ3czalNXaUwyTzdWdjlWMk1pMWxMIn0.La8oeUy88Or7q6SGuBjgyPt6QhXy61feM8wr1l_LNmVLCnOvytCI_pVkn0d2IiUED5TA-AAzLlc3LNFvITjnUJXKPPKiEMpIQLnpvsa3t6FGcJXhHvNFk3FNEJkCvNSG63nwV3Cl3XXutnx5t7e_RLQTdPdhpGz2mhtOJqMRTHKFoBYr8RNwuphE5L7l3C-V8NHdjQUNPSFZwACx18mkZt7cZMta1B7vs7_YyFnVJyXB5KTihsnyPOynZA-8E-gswSC0jmSlFlk6hetOxrN5Og_aSdeOWB3E5oUse7hG7dqEJr2Q161-nsCbp28h5SB3t8ZaXFnhxpDIkMP-uB4xiR-jiVUoO6r21Gkjq_LPEST6X3Lnya4R7LrYLIXuN2b9bAvV2hVfPsZuX_H0S65-EQ47wdbiWMCFUNu_cipDYFHFjb64wjM8UpN5bZD8DHoNdU3-Pp39qL1ngYlO_rttcXs7BkVfhzNIYVwqG4TdQejC9bZzAmNq25jPXKGkiLqYfURWQ3smXlN7psMdhJvm7y_jMu9G4gywhrFa2DmgIMD-LCgWiUhOkfVMmgursVzmNGYc0o91RwrcHaEwnSY37Pd7Ky7Mc4HPeIetYgTDdrdfYI8iKxUP45KErin5eN98YTvuZvsd9Kpoqlq-ibtIVpdJ6KUlxcRVT_L1enlekBo; _ssrtk=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MDQ0MzEwNzMsImV4cCI6MTczNTk2NzA3MywidXNlcm5hbWUiOiJhYWRkMjAwMzIwMDNAc2luYS5jb20iLCJpZCI6IjhiYWQwNDI0LWQxYWEtNDUzMi04NmNkLWQ3ZmI4NDQxOGI2NiIsInJ0IjoiNHhMMG0rYnVNeEFTU3pGU0phcWZYYUxpcHpaU0hDVjlLamEvWEE5a0prVTd4OEpiWkJWaFdwYi9FZmtZT3JMWSJ9.DPb2FHvQMfD4RTiPLm5mHnoXGm3bkg_MPsdJqF_kIX8GESbgZ1Vzfs7njh9_8S9A_fIrvK23fNgJ2dVadUqcEv6dQjFu53TxKpCDyf4JeeEJ3Kz9xlE4tqekB1fv4KaYyDGwLMJInSsQH6XmeNf2j1wCab6QfMuK9X9c64twLJ5SyaZYVrIdi2zJTXaSKL7071IvAudBFZqQaErBZGtkZZ36cDmbmFbY6o59WTCG89zN78XRU40311wLdn6a8La6DoL6LkASXt5iZPOpKonR7W2Rrjy6r5bNJqvkZE5rczag4IFAMy7ahZujHr9VTYGU9zVi-qKkvzixzPmBkN0cW_MzhTac3y_Kmc1okN0p_vcWZ2gQMe7n5jIUyHw7h2IOhKABEj-AHDTDQA_aOF5JGNtOdkLkq-FeKEjSWpRAPmDSUVa9-AQoWHlwRwjETt8YVbc_vRZCwEFcPCFgSMPI-2HfkYWiwaFu6fu2uRlsrZ4eDsepGCh-ioGJ7mC3Dl2keO_DStX-WJ_g9eMcR6ZmNl9-iufdJKZmfzkje-Lp0nC0D_7fB21GUiziKh6cgwEGqpkS5wav3nq4LeD7VFrT0uiIMkamSZ-3-jLs1sYKzHD_S5aEES4bse-IOrokIQVczqllNcOrLL3MH5hc_Orxb6aWcBsxvpU7kcwyslTgDgA; _ssli=1; _fbp=fb.1.1704431075229.1735010498; _ga_10ZY7M4LNV=GS1.1.1704431073.1.0.1704431076.57.0.0; surfshark-screen=0; _ga=GA1.2.1025821501.1704431072; __cf_bm=jfeguJ7DoHrnkKkv4w0A.kmqrwDFdaT0v3yUTABSwNo-1704435798-1-AQ1IJcSoXEg9lvb6qco%2Fb%2F%2FGM3bM51AnOZNG%2Fm26GYQ7xMf5hCK6YWixB%2BOx%2BmXuzszl1W%2B6TVG15pvPwnAuNas%3D; _cfuvid=Kj5A1Z0dVERLFsPaoZBA.Xu7uoAABAfpJvO1EEF0WNM-1704435798711-0-604800000; __cf_bm=fqpM5Oged2fsaVdJ9f4L5hMLERi78Me25U8iSQoQG4g-1704436131-1-AYJ7D01ENRYiQEUJoavtCqdUu4KVeiyzipwaYuxCp+0FQqrWXRH+72X8BncZKa3k+H7t5ohVYa39LnKnOO+6tQc=; _gat_UA-116900630-1=1'
        }
        self.FileUrl = "https://my.shark-china.com/vpn/p_api/v1/server/configurations?unrestricted=1"
        self.code = 9   #如果为9 未初始化 如果未 0 则成功 为 1则失败
        self.filepath = ""


    def run(self):
        #判断目录是否存在
        if os.path.isdir(self.Cwd):
            self.down()
        else:
            os.mkdir(self.Cwd)
            self.down()
    def down(self):
        #开始下载文件
        self.filepath = os.path.join(self.Cwd,"down.zip")
        response = requests.get(self.FileUrl,headers=self.headers)
        if response.status_code == 200:  #判断是否能正常访问
            with open(self.filepath, 'wb') as file:
                #保存文件
                file.write(response.content)
                self.code = 0
        else:
            self.code = 1
