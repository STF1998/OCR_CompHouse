import pytesseract
import os, re
import pandas
from PIL import Image
from io import StringIO
import pre_processing as proc
from financial_statement.Balance_sheet import Balance_sheet
from financial_statement.PandL import PandL
import numpy
from pythonds.basic import Stack

def make_measurments(df):

    df["bottom"] = df["top"] + df["height"]
    df["right"] = df["left"] + df["width"]
    return df



def get_labels_and_values(page_dataframe):

        page_description = page_dataframe.iloc[0]

        def retrieve_column_pixels(df):

            buffer = 25

            occupied_pixels = []
            columns = []
            for i in range(page_description["width"]):
                result = (( df['right'] >= i ) & ( df['left'] <= i )).sum() > 0
                if result:
                    occupied_pixels.append(i)
                else:
                    if len(occupied_pixels) != 0:
                        columns.append([min(occupied_pixels), max(occupied_pixels)])
                        occupied_pixels = []

            error_adjusted = []
            main_column = columns[0]

            for i in range(1, len(columns)):
                if main_column[1] >= columns[i][0] - buffer:
                    main_column[1] = columns[i][1]
                else:
                    error_adjusted.append(main_column)
                    main_column = columns[i]
                if i == len(columns) - 1:
                    error_adjusted.append(main_column)
            
            
            return error_adjusted
        
        def retrieve_row_pixels(df):

            occupied_pixels = []
            rows = []
            for i in range(page_description["height"]):
                result = (( df['bottom'] >= i ) & ( df['top'] <= i )).sum() > 0
                if result:
                    occupied_pixels.append(i)
                else:
                    if len(occupied_pixels) != 0:
                        rows.append([min(occupied_pixels), max(occupied_pixels)])
                        occupied_pixels = []
            return rows
        
        def condense_columns(full_data: list):

            new_cols = []

            if len(full_data) == 8:
                return [full_data[0], full_data[1], full_data[4], full_data[7]]

            for i in range(len(full_data) - 1, 1, -2):
                final_columns = []
                for j in range(min(len(full_data[i]),len(full_data[i - 1]))):
                    if j != 0:
                        if full_data[i][j].strip() == '' or full_data[i-1][j].strip() == '':
                            final_columns.append((full_data[i][j] + full_data[i-1][j]).strip())
                        else:
                            print("trying to join non-null columns - manual check required")
                    else:
                        final_columns.append(full_data[i][j])
                new_cols.append(final_columns)

            final_columns = full_data[:2]
            for j in range(len(new_cols) - 1, -1, -1):
                final_columns.append(new_cols[j])
            
            
            return final_columns
        
        def run_corrections(full_data):

            # remove columns that have very few items
            for i in range(len(full_data) - 1, -1, -1):
                count = 0
                for item in full_data[i]:
                    if item == '':
                        count += 1
                if (count / len(full_data[i])) > 0.85:
                    del full_data[i]
        
           
            # there should now be an even number of columns
            if len(full_data)%2 != 0:
                print("odd number of columns")
                exit(2)

            # join working columns
            if len(full_data) > 4:
                full_data = condense_columns(full_data)

            if len(full_data) != 4:
                print("column condensation failure")
                exit(3)

            return full_data
        


        page_dataframe = page_dataframe[page_dataframe["conf"] != -1]
        page_dataframe = page_dataframe[page_dataframe['text'].apply(lambda words: str(words).strip() != "")]
        page_dataframe = page_dataframe[page_dataframe['text'].apply(lambda words: str(words).strip("|") != "")]


        columns = retrieve_column_pixels(page_dataframe)
        rows = retrieve_row_pixels(page_dataframe)


        full_data = []
    
        for i in range(len(columns)):
            column_data = []
            for row in rows:
                horizontal = (page_dataframe['bottom'] <= row[1]) & (page_dataframe['top'] >= row[0])
                vertical = (page_dataframe['right'] <= columns[i][1]) & (page_dataframe['left'] >= columns[i][0])
                selection = horizontal & vertical
                column_data.append("".join([str(word) for word in page_dataframe[selection]['text']]))
            
            full_data.append(column_data)
        
        full_data = run_corrections(full_data)

        data = {
            "label":full_data[0],
            "t": full_data[2],
            "t-1": full_data[3]
        }
        
        return pandas.DataFrame(data)







def get_table_dataframe(page_dataframe, page_lines):
            
            if len(page_dataframe) == 0:
                return None

            unit_regex = r'^(.*([£$ ]+m|[£$(US$) ]+k|[£$ ]+000|[£$]|[£$ ]+million|[£$ ]+thousand)+.*)*$'
            table_end = r'^(.*(shareholder|loss|profit|results|income|earnings)+.*)*[0-9-()]+$'

            start = -1
            finish = -1
            for i in range(len(page_lines)):
                line = page_lines[i]
                if re.match(unit_regex, line[0]) and start == -1:
                    start = line[2]
                if re.match(table_end, line[0].lower()):
                    finish = line[3]

            #print("start =", start)
            #print("finish =", finish)

            if finish != -1 and start != -1:
                upper = page_dataframe["top"] >= start
                lower = page_dataframe["bottom"] <= finish
                upper[0] = True
                lower[0] = True
                return page_dataframe[upper & lower].reset_index(drop = True)

            return None










        



def get_lines(dataframe, space):

        lines = []

        get_numpy_of_concern = lambda row: numpy.array([row["pdf_page"], row["block_num"], row["par_num"], row["line_num"]])

        row_iterator = dataframe.iterrows()
        not_used, row_of_concern = row_iterator.__next__()
        array_of_concern = get_numpy_of_concern(row_of_concern)
        string = " "
        top = float("inf")
        bottom = 0

        for index, current_row in row_iterator:
            test_array = get_numpy_of_concern(current_row)
            if numpy.array_equiv(array_of_concern, test_array) and current_row['text'] != None:
                if bool(re.match(r'^[ \t]+$', current_row['text'])) == False and current_row['text'] != "":
                    string = string + space + current_row['text'].strip()
                    if current_row["top"] < top:
                        top = current_row["top"]
                    if current_row["bottom"] > bottom:
                        bottom = current_row["bottom"]
            else:
                if (string := string.strip()) != "":
                    four_cell = [string, row_of_concern["pdf_page"], top, bottom]
                    lines.append(four_cell)
                top = float("inf")
                bottom = 0
                row_of_concern = current_row
                array_of_concern = get_numpy_of_concern(row_of_concern)
                string = " "
        
        return lines






def run_OCR(png_file):

    print(f"analysing {png_file} with OCR")

    image = Image.open(png_file)

    configuration = """--psm 6 --oem 1 -c tessedit_char_blacklist=.°_=*~`;“”:,|\}{[]^%@!?><±§+‘’\\"\\'"""

    # --psm 6 is important as the get_lines function treats the whole page as a single block
    image_to_data = StringIO(pytesseract.image_to_data(image, config= configuration, lang="eng"))
    data = pandas.read_csv(image_to_data, sep=' |\t', error_bad_lines=False, engine='python')
    
    os.remove(png_file)

    return data








def analyse_pages(pages, dataframe, page_lines):

    def sort_line_continuations(dataframe: pandas.DataFrame):

        regex = r'^[a-z]'

        value_list =[list(dataframe.iloc[i]) for i in range(len(dataframe.index))]
        returning_data = []
        continued_line = value_list[0]

        for i in range(1, len(value_list)):

            if bool(re.match(regex, value_list[i][0])):
                text = continued_line[0] + value_list[i][0]
                t = continued_line[1] + value_list[i][1]
                tLessOne = continued_line[2] + value_list[i][2]
                continued_line= [text, t, tLessOne]
                
            if bool(re.match(regex, value_list[i][0])) == False:
                continued_line[0] = continued_line[0].lower()
                returning_data.append(continued_line)
                continued_line = value_list[i]
            
            if i == len(value_list) - 1:
                continued_line[0] = continued_line[0].lower()
                returning_data.append(continued_line)
        
        return pandas.DataFrame(data = returning_data, columns = ["label", "t", "t-1"])

        
    def  sort_units(ordered_df):

        units = [ordered_df.iloc[0]["t"], ordered_df.iloc[0]["t-1"]]
        if units[0] != units[1]:
            print("Manual Check required")

        multiplier = re.sub(r'[£\',US$\s]', "", str(units[0]))
        if multiplier == "":
            multiplier = "1"
        multiplier = re.sub(r"(000|k|thousand)", "1000", multiplier)
        multiplier = re.sub(r"(m|million)", "1000000", multiplier)

        multiplier = int(multiplier)

        for i in range(1, len(ordered_df.index)):
            if ordered_df.iloc[i]["t"] != None:
                ordered_df.iloc[i]["t"] = ordered_df.iloc[i]["t"] * multiplier
            if ordered_df.iloc[i]["t-1"] != None:
                ordered_df.iloc[i]["t-1"] = ordered_df.iloc[i]["t-1"] * multiplier

        value = re.findall(r"[£$]", ordered_df.iloc[0]["t"])
        if len(value) != 0:
            ordered_df.iloc[0]["t"] = value[0]
        value = re.findall(r"[£$]", ordered_df.iloc[0]["t-1"])
        if len(value) != 0:
            ordered_df.iloc[0]["t-1"] = value[0]
        
        return ordered_df


    def integer_conversion(ordered_df):

        def convertible(continued_line):

            if continued_line == None:
                return False

            continued_line = continued_line.strip()

            if continued_line == "":
                return False

            if re.match(r'[-.,]', continued_line):
                return False
                
            return True

        def clean_numbers(continued_line):

            sub = r'[^0-9(]'

            if continued_line["t"].strip() == "-" and continued_line["t-1"].strip() == "":
                continued_line["t"] = ""
            if continued_line["t-1"].strip() == "-" and continued_line["t"].strip() == "":
                continued_line["t-1"] = ""

            if continued_line["t"].strip() == "-":
                continued_line["t"] = "0"
            if continued_line["t-1"].strip() == "-":
                continued_line["t-1"] = "0"

            continued_line["t"] = re.sub(sub, '', continued_line["t"])
            continued_line["t-1"] = re.sub(sub, '', continued_line["t-1"])

            return continued_line
        
        to_int = lambda continued_line: int(continued_line.replace("(", "-"))

        for i in range(len(ordered_df.index)):
            if i != 0:
                ordered_df.iloc[i] = clean_numbers(ordered_df.iloc[i])
                if convertible(ordered_df.iloc[i]["t"]) == True:
                    ordered_df.iloc[i]["t"] = to_int(ordered_df.iloc[i]["t"])
                else:
                    ordered_df.iloc[i]["t"] = None
                if convertible(ordered_df.iloc[i]["t-1"]) == True:
                    ordered_df.iloc[i]["t-1"] = to_int(ordered_df.iloc[i]["t-1"])
                else:
                    ordered_df.iloc[i]["t-1"] = None
        
        return ordered_df
    
    def sort_headings_totals(ordered_df):

        stack = Stack()
        iterator = ordered_df.iterrows()
        iterator.__next__()

        t = 0
        tMinOne = 0

        for index, row in iterator:
            if stack.isEmpty() == False:
                if row['t'] != None:
                    t += row["t"]
                if row['t-1'] != None:
                    tMinOne += row['t-1']
                if row['t'] == None and row['t-1'] == None:
                    ordered_df.iloc[index]["label"] = stack.pop()
                    ordered_df.iloc[index]["t"] = t
                    ordered_df.iloc[index]["t-1"] = tMinOne
                    t, tMinOne = 0, 0 
            if row["label"] != "" and row["t"] == None and row["t-1"] == None:
                stack.push(row['label'])
                ordered_df.iloc[index]["label"] = ""
            if row["label"] == "" and (row["t"] != None or row["t-1"] != None):
                if stack.isEmpty() == False:
                    ordered_df.iloc[index]["label"] = stack.pop()

        return ordered_df

        


    for page_number in pages:
        dataframe = dataframe[dataframe["pdf_page"] == page_number]
        table_dataframe = get_table_dataframe(dataframe, page_lines)
        if type(table_dataframe) != type(None):
            ordered_df = get_labels_and_values(table_dataframe)
            ordered_df = sort_line_continuations(ordered_df)
            ordered_df = integer_conversion(ordered_df)
            ordered_df = sort_units(ordered_df)
            ordered_df = sort_headings_totals(ordered_df)
            return ordered_df

    print("Couldn't extract info - probably because I couldn't find the table")
    exit(4)



def investigate_accounts(type, df, all_lines):

    if len(pages := type.find_pages(all_lines)) == 0:
        print(f"Can't find {type.get_type()} pages")
        exit(5)

    page_lines = [line for line in all_lines if line[1] in pages]

    return analyse_pages(pages, df, page_lines)







def analyse_units(units_array):

        note_regex = r'(Notes|notes|NOTES)'
        money_regex = '[£$][ ]*[(million)(thousand)(m)(k)]*'
        dictionary = {}

        for array in units_array:
            for unit in array:
                if unit != '':
                    unit = re.sub(note_regex, '', unit).strip()
                    new = re.findall(money_regex, unit)

                    dictionary = {}
                    for key in new:
                        if key in dictionary:
                            dictionary[key] += 1
                        else:
                            dictionary[key] = 1
        
        if bool(dictionary) == False:
            return "£"
    
        return max(dictionary, key=(lambda key: dictionary[key])).strip()

    




 
def OCR_pdf(filepath):

    # Convert the pdf to png, pre-process and remove the pdfs
    print("converting PDFs to PNGs")
    proc.pdf_to_png(filepath)
    png_filepaths = proc.pre_process(filepath.replace(".pdf", ""))
    os.remove(filepath)
    
    # If there are not any images then return an empty array
    if len(png_filepaths) == 0:
        print("No images to OCR")
        exit(6)

    # Run OCR on each page
    df = pandas.DataFrame()
    page_number = 1
    for png_file in png_filepaths:
        data = run_OCR(png_file)
        data["pdf_page"] = page_number
        page_number += 1
        df = df.append(data)
    df = make_measurments(df)
    os.rmdir(filepath.split("/")[0])

    """with open("OCR_Output.csv", "w") as ocr:
        df.to_csv(ocr)
    
    exit()"""

    # Get all of the lines in the document
    all_lines = []
    for page in range(1,df["pdf_page"].max() + 1):
        page_lines = get_lines(df[df['pdf_page'] == page], "")
        all_lines = all_lines + page_lines
    
    # find the balance sheet pages
    print("Balance Sheet search")
    Balance_information = investigate_accounts(Balance_sheet(), df, all_lines)
    print("PandL search")
    PandL_information = investigate_accounts(PandL(), df, all_lines)

    # Join the extracted info for P&L and Balance sheet together
    return pandas.concat([Balance_information, PandL_information.iloc[1:]], ignore_index=True, sort=False)



def practise_OCR():

    with open("OCR_Output.csv", "r") as input:
        df = pandas.read_csv(input, index_col=[0])
    

    # Get all of the lines in the document
    all_lines = []
    for page in range(1,df["pdf_page"].max() + 1):
        page_lines = get_lines(df[df['pdf_page'] == page], "")
        all_lines = all_lines + page_lines
    
    # find the balance sheet pages
    print("Balance Sheet search")
    Balance_information = investigate_accounts(Balance_sheet(), df, all_lines)
    print("PandL search")
    PandL_information = investigate_accounts(PandL(), df, all_lines)

    # Join the extracted info for P&L and Balance sheet together
    return pandas.concat([Balance_information, PandL_information.iloc[1:]], ignore_index=True, sort=False)

        