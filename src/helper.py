import os
import sys
import time
import shutil
import glob
import pandas as pd
from box_api import client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from constants import *


def setup_driver():
    """
    This function returns a Firefox selenium webdriver in headless mode
    """
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    return driver


def extract_list_from_clubspark(driver, list_type, file_type, upload_location,
                                columns_to_delete_list=None):
    delete_preexisting_lists(file_type)
    print(get_divided_string('Extract List From ClubSpark'))
    sign_in_to_clubspark(driver)
    download_list(driver, list_type, file_type)
    sign_out_of_clubspark(driver)
    apply_formatting_to_csv(columns_to_delete_list)
    list_file_name = rename_list(list_type, file_type)
    if upload_location == 'box':
        upload_list_to_box(file_type)
    else:
        # implement upload to google drive function
        pass
    print('\nClubSpark members list extract complete.')


def delete_preexisting_lists(file_type):
    print(get_divided_string('Delete Pre-existing Lists'))
    preexisting_lists_in_downloads = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH')
                                               + '.' + file_type)
    if len(preexisting_lists_in_downloads) > 0:
        for membership_list in preexisting_lists_in_downloads:
            os.remove(membership_list)
        print(f'Deleted {len(preexisting_lists_in_downloads)} list(s) in the Downloads folder.')
    else:
        print('There are no lists in the Downloads folder to delete.')


def sign_in_to_clubspark(driver):
    # Get login page
    driver.get(CLUBPSPARK_SIGN_IN_URL)
    # Enter service account email
    element = driver.find_element(By.ID, 'EmailAddress')
    element.send_keys(CLUBSPARK_SERVICE_ACCOUNT_EMAIL)
    # Enter service account password
    element = driver.find_element(By.ID, 'Password')
    element.send_keys(CLUBSPARK_SERVICE_ACCOUNT_PASSWORD)
    # Click sign in button
    driver.find_element(By.ID, 'signin-btn').click()
    time.sleep(3)
    print('Signed in to ClubSpark.')


def download_list(driver, list_type, file_type):
    if list_type == 'all members':
        driver.find_element(By.CSS_SELECTOR, 'th.select-record > label:nth-child(1)').click()
        driver.find_element(By.CSS_SELECTOR, 'a.btn:nth-child(2)').click()
        driver.find_element(By.CSS_SELECTOR, '.btn-' + file_type).click()
        time.sleep(3)
        print('Downloaded all members list.')
    else:
        # implement download of unpaid members list functionality
        pass


def sign_out_of_clubspark(driver):
    driver.get(CLUBSPARK_SIGN_OUT_URL)
    driver.quit()
    print('Signed out of ClubSpark.')


def apply_formatting_to_csv(columns_to_delete_list=None):
    print(get_divided_string('Apply Formatting to CSV'))
    downloaded_list = glob.glob(LIST_DOWNLOAD_PATH + '.csv')
    data = pd.read_csv(downloaded_list[0])
    data.rename(columns={'Venue ID': 'Access key number'}, inplace=True)
    print(f'Renamed column \'Venue ID\' to \'Access key number\'')
    if columns_to_delete_list is not None:
        for column in columns_to_delete_list:
            data.drop(column, inplace=True, axis=1)
            print(f'Deleted column \'{column}\'')
    data.to_csv(downloaded_list[0], index=False)


def rename_list(list_type, file_type):
    print(get_divided_string('Renaming List File'))
    downloaded_list = glob.glob(f'{LIST_DOWNLOAD_PATH}.{file_type}')
    new_file_name = f'Wheelers-Hill-Tennis-Club-{list_type}.{file_type}'
    os.rename(downloaded_list[0], new_file_name)
    print(f'Renamed {downloaded_list[0]} to {new_file_name}')
    return new_file_name


def upload_list_to_box(file_type):
    print(get_divided_string('Upload List to Box'))
    downloaded_lists = glob.glob(os.getenv('MEMBERSHIP_LIST_DOWNLOADS_PATH') + file_type)
    if len(downloaded_lists) > 0:
        for membership_list in downloaded_lists:
            shutil.move(membership_list, os.getenv('MEMBERSHIP_LIST_BOX_UPLOAD_PATH'))
        print('List uploaded to Box.')
    else:
        quit_with_error('There is no list to upload to Box.')


def upload_list_to_google_drive():
    pass


def quit_with_error(error_msg):
    print(f'Error: {error_msg}', file=sys.stderr)
    sys.exit(1)


def get_bordered_string(string, char='#'):
    border = char * (len(string) + 4)
    return f'{border}\n{char} {string} {char}\n{border}'


def get_divided_string(string, char='-'):
    divider = char * len(string)
    return f'\n{divider}\n{string}\n{divider}'
