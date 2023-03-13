"""
Extracts membership list from ClubSpark, performs necessary formatting, then uploads file to cloud
file storage.
"""

import os
import time
import shutil
import glob
import argparse
import pandas as pd
from common import *
from dotenv import load_dotenv, find_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

load_dotenv(find_dotenv())

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'),
                          options=chrome_options)


def delete_columns_in_csv(columns_to_delete_list):
    downloaded_list = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH') + '.csv')
    data = pd.read_csv(downloaded_list[0])
    for column in columns_to_delete_list:
        data.drop(column, inplace=True, axis=1)
        print(f'Deleted column \'{column}\'')
    data.to_csv(downloaded_list[0], index=False)


def delete_preexisting_lists(file_type):
    preexisting_lists_in_downloads = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH')
                                               + file_type)
    preexisting_lists_in_box = glob.glob(os.getenv('MEMBERSHIP_LIST_BOX_PATH') + file_type)

    if len(preexisting_lists_in_downloads) > 0:
        for membership_list in preexisting_lists_in_downloads:
            os.remove(membership_list)
        print(f'Deleted {len(preexisting_lists_in_downloads)} pre-existing membership list(s) in '
              f'the Downloads folder.')
    else:
        print('There are no pre-existing membership lists in the Downloads folder to delete.')

    if len(preexisting_lists_in_box) > 0:
        for membership_list in preexisting_lists_in_box:
            os.remove(membership_list)
        print(f'Deleted {len(preexisting_lists_in_box)} pre-existing membership list(s) in Box.')
    else:
        print('There are no pre-existing membership lists in Box to delete.')


def upload_list_to_box(file_type):
    downloaded_lists = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH') + file_type)
    if len(downloaded_lists) > 0:
        for membership_list in downloaded_lists:
            shutil.move(membership_list, os.getenv('MEMBERSHIP_LIST_BOX_UPLOAD_PATH'))
        print('Membership list uploaded to Box.')
    else:
        quit_with_error('There is no membership list to upload to Box.')


def sign_in_to_clubspark():
    # Get login page
    driver.get('https://play.tennis.com.au/wheelershilltennisclub/Admin/Membership/members')
    # Enter service account email
    element = driver.find_element(By.ID, 'EmailAddress')
    element.send_keys(os.getenv('CS_SERVICE_ACCOUNT_EMAIL'))
    # Enter service account password
    element = driver.find_element(By.ID, 'Password')
    element.send_keys(os.getenv('CS_SERVICE_ACCOUNT_PASSWORD'))
    # Click sign in button
    driver.find_element(By.ID, 'signin-btn').click()
    time.sleep(5)
    print('Signed in to ClubSpark.')


def sign_out_of_clubspark():
    driver.get('https://play.tennis.com.au/wheelershilltennisclub/Account/SignOut')
    driver.quit()
    print('Signed out of ClubSpark.')


def extract_pdf_list():
    delete_preexisting_lists('.pdf')
    sign_in_to_clubspark()
    driver.find_element(By.CSS_SELECTOR, 'th.select-record > label:nth-child(1)').click()
    driver.find_element(By.CSS_SELECTOR, 'a.btn:nth-child(2)').click()
    driver.find_element(By.CSS_SELECTOR, '.btn-pdf').click()
    time.sleep(5)
    print('Downloaded PDF membership list.')
    sign_out_of_clubspark()
    upload_list_to_box('.pdf')
    print('ClubSpark membership list extract complete.')


def extract_csv_list(columns_to_delete_list):
    delete_preexisting_lists('.csv')
    sign_in_to_clubspark()
    driver.find_element(By.CSS_SELECTOR, 'th.select-record > label:nth-child(1)').click()
    driver.find_element(By.CSS_SELECTOR, 'a.btn:nth-child(2)').click()
    driver.find_element(By.CSS_SELECTOR, '.btn-csv').click()
    time.sleep(5)
    print('Downloaded CSV membership list.')
    sign_out_of_clubspark()
    delete_columns_in_csv(columns_to_delete_list)
    upload_list_to_box('.csv')
    print('ClubSpark membership list extract complete.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Membership List Extractor',
                                     description='Extracts membership list from ClubSpark, performs'
                                                 ' necessary formatting, then uploads file to cloud'
                                                 ' file storage.')
    parser.add_argument('-f', '--file-type', required=True, help='The file type of the extracted '
                                                                 'membership list. Accepted file '
                                                                 'types: pdf, csv.')
    parser.add_argument('-d', '--delete-columns', help='Comma separated list of columns in CSV to '
                                                       'be deleted.')
    args = parser.parse_args()
    argument_delimiter = ','
    columns_to_delete = args.delete_columns.split(argument_delimiter)

    print(get_bordered_string('ClubSpark membership list extractor'))

    if args.file_type == 'pdf':
        extract_pdf_list()
    elif args.file_type == 'csv':
        extract_csv_list(columns_to_delete)
