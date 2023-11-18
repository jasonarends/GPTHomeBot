from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
slack_api_key = os.getenv('SLACK_API_KEY')
# ... and so on
