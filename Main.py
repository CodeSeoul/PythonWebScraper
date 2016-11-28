import urllib.request as request
import urllib.error as urlerror

import html.parser as parser

import sys


#try:
    #response = request.urlopen('https://d3go.com/forums/viewtopic.php?f=31&t=55103')
    # server likely expects more headers

request_obj = request.Request(
    'https://d3go.com/forums/viewtopic.php?f=31&t=55103',
    headers={
        'User-Agent': 'Learn to Code Seoul'
    })

try:
    response = request.urlopen(request_obj)
except urlerror.HTTPError as err:
    print('Request failed with HTTPError:', err.code, "-", err.reason)
    sys.exit(-1)
except urlerror.URLError as err:
    print('Request failed with URLError:', err.reason)

if response.getcode() != 200:
    print("HTTPS request failed:". response.reason)
    sys.exit(-1)

body = str(response.read())


class Post:
    def __init__(self):
        self.author = ""
        self.content = ""

    def __str__(self):
        return self.author + " authored: " + self.content


class CustomParser(parser.HTMLParser):

    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)

        # Here are a bunch of properties to help us keep track
        # of where we are in the page
        self.is_in_post = False
        self.post_depth = 0

        self.is_in_author = False
        self.is_in_author_strong = False
        self.is_in_author_link = False

        self.is_in_content = False
        self.content_depth = 0

        self.is_in_blockquote = False
        self.blockquote_depth = 0

        self.current_content = ""

        self.post_list = []

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if tag == 'div' and not self.is_in_blockquote:
            if self.is_in_post:
                self.post_depth += 1
                for attr in attrs:
                    if attr[0] == 'class':
                        if 'content' in attr[1]:
                            self.is_in_content = True
                            self.content_depth = 0
            else:
                for attr in attrs:
                    if attr[0] == 'class':
                        if 'postbody' in attr[1]:
                            self.is_in_post = True
                            self.post_depth = 0
                            self.post_list.append(Post())
            if self.is_in_content:
                self.content_depth += 1
        if tag == 'p':
            for attr in attrs:
                if attr[0] == 'class' and 'author' in attr[1]:
                    self.is_in_author = True
        if tag == 'strong' and self.is_in_author:
            self.is_in_author_strong = True
        if tag == 'a' and self.is_in_author_strong:
            self.is_in_author_link = True
        if tag == 'blockquote':
            if self.is_in_blockquote:
                self.blockquote_depth += 1
            else:
                self.is_in_blockquote = True
                self.blockquote_depth = 0

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if tag == 'div' and not self.is_in_blockquote:
            if self.is_in_content:
                self.content_depth -= 1
                if self.content_depth == 0:
                    self.is_in_content = False
                    self.post_list[-1].content = self.current_content
                    self.current_content = ""
            if self.is_in_post:
                self.post_depth -= 1
                if self.post_depth == 0:
                    self.is_in_post = False

        if tag == 'a' and self.is_in_author_link:
            self.is_in_author_link = False
        if tag == 'strong' and self.is_in_author_strong:
            self.is_in_author_strong = False
        if tag == 'p' and self.is_in_author:
            self.is_in_author = False
        if tag == 'blockquote':
            self.blockquote_depth -= 1
            if self.blockquote_depth < 0:
                self.is_in_blockquote = False

    def handle_data(self, data):
        super().handle_data(data)
        if self.is_in_author_link:
            self.post_list[-1].author = data
        if self.is_in_content and not self.is_in_blockquote:
            self.current_content += " " + data


parser_obj = CustomParser()
parser_obj.feed(body)

for post in parser_obj.post_list:
    print('post:', post)


