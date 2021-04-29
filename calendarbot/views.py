from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

from .database import Process_Query
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if request.META['HTTP_HOST'].split('.')[1] == 'herokuapp':
        dev_mode = False
    else:
        dev_mode = True
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:

            # For Dev Using
            if event.source.user_id in ['Uf7fc5548d27146e9ee5f4e39f3f557b5'] and dev_mode:
                reply = dev(event, dev_mode)
                return HttpResponse()

            # For General Using
            if isinstance(event, MessageEvent):
                query = event.message.text
                _id   = event.source.user_id
                try:
                    reply_message = Process_Query(_id, query, dev_mode)
                except:
                    reply_message = '無法完成你的請求，請聯絡8ma'

                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_message)
                )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def dev(event, dev_mode):
    if isinstance(event, MessageEvent):
        # Test_Database()

        query = event.message.text
        _id   = event.source.user_id
        try:
            reply_message = Process_Query(_id, query, dev_mode)
        except:
            reply_message = '無法完成你的請求，請聯絡8ma'

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message))
    return