from Extractors.Full_extractor import Full_extractor
from csv import writer
import API as api
import OCR as ocr
import os, time
from pebble import ProcessPool
from concurrent.futures import TimeoutError
import pandas

data_columns = ["Fixed Assets (t)",
        "Cash (t)",
        "Debtors (t)",
        "Current Liabilities (t)", 
        "Working Capital (t)",
        "Current Assets (t)",
        "Capital Employed (t)",
        "Shareholders's Funds (t)",
        "Turnover (t)",
        "Cost of Sales (t)",
        "Gross profit (t)", 
        "Administrative Expenses (t)",
        "Operating profit (t)",
        "Interest payable (t)",
        "Profit before tax (t)",
        "Tax (t)",
        "Profit after tax (t)",
        "Fixed Assets (t-1)",
        "Cash (t-1)",
        "Debtors (t-1)",
        "Current Liabilities (t-1)", 
        "Working Capital (t-1)",
        "Current Assets (t-1)",
        "Capital Employed (t-1)",
        "Shareholders's Funds (t-1)",
        "Turnover (t-1)",
        "Cost of Sales (t-1)",
        "Gross profit (t-1)", 
        "Administrative Expenses (t-1)",
        "Operating profit (t-1)",
        "Interest payable (t-1)",
        "Profit before tax (t-1)",
        "Tax (t-1)",
        "Profit after tax (t-1)", 
        "Firm Reg"]
    
exit_codes={1: 0, # Too many missing values
            2: 0, # Odd number of columns detected
            3: 0, # Too many columns detected
            4: 0, # No table found
            5: 0, # Couldn't find pages
            6: 0, # PDF conversion error
            7: 0} # Ambiguous detection of pages


def write_results(results):

    values = []
    for key, value in results.items():
        values.append(value)

    with open("information_repo/results.csv", "a+") as file:
        csv_writer = writer(file)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(values)


def task_done(future):
    
    try:
        future.result() # blocks until results are ready
    except TimeoutError as error:
        print("Function took longer than %d seconds" % error.args[1])
    except Exception as error:
        problemo = error.exitcode
        exit_codes[problemo] += 1
        if problemo == 5:
            print("No Table Found!")


def driver(firm_reg):

    print(firm_reg)

    folder = f"images_{firm_reg}"
    os.mkdir(folder)
    pathway = f"{folder}/companies_house_document.pdf"

    # call CH api to retrieve and save the pdf for company accounts
    api.api_drive(firm_reg, pathway)

    # extract all balance sheet data relating to the company accounts
    data = ocr.OCR_pdf(pathway)
    #data = ocr.practise_OCR()

    full = Full_extractor(data)
    full.get_variables()
    check_required = False

    results = results = full.get_results()
    full.fill_obvious_gaps()
    results["Firm Registration"] = firm_reg
    for key, value in results.items():
        print(key, value)

    if full.is_missing_items() == True:
        print("Missing data, checks required")
        if full.get_number_missing() < 5:
            check_required = True
            write_results(results)
        else:
            print(f"Info dumped with {full.get_number_missing()} missing items")
            exit(1)
    else:
        write_results(results)

    if os.path.isfile("manual_checks_list.csv") and check_required == True:
        with open("manual_checks_list.csv", "a") as checker:
            checker.write(firm_reg + "\n")



if __name__ == '__main__':

    
    with open("information_repo/manual_checks_list.csv", "w") as checker:
        checker.write("Firm Registration\n")

    with open("information_repo/results.csv", "w") as results:
        pandas.DataFrame(columns = data_columns).to_csv(results)    
    
    with open("information_repo/basics.csv", "r") as info:
        df = pandas.read_csv(info)
    
    firm_list = df["CompanyNumber"].sample(50)
    firm_list = [firm for firm in firm_list]


    with ProcessPool(max_workers=1) as pool:
        for firm_reg in firm_list:
            future = pool.schedule(driver, args=[firm_reg], timeout= 600)
            future.add_done_callback(task_done)

    with open("information_repo/exitcodes.csv", "w") as exit:
        pandas.DataFrame(exit_codes).to_csv(exit)