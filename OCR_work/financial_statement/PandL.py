from .Financial_document import Fin_Doc
import re
import pandas

class PandL(Fin_Doc):

    def __init__(self):
        self.info_type = "P and L"

    def find_pages(self, lines):

        required = ["profitandlossaccount", "statementofincome", "pandlreport", "incomestatement"]
        comp = ["statementofcomprehensiveincome"]
        not_required = ["balancesheet", "officersand", "directorsreport", "directorssreport",
                        "auditorsreport", "statementofchangesinequity", "statementofchanges",
                        "notestothefinancialstatement", "notestotheaccounts", "statementofaccountingpolicies",
                        "cashflow", "messagefromtheceo", "statementofdirectorsresponsibilit", 
                        "statementofdirectorssresponsibilit", "statementoffinancialposition",
                        "accountingpolicies", "statementoftotalrecognisedgainsandlosses", "(continued)"]

        include, exclude, comp = [],[],[]

        df = pandas.DataFrame({'text': [line[0] for line in lines], 'page': [line[1] for line in lines]})
        df = df.groupby('page').head(8).reset_index(drop=True)
        
        for index, row in df.iterrows():
            text = row['text'].lower()
            if any(item in text for item in required):
                include.append(row['page'])
            if any(item in text for item in not_required):
                exclude.append(row['page'])
            if any(item in text for item in comp):
                comp.append(row['page'])
        

        print("Include =", include)
        print("Exclude =", exclude)

        answer = [number for number in include if number not in exclude]

        if len(answer) == 0:
            answer = [number for number in comp if number not in exclude]
        
        if len(answer) > 1:
            print("Place of PandL is ambiguous")
            exit(7)

        return answer

   
    def extract_text(self, text):

        def sort_line_continuations(table_text):

            new_table_text = [table_text[0]]
            regex = r'[a-z]'

            for i in range(1, len(table_text)):
                if bool(re.match(regex, table_text[i][0])):
                        new_table_text[-1] = f"{new_table_text[-1]} {table_text[i]}"
                else:
                    new_table_text.append(table_text[i])

            return new_table_text

        def sort_brackets(line):

            new_text = []

            for i in range(0, len(line)):
                if line[i] != '(' or bool(re.match(r'[A-Za-z -]', line[i+1])) == False:
                    new_text.append(line[i])

            return "".join(new_text).replace("(", "-")
            


        finance_regex = r'(.*)\s+(\(?\-?[\,0-9-]+\)?)\s+(\(?\-?[\,0-9-]+\)?)$'
        panic_regex = r'^([a-zA-Z/]+(\s+[\sa-zA-Z/]+)*)\s+[0-9]+$'
        numbers_regex = r'(?<![a-zA-Z:])[-+]?\d*\.?\d+'
        label_regex = r'(\b[a-zA-Z/ ]*\b)'
        info = {}


        text = sort_line_continuations(text)

        for line in text:
            line = re.sub(r'[^\s/0-9A-Za-z(-]', "", line)
            line = sort_brackets(line)

            if re.match(panic_regex, line):
                return None

            if bool(re.match(finance_regex, line)):
                label = re.match(label_regex, line).group().strip()
                values = re.findall(numbers_regex, line)
                info[label.lower()] = values[-2]
        
        return info
