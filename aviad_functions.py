from selenium.webdriver.support.ui import WebDriverWait
FILE_SUFFIX = ['pdf', 'PDF', 'zip', 'ZIP', 'jpg', 'png']


def get_text_or_value(browser, css_identifier):
    text = browser.find_element_by_id(css_identifier).get_attribute("value")
    print("text1: ", text)
    if text == '':
        text = browser.find_element_by_id(css_identifier).text
        print("text2: ", text)
    return text


def is_pdf_zip_or_image(suffix):
    if suffix in FILE_SUFFIX:
        return True


def load_block(block_number, browser):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    # load new block:
    try:
        browser.get("http://mavat.moin.gov.il/mavatps/forms/sv3.aspx?tid=3")
        load_block_text = browser.find_element_by_id("ctl00_ContentPlaceHolder1_txtFromBlock")
        load_block_text.send_keys(block_number)

        filter_button = browser.find_element_by_id("ctl00_ContentPlaceHolder1_btnFilter")
        filter_button.click()
    except:
        print("can't load block")


def scrape_plan(plan_data, browser, reason):
    from selenium import webdriver

    try:
        # find status and date:
        plan_header = browser.find_element_by_id("ctl00_ContentPlaceHolder1_tbPlanStatus")
        stat_and_date = plan_header.find_elements_by_tag_name("b")[:2]
        plan_data.append(stat_and_date[0].text)
        plan_data.append(stat_and_date[1].text)
        # find type and detailed:
        Type = browser.find_element_by_name("ctl00$ContentPlaceHolder1$planEntitySubtype").get_attribute("value")
        Detailed = browser.find_element_by_id("ctl00_ContentPlaceHolder1_tdDETAILED").text
        plan_data.append(Type)
        plan_data.append(Detailed)

    except Exception as e:

        try:  # check if there is a reason for not excepting the plan
            css_identifier = "ctl00_ContentPlaceHolder1_ENTITY_SUBTYPE"
            reason = get_text_or_value(browser, css_identifier)
            print("bad reason: ", reason)
        except:
            pass
        print("reason: ", reason)
        for x in range(4):
            if x == 2 and reason != '-':
                plan_data.append(reason)
            else:
                plan_data.append("-")
        plan_data.append("N")
        raise e

    return plan_data


def sketch_available(browser):
    from selenium import webdriver

    available = False
    # check if sketch files available
    try:
        table = browser.find_element_by_id("tblDocs")
        rows = table.find_elements_by_class_name("clsTableRowNormal")
        for row in rows:
            str = row.find_element_by_class_name("clsTableCell").text
            if str.find("תשריט") > -1:
                available = True
    except Exception as e:
        available = False
    finally:
        return available


def sketch_download(browser):
    from selenium import webdriver
    from selenium.webdriver.support.expected_conditions import element_to_be_clickable
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    pdf_buttons = []
    # download sketch file:
    table = browser.find_element_by_id("tblDocs")
    documents_info = table.find_elements_by_class_name("clsTableRowNormal")
    for document in documents_info:
        str = document.find_element_by_class_name("clsTableCell").text
        if str.find("תשריט") > -1:
            pdf_buttons.append(document.find_element_by_tag_name("img"))

    return pdf_buttons


def shp_available(browser):
    from selenium import webdriver

    available = False
    # check if plan SHP files available
    try:
        # find SHP file:
        documents_table = browser.find_element_by_id("tblDocs")
        documents_info = documents_table.find_elements_by_class_name("clsTableRowNormal")
        for document in documents_info:
            str = document.find_elements_by_class_name("clsTableCell")[1].text
            if str.find("shp") > -1 or str.find("SHP") > -1:
                available = True
                break
    except Exception as e:
        available = False
    finally:
        return available


def shp_download(browser):
    from selenium import webdriver

    # download SHP file:
    documents_table = browser.find_element_by_id("tblDocs")
    documents_info = documents_table.find_elements_by_class_name("clsTableRowNormal")
    for document in documents_info:
        document_info = document.find_elements_by_class_name("clsTableCell")
        str = document_info[1].text
        if str.find("shp") > -1 or str.find("SHP") > -1:
            document_info[4].find_element_by_tag_name("img").click()
            break


def find_csv():
    import os
    import pandas as pd

    scraped_plans = "scraped_plans.csv"

    try: #changed from if statement
        # if os.path.isfile(scraped_plans):
        plans = pd.read_csv(scraped_plans, header=None)

    except:
        plans = pd.DataFrame()

    return plans


def plan_is_duplicate(plan_data):
    duplicate = False
    plans = find_csv()

    if not (plans.empty):
        for plan_name in plans.values:
            if plan_data[1] == plan_name[1]:
                duplicate = True
                break

    return duplicate


def select_file():
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    # open select input file window:
    Tk().withdraw()
    selected_file = askopenfilename()
    # selected_file = selected_file.replace("/", "\\")

    return selected_file

