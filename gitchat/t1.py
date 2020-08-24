import pdfkit
import gitchat.settings as settings

confg = pdfkit.configuration(wkhtmltopdf='D:/dev/wkhtmltox/bin/wkhtmltopdf.exe')

url = 'https://gitbook.cn/books/5f3a7fefd8cfc5171638e2f4/index.html'  # 一篇博客的url

options = {'cookie': []}

for item in settings.COOKIE.items():
    options['cookie'].append(item)

print(options)
pdfkit.from_url(url, './data/1.pdf', configuration=confg, options=options)
