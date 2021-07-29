import os 
import time
import pandas


with open("Insolvent_firms/available_accounts.csv", "r") as avail:
    df = pandas.read_csv(avail)

header_names = df.columns
"""
for name in header_names:
    print(name)"""


selected_columns = [" CompanyNumber", 
                    "CompanyName",
                    "Mortgages.NumMortCharges",
                    "Mortgages.NumMortOutstanding",
                    "Mortgages.NumMortPartSatisfied",
                    "Mortgages.NumMortSatisfied"]

"""check =  all(item in header_names for item in selected_columns)

print(check)
exit()"""


dataframe = df[selected_columns]

working_df = df[[" PreviousName_1.CompanyName",
                " PreviousName_2.CompanyName",
                " PreviousName_3.CompanyName",
                " PreviousName_4.CompanyName",
                " PreviousName_5.CompanyName",
                " PreviousName_6.CompanyName",
                " PreviousName_7.CompanyName",
                " PreviousName_8.CompanyName",
                " PreviousName_9.CompanyName",
                " PreviousName_10.CompanyName"]]

dataframe["numberPrevNameChanges"] = working_df.count(axis = 1)

print(working_df.head())

working_df = df[["SICCode.SicText_1",
                "SICCode.SicText_2",
                "SICCode.SicText_3",
                "SICCode.SicText_4"]]

dataframe["NumberOfIndustires"] = working_df.count(axis = 1)
dataframe["PrimaryIndustry"] = df["SICCode.SicText_1"]


with open("desired_attributes.csv", "w") as des:
    dataframe.to_csv(des)


