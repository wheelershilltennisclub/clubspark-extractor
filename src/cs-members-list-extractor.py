"""
Extracts membership list from ClubSpark, performs necessary formatting, then uploads file to cloud
file storage.
"""

import os
import sys
import time
import shutil
import glob
import argparse
import pandas as pd
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


def extract_list_from_clubspark(file_type, columns_to_delete_list=None):
    delete_preexisting_lists(file_type)
    print(get_divided_string('Extract List From ClubSpark'))
    sign_in_to_clubspark()
    download_list(file_type)
    sign_out_of_clubspark()
    if columns_to_delete_list is not None:
        delete_columns_in_csv(columns_to_delete_list)
    upload_list_to_box(file_type)
    print('\nClubSpark members list extract complete.')


def delete_preexisting_lists(file_type):
    print(get_divided_string('Delete Pre-existing Lists'))
    preexisting_lists_in_downloads = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH')
                                               + '.' + file_type)
    preexisting_lists_in_box = glob.glob(os.getenv('MEMBERSHIP_LIST_BOX_PATH') + '.' + file_type)

    if len(preexisting_lists_in_downloads) > 0:
        for membership_list in preexisting_lists_in_downloads:
            os.remove(membership_list)
        print(f'Deleted {len(preexisting_lists_in_downloads)} list(s) in the Downloads folder.')
    else:
        print('There are no lists in the Downloads folder to delete.')

    if len(preexisting_lists_in_box) > 0:
        for membership_list in preexisting_lists_in_box:
            os.remove(membership_list)
        print(f'Deleted {len(preexisting_lists_in_box)} list(s) in Box.')
    else:
        print('There are no lists in Box to delete.')


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
    time.sleep(3)
    print('Signed in to ClubSpark.')


def download_list(file_type):
    driver.find_element(By.CSS_SELECTOR, 'th.select-record > label:nth-child(1)').click()
    driver.find_element(By.CSS_SELECTOR, 'a.btn:nth-child(2)').click()
    driver.find_element(By.CSS_SELECTOR, '.btn-' + file_type).click()
    time.sleep(3)
    print('Downloaded list.')


def sign_out_of_clubspark():
    driver.get('https://play.tennis.com.au/wheelershilltennisclub/Account/SignOut')
    driver.quit()
    print('Signed out of ClubSpark.')


def delete_columns_in_csv(columns_to_delete_list):
    print(get_divided_string('Apply Formatting to CSV'))
    downloaded_list = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH') + '.csv')
    data = pd.read_csv(downloaded_list[0])
    for column in columns_to_delete_list:
        data.drop(column, inplace=True, axis=1)
        print(f'Deleted column \'{column}\'')
    data.to_csv(downloaded_list[0], index=False)


def upload_list_to_box(file_type):
    print(get_divided_string('Upload List to Box'))
    downloaded_lists = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH') + file_type)
    if len(downloaded_lists) > 0:
        for membership_list in downloaded_lists:
            shutil.move(membership_list, os.getenv('MEMBERSHIP_LIST_BOX_UPLOAD_PATH'))
        print('List uploaded to Box.')
    else:
        quit_with_error('There is no list to upload to Box.')


def quit_with_error(error_msg):
    print(f'Error: {error_msg}', file=sys.stderr)
    sys.exit(1)


def get_bordered_string(string, char='#'):
    border = char * (len(string) + 4)
    return f'{border}\n{char} {string} {char}\n{border}'


def get_divided_string(string, char='-'):
    divider = char * len(string)
    return f'\n{divider}\n{string}\n{divider}'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Membership List Extractor',
                                     description='Extracts membership list from ClubSpark, performs'
                                                 ' necessary formatting, then uploads file to cloud'
                                                 ' file storage.')
    parser.add_argument('-f', '--file-type', required=True, help='The file type of the extracted '
                                                                 'membership list. Accepted file '
                                                                 'types: pdf, csv.')
    parser.add_argument('-d', '--delete-columns', default=None, help='Comma separated list of'
                                                                     ' columns in CSV to be'
                                                                     ' deleted.')
    args = parser.parse_args()
    delimiter = ','

    print(get_bordered_string('CLUBSPARK MEMBERS LIST EXTRACTOR', ))

    if args.file_type == 'pdf':
        print(get_divided_string('Extract Settings'))
        print('File type: PDF')
        extract_list_from_clubspark('pdf')
    elif args.file_type == 'csv':
        print(get_divided_string('Extract Settings'))
        print('File type: CSV')
        if args.delete_columns is not None:
            columns_to_delete = args.delete_columns.split(delimiter)
            print(f'Columns to delete: {columns_to_delete}')
            extract_list_from_clubspark('csv', columns_to_delete)
        else:
            extract_list_from_clubspark('csv')
    else:
        quit_with_error('Please specify a valid file type. Accepted file types: pdf, csv.')
