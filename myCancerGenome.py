import requests
from bs4 import BeautifulSoup
import pickle
import os
import time
import random
from pymongo import MongoClient


def get_data(hits):
    path = os.getcwd() + '\\data'
    if hits % 10:
        all = hits // 10 + 1
    else:
        all = hits // 10
    if os.path.exists(path):
        with open('data', 'rb') as f:
            data = pickle.load(f)
            long = len(data)
            if long == hits:
                return
            long = long // 10 + 1
            all_data = data
    else:
        all_data = []
        long = 1
    session = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                             '7.0.4280.67 Safari/537.36 Edg/87.0.664.47',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,applica'
                         'tion/signed-exchange;v=b3;q=0.9',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
               'cache-control': 'no-cache',
               'dnt': '1',
               'pragma': 'no-cache',
               'sec-fetch-dest': 'document',
               'sec-fetch-mode': 'navigate',
               'sec-fetch-site': 'none',
               'sec-fetch-user': '?1',
               'upgrade-insecure-requests': '1'}
    try:
        session.get('https://www.mycancergenome.org/content/biomarkers/', headers=headers, timeout=10)
    except:
        raise TimeoutError('获取会话超时')
    url = 'https://www.mycancergenome.org/mcg/omni_mcg/biomarkers/?fields=alteration_groups&fields=name&fields=biomarke' \
          'r_type&fields=genes&fields=in_diseases&fields=pathways&fields=summary&fields=trial_count&fields=therapy_coun' \
          't&fields=drug_count&page={}&search='
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                             '7.0.4280.67 Safari/537.36 Edg/87.0.664.47',
               'authorization': 'Token 989c38a36eec154f01167274dbce2334ccf8ef11',
               'accept': 'application/json, text/plain, */*',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
               'cache-control': 'no-cache',
               'dnt': '1',
               'pragma': 'no-cache',
               'sec-fetch-dest': 'empty',
               'sec-fetch-mode': 'cors',
               'sec-fetch-site': 'same-origin',
               'referer': 'https://www.mycancergenome.org/content/biomarkers/'}
    # z = 0
    for page in range(long, all):
        try:
            response = session.get(url.format(page), headers=headers, timeout=10)
            # z += 1
        except:
            raise TimeoutError('获取列表超时')
        time.sleep(random.randrange(1, 4, 1) + random.random())
        if response.status_code == 200:
            cache = response.json()
            for i in range(len(cache['results'])):
                data = []
                data.append(cache['results'][i]['name'])
                try:
                    data.append(cache['results'][i]['drug_count'])
                except:
                    pass
                all_data.append(data)
        else:
            print('发生异常，响应码：', response.status_code)
            break
        """
        启用此代码则每次运行只获取10条数据
        注释此代码则运行获取全部数据
        """
        # break  # 调试使用
        """
        启用此代码则每次运行获取1000条数据
        注释此代码则运行获取全部数据
        """
        # if z >= 100:
        #     print(len(all_data))
        #     break
    with open('data', 'wb') as f:
        pickle.dump(all_data, f)


def get_info():
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q'
                         '=0.8,application/signed-exchange;v=b3;q=0.9',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.9',
               'cache-control': 'no-cache',
               'dnt': '1',
               'pragma': 'no-cache',
               'referer': 'https://www.mycancergenome.org/content/biomarkers/',
               'sec-fetch-dest': 'document',
               'sec-fetch-mode': 'navigate',
               'sec-fetch-site': 'same-origin',
               'sec-fetch-user': '?1',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                             '7.0.4280.66 Safari/537.36'}
    path = os.getcwd() + '\\progress'
    if os.path.exists(path):
        with open('progress', 'rb') as f:
            progress = pickle.load(f)
    else:
        progress = 0
    with open('data', 'rb') as f:
        data = pickle.load(f)
    client = MongoClient()
    db = client['癌症基因组数据库']
    collection = db['详细数据']
    z = 0
    for i in data[progress:]:
        if len(i) == 1:
            info = {'Name': '', 'Drugs': None, 'Info': None}
            info['Name'] = i[0]
            save_data(info, collection)
            progress += 1
        elif len(i) == 2 and i[1] == 0:
            info = {'Name': '', 'Drugs': '', 'Info': None}
            info['Name'] = i[0]
            info['Drugs'] = i[1]
            save_data(info, collection)
            progress += 1
        elif len(i) == 2:
            try:
                z += 1
                cache = open_url_T_1(headers, i[0])
                if cache:
                    info = {'Name': '', 'Drugs': '', 'Info': ''}
                    info['Name'] = i[0]
                    info['Drugs'] = i[1]
                    info['Info'] = cache
                    save_data(info, collection)
                    time.sleep(random.randrange(1, 4, 1) + random.random())
                else:
                    break
            except:
                time.sleep(random.randrange(1, 4, 1) + random.random())
                z += 1
                cache = open_url_T_2(headers, i[0])
                if cache:
                    info = {'Name': '', 'Drugs': '', 'Info': ''}
                    info['Name'] = i[0]
                    info['Drugs'] = i[1]
                    info['Info'] = cache
                    save_data(info, collection)
                else:
                    break
            progress += 1

        else:
            raise ValueError(i)
        # break  # 调试使用
        """
        启用此代码则每次运行发送50次请求后关闭程序
        注释此代码则运行获取全部数据
        """
        if z >= 50:
            break
    with open('progress', 'wb') as f:
        pickle.dump(progress, f)
        # print(progress)  # 调试使用


def open_url_F(name):
    """
    暂时不需要调用
    """
    headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q='
                         '0.8,application/signed-exchange;v=b3;q=0.9',
               'accept-encoding': 'gzip, deflate, br',
               'accept-language': 'zh-CN,zh;q=0.9',
               'cache-control': 'no-cache',
               'dnt': '1',
               'pragma': 'no-cache',
               'referer': 'https://www.mycancergenome.org/content/biomarkers/',
               'sec-fetch-dest': 'document',
               'sec-fetch-mode': 'navigate',
               'sec-fetch-site': 'same-origin',
               'sec-fetch-user': '?1',
               'upgrade-insecure-requests': '1',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/8'
                             '7.0.4280.66 Safari/537.36'}
    url = 'https://www.mycancergenome.org/content/alteration/{}/'
    response = requests.get(url.format(name), headers=headers)
    html = response.content.decode(response.encoding)
    soup = BeautifulSoup(html, 'lxml')
    num = soup.select('body > div.main-content > div.alteration-detail > div.row.header > div.small-12.medium-9.column'
                      's > div:nth-child(1) > div > p > a')[0].text
    print(soup.select('body > div.main-content > div.alteration-detail > div.row.header > div.small-12.medium-9.column'
                      's > div:nth-child(2) > div > p:nth-child({})'.format(int(num) + 1))[0].text.strip())


def open_url_T_1(headers, name, url='https://www.mycancergenome.org/content/alteration/{}/'):
    try:
        response = requests.get(
            url.format(
                name.replace(')', '').replace('(', '-').replace(';', '-').replace(' ', '-').replace('--', '-').lower()),
            headers=headers, timeout=10)
        # print(response.url)  # 调试代码
        # print(response.status_code)
    except:
        return None
    if response.status_code == 200:
        data = []
        data.append(name)
        data.append(response.url)
        html = response.content.decode(response.encoding)
        soup = BeautifulSoup(html, 'lxml')
        info = soup.select('div#therapies-toggle > p')
        content = ''
        for i in info:
            content += i.text
        data.append(content.replace('\n', '').replace('  ', '').strip())
        num = soup.select('div#therapies-toggle > p:last-of-type > a')[0].text
        reference = soup.select('div.small-12.columns > p.reference')[int(num) - 1].text
        data.append(reference.replace('\n', '').replace('  ', '').strip())
        BDT = soup.select('div#therapies-toggle > div.about-alteration-therapy-row')
        data.append({})
        for a in BDT:
            title = a.select('p.about-alteration-therapy-header')[0].text.replace('+', '').strip()
            if title == 'Bosutinib' or title == 'Imatinib':
                data[4][title] = []
                Bosutinib = a.select('div.about-alteration-therapy-content > div.about-alteration-therapy-disease-row')
                for b, c in enumerate(Bosutinib):
                    data[4][title].append([])
                    t1 = c.select('p.about-alteration-therapy-disease-header')[0].text.replace('-', '')
                    data[4][title][b].append(t1.replace('\n', '').replace('  ', '').strip())
                    t2 = c.select('div.row.table-row.targeted-therapy-table-small-screen-container')
                    for f in t2:
                        data[4][title][b].append([])
                        t3 = f.select('div.small-12.columns.biomarker-criteria')
                        data[4][title][b][-1].append(t3[0].text.replace('\n', '').replace('  ', '').strip())
                        row = f.select('div.small-12.columns.response-setting-note > div.row')
                        data[4][title][b][-1].append([])
                        for d, e in enumerate(row):
                            data[4][title][b][-1][-1].append(e.text.replace('\n', '').replace('  ', '').strip())
            else:
                continue
        return data
    elif response.status_code == 404:
        raise ValueError
    else:
        return None


def open_url_T_2(headers, name, url='https://www.mycancergenome.org/content/gene/{}/'):
    try:
        response = requests.get(
            url.format(
                name.replace(')', '').replace('(', '-').replace(';', '-').replace(' ', '-').replace('--', '-').lower()),
            headers=headers, timeout=10)
        # print(response.url)  # 调试代码
        # print(response.status_code)
    except:
        return None
    if response.status_code == 200:
        data = []
        data.append(name)
        data.append(response.url)
        html = response.content.decode(response.encoding)
        soup = BeautifulSoup(html, 'lxml')
        info = soup.select('div#therapies-toggle > p')
        content = ''
        for i in info:
            content += i.text
        data.append(content.replace('\n', '').replace('  ', '').strip())
        num = soup.select('div#therapies-toggle > p:last-of-type > a')[0].text
        reference = soup.select('div.small-12.columns > p.reference')[int(num) - 1].text
        data.append(reference.replace('\n', '').replace('  ', '').strip())
        BDT = soup.select('div#therapies-toggle > div.about-gene-therapy-row')
        data.append({})
        for a in BDT:
            title = a.select('p.about-gene-therapy-header')[0].text.replace('+', '').strip()
            if title == 'Bosutinib' or title == 'Imatinib':
                data[4][title] = []
                Bosutinib = a.select('div.about-gene-therapy-content > div.about-gene-therapy-disease-row')
                for b, c in enumerate(Bosutinib):
                    data[4][title].append([])
                    t1 = c.select('p.about-gene-therapy-disease-header')[0].text.replace('-', '')
                    data[4][title][b].append(t1.replace('\n', '').replace('  ', '').strip())
                    t2 = c.select('div.row.table-row.targeted-therapy-table-small-screen-container')
                    for f in t2:
                        data[4][title][b].append([])
                        t3 = f.select('div.small-12.columns.biomarker-criteria')
                        data[4][title][b][-1].append(t3[0].text.replace('\n', '').replace('  ', '').strip())
                        row = f.select('div.small-12.columns.response-setting-note > div.row')
                        data[4][title][b][-1].append([])
                        for d, e in enumerate(row):
                            data[4][title][b][-1][-1].append(e.text.replace('\n', '').replace('  ', '').strip())
            else:
                continue
        return data
    elif response.status_code == 302:
        raise ValueError(name, response.url)
    else:
        return None


def save_data(data, collection):
    collection.insert_one(data)


def main():
    hits = 16380  # 数据总数，手动修改
    get_data(hits)
    # get_info()
    print('程序已结束')


if __name__ == '__main__':
    main()
