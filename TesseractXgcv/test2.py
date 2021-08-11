import time
from typing import final
import pandas
from csv import writer
import re
import sys
import numpy
from pebble import ProcessPool
import os
import jellyfish
import math
from pythonds.basic import Stack

def sort_line_continuations(dataframe: pandas.DataFrame):

        def join(continued_line, value_list, i):

            text = continued_line[0] + value_list[i][0]
            return [text, value_list[i][1], value_list[i][2]]
        
        def append_returning_data(returning_data, continued_line):
            continued_line[0] = continued_line[0].lower()
            returning_data.append(continued_line)


        value_list =[list(dataframe.iloc[i]) for i in range(len(dataframe.index))]
        returning_data = []
        returning_data.append([value_list[0][0], value_list[0][1], value_list[0][2]])
        continued_line = value_list[1]

        for i in range(2, len(value_list)):

            value_list[i][0] = re.sub(r'[0-9]', '', value_list[i][0])
            joining = False

            if value_list[i][0] != "" and continued_line[0] != "":
                if continued_line[0][-1].isupper() == value_list[i][0][0].isupper():
                    if value_list[i][0][0].isupper() == value_list[i][0][1].isupper():
                        if continued_line[1] == "" and continued_line[2] == "":
                            continued_line = join(continued_line, value_list, i)
                            joining = True
    
            if joining == False:
                append_returning_data(returning_data, continued_line)
                continued_line = value_list[i]
            
            if i == len(value_list) - 1:
                continued_line[0] = continued_line[0].lower()
                returning_data.append(continued_line)

        return pandas.DataFrame(data = returning_data, columns = ["label", "t", "t-1"])


with open("header.csv", "r") as file:
    df = pandas.read_csv(file, index_col=[0])

for index, row in df.iterrows():
    if type (row['label']) == type(1.1):
        row['label'] = ''
    if type (row['t']) == type(1.1):
        row['t'] = ""
    if type (row['t-1']) == type(1.1):
        row['t-1'] = ""


print(df[-1])




