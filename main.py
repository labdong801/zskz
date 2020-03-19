# -*- coding=utf-8 -*-

"""
验证码在2分钟内有效
不要太早刷
"""

import sys
import requests
import json
import time
import random
import hashlib
from skimage import io,data

import matplotlib.pyplot as plt

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


# 手机信息
info = """
    [
        {
            "phone":"xxxxxxxxxx",
            "captcha":"xxxxxx",
            "enable":0
        },
        {
            "phone":"xxxxxxxxxx",
            "captcha":"xxxxxx",
            "enable":0
        }
    ]
"""





#################### 下面参数不需要填写 ############################

# 验证码随机数
nonce = ""

# 验证码值
imgCode = ""

def uuid():
    s = "0123456789uvwxyzabc"
    u = []
    for i in range(36):
        index = random.randint(0, len(s) -1 )
        u.append(s[index])
    u[14] = '4'
    #t[19] = e.substr(3 & t[19] | 8, 1),
    ii = 3 & ord(u[19]) | 8
    u[19] = s[ii]
    u[8] = u[13] = u[18] = u[23] = "-"

    return ''.join(u)


def handle_pub_key(key):
    """
    处理公钥
    公钥格式pem，处理成以-----BEGIN PUBLIC KEY-----开头，-----END PUBLIC KEY-----结尾的格式
    :param key:pem格式的公钥，无-----BEGIN PUBLIC KEY-----开头，-----END PUBLIC KEY-----结尾
    :return:
    """
    start = '-----BEGIN PUBLIC KEY-----\n'
    end = '-----END PUBLIC KEY-----'
    result = ''
    # 分割key，每64位长度换一行
    divide = int(len(key) / 64)
    divide = divide if (divide > 0) else divide+1
    line = divide if (len(key) % 64 == 0) else divide+1
    for i in range(line):
        result += key[i*64:(i+1)*64] + '\n'
    result = start + result + end
    return result


def rsaEncrypt(content):
    pub_key = handle_pub_key("MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkEx3/B1MAXNlqPUVQ/rWjZO5ltGRuQb5NpJXVW/Vhr7NcCQy7/pBg1ygPYlip0RlhfUdX1HAr0Na1Uqc+b/9o0C6gTMQ1Q17tr3VKKPev8VkmqBFtERIf8I4+wI1OnIFDyZ6yl/gYL81ohoaIlGqVOIMbpzJtSPlYyP2hnG5r4vBX81wCRy6CW6YHY725d5zy815E51ofCeoviCnkYsVE6+qwfwTiPN4IGAjUmbWM7DcvKFkvlGu2rJOxYYWNvpbsLX/DW7HtQ38cs2zrWC4QFiIjN+a1nBdX0UDkmQJJU3wM+z602uopLSI7Ml2PiwSkrMvCmmyT4/Qtc+ilPOTzwIDAQAB")
    pub = RSA.importKey(pub_key)
    cipher = PKCS1_v1_5.new(pub)
    encrypt_bytes = cipher.encrypt(content.encode(encoding='utf-8'))
    result = base64.b64encode(encrypt_bytes)
    result = str(result, encoding='utf-8')
    return result


# 获取验证码，需要手工输入
def getCaptche():
    timestamp = str(int(round(time.time() * 1000)))
    global nonce 
    nonce = timestamp + uuid()
    captche_url = 'http://kz.yq.zszwfw.cn/kzyy-book-service/paramSet/makeLoginCode/' + nonce + '/0'
    filename='1.jfif'

    response = requests.get(captche_url, stream=True)
    status = response.status_code
    if status == 200:
        with open(filename,"wb")as f:
            f.write(response.content)
        
        img=io.imread(filename)
        io.imshow(img)
        plt.show()
        return input("input:")
    else:
        print(response)
        time.sleep(10)
        return getCaptche()
        


def login(session, data): 
    url = 'http://kz.yq.zszwfw.cn/kzyy-book-service/paramSet/validatePhoneCaptcha'
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }

    resp = session.post(url=url, data=json.dumps(data), allow_redirects=True)

    # 不太明白为什么会307
    if resp.status_code == 307 :
        print("[" + data["phone"] + "]" + resp)
        login(session, data)
        time.sleep(100)
    
    print("[" + data["phone"] + "]" + resp.text)

def doGet(session, data):
    timestamp = str(int(round(time.time() * 1000)))
    nonceStr = timestamp + uuid()
    #page = 'getNewOrder'
    page = 'orderData'
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; U; Android 4.1.2; zh-cn; GT-I9300 Build/JZO54K) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30 MicroMessenger/5.2.380",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "nonceStr": nonceStr,
        "kz-timestamp": timestamp,
        "signature": "FAE6917A82548F743E9B8C89A86252CA",
        "url": "kzyy-book-service/paramSet/" + page,
        "Referer": "http://kz.yq.zszwfw.cn/kzyy-register/",
        "Origin": "http://kz.yq.zszwfw.cn",
    }
    # payload = {"data":"WbuU1vv7tn8qr7NEgW8BS1FalUbbG8PY7dYLngU8Va/rYCHGzJKKa/GMReds9I5ncab10kpEYZnFWRsEnjLCYtc1vJXQ/k1bAkLgdg+v/l1EQLXDiMvHd914qf8zUGRp6rvHRsZjEOCjgDcHE5U7PgNfQAiCLDUiBkYH990iYFQkxsAtunOwxJqIEwH143Zo462n+0zYTOj/nv1JFDoOkXQA+BhHR8Xv6LQjQXGI0d30EMAJB9BB//ELRoRY4eGy1DdLkVD+Stv8L/Bm0wM47NIannSj97m71X+JuO/ft1zV4di5zR+7vLED7UnGMwDqWVmEl/aIqyeHVVYhUw5LLA=="}
    # payload = {"data":"K5MG9oPByHyMojBOksUTR/Sl6qEqfvWAQpn1bsYIKwUOGISHtmWm/dnkFQKBJAFFsjq5Mt/0JKgCta1xUL4ZKMrbnrOvn1uHh73KuH+PapY+LrCvF+Odcj1JuNrRziUvSQSAr2gTcXbZztbDENgbH+/3zC7LE0S4CdhqtnJ5dOTAwmGpvAszgy/4ZRFXBBWaOjRbWM63IXTSnf2XKmNFvGdLlo9R2TC/06Ou29+qumSfX0OP4bHeXpp4V3SUyXJcOEmXJ2hJjpL5EknFmUBAfYkMkv7bLGb1uJ/G2k3uvWeeAxDJktbpVmZBa0aVLRyy9NhL0TZpR0ACIcMvUObbdg=="}

    payload = {"data": rsaEncrypt(json.dumps(data))}

    template = 'dataMap=' + json.dumps(payload) + '&kz-timestamp=' + timestamp + '&nonceStr=' + nonceStr + '&url=kzyy-book-service/paramSet/'+ page + '&key=5a2ea0b36e9f4d39ac0b39300d35ad19'
    signature = hashlib.md5(template.encode(encoding='UTF-8')).hexdigest().upper()
    headers["signature"] = signature

    session.headers = headers

    url = 'http://kz.yq.zszwfw.cn/kzyy-book-service/paramSet/' + page
    resp = session.post(url=url, data=json.dumps(payload), allow_redirects=True)

    print("[" + data["phone"] + "]" + resp.text)

    return json.loads(resp.text)


def getMask(phone, captcha) :
    
    session = requests.session()

    # 数据准备
    data = {
        "phone":phone,
        "captcha":captcha,
        "imgCode":imgCode,
        "nonce":nonce
    }

    # 登录
    login(session, data)

    # 当前日期
    day = time.strftime("%Y-%m-%d", time.localtime())

    # 开始抢口罩
    running = True
    while (running):
        try:
            ret = doGet(session, data)
            if(ret["errMsg"].startswith(u"你最近预约成功日期为")) :
                running = False

            if(ret["time"] is None):
                running = True
                time.sleep(1)
            # 最后10秒全速
            elif ret["time"].startswith(day + " 08:59:5") :
                running = True
                # timesleep = random.randint(1, 3) / 40
                # time.sleep(timesleep)
            # 9点后停止
            elif ret["time"].startswith(day + " 09:00:") :
                running = False
            # 1秒请求1次
            else :
                time.sleep(5)
        except Exception as e:
            print(traceback.format_exc())
            time.sleep(1)

def main():
    # 获取验证码
    global imgCode 
    imgCode = getCaptche()


    # 线程池
    executor = ThreadPoolExecutor(max_workers=20)
    task_list = []
    for i in json.loads(info) :
        if i["enable"] == 1 :
            task_list.append(executor.submit(getMask, i["phone"], i["captcha"]))
    wait(task_list, return_when=ALL_COMPLETED)

    
    


    
if __name__ == '__main__':
    main()