from .Parent_extractor import Parent
import pandas

class Full_extractor(Parent):

    def __init__(self, information: pandas.DataFrame):

        self.company_information = information
        self.results = {
        "Fixed Assets (t)": "",
        "Cash (t)": "",
        "Debtors (t)": "",
        "Current Liabilities (t)": "", 
        "Working Capital (t)": "",
        "Current Assets (t)": "",
        "Capital Employed (t)": "",
        "Shareholders's Funds (t)": "",
        "Turnover (t)": "",
        "Cost of Sales (t)": "",
        "Gross profit (t)": "", 
        "Administrative Expenses (t)": "",
        "Operating profit (t)": "",
        "Interest payable (t)": "",
        "Profit before tax (t)": "",
        "Tax (t)": "",
        "Profit after tax (t)": "",
        "Fixed Assets (t-1)": "",
        "Cash (t-1)": "",
        "Debtors (t-1)": "",
        "Current Liabilities (t-1)": "", 
        "Working Capital (t-1)": "",
        "Current Assets (t-1)": "",
        "Capital Employed (t-1)": "",
        "Shareholders's Funds (t-1)": "",
        "Turnover (t-1)": "",
        "Cost of Sales (t-1)": "",
        "Gross profit (t-1)": "", 
        "Administrative Expenses (t-1)": "",
        "Operating profit (t-1)": "",
        "Interest payable (t-1)": "",
        "Profit before tax (t-1)": "",
        "Tax (t-1)": "",
        "Profit after tax (t-1)": ""
        }



            
    
    def get_variables(self):

        def register_result(self, row, list, label):

            if any(item in row["label"] for item in list):
                if self.results[label + " (t)"] == "":
                    self.results[label + " (t)"] = row["t"]
                if self.results[label + " (t-1)"] == "":
                    self.results[label + " (t-1)"] = row["t-1"]


        check_list = [["Current Liabilities", ["creditorsamountsfallingduewithinoneyear", "creditors"]],
            ["Working Capital", ["netcurrentliabilities", "netcurrentassets", "workingcapital"]],
            ["Capital Employed", ["totalassetslesscurrentliabilities", "assetslesscurrent"]],
            ["Shareholders's Funds", ["shareholders'funds", "capitalandreserves", "totalequity", "shareholders'",
                                    "reserves", "shareholdersfunds", "shareholders"]],
            ["Current Assets", ["currentassets"]],
            ["Cash", ["cashatbankandinhand", "cashatbank", "cash"]],
            ["Debtors", ["debtorsamountsfallingduewithinoneyear", "debtors"]],
            ["Turnover", ["turnover", "revenue"]],
            ["Cost of Sales", ["costofsales"]],
            ["Gross profit", ["grossprofit", "grossloss"]],
            ["Administrative Expenses", ["administrativeexpenses", "administrativecosts", "administrative"]],
            ["Operating profit",["operatingprofit", "operatingloss", "operating(loss)"]],
            ["Interest payable",["interestpayableandsimilarcharges", "interestpayable"]],
            ["Profit before tax",["lossonordinaryactivitiesbeforetax", "profitonordinaryactivitiesbeforetax",
                                "beforetax", "beforeincometax"]],
            ["Tax",["taxonprofit", "taxonloss", "taxon(loss)", "taxexpense"]],
            ["Profit after tax",["lossforthefinancialperiod", "profitforthefinancialperiod", "aftertax",
                                 "lossfortheyear", "profitforthefinancialyear", "(loss)/profitforthefinancialyear",
                                 "lossforthefinancialyear"]],
            ["Fixed Assets", ["fixedassets", "fixed"]]]


        for index, row in self.company_information.iterrows():

            equity_list = False
            t = 0
            tLessOne = 0
            
            if index != 0:
                for item in check_list:
                    register_result(self, row, item[1], item[0])
                if "sharecapital" in row["label"] or "called" in row["label"]:
                    equity_list = True
                if equity_list == True:
                    if row['t'] != None:
                        t += row['t']
                    if row['t-1'] != None:
                        tLessOne += row['t-1']
                if "profitandlossaccount" in row["label"] or "retainedearnings" in row["label"]:
                    equity_list = False


        if self.results["Shareholders's Funds (t)"] == "":
            print("No Shareholders funds detected", t)
            self.results["Shareholders's Funds (t)"] = t
        if self.results["Shareholders's Funds (t-1)"] == "":
            print("No Shareholders funds detected", tLessOne)
            self.results["Shareholders's Funds (t-1)"] = tLessOne
                   

    def fill_obvious_gaps(self):



        if self.results['Current Assets (t)'] == "" and self.results['Current Assets (t-1)'] == "":
            if self.results["Working Capital (t)"] != "" and self.results["Current Liabilities (t)"] != "":
                self.results["Current Assets (t)"] = self.results["Working Capital (t)"] - self.results["Current Liabilities (t)"]
                print("Current assets (t) = ", self.results['Current Assets (t)'])
            if self.results["Working Capital (t-1)"] != "" and self.results["Current Liabilities (t-1)"] != "":
                self.results["Current Assets (t-1)"] = self.results["Working Capital (t-1)"] - self.results["Current Liabilities (t-1)"]
                print("Current assets (t-1) = ", self.results['Current Assets (t-1)'])



    def fill_missing_variables(self, time):

        if self.results["Fixed Assets " + time] == "" and self.results["Total Assets " + time] != "" and self.results["Current Assets"] != "":
            self.results["Fixed Assets " + time] = self.results["Total Assets " + time] - self.results["Current Assets " + time]
        
        if self.results["Current Assets " + time] == "" and self.results["Fixed Assets " + time] != "" and self.results["Total Assets " + time] != "":
            self.results["Current Assets " + time] = self.results["Total Assets " + time] - self.results["Fixed Assets " + time]

    def is_missing_items(self):

        count = 0

        for key, value in self.results.items():
            if value == "":
                count += 1

        self.count = count
        
        if count > 0:
            return True

        return False

    def get_number_missing(self):

        return self.count


    def are_results_valid(self, time):

        
        # if current assets + fixed assets minus total liabilities != shareholder funds
        if (self.results["Current Assets " + time] + self.results["Fixed Assets " + time]) + self.results["Total Liabilities " + time] != self.results["Shareholders's Funds " + time]:
            print("Test 1 failed")
            return False
        
        # Check that gross profit = turnover - cost of sales
        if self.results["Turnover " + time] + self.results["Cost of Sales " + time] != self.results["Gross profit " + time]:
            print("Test 2 failed")
            return False
        
        # Check that Earnings after tax is equal to earnings before tax + tax on profit/loss
        if self.results["Profit before tax " + time] + self.results["Tax " + time] != self.results["Profit after tax " + time]:
            print("Test 3 failed")
            return False

        # Check that earning before tax + interest payable == operating profit
        if self.results["Profit before tax " + time] + self.results["Interest payable " + time] != self.results["Operating profit " + time]:
            print("Test 4 failed")
            return False
        
        print("Data validity checks passed - no need for manual checks")
        return True


    def get_results(self):
        return self.results
