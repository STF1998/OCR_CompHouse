import API_Test as api
import pandas as pd
from bs4 import BeautifulSoup, NavigableString, Tag
import os
import csv


def get_data_to_csv(html_structure, firm_reg_numbers):

    base_path = "Balance sheets/"

    if os.path.isfile(f"{base_path}{firm_reg_numbers}.csv"):
        os.remove(f"{base_path}{firm_reg_numbers}.csv")
    
    soup = BeautifulSoup(html_structure,'html.parser')
    tables = soup.findAll("table")

    i = 0

    for table in tables:
        list_headers = []
        data = []
        tr = table.find("tr")
        for element in tr:
            if isinstance(element, NavigableString):
                continue
            if isinstance(element, Tag):
                text = element.get_text().replace("\n","").replace("|", "")
                list_headers.append(text)
        for tr in table.find_all("tr")[1:]:
            sub_data = []
            is_full_of_null = True
            for element in tr:
                if isinstance(element, NavigableString):
                    continue
                if isinstance(element, Tag):
                    text = element.get_text().replace("\n","").replace("|", "")
                    if text != "":
                        is_full_of_null = False
                    sub_data.append(text)
            if is_full_of_null == False:
                data.append(sub_data)

        dataFrame = pd.DataFrame(data = data, columns = list_headers)
        if os.path.isfile(f'{base_path}{firm_reg_numbers}.csv'):
            dataFrame.to_csv(f'{base_path}{firm_reg_numbers}.csv', mode='a')
        else:
            dataFrame.to_csv(f'{base_path}{firm_reg_numbers}.csv')