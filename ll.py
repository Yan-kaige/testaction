from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import time
from tqdm import tqdm  # 导入 tqdm
import os

# 获取开始时间
start_time = datetime.now()
print("Start Time:", start_time.strftime('%Y-%m-%d %H:%M:%S'))

# 设置代理（如果需要）
proxy = "localhost:10809"

# 配置 Chrome Options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
# chrome_options.add_argument(f'--proxy-server=http://{proxy}')  # 设置代理
chrome_options.add_argument("--window-size=1920x1080")  # 设置窗口大小（有时会影响一些元素加载）
# chrome_options.add_argument("Cookie=_ga=GA1.1.373046596.1733502673; kt_tcookie=1; kt_ips=116.87.139.230%2C118.100.134.208; PHPSESSID=g7p0bdg9m6baijcgvum6k47bo7; asgfp2=1f999dd606ea1b05b9149595cb91dbbc; cf_clearance=Ul0.ULJc3Fw6JtYeGtKxvQDvNjm3C2Ad9rMDWNaU1IQ-1733553736-1.2.1.1-FKJC1blVrC.BDVlwr0GORJHD1YENxf9lnkXbcw9QiKJPTeV2Edoe_7.syybURmIVMHFNO2BARE2nvDeWO6OOFb8YYGBf_4AG3m6xNLyGluVYWl83iGfTMGWFBaiB9_NEjIedR.fcsKwQHCoENl9YV8B1sy.ClkgzKjX9YpuyOBqZMvVtRMWvZt3F4r5O3ltPLNJdWZuhcZ6Esih2.XFYGmv1ZzqajVYWaraEmCaK0wXeXMbYs9mrwNxyUCDsBuKQlOzZnA2W2f0BBPUjI.CkDtrH9l4hVrHtoLdVqKl8qMDo2Sq7TKMZA.JCHveWywlcEVqjKhj6SNYofhfiSp6qHQ_UsROT3uVqDHkiQZw9ukClsQHGWv4DETuQHIRxaUAPBA8iQoOZ4hwO1zCc_Dk.pg; _ga_1DTX7D4FHE=GS1.1.1733553736.3.1.1733553783.0.0.0; __cf_bm=Wa.dISW4xD9BkPSSz2wuc4j50lqpbMYte8Ct8dT3YCA-1733554786-1.0.1.1-WfEDOR4yvDW5vLvrBZ6IeZNtN3Z1NK_jBZiKkO4cOiu2hoG6KQv5Mz9tFfRz7M7U5ZqUCNCA5o028pns8_unTw")  # 设置窗口大小（有时会影响一些元素加载）
chrome_options.add_argument(
    'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')  # 设置 User-Agent

# 初始化 WebDriver（使用 Chrome 浏览器）
driver = webdriver.Chrome(options=chrome_options)

# 创建一个列表来存储 VideoInfo 对象
video_info_list = []

order = 1


# 循环从 01 到 1200 修改 URL 中的 from 参数
for day in tqdm(range(1, 3), desc="Processing Pages"):
    # 动态生成 URL，确保 'from' 参数始终是两位数
    url = f"https://jable.tv/latest-updates/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from={day:02d}&_=1733499634983"

    # 访问页面
    driver.get(url)

    # 等待页面加载
    time.sleep(0.05)

    # 获取页面源代码
    html_content = driver.page_source

    # 解析页面内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 查找所有 detail 元素
    detail_elements = soup.find_all('div', class_='detail')
    # print(f"第{day}页: {len(detail_elements)}")

    # 遍历每个 detail 元素

    for detail in detail_elements:
        # 提取链接
        link = detail.find('a')['href']
        # 提取链接的文本内容
        link_text = detail.find('a').text

        # 提取数字
        sub_title = detail.find('p', class_='sub-title').text
        aa = sub_title.replace('\n', '-').replace('\t', '-')
        split_text = aa.split('-')
        filtered_data = [item.replace(' ', '') for item in split_text if item != '']

        # 定位到与 detail 一一对应的 img-box
        img_box = detail.find_previous_sibling('div', class_='img-box')
        fav_video_id = None
        if img_box:
            # 提取 data-fav-video-id
            span = img_box.find('span', {'data-fav-video-id': True})
            if span:
                fav_video_id = span['data-fav-video-id']

        if len(filtered_data) != 0:
            first_number = filtered_data[0]  # 第一个数字
            last_number = filtered_data[1]  # 最后一个数字
            # 创建 VideoInfo 对象
            video_info = {
                'link': link,
                'link_text': link_text,
                'fav_video_id': fav_video_id if fav_video_id else "None",
                'number': first_number,
                'favorite': last_number,
                "order": order,
                "update_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            order = order + 1

            video_info_list.append(video_info)

# 过滤出 number > 1 的条目
filtered_videos = [video for video in video_info_list if int(video['number']) > 50000]
filtered_videos = [video for video in filtered_videos if int(video['favorite']) > 2000]

# 打印结果
for video in filtered_videos:
    print(video)



time.sleep(1)

# 关闭浏览器
driver.quit()
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
print(f"Connecting to: {db_host}, DB: {db_name}")
# 连接到数据库
conn = psycopg2.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_name,
    port=5432
)
cur = conn.cursor()

insert_query = """
    INSERT INTO "my_user" (id, name, video, favorite, link,orders,update_time)
    VALUES (%s, %s, %s, %s, %s,%s,%s)
    ON CONFLICT (id)
    DO UPDATE SET
        name = EXCLUDED.name,
        video = EXCLUDED.video,
        favorite = EXCLUDED.favorite,
        link = EXCLUDED.link,
        orders = EXCLUDED.orders,
        update_time = EXCLUDED.update_time
        ;
"""
# 记录插入和更新的行数
inserted_rows = 0
updated_rows = 0
for video in filtered_videos:
    cur.execute(insert_query, (
        int(video.get('fav_video_id')),
        video.get('link_text'),
        int(video.get('number')) ,
        int(video.get('favorite')),
        video.get('link'),
        video.get('order'),
        video.get('update_time'),
    ))

    # 获取受影响的行数
    if cur.rowcount == 1:
        # 如果是插入
        inserted_rows += 1
    elif cur.rowcount == 2:
        # 如果是更新
        updated_rows += 1


# 提交事务
conn.commit()

# 关闭游标和连接
cur.close()
conn.close()

print("Data inserted successfully.")
# 输出插入和更新的行数
print(f"Inserted rows: {inserted_rows}")
print(f"Updated rows: {updated_rows}")

# 获取结束时间
end_time = datetime.now()
print("End Time:", end_time.strftime('%Y-%m-%d %H:%M:%S'))

# 计算并打印运行时间
duration = end_time - start_time
print("Duration:", duration)