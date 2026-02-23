from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from dotenv import load_dotenv
import os

load_dotenv()

FacebookAdsApi.init(
    app_id=os.getenv("FACEBOOK_APP_ID"),
    app_secret=os.getenv("FACEBOOK_APP_SECRET"),
    access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
)

account = AdAccount(os.getenv("FACEBOOK_AD_ACCOUNT_ID"))
