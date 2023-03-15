"""
Config file for access to BOX API to upload/delete files.
"""

import os

from boxsdk import Client, OAuth2

auth = OAuth2(access_token=os.getenv('BOX_APP_TOKEN'))
client = Client(auth)
