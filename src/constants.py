import os
import keyring
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# ClubSpark Constants
CLUBSPARK_SERVICE_ACCOUNT_EMAIL = os.environ.get('CLUBSPARK_SERVICE_ACCOUNT_EMAIL')
CLUBSPARK_SERVICE_ACCOUNT_PASSWORD = keyring.get_password('ClubSpark Extractor - ClubSpark SA',
                                                          CLUBSPARK_SERVICE_ACCOUNT_EMAIL)
CLUBPSPARK_SIGN_IN_URL = \
    'https://play.tennis.com.au/wheelershilltennisclub/Admin/Membership/members'
CLUBSPARK_SIGN_OUT_URL = 'https://play.tennis.com.au/wheelershilltennisclub/Account/SignOut'

# Box Constants
BOX_CLIENT_ID = keyring.get_password('ClubSpark Extractor - Box Client ID', 'Box Client ID')
BOX_APP_TOKEN_PRIMARY = keyring.get_password('ClubSpark Extractor - Box App Token Primary',
                                             'Box App Token Primary')
BOX_ALL_MEMBERS_FOLDER_ID = '199099109731'
BOX_UNPAID_MEMBERS_FOLDER_ID = '199098777969'

# Google Drive Constants

# File System Path Constants
LIST_DOWNLOAD_PATH = os.environ.get('LIST_DOWNLOAD_PATH')
DOWNLOADS_FOLDER_PATH = os.environ.get('DOWNLOADS_FOLDER_PATH')
