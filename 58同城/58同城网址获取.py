from requests_html import HTMLSession
import json


def get_html():
    session = HTMLSession()
    html = session.get('https://www.58.com/changecity.html?catepath=chuzu')
    html.html.render()
    data_1 = html.html.find('.hot-city')
    data_2 = html.html.find('.content-city')
    url = {item.text: 'https:' + item.attrs['href'] for item in data_1}
    for item in data_2:
        url[item.text] = 'https:' + item.attrs['href']
    return url


def save(data):
    with open('area.txt', 'w+') as file:
        data = json.dumps(data)
        file.write(data)


def main():
    data = get_html()
    save(data)


if __name__ == '__main__':
    main()
