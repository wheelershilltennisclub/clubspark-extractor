import sys
import time
import glob
import string
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
    time.sleep(3)
    download_list(driver, list_type, file_type)
    sign_out_of_clubspark(driver)
    apply_formatting_to_csv(columns_to_delete_list)
    list_file_name = rename_list(list_type, file_type)
    if upload_location == 'box':
        upload_list_to_box(list_file_name, list_type, file_type)
    else:
        # implement upload to google drive function
        pass
    print('\nClubSpark extract complete.')


def delete_preexisting_lists(file_type):
    print(get_divided_string('Delete Pre-existing Lists'))
    preexisting_lists_in_downloads = glob.glob(os.getenv('LIST_DOWNLOAD_PATH') + '.' + file_type)
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
        driver.find_element(By.CSS_SELECTOR, '#member').click()
    elif list_type == 'unpaid members':
        driver.find_element(By.CSS_SELECTOR, '#membernotpaid').click()
    elif list_type == 'paid members':
        driver.find_element(By.CSS_SELECTOR, '#memberpaid').click()
    else:
        quit_with_error('Invalid list type.')
    driver.find_element(By.CSS_SELECTOR, 'th.select-record > label:nth-child(1)').click()
    driver.find_element(By.CSS_SELECTOR, 'a.btn:nth-child(2)').click()
    driver.find_element(By.CSS_SELECTOR, '.btn-' + file_type).click()
    time.sleep(3)
    print(f'Downloaded {list_type} list.')


def sign_out_of_clubspark(driver):
    driver.get(CLUBSPARK_SIGN_OUT_URL)
    driver.quit()
    print('Signed out of ClubSpark.')


def apply_formatting_to_csv(columns_to_delete_list=None):
    print(get_divided_string('Apply Formatting to CSV'))
    downloaded_list = glob.glob(LIST_DOWNLOAD_PATH + '.csv')
    data = pd.read_csv(downloaded_list[0])
    data.rename(columns={'Venue ID': 'Access key ID'}, inplace=True)
    print(f'Renamed column \'Venue ID\' to \'Access key ID\'')
    if columns_to_delete_list is not None:
        for column in columns_to_delete_list:
            data.drop(column, inplace=True, axis=1)
            print(f'Deleted column \'{column}\'')
    data.to_csv(downloaded_list[0], index=False)


def rename_list(list_type, file_type):
    print(get_divided_string('Renaming List File'))
    downloaded_list = glob.glob(f'{LIST_DOWNLOAD_PATH}.{file_type}')
    new_file_name = f'{DOWNLOADS_FOLDER_PATH}\\Wheelers-Hill-Tennis-Club-Members-' \
                    f'{string.capwords(list_type.split(" ", 1)[0])}.{file_type}'
    os.rename(downloaded_list[0], new_file_name)
    print(f'Renamed {downloaded_list[0]} to {new_file_name}')
    return new_file_name


def upload_list_to_box(file_name, list_type, file_type):
    print(get_divided_string('Upload List to Box'))
    folder_id = ''
    if list_type == 'all members':
        folder_id = BOX_ALL_MEMBERS_FOLDER_ID
    elif list_type == 'unpaid members':
        folder_id = BOX_UNPAID_MEMBERS_FOLDER_ID
    elif list_type == 'paid members':
        folder_id = BOX_PAID_MEMBERS_FOLDER_ID
    else:
        quit_with_error('Invalid list type')

    try:
        new_file = client.folder(folder_id).upload(file_name)
        print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')
    except Exception as e:
        print(f'File already exists in box, uploading a new version instead.\n{e}')
        items = client.folder(folder_id).get_items()
        file_name_relative = file_name.removeprefix(f'{DOWNLOADS_FOLDER_PATH}\\')
        file_id = ''
        for item in items:
            if item.name == file_name_relative:
                file_id = item.id
        updated_file = client.file(file_id).update_contents(file_name)
        print(f'File "{updated_file.name}" has been updated in Box.')


def upload_list_to_google_drive():
    pass


def quit_with_error(error_msg):
    print(f'Error: {error_msg}', file=sys.stderr)
    sys.exit(1)


def get_bordered_string(input_string, char='#'):
    border = char * (len(input_string) + 4)
    return f'{border}\n{char} {input_string} {char}\n{border}'


def get_divided_string(input_string, char='-'):
    divider = char * len(input_string)
    return f'\n{divider}\n{input_string}\n{divider}'
