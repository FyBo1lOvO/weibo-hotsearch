import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import matplotlib.colors as mcolors
import json
import openpyxl
import csv
from datetime import datetime
# 目标URL和请求头
url = 'https://www.weibo.com/ajax/side/hotSearch'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
    'Referer': 'https://www.weibo.com/hot/search',
    'Cookie': 'SCF=AhZskOkOxMJR3jUA-no2NdIS0QOHAxxExLhpUGrP7bQWGK9huWMxHxwDKKI-l2yJjCXVIHjmGUDUyE61nnxbEMg.; SUB=_2A25EKpQBDeRhGeBM6FIU8yjKyTiIHXVnSanJrDV8PUNbmtANLUbwkW9NRO_I43UALSDySHz6aIxgNlP_b26x9LhQ; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhozdfB52I1REFNs1qsqdJT5JpX5KzhUgL.FoqEe05fe0qceoB2dJLoI7LKB-fkPX9FMJYt; ALF=02_1767272785; PC_TOKEN=c1f62aa972; XSRF-TOKEN=1k8JUU1gpuuPyp8XjgEUAP_B; WBPSESS=bjCFc0vP5qpUsuOEw4oLCoSGss0KRZoZcSdnPH6fdODnF1kzDG7fCyURBKYKOpA8Lm4F_yQEPLaMaKFx9dgp2vTULWDsvtkL1IL14nZDcURcqxvutVdQxGD3rgMPykRUmWb3tzxj25G0Qv5Wb5YV8A==',
    'X-XSRF-TOKEN': 'i7XvUVQ20-NDHnsh0ijQZKPB'  # 补充XSRF令牌，增强请求有效性
}

try:
    # 发送请求（添加超时设置，避免无限等待）
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # 触发HTTP错误（如404、500）
    
    # 解析JSON数据
    data = response.json()
    hot_search_list = data.get('data', {}).get('realtime', [])
    
    if not hot_search_list:
        print("未获取到有效热搜数据")
        exit()
    
    # 准备CSV文件写入
    csv_filename = "D:/Jupyter Code/数据采集期末论文/2025.12.03.2110微博数据/解析后csv文件/weibo_total_hotsearch_data.csv"
    # 定义CSV字段
    fieldnames = ['热搜排名', '热搜内容', '热搜热度']
    
    # 打开CSV文件
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        # 获取当前采集时间
        crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 遍历热搜数据，写入每行内容
        for item in hot_search_list:
            # 提取数据（处理可能的缺失值）
            rank = item.get('realpos', '')  # 排名
            keyword = item.get('word', '')  # 热搜关键词
            hot_value = item.get('num', 0)  # 热度值
            
            # 写入一行数据
            writer.writerow({
                '热搜排名': rank,
                '热搜内容': keyword,
                '热搜热度': hot_value
            })
    
    print(f"热搜数据已成功保存到 {csv_filename}")
    print(f"共采集到 {len(hot_search_list)} 条热搜")

except requests.exceptions.RequestException as e:
    print(f"请求失败：{str(e)}")
except json.JSONDecodeError:
    print("JSON数据解析失败")
except Exception as e:
    print(f"程序异常：{str(e)}")


import requests
import json
import os
import time
import warnings

def get_life_json(json_filename):
    # 抑制SSL警告
    warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


    # 会话对象（模拟真实用户，提高爬取成功率）
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'Referer': 'https://www.weibo.com/',
        'Accept': 'application/json, text/plain, */*',
        'X-XSRF-TOKEN': 'i7XvUVQ20-NDHnsh0ijQZKPB'
    })

    # 最新Cookie（必须替换为你浏览器的有效Cookie！）
    cookies = {
        'SCF': 'AhZskOkOxMJR3jUA-no2NdIS0QOHAxxExLhpUGrP7bQWGK9huWMxHxwDKKI-l2yJjCXVIHjmGUDUyE61nnxbEMg.',
        'SUB': '_2A25EKpQBDeRhGeBM6FIU8yjKyTiIHXVnSanJrDV8PUNbmtANLUbwkW9NRO_I43UALSDySHz6aIxgNlP_b26x9LhQ',
        'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WhozdfB52I1REFNs1qsqdJT5JpX5KzhUgL.FoqEe05fe0qceoB2dJLoI7LKB-fkPX9FMJYt',
        'ALF': '02_1767272785',
        'XSRF-TOKEN': 'i7XvUVQ20-NDHnsh0ijQZKPB',
        'WBPSESS': 'bjCFc0vP5qpUsuOEw4oLCoSGss0KRZoZcSdnPH6fdODnF1kzDG7fCyURBKYKOpA8Lm4F_yQEPLaMaKFx9dgp2pWYB4PxCrB4lY6oi6ozV_PQTAQDTfo8jNong9UaTkBYdoFznRK8tXaaOn-JfpKCEg=='
    }
    session.cookies.update(cookies)

    try:
        print("🔍 模拟访问微博首页...")
        session.get('https://www.weibo.com/', timeout=10, verify=False)
        time.sleep(2)  # 随机等待

        url = 'https://www.weibo.com/ajax/statuses/life'
        response = session.get(url, timeout=15, verify=False)
        response.raise_for_status()
    
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
    
        print(f"✅ JSON数据已保存到：{json_filename}")
        print("📌 后续可直接读取本地JSON，无需再次请求服务器")

    except Exception as e:
        print(f"❌ 爬取JSON失败：{str(e)}")
        # 若JSON接口失败，降级为HTML爬取后保存JSON
        print("🔄 尝试HTML爬取后转换为JSON...")
        url = 'https://www.weibo.com/hot/life'
        response = session.get(url, timeout=15, verify=False)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        hot_list = []
        # 解析HTML并构造JSON数据
        for idx, card in enumerate(soup.find_all('div', class_='card-wrap')[:50], 1):
            keyword = card.find('span', class_='txt').get_text(strip=True) if card.find('span', class_='txt') else ''
            hot_value = card.find('span', class_='hot').get_text(strip=True) if card.find('span', class_='hot') else '0'
            if keyword:
                hot_list.append({
                    '排名': idx,
                    '热搜关键词': keyword,
                    '热度值': hot_value,
                    '分类': '生活',
                    '采集时间': time.strftime('%Y-%m-%d %H:%M:%S')
                })
        # 保存构造的JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({'data': hot_list}, f, ensure_ascii=False, indent=2)
        print(f"✅ 已通过HTML解析构造JSON并保存到：{json_filename}")


import requests
import json
import os
import time
import warnings

def get_social_json(json_filename):
    # 抑制SSL警告
    warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # 会话对象（模拟真实用户，提高爬取成功率）
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://www.weibo.com/',
        'Accept': 'application/json, text/plain, */*',
        'X-XSRF-TOKEN': 'i7XvUVQ20-NDHnsh0ijQZKPB'
    })

    # 最新Cookie（必须替换为你浏览器的有效Cookie！）
    cookies = {
        "XSRF-TOKEN": "TWrs0v9VQUWlSxV_iyFBtxMa",
        "SCF": "AoT3RMJQvYRdO_ToyeJLF6X4B4RgFWpZhj9SXLWqkE1vdhBCjgCLATqI0UWuYMYcz_CN7SHqchlq36byDgKJaXs.",
        "SUB": "_2A25EK_4uDeRhGeBM6FIU8yjKyTiIHXVnSX_mrDV8PUNbmtANLWPwkW9NRO_I41Y3tA75vVMmRaHQ6hbzRn-5zJ6j",
        "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhozdfB52I1REFNs1qsqdJT5JpX5KzhUgL.FoqEe05fe0qceoB2dJLoI7LKB-fkPX9FMJYt",
        "ALF": "02_1767316350",
        "WBPSESS": "bjCFc0vP5qpUsuOEw4oLCoSGss0KRZoZcSdnPH6fdOAE23H6lD7r0QK_ljLtvI-VplpJtqG36yWgFWcGV2Z-XphfrtqzlYgasGZzDmaLARm7OTMDlRcYp2GfHc1DU5ygvIwMBvmR6xHad-bX0_K-zQ=="
    }
    session.cookies.update(cookies)

    try:
        print("🔍 模拟访问微博首页...")
        session.get('https://www.weibo.com/', timeout=10, verify=False)
        time.sleep(2)  # 随机等待

        url = 'https://weibo.com/ajax/statuses/social'
        response = session.get(url, timeout=15, verify=False)
        response.raise_for_status()
    
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
    
        print(f"✅ JSON数据已保存到：{json_filename}")
        print("📌 后续可直接读取本地JSON，无需再次请求服务器")

    except Exception as e:
        print(f"❌ 爬取JSON失败：{str(e)}")
        # 若JSON接口失败，降级为HTML爬取后保存JSON
        print("🔄 尝试HTML爬取后转换为JSON...")
        url = 'https://www.weibo.com/hot/life'
        response = session.get(url, timeout=15, verify=False)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        hot_list = []
        # 解析HTML并构造JSON数据
        for idx, card in enumerate(soup.find_all('div', class_='card-wrap')[:50], 1):
            keyword = card.find('span', class_='txt').get_text(strip=True) if card.find('span', class_='txt') else ''
            hot_value = card.find('span', class_='hot').get_text(strip=True) if card.find('span', class_='hot') else '0'
            if keyword:
                hot_list.append({
                    '排名': idx,
                    '热搜关键词': keyword,
                    '热度值': hot_value,
                    '分类': '生活',
                    '采集时间': time.strftime('%Y-%m-%d %H:%M:%S')
                })
        # 保存构造的JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({'data': hot_list}, f, ensure_ascii=False, indent=2)
        print(f"✅ 已通过HTML解析构造JSON并保存到：{json_filename}")


import requests
import json
import os
import time
import warnings

def get_entertainment_json(json_filename):
    # 抑制SSL警告
    warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # 会话对象（模拟真实用户，提高爬取成功率）
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Referer': 'https://www.weibo.com/',
        'Accept': 'application/json, text/plain, */*',
        'X-XSRF-TOKEN': 'i7XvUVQ20-NDHnsh0ijQZKPB'
    })

    # 最新Cookie（必须替换为你浏览器的有效Cookie！）
    cookies = {
        "XSRF-TOKEN": "TWrs0v9VQUWlSxV_iyFBtxMa",
        "SCF": "AoT3RMJQvYRdO_ToyeJLF6X4B4RgFWpZhj9SXLWqkE1vdhBCjgCLATqI0UWuYMYcz_CN7SHqchlq36byDgKJaXs.",
        "SUB": "_2A25EK_4uDeRhGeBM6FIU8yjKyTiIHXVnSX_mrDV8PUNbmtANLWPwkW9NRO_I41Y3tA75vVMmRaHQ6hbzRn-5zJ6j",
        "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9WhozdfB52I1REFNs1qsqdJT5JpX5KzhUgL.FoqEe05fe0qceoB2dJLoI7LKB-fkPX9FMJYt",
        "ALF": "02_1767316350",
        "WBPSESS": "bjCFc0vP5qpUsuOEw4oLCoSGss0KRZoZcSdnPH6fdOAE23H6lD7r0QK_ljLtvI-VplpJtqG36yWgFWcGV2Z-XphfrtqzlYgasGZzDmaLARm7OTMDlRcYp2GfHc1DU5ygvIwMBvmR6xHad-bX0_K-zQ=="
    }
    session.cookies.update(cookies)

    try:
        print("🔍 模拟访问微博首页...")
        session.get('https://www.weibo.com/', timeout=10, verify=False)
        time.sleep(2)  # 随机等待

        url = 'https://weibo.com/ajax/statuses/entertainment'
        response = session.get(url, timeout=15, verify=False)
        response.raise_for_status()
    
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)
    
        print(f"✅ JSON数据已保存到：{json_filename}")
        print("📌 后续可直接读取本地JSON，无需再次请求服务器")

    except Exception as e:
        print(f"❌ 爬取JSON失败：{str(e)}")
        # 若JSON接口失败，降级为HTML爬取后保存JSON
        print("🔄 尝试HTML爬取后转换为JSON...")
        url = 'https://www.weibo.com/hot/life'
        response = session.get(url, timeout=15, verify=False)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        hot_list = []
        # 解析HTML并构造JSON数据
        for idx, card in enumerate(soup.find_all('div', class_='card-wrap')[:50], 1):
            keyword = card.find('span', class_='txt').get_text(strip=True) if card.find('span', class_='txt') else ''
            hot_value = card.find('span', class_='hot').get_text(strip=True) if card.find('span', class_='hot') else '0'
            if keyword:
                hot_list.append({
                    '排名': idx,
                    '热搜关键词': keyword,
                    '热度值': hot_value,
                    '分类': '生活',
                    '采集时间': time.strftime('%Y-%m-%d %H:%M:%S')
                })
        # 保存构造的JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
             json.dump({'data': hot_list}, f, ensure_ascii=False, indent=2)
        print(f"✅ 已通过HTML解析构造JSON并保存到：{json_filename}")

import csv
import json
import os

def process_lifeAndSocial_json_to_csv(json_path, csv_path):
    try:
        # 1. 读取本地JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. 提取目标数据（适配你的JSON结构：data → band_list）
        hot_search_list = data.get("data", {}).get("band_list", [])
        if not hot_search_list:
            print("❌ JSON中未找到有效数据，请检查结构是否匹配")
            return
        
        # 3. 定义CSV字段
        fieldnames = ["热搜排名", "热搜分类", "热搜内容", "热搜热度"]
        
        # 4. 写入CSV文件
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # 写入表头
            
            # 按出现顺序生成排名，遍历提取数据
            for rank, item in enumerate(hot_search_list, start=1):
                writer.writerow({
                    "热搜排名": rank,
                    "热搜分类": item.get("m_category", "未知分类"),
                    "热搜内容": item.get("word", "无内容"),
                    "热搜热度": item.get("num", 0)
                })
        
        print(f"✅ 处理完成！共提取 {len(hot_search_list)} 条数据")
        print(f"📂 CSV文件已保存至：{os.path.abspath(csv_path)}")

    except FileNotFoundError:
        print(f"❌ 找不到JSON文件：{json_path}")
    except json.JSONDecodeError:
        print(f"❌ JSON文件解析失败（文件可能损坏或格式错误）")
    except Exception as e:
        print(f"❌ 处理过程出错：{str(e)}")



def process_entertainment_json_to_csv(json_path, csv_path):
    try:
        # 1. 读取本地JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. 提取目标数据（适配你的JSON结构：data → band_list）
        hot_search_list = data.get("data", {}).get("band_list", [])
        if not hot_search_list:
            print("❌ JSON中未找到有效数据，请检查结构是否匹配")
            return
        
        # 3. 定义CSV字段
        fieldnames = ["热搜排名", "热搜分类", "热搜内容", "热搜热度","相关艺人"]
        
        # 4. 写入CSV文件
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # 写入表头
            
            # 按出现顺序生成排名，遍历提取数据
            for rank, item in enumerate(hot_search_list, start=1):
                writer.writerow({
                    "热搜排名": item.get("realpos","0"),
                    "热搜分类": item.get("category", "未知分类"),
                    "热搜内容": item.get("word", "无内容"),
                    "热搜热度": item.get("num", 0),
                    "相关艺人": item.get("star_name","未知艺人")
                })
        
        print(f"✅ 处理完成！共提取 {len(hot_search_list)} 条数据")
        print(f"📂 CSV文件已保存至：{os.path.abspath(csv_path)}")

    except FileNotFoundError:
        print(f"❌ 找不到JSON文件：{json_path}")
    except json.JSONDecodeError:
        print(f"❌ JSON文件解析失败（文件可能损坏或格式错误）")
    except Exception as e:
        print(f"❌ 处理过程出错：{str(e)}")





import json
import csv
import os

def process_entertainment_json_to_csv(json_path, csv_path):
    try:
        # 1. 读取本地JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 2. 提取目标数据（适配你的JSON结构：data → band_list）
        hot_search_list = data.get("data", {}).get("band_list", [])
        if not hot_search_list:
            print("❌ JSON中未找到有效数据，请检查结构是否匹配")
            return
        
        # 3. 定义CSV字段
        fieldnames = ["热搜排名", "热搜分类", "热搜内容", "热搜热度","相关艺人"]
        
        # 4. 写入CSV文件
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # 写入表头
            
            # 按出现顺序生成排名，遍历提取数据
            for rank, item in enumerate(hot_search_list, start=1):
                writer.writerow({
                    "热搜排名": item.get("realpos","0"),
                    "热搜分类": item.get("category", "未知分类"),
                    "热搜内容": item.get("word", "无内容"),
                    "热搜热度": item.get("num", 0),
                    "相关艺人": item.get("star_name","未知艺人")
                })
        
        print(f"✅ 处理完成！共提取 {len(hot_search_list)} 条数据")
        print(f"📂 CSV文件已保存至：{os.path.abspath(csv_path)}")

    except FileNotFoundError:
        print(f"❌ 找不到JSON文件：{json_path}")
    except json.JSONDecodeError:
        print(f"❌ JSON文件解析失败（文件可能损坏或格式错误）")
    except Exception as e:
        print(f"❌ 处理过程出错：{str(e)}")

    
