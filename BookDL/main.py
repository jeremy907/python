import os.path
import requests
import re
import parsel

list_url = 'https://www.kanunu8.com/files/dushi/200909/840.html'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}
html_bytes = requests.get(url=list_url, headers=headers).content
html_data = html_bytes.decode('ansi')
bookname = re.findall('<Td height="60" valign="middle" align="center"><h2><b>(.*?)</b></h2></Td>',html_data)[0]
print(bookname)
dir = f'{bookname}\\'
if not os.path.exists(dir):
    os.mkdir(dir)
    url_list = re.findall('<td><a href="(.*?)">',html_data)
    for url in url_list:
        index_url = 'https://www.kanunu8.com/' + url

        #url = 'https://www.kanunu8.com/files/dushi/200909/840/5616.html'
        response_bytes = requests.get(url=index_url, headers=headers).content
        response_text = response_bytes.decode('ansi')
        # print(response)
        # print(response.text)
        # title = re.findall('<div id="title">(.*?)</div>', response.text)[0]
        # print(title)
        # content = re.findall('<div id=\'content\' class="connie">(.*?)</div>', response.text, re.S)[0].replace('<br>', '\n')
        # print(content)
        #with open('output.txt', 'w', encoding='utf-8') as f:f.write(response.text)

        selector = parsel.Selector(response_text)
        # title = selector.css('#title::text').get()
        title = selector.xpath('//*[@id="title"]/text()').get()
        #content = '\n'.join(selector.css('#content::text').getall())
        content = ''.join(selector.xpath('//*[@id="content"]/text()').getall())
        content = re.sub(r"\s*\n", "\n", content)
        print(title)
        print(content)
        with open(dir + bookname + '.txt', mode='a', encoding='utf-8') as f:
            f.write(title)
            f.write('\n')
            f.write(content)
            f.write('\n')
