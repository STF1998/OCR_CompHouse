import pandas
import csv


metrics = ["Fixed Assets", "Cash", "Debtors", "Current Liabilities", "Working Capital",
        "Current Assets", "Capital Employed", "Shareholders's Funds", "Turnover", "Cost of Sales",
        "Gross profit", "Administrative Expenses", "Operating profit", "Interest payable",
        "Profit before tax", "Tax", "Profit after tax"]

def get_num_missing(row):
    count = 0
    for item in metrics:
        if pandas.isnull(row[item + " (t)"]):
            count += 1
        
    return count
        


with open("Data/check_list.csv", "w") as output:
    output.write("Firm Registration\n")


with open("Data/Bankruptcy_results.csv", "r") as file:
    df = pandas.read_csv(file, index_col=False)


for index, row in df.iterrows():
    numbers = get_num_missing(row)
    count = 0
    if numbers == 1 or numbers == 2:
        print(row["Firm Reg"])
        for item in metrics:
            if pandas.isnull(row[item + " (t)"]) and pandas.isnull(row[item + " (t-1)"]) == False:
                count = 1
            if pandas.isnull(row[item + " (t)"]) == False and pandas.isnull(row[item + " (t-1)"]):
                count = 1
    
    if count == 1:
        with open("Data/check_list.csv", "a") as output:
            output.write(row["Firm Reg"] + "\n")
