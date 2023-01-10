# Request HTML
# pip install requests_html
from requests_html import HTMLSession
url = 'https://www.google.com/search?q=python'
session = HTMLSession()
req = session.get(url, timeout=20)
req.html.render(sleep=1)
print(req.status_code)
print(req.html.html)

