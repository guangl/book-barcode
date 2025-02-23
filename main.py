import os
from time import sleep

import requests
from bs4 import BeautifulSoup
from pony.orm import *

# APP_KEY = '10e65f37bb9c46ca8ab44cd6c7ccfafa'

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
database_path = os.path.join(project_root, 'book.db')

db = Database()
db.bind(provider='sqlite', filename=database_path, create_db=True)


class BookDetails(db.Entity):
    """书籍详细信息"""

    _table_ = 'books'
    isbn = PrimaryKey(str)  # ISBN
    name = Required(str)  # 书名
    subtitle = Optional(str)  # 副标题
    original_title = Optional(str)  # 原作名
    author = Optional(StrArray)  # 作者
    publisher = Optional(str)  # 出版社
    seller = Optional(str)  # 出品方
    translator = Optional(StrArray)  # 译者
    publish_date = Optional(str)  # 出版日期
    page_number = Optional(str)  # 页数
    price = Optional(str)  # 定价
    binding = Optional(str)  # 装帧
    series = Optional(str)  # 丛书
    score = Optional(str)  # 评分
    cover = Optional(str)  # 封面


@db_session
def get_douban_book(isbn: str) -> BookDetails | None:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Connection': 'keep-alive',
    }
    cookies = {
        'bid': 'NHXxGvBzxX0',
        'll': '118254',
        'viewed': '1220562_30297919_36579958',
        'dbcl2': '203360694:Ug2gMdLxfP0',
        'ck': 'qVMJ; ',
    }

    url = f'https://book.douban.com/isbn/{isbn}'
    response = requests.get(url=url, headers=headers, cookies=cookies)
    if response.status_code != 200:
        print('请求失败')
        return None

    book_detail = {
        'isbn': isbn,
        'name': '',
        'subtitle': '',
        'original_title': '',
        'author': [],
        'publisher': '',
        'seller': '',
        'translator': [],
        'publish_date': '',
        'page_number': '',
        'price': '',
        'binding': '',
        'series': '',
        'score': '',
        'cover': ''
    }

    book_soup = BeautifulSoup(response.text, 'html.parser')

    book_wrapper = book_soup.find('div', id='wrapper')
    book_detail['name'] = book_wrapper.find('h1').text.strip()
    book_detail['cover'] = book_wrapper.find('div', id='mainpic').find('img')['src']
    book_detail['score'] =book_wrapper.find('strong', class_='ll rating_num').text.strip()

    book_info = book_wrapper.find('div', id='info')
    formatted_book = book_info.text.replace("\n", "").replace(" ", "")
    formatted_book = (formatted_book
                      .replace('副标题:', '\n副标题:')
                      .replace('原作名:', '\n原作名:')
                      .replace("作者:", "\n作者:")
                      .replace("出版社:", "\n出版社:")
                      .replace("出品方:", "\n出品方:")
                      .replace("译者:", "\n译者:")
                      .replace("出版年:", "\n出版年:")
                      .replace("页数:", "\n页数:")
                      .replace("定价:", "\n定价:")
                      .replace("装帧:", "\n装帧:")
                      .replace("丛书:", "\n丛书:")
                      .replace("ISBN:", "\nISBN:"))
    books = formatted_book.split('\n')

    for book in books:
        if book.startswith('副标题'):
            book_detail['subtitle'] = book.replace('副标题:', '').strip()
        elif book.startswith('原作名'):
            book_detail['original_title'] = book.replace('原作名:', '').strip()
        elif book.startswith('作者'):
            book_detail['author'] = book.replace('作者:', '').strip().split('/')
        elif book.startswith('出版社'):
            book_detail['publisher'] = book.replace('出版社:', '').strip()
        elif book.startswith('出品方'):
            book_detail['seller'] = book.replace('出品方:', '').strip()
        elif book.startswith('译者'):
            book_detail['translator'] = book.replace('译者:', '').strip().split('/')
        elif book.startswith('出版年'):
            book_detail['publish_date'] = book.replace('出版年:', '').strip()
        elif book.startswith('页数'):
            book_detail['page_number'] = book.replace('页数:', '').strip()
        elif book.startswith('定价'):
            book_detail['price'] = book.replace('定价:', '').strip()
        elif book.startswith('装帧'):
            book_detail['binding'] = book.replace('装帧:', '').strip()
        elif book.startswith('丛书'):
            book_detail['series'] = book.replace('丛书:', '').strip()

    return BookDetails(**book_detail)


@db_session
def main():
    db.generate_mapping()
    set_sql_debug(True)

    # book = BookDetails.get(isbn='9787101158120')
    # print(len(book.translator))

    while True:
        isbn = input("input ISBN(y/Y) to close: ")  # 9787302153894

        if isbn == 'y' or isbn == 'Y':
            break

        if len(isbn) == 10 or len(isbn) == 13:
            get_douban_book(isbn)
            sleep(10)


if __name__ == '__main__':
    main()
