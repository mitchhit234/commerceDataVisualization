import datetime
import eml_parser
from bs4 import BeautifulSoup

#datetime = ['header']['date']




with open('email.eml', 'r') as f:
  raw = f.read()


ep = eml_parser.EmlParser()
parsed_eml = ep.decode_email('email.eml')
a = ep.get_raw_body_text(ep.msg)

a = a[0]
html = a[1]

soup = BeautifulSoup(html, 'html.parser')
results = soup.find_all('font')

for i in results:
  print(i.text)

