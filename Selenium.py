# 导入selenium库  备选webdriver-manager驱动管理库
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# 引入定位工具
from selenium.webdriver.common.by import By
# 引入验证码识别工具
import ddddocr
import time

# =============自定义时长转换函数===============
def duration_to_seconds(duration_str):
    """
    将 'HH:MM:SS' 或 'MM:SS' 格式的字符串转换为总秒数
    例如 '00:53:23' -> 53*60 + 23 = 3203 秒
    """
    parts = duration_str.strip().split(':')
    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
    elif len(parts) == 2:
        hours = 0
        minutes, seconds = map(int, parts)
    else:
        return 0
    return hours * 3600 + minutes * 60 + seconds
# ==================结束=========================

# ===========配置============
URL = r"https://qingdao.training.sdufe.edu.cn/home/index?logtype=new4&ReturnUrl=%2flearning%2fCollection%2f0"
# 1.创建一个浏览器实例 驱动管家自动准备好驱动
# 备选webdriver-manager驱动管理库方法 service = Service(ChromeDriverManager().install())
service = Service(executable_path=r"F:\python\chromedriver.exe")
driver = webdriver.Chrome(service=service)
# 2.打开网址
driver.get(URL)
# ===========结束============


# ==================用户登录============
# 1. 找到用户名输入框
# driver.find_element(By.XPATH, "//INPUT[@ID='LoginName']").clear().send_keys("370")
username_input = driver.find_element(By.ID, "LoginName")
# 2. 清空里面可能有的默认文字
username_input.clear()
# 3. 输入用户名
username_input.send_keys("")
# 4.输入姓名
password_input = driver.find_element(By.ID, "Password")
password_input.clear()
password_input.send_keys("")

#--------------------验证码填写处理-------------------
#1.找到验证码图片截图保存
captcha_img = driver.find_element(By.ID,"codeCap")
captcha_img.screenshot("captcha.png")
# 2.ddddocr识别
# result = OCR.classification(open("captcha_png","rb").read())
# yzm = driver.find_element(By.ID, "yzm").send_keys(result)
# 效率优化 用完即关
ocr = ddddocr.DdddOcr()
with open("captcha.png", "rb") as f:
    img_bytes = f.read()
result = ocr.classification(img_bytes)
# 3.验证码填写
yzm = driver.find_element(By.ID, "yzm")
yzm.clear()
yzm.send_keys(result)
# -----------------------登录---------------------

#4.登录处理
login_button = driver.find_element(By.ID, "loginbtn")
login_button.click()
time.sleep(3)
# =======================结束==========================


# =====================选择对应年份课程===================
# 1.选择年限
year = driver.find_element(By.XPATH,"//a[contains(@href,'2026')]")
year.click()
# 2.等待页面加载
time.sleep(3)
# =======================结束==========================


# ====================课程列表========================
# 1.统计课程 获取所有“进入学习”的链接
# total = len(driver.find_elements(By.XPATH, "//td[@class='td005']/a"))
_all_links = driver.find_elements(By.XPATH, "//td[@class='td005']/a")
# 2.拿到所有链接的href
total = len(_all_links)
print(f"共找到 {total} 章课程")

# 3.循环看课 ------------------第一层盒子--------------------------
for i in range(total):
    #a.每次循环重新获取当前页面的链接列表（避免元素失效）
    current_links = driver.find_elements(By.XPATH, "//td[@class='td005']/a")
    link = current_links[i]
    #b.获取课程名称 显示进度
    course_names = driver.find_elements(By.XPATH, "//td[@class='td002']")
    course_name = course_names[i].text if i < len(course_names) else "未知课程"
    print(f"正在学习第 {i + 1}/{total} 章：{course_name}")
    #c.进入学习
    link.click()
    time.sleep(3)

# 4.进入页面后------------------第二层盒子--------------------------
    #1.获取所有待听课程
    sections = driver.find_elements(By.XPATH, "//a[@class='Html5' and @title='H5听课']")
    total_sections = len(sections)
    #2.循环播放待听课程
    for j in range(total_sections):
        #2.1每次循环重新获取当前页面的链接列表（避免元素失效）
        current_section = driver.find_elements(By.XPATH, "//a[@class='Html5' and @title='H5听课']")[j]
        #2.2获取该行所有 td003 下的 a 标签文本
        td003_links = driver.find_elements(By.XPATH, f"(//tr[@class='td00a'])[{j + 1}]//td[@class='td003']/a")
        print(f"时长比对：{td003_links}")
        #2.3索引0123 获取总时长和已观看时长
        total_duration = td003_links[1].text
        watched_duration = td003_links[2].text
        #2.4总时长和已观看时长条件判断 相等或等于0000则跳过
        if total_duration == watched_duration or (total_duration == "00:00:00" and watched_duration == "00:00:00"):
            print(f"  小节 {j + 1} 已看完或时长为0，跳过")
            continue
        else:
            # 2.4.1记录窗口ID 方便跳转后切换窗口
            original_window = driver.current_window_handle
            current_section.click()
            print(f"  小节 {j + 1} 需要观看，总时长：{total_duration}，已观看：{watched_duration}")
            # 2.4.2切换到视频播放标签页
            for window in driver.window_handles:
                if window != original_window:
                    driver.switch_to.window(window)
                    break
            # 2.4.3调用自定义函数 等待视频播放 + 额外1分钟
            wait_time = duration_to_seconds(total_duration) + 60
            print(f"  等待 {wait_time} 秒...")
            time.sleep(wait_time)
            # 2.4.4关闭新标签页，切回原页面
            driver.close()
            driver.switch_to.window(original_window)
            print(f"  小节 {j + 1} 完成")
        time.sleep(2)
    # --------------------第二层盒子结束-----------------------
    driver.back()
    time.sleep(2)
# ----------------------第一层盒子结束----------------------------
time.sleep(2)
# ======================课程结束================================
driver.quit()
print("所有课程已处理完毕！")