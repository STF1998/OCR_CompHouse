# Importing the required modules
import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
import numpy

def negate(string):

    open = string.find('(')
    close = string.find(')')
    if open == -1:
        open = 0
    if close == -1:
        close = len(string)

    print(string[open + 1:close])

    return f"-{string[open + 1:close]}"




def retrieve_data(line, current, current_value, pounds):

    print(line)
    
    if current_value != "":
        return current_value

    index = [current]
    for i in range(current + 1, len(line)):
        if line[i] != "":
            index.append(i)

    if len(index) == 4:
        print(index[2])
        print(index)
        return line[index[2]]
    if len(index) == 3 and pounds%2 == 0:
        print(index[1])
        print(index)
        return line[index[1]]
    if len(index) == 3 and pounds%2 != 0:
        print(index[2])
        print(index)
        return line[index[2]]
    return ""

def count_pounds(line, i):

    pounds = 0
    for j in range (i + 1, len(line)):
        if "£" in line[j]:
            pounds = pounds + 1

    return pounds

def extract(csv_reader):

    index = -1
    dict = {
        "working capital": "",
        "provision": "",
        "current liabilities":"",
        "currrent assets": ""
    }

    for line in csv_reader:
        loop = True
        i = 0
        pounds = 0
        while loop == True:
            word = line[i].lower()
            if "note" in line[i]:
                pounds = count_pounds(line, i)
            if "net current assets" in word or "net current liabilities" in word:
                loop = False
                dict["working capital"] = retrieve_data(line, i, dict["working capital"], pounds)
            if "provision" in word:
                loop = False
                dict["provision"] = retrieve_data(line, i, dict["provision"], pounds)
            if "creditors" in word or "due within one year" in word:
                loop = False
                dict["current liabilities"] = retrieve_data(line, i, dict["current liabilities"], pounds)
            i = i + 1
            if i > len(line) - 1:
                loop = False
    if dict["current liabilities"] != "" and dict["working capital"] != "":
        curr_assets =  int(dict["working capital"]) + int(dict["current liabilities"])
        dict["currrent assets"] = str(curr_assets)
    return dict



def parse_structure_HTML(HTML_content):

    data = []

    # for getting the header from
    # the HTML file
    list_header = []
    soup = BeautifulSoup(HTML_content,'html.parser')

    tables = soup.find_all("table")

    for table in tables:
        for element in table.find_all("tr"):
            sub_data = []
            for sub_element in element:
                try:
                    sub_element = sub_element.get_text().replace("\n","").replace("|", "")
                    if len(sub_element) != 0:
                        sub_data.append(sub_element)
                except:
                    continue
            if len(sub_data) != 0:
                data.append(sub_data)

    return data
