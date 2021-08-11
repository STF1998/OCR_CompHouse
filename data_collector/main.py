import API_Test as api
import data_scrape as scrape
import table_extract as extract
import requests
from requests.auth import HTTPBasicAuth

array = ["10665117"]

accounts = api.get_filing_history(array[0])
index = api.search_for_file(accounts)
link = api.get_link_to_download(index, accounts)

link = link.split('/')
document_id = link[-1]

pdf_file = requests.get(f"https://document-api.company-information.service.gov.uk/document/{document_id}/contents",
auth=HTTPBasicAuth('afc84b20-eab4-496b-b347-844ba6c893ab',''))

with open("my_pdf" + ".pdf", 'wb') as file:
    file.write(pdf_file.read())



