from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import url_contains
from selenium.webdriver.support.expected_conditions import presence_of_all_elements_located

import xlsxwriter
import pandas as pd

import time
import os
import shutil
import zipfile

from translate_hebrow2english import translate
from aviad_functions import *
PATH_SEP = os.path.sep
FILE_SUFFIX = ['pdf', 'PDF', 'zip', 'ZIP', 'jpg', 'png']


def main():
    print(os.getcwd())
    blocks_file = select_file()
    print("blocks_file:", blocks_file)
    download_path = PATH_SEP.join(blocks_file.split(PATH_SEP)[:-1])
    print("download_path:", download_path)
    # open browser:
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True})
    if os.name != 'posix':
        path_to_chromedriver = os.path.join(os.path.join(os.getcwd(), "windows_webdriver"), "chromedriver.exe")
    else:
        path_to_chromedriver = os.path.join(os.path.join(os.getcwd(), "linux_webdriver"), "chromedriver")
    print(path_to_chromedriver)
    # print(path_to_chromedriver)
    browser = webdriver.Chrome(options=options, executable_path=path_to_chromedriver)

    # don't understand this
    # i = 0
    output_path = os.path.join(download_path, "minhal_output.xlsx")
    # while os.path.isfile(output_path):
    #     output_path = output_path.replace(str(i), str(i + 1))
    #     i += 1

    # create output file to write plan data into:
    file_header = ["גוש", " תיקייה", "מספר תבע", "סטאטוס", "תאריך", "סוג תכנית", "מפורטת?", "האם יש חומר"]
    output_file = xlsxwriter.Workbook(output_path)
    data_sheet = output_file.add_worksheet()
    data_sheet.write_row(0, 0, file_header, output_file.add_format({'bold': True}))
    next_row_index = 1
    # can't close the file because xlsxwriter can't append to existing file

    # select block number:
    blocks = pd.read_excel(blocks_file, header=None)
    print("blocks: ", blocks[0])

    try:
        for block_number in blocks[0]:  # loop loads all blocks in input file

            # load new block:
            print("loading block " + str(block_number))
            load_block(block_number, browser)

            single_plan = True

            # check if block loaded plan list or single plan
            block_url = browser.current_url
            try:
                WebDriverWait(browser, timeout=10).until(
                    url_contains("http://mavat.moin.gov.il/mavatps/forms/SV4.aspx?tid=4"))
            except Exception as e:
                single_plan = False

            # SINGLE PLAN: %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            if single_plan:  # check if block has multiple or single plans
                print("loaded single-plan block")
                print("0")
                bad_plan = True
                reason = '-'
                try:  # if plan passes try then it is a bad plan

                    title = browser.find_element_by_id("ctl00_ContentPlaceHolder1_NPlanEntityTitle").text
                    title_s = "ערר על החלטת ועדה מקומית בהיתר,השבחה,פיצויים ותכנית "
                    plan_number = title.split(title_s)[1]
                    reasone_id = "ctl00_ContentPlaceHolder1_ENTITY_SUBTYPE"
                    reason = get_text_or_value(browser, reasone_id)
                    # store plan values in plan_data list:
                    plan_data = [block_number,  # store block number in first index
                                 translate(plan_number),  # store translated plan name in second index
                                 plan_number]  # store plan name in third index

                except Exception as e:  # if plan doesn't pass try then it is a good plan
                    # plan is a regular plan because it has a regular title
                    bad_plan = False
                    print("BLOCK URL ", block_url)
                    try:
                        title = browser.find_element_by_id("ctl00_ContentPlaceHolder1_tbPlanEntityNum").\
                            get_attribute("value")
                    except :
                        title = browser.find_element_by_id("ctl00$ContentPlaceHolder1$tbPlanEntityNum").text
                    title_s = "תכנית "
                    # title_name = browser.find_element_by_id("ctl00_ContentPlaceHolder1_tbPlanEntityName").\
                    #     get_attribute("value")
                    plan_number = title.split(title_s)[1]

                    # store plan values in plan_data list:
                    plan_data = [block_number,  # store block number in first index
                                 translate(plan_number),  # store translated plan name in second index
                                 plan_number]  # store plan name in third index

                if (not (plan_is_duplicate(plan_data))):  # check if plan was already scanned before
                    sketch = sketch_available(browser)
                    shp = shp_available(browser)
                    if ((sketch or shp) and (not bad_plan)):
                        plan_data = scrape_plan(plan_data, browser, reason)
                        plan_data.append("Y")

                        try:
                            plan_path = os.path.join(download_path, plan_data[1])
                            if not os.path.exists(plan_path):
                                os.mkdir(plan_path)

                        except Exception as e:
                            raise e

                        if sketch:  # sketch download:
                            print("sketch: ", sketch)
                            sketch_download_buttons = sketch_download(browser)
                            for button in sketch_download_buttons:
                                file_downloaded = False
                                count = 0
                                button.click()
                                while (not file_downloaded):
                                    if count >= 20:
                                        button.click()
                                        count = 0
                                    time.sleep(1)
                                    count += 1
                                    sketch_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)],
                                                          key=os.path.getmtime)
                                    if is_pdf_zip_or_image(sketch_file[-3:]):
                                        file_downloaded = True
                                        print(sketch_file)
                                        new_sketch_name = sketch_file.split("\\")[-1]
                                        print("new_sketch_name: ", new_sketch_name)
                                        shutil.move(sketch_file, os.path.join(plan_path,
                                                                              new_sketch_name))  # move sketch file to plan folder

                                    else:
                                        print("waiting for file to download...")

                        if shp:  # shp download:
                            print("shp: ", shp)
                            shp_download(browser)
                            file_downloaded = False
                            count = 0
                            while (not file_downloaded):

                                if count >= 20:
                                    shp_download(browser)
                                    count = 0
                                time.sleep(1)
                                count += 1
                                shp_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)],
                                                          key=os.path.getmtime)
                                if is_pdf_zip_or_image(sketch_file[-3:]):
                                    file_downloaded = True
                                    new_shp_name = shp_file.split("\\")[-1]
                                    print(shp_file)
                                    shutil.move(shp_file,
                                                os.path.join(plan_path, new_shp_name))  # move shp file to plan folder

                                else:
                                    print("waiting for file to download...")

                            shp_file = os.path.join(plan_path, new_shp_name)
                            with zipfile.ZipFile(shp_file, 'r') as zip_ref:
                                zip_ref.extractall(plan_path)

                    else:  # there are no files to download
                        for x in range(4):
                            if x == 2 and reason:
                                plan_data.append(reason)
                            else:
                                plan_data.append("-")
                        plan_data.append("N")

                    df = pd.DataFrame([plan_data])
                    df.to_csv("scraped_plans.csv", mode="a", index=False,
                              header=False)  # note that this plan was scraped

                    data_sheet.write_row(next_row_index, 0, plan_data)
                    next_row_index += 1

                else:
                    print("plan is duplicate")

            # PLAN LIST: %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            else:  # if block loaded plan list continue as usual
                print("loaded block plan list")
                plan_links = browser.find_elements_by_class_name("clsTableCellLink")

                for x, plan_link in enumerate(plan_links):  # loop opens all plans in block
                    print("plane link: ", x)

                    # store plan values in plan_data list:
                    plan_data = [block_number,  # store block number in first index
                                 translate(plan_link.text),  # store translated plan name in second index
                                 plan_link.text]  # store plan name in third index
                    plan_link.click()

                    if (not (plan_is_duplicate(plan_data))):  # check if plan was already scanned before

                        sketch = sketch_available(browser)
                        shp = shp_available(browser)
                        reason = '-'
                        # if sketch or shp: changed this if to try except
                        try:
                            plan_data = scrape_plan(plan_data, browser, reason)
                            plan_data.append("Y")
                            try:
                                plan_path = os.path.join(download_path, plan_data[1])
                                if not os.path.exists(plan_path):
                                    os.mkdir(plan_path)

                            except Exception as e:
                                raise e
                            if sketch:  # sketch download:

                                sketch_download_buttons = sketch_download(browser)
                                # print("sketch_download_buttons:", sketch_download_buttons)
                                for button in sketch_download_buttons:
                                    file_downloaded = False
                                    count = 0
                                    button.click()
                                    while (not file_downloaded):
                                        if count >= 20:
                                            button.click()
                                            count = 0
                                        time.sleep(1)
                                        count += 1
                                        # sketch_file = max([download_path + "\\" + f for f in os.listdir(download_path)],
                                        #                   key=os.path.getmtime)  # get sketch file name
                                        sketch_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)],
                                                          key=os.path.getmtime)  # get sketch file name
                                        if is_pdf_zip_or_image(sketch_file[-3:]):
                                            file_downloaded = True
                                            print("sketch_file:", sketch_file)
                                            new_sketch_name = sketch_file.split(PATH_SEP)[-1]
                                            shutil.move(sketch_file, os.path.join(plan_path,
                                                                                  new_sketch_name))  # move sketch file to plan folder

                                        else:
                                            print("waiting for file to download...")

                            if shp:  # shp download:

                                shp_download(browser)
                                file_downloaded = False
                                count = 0
                                while (not file_downloaded):

                                    if count >= 20:
                                        shp_download(browser)
                                        count = 0
                                    time.sleep(1)
                                    count += 1
                                    # shp_file = max([download_path + "\\" + f for f in os.listdir(download_path)],
                                    #                key=os.path.getmtime)  # get shp file name
                                    shp_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)],
                                                      key=os.path.getmtime)  # get sketch file name
                                    if is_pdf_zip_or_image(shp_file[-3:]):
                                        file_downloaded = True
                                        new_shp_name = shp_file.split(PATH_SEP)[-1]
                                        print(shp_file)
                                        shutil.move(shp_file, os.path.join(plan_path,
                                                                           new_shp_name))  # move shp file to plan folder

                                    else:
                                        print("waiting for file to download...")

                                shp_file = os.path.join(plan_path, new_shp_name)
                                with zipfile.ZipFile(shp_file, 'r') as zip_ref:
                                    zip_ref.extractall(plan_path)

                        except:
                            print("this plan is bad")

                        df = pd.DataFrame([plan_data])
                        df.to_csv("./scraped_plans.csv", mode="a", index=False,
                                  header=False)  # note that this plan was scraped

                        data_sheet.write_row(next_row_index, 0, plan_data)
                        next_row_index += 1

                    else:
                        print("plan is duplicate")
                    browser.back()
                    plan_links = browser.find_elements_by_class_name("clsTableCellLink")
    except Exception as e:
        raise e

    finally:
        output_file.close()
        browser.close()
        try:
            os.remove('scraped_plans.csv')
        except:
            print("no scraped_plans file found!")


def get_variables(download_path_minhal, file_excel):
    file_excel_gushim_path = file_excel

    main(file_excel)


if __name__ == "__main__":
    main()
