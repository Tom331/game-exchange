from blog.models import Game, Trade, Transaction
import csv
from django.utils import timezone

# from .users.models import MyUser

from django.contrib.auth import get_user_model
User = get_user_model()
# from django.conf import settings
# User = settings.AUTH_USER_MODEL

# command to run in manage.py shell - ENSURE CORRECT DATABASE IS SET IN 'PRINTENV':
#   exec(open('tempScript.py').read())


# ~~~INSERT blog_game SCRIPT~~~
with open('zResources-ignore/Game_Datasets/IGDB/Mar31-May1/csv/Mar31-May1.csv') as f:
    admin = User.objects.filter(username='admin').first()
    reader = csv.reader(f)
    i = 0
    for row in reader:
        _, created = Game.objects.get_or_create(
            id=row[0],
            name=row[1],
            platform=row[2],
            author=admin,
        )
        i = i+1
        if (i % 20) == 0:
            print(str(i) + ' rows done out of 236...')


# ~~~Data Update Script~~~
# users = User.objects.filter(key_expires != None)
# for user in users:
#     user.key_expires = timezone.now


# ~~~LOCATION TESTING~~~ https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
# import mpu
# from math import sin, cos, sqrt, atan2, radians
# from django.db import connection
#
# from django.contrib.auth import get_user_model
# MyUser = get_user_model()
#
# R = 6373.0 # approximate radius of earth in km
# myLat = radians(49.261236)
# myLong = radians(-122.784858)
# parentsLat = radians(49.238683)
# parentsLong = radians(-122.561352)
#
# dlat = myLat - parentsLat
# dlon = myLong - parentsLong
#
# a = (sin(dlat / 2)**2 + cos(myLat) * cos(parentsLat) * sin(dlon / 2)**2)
# c = (2 * atan2(sqrt((sin(dlat / 2)**2 + cos(myLat) * cos(parentsLat) * sin(dlon / 2)**2)),
#               sqrt(1 - (sin(dlat / 2)**2 + cos(myLat) * cos(parentsLat) * sin(dlon / 2)**2))))
#
# distance = (6373.0 * (2 * atan2(sqrt((sin(dlat / 2)**2 + cos(myLat) * cos(parentsLat) * sin(dlon / 2)**2)),
#               sqrt(1 - (sin(dlat / 2)**2 + cos(myLat) * cos(parentsLat) * sin(dlon / 2)**2)))))
# dist = mpu.haversine_distance((myLat, myLong), (parentsLat, parentsLong))
#
# admin_id = 3
# current_user = MyUser.objects.get(id=admin_id)
#
# # dlat = (current_user.lat - u1.lat)
# # dlon = (current_user.long - u1.long)
#
# print('Expected: about 16.36km; Actual: ' + str(distance))
#
# trades = Trade.objects.raw('SELECT DISTINCT t1.id AS id, '
#                            't2.id AS t2_id, '
#                            't2.name AS t2_name, '
#                            't1.owned_game as t1_owned_game, '
#                            't1.desired_game as t1_desired_game, '
#                            't2.user_who_posted_id as t2_user_who_posted_id, '
#                            't2.created_date as t2_created_date, '
#                            'u1.username as t2_username, '
#                            'u1.lat as t2_lat, '
#                            'u1.long as t2_long, '
#                            'u1.travel_radius as t2_travel_radius '
#                            'FROM blog_Trade t1, blog_Trade t2, users_myuser u1 '
#                            'WHERE t1.owned_game = t2.desired_game '
#                            'AND t1.desired_game = t2.owned_game '
#                            'AND t1.user_who_posted_id = %s '
#                            'AND t1.is_trade_proposed = false '
#                            'AND t2.is_trade_proposed = false '
#                            'AND u1.id = t2.user_who_posted_id '
#
#                            """
#                            AND (6373.0 * (2 * atan2(sqrt((POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
#                            * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2))),sqrt(1 - (POWER(sin((%s - RADIANS(u1.lat)) / 2), 2) + cos(%s)
#                            * cos(RADIANS(u1.lat)) * POWER(sin((%s - RADIANS(u1.long)) / 2), 2)))))) < ( %s + u1.travel_radius )
#                             """,
#                            [current_user.id, radians(current_user.lat), radians(current_user.lat), radians(current_user.long),
#                              radians(current_user.lat), radians(current_user.lat), radians(current_user.long),
#                             current_user.travel_radius])
#
# for trade in trades:
#     print('trade: ' + str(trade))
# print(trades.query)



# ~~~INSERT auth_user SCRIPT~~~
# i = 18
# while i < 500:
#     username = 'user' + str(i)
#     user = User(username=username)
#     user.save()
#     i+=1


# ~~~INSERT n matches into blog_trade ~~~
# users = User.objects.all()
# games = Game.objects.all()
#
# num_matches = 30
# userid = 1
#
# owned_game_id = 1
# desired_game_id = 2
#
# a = 0
# while a < num_matches:
#     user = users.filter(id=userid).first()
#     if user is None:
#         userid += 1
#         continue
#     owned_game = games.filter(id=owned_game_id).first()
#     desired_game = games.filter(id=desired_game_id).first()
#     trade = Trade(user_who_posted = user, owned_game=owned_game, desired_game=desired_game)
#     trade.save()
#     owned_game_id += 1
#     desired_game_id += 1
#     userid += 1
#     a += 1
# ~~~~~~


# ~~~INSERT n NON matches into blog_trade
# users = User.objects.all()
# games = Game.objects.all()
# num_non_matches = 420
#
# userid = 1
# owned_game_id = 4
# desired_game_id = 5
#
# while userid < 410:
#     a = 0
#     while a < 10:
#         user = users.filter(id=userid).first()
#         if user is None:
#             userid += 1
#             continue
#         owned_game = games.filter(id=owned_game_id).first()
#         desired_game = games.filter(id=desired_game_id).first()
#         trade = Trade(user_who_posted = user, owned_game=owned_game, desired_game=desired_game)
#         trade.save()
#         owned_game_id += 1
#         desired_game_id += 1
#         a += 1
#     userid += 1

# ~~~INSERT n_NON_matches into blog_trade
# while userid < 420:
#     print('userid: ' + str(userid))
#     a = 0
#     while a < 10:
#         user = users.filter(id=userid).first()
#         if user is None: #
#             userid += 1
#             continue
#         owned_game = games.filter(id=owned_game_id).first()
#         desired_game = games.filter(id=desired_game_id).first()
#         print('owned_game_id: ' + str(owned_game_id) + '; desired_game: ' + str(desired_game_id))
#         trade = Trade(user_who_posted = user, owned_game=owned_game, desired_game=desired_game)
#         owned_game_id += 1
#         desired_game_id += 1
#         a += 1
#     userid += 1
#     print('done user: ' + str((userid-1)) + '... starting user: ' + str(userid))


# ~~~INSERT n_NON_matches into blog_trade FOR A SINGLE USER
# a = 17307 # loaded series x from csv and lowest id was this
# b = 17499 # loaded series x from csv and highest id was this
# count = 0
# admin = User.objects.filter(username='admin').first()
# while count < 28:
#     owned_game = Game.objects.filter(id=a).first()
#     if owned_game is None:
#         print('didnt find owned_game: ' + str(a))
#         a += 1
#         continue
#
#     desired_game = Game.objects.filter(id=b).first()
#     if desired_game is None:
#         print('didnt find desired_game: ' + str(b))
#         b -= 1
#         continue
#     trade = Trade(user_who_posted = admin, owned_game=owned_game, desired_game=desired_game)
#     trade.save()
#     count +=1
#     a += 1
#     b -= 1
