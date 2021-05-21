# chat/views.py
from django.shortcuts import render
import json
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

def index(request):
    return render(request, 'chat/index.html')


# @login_required
# def room(request, room_name): # OLD: Front end WORKING (Mar 22, 6pm) but did not send to websocket
#     print('~~~DEBUG~~~')
#     return render(request, 'chat/room.html', {
#         'room_name': room_name
#         #'room_name_json': room_name
#         # 'room_name_json': mark_safe(json.dumps(room_name)),
#         # 'username': mark_safe(json.dumps(request.user.username)),
#     })


@login_required
def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name)),
        'user': mark_safe(json.dumps(request.user.username))
    })