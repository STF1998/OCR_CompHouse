import requests
from requests.auth import HTTPBasicAuth
import csv


def get_next_firm():
    
    with open("/Users/samfitton/Documents/MyGitProjects/ML_MastersThesis/data_collector/UK_registered_companies/UK_companies_list.csv", "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        return next(csv_reader)

def search_for_file(company_Accounts):

    i = 0 
    for item in company_Accounts:
        i = i + 1
        if '"description"' in item:
            if 'accounts-with-accounts' in item:
                return i
    
    return -1

def get_link_to_download(index, company_Accounts):

    for i in range(index, len(company_Accounts) - 1):
        item = company_Accounts[i]
        if '"links":{"self":"' in item:
            start = item.find('/')
            return item[start: -1]
            

def get_filing_history(company_id):

    response = requests.get(f"https://api.company-information.service.gov.uk/company/{company_id}/filing-history",
    auth=HTTPBasicAuth('afc84b20-eab4-496b-b347-844ba6c893ab',''))
    filing_history = response.content
    return filing_history.decode('utf8').split(",")

def get_HTML_link(filing_history):

    index = search_for_file(filing_history)
    return get_link_to_download(index, filing_history)


def get_html_doc(link):

    link = f"https://find-and-update.company-information.service.gov.uk{link}/document?format=xhtml&download=1"
    response = requests.get(link)
    return response.text





#document_id = "dXYeiTj5QfaoOSi5jMGOv8cwkLx6ZDlj_7JHE1G_QdE"

# step one read in the PDF file
#response = requests.get(f"https://document-api.company-information.service.gov.uk/document/{document_id}/content",
#auth=HTTPBasicAuth('afc84b20-eab4-496b-b347-844ba6c893ab',''))
#my_raw_data = response.content

