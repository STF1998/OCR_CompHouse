import pandas
import numpy
import math
from datetime import datetime

pandas.options.mode.chained_assignment = None

with open("Data/.BasicCompanyDataAsOneFile-2021-08-01.csv.icloud", "r") as file:
    df = pandas.read_csv(file)


df = df[df["CompanyStatus"] == 'Active']
df = df[df["Accounts.AccountCategory"] == "FULL"]
df = df[df[" CompanyNumber"].str.contains("FC") == False]


df = df.sample(frac=1)
number_of_rows = len(df.index)
file_length = math.floor(number_of_rows/5)

accounting_per_start = ['2015', '2016', '2017', '2018', '2019']

for i in range(0, len(accounting_per_start) - 1):
    with open("Data/" + accounting_per_start[i] + '.csv', 'w') as accounts:
        lower_bound = i * file_length
        upper_bound = (i + 1) * file_length
        df[lower_bound:upper_bound].to_csv(accounts)

last_file = df[4*file_length:5*file_length]
with open("Data/" + accounting_per_start[4] + '.csv', 'w') as accounts:
    last_file.to_csv(accounts)










