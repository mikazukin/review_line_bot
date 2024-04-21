from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuArea,
    RichMenuBounds,
    RichMenuRequest,
    RichMenuSize,
    RichMenuSwitchAction,
    ReplyMessageRequest,
    TextMessage,
    URIAction,
    PushMessageRequest
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

import json

app = Flask(__name__)

configuration = Configuration(access_token='f3+CiVamf26s1PRr03BznTat92Zts5wmMaefVKOYxrokkhJhUTwttOfJGxo5fK66kQ308F/exKnmIWnbCrxNvb2G2ZyqHP/FZvrEdlVg9TC5KiOOKqKgEYmlYqJhUhAhfmksPDq03sJPQMJx6xzTZQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('05f7ff3dcb80c0da2d6f2acda1ab5357')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@app.route("/push", methods=['POST'])
def push():
    message = '{\"to\":\"U513aa0cadc2c150bc56fe5f347261264",\"messages\":[{\"type\":\"text\",\"text\":\"\"}]}'
    message_dict = json.loads(message)
    # 送りたいメッセージを記載する.今回はHello World!
    message_dict['messages'][0]['text'] = "Hello World!"

    # Enter a context with an instance of the API client
    with ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = MessagingApi(api_client)
        push_message_request = PushMessageRequest.from_dict(message_dict) # PushMessageRequest | 

        try:
            api_response = api_instance.push_message(push_message_request)
            # print("The response of MessagingApi->push_message:\n")
        except Exception as e:
            print("Exception when calling MessagingApi->push_message: %s\n" % e)
        return 'OK'
    

def rich_menu_object_a_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "richmenu-a",
        "chatBarText": "Tap to open",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 1666,
                    "height": 1686
                },
                "action": {
                    "type": "uri",
                    "label": "メインストーリー",
                    "uri": "https://developers.line.biz/ja/news/"
                }
            },
            {
                "bounds": {
                    "x": 1667,
                    "y": 0,
                    "width": 834,
                    "height": 843
                },
                "action": {
                    "type": "uri",
                    "label": "サブ",
                    "uri": "https://lineapiusecase.com/ja/top.html"
                }
            },
            {
                "bounds": {
                    "x": 1667,
                    "y": 844,
                    "width": 834,
                    "height": 843
                },
                "action": {
                    "type": "uri",
                    "label": "遊び方",
                    "uri": "https://techblog.lycorp.co.jp/ja/"
                }
            }
        ]
    }

def create_action(action):
    if action['type'] == 'uri':
        return URIAction(uri=action.get('uri'))
    else:
        return RichMenuSwitchAction(
            rich_menu_alias_id=action.get('richMenuAliasId'),
            data=action.get('data')
        )
    
@app.route("/create_rich_menu", methods=['POST'])
def create_rich_menu():
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_blob_api = MessagingApiBlob(api_client)

        # 2. Create rich menu A (richmenu-a)
        rich_menu_object_a = rich_menu_object_a_json()
        areas = [
            RichMenuArea(
                bounds=RichMenuBounds(
                    x=info['bounds']['x'],
                    y=info['bounds']['y'],
                    width=info['bounds']['width'],
                    height=info['bounds']['height']
                ),
                action=create_action(info['action'])
            ) for info in rich_menu_object_a['areas']
        ]

        rich_menu_to_a_create = RichMenuRequest(
            size=RichMenuSize(width=rich_menu_object_a['size']['width'],
                              height=rich_menu_object_a['size']['height']),
            selected=rich_menu_object_a['selected'],
            name=rich_menu_object_a['name'],
            chat_bar_text=rich_menu_object_a['name'],
            areas=areas
        )

        rich_menu_a_id = line_bot_api.create_rich_menu(
            rich_menu_request=rich_menu_to_a_create
        ).rich_menu_id

        # 3. Upload image to rich menu A
        with open('./public/richmenu_1713681707553.jpg', 'rb') as image:
            line_bot_blob_api.set_rich_menu_image(
                rich_menu_id=rich_menu_a_id,
                body=bytearray(image.read()),
                _headers={'Content-Type': 'image/jpeg'}
            )

        line_bot_api.set_default_rich_menu(rich_menu_id=rich_menu_a_id)
        return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )

if __name__ == "__main__":
    app.run(port=8080)
