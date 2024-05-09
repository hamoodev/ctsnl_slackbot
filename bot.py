import os
import schedule
import time
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import tempfile
from datetime import datetime
import chevron
from cairosvg import svg2png
logging.basicConfig(level=logging.DEBUG)



def prepare_message():
    with open("./template/jumping-bean-meetup-poster.svg", "r") as reader:
        template = reader.read()
        
    with tempfile.NamedTemporaryFile(suffix=".svg") as fp:
        #   { year = "2023", date = "August 10th", time = "7pm" },
        
        data = {}
        data['year'] = datetime.now().year
        data['date'] = datetime.now().strftime("%B %-dth")
        data['time'] = "7pm"
        
        rendered = chevron.render(template=template, data=data)

        fp.write(rendered.encode("utf-8"))
        
      
        
        png_file = svg2png(rendered, write_to="/tmp/image.png")
        
        return "/tmp/image.png"

def sendMessage(slack_client, msg, image_path=None):
    image_path = prepare_message()
    try:
        if image_path:
            slack_client.files_upload(
                channels='#general',
                initial_comment=msg,
                file=image_path
            )
        else:
            slack_client.chat_postMessage(
                channel='#general',
                text=msg
            )
        logging.debug("Message sent successfully")
    except SlackApiError as e:
        logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
        logging.error(e.response)



if __name__ == "__main__":
    SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
    slack_client = WebClient(SLACK_BOT_TOKEN)
    logging.debug("authorized slack client")

    # Prepare Message
    
    msg = ":coffee:"

    # schedule.every(60).seconds.do(lambda: sendMessage(slack_client, msg))

    schedule.every().thursday.at("10:00").do(lambda: sendMessage(slack_client, msg))
    
    logging.info("entering loop")

    while True:
        schedule.run_pending()
        time.sleep(5) 