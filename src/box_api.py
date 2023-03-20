from constants import BOX_CLIENT_ID, BOX_APP_TOKEN_PRIMARY
from boxsdk import Client, OAuth2

auth = OAuth2(
  client_id=BOX_CLIENT_ID,
  client_secret='',
  access_token=BOX_APP_TOKEN_PRIMARY
)
client = Client(auth)