from blog.models import Game, Trade, Transaction
import csv
from django.contrib.auth.models import User

# ~~~INSERT blog_game SCRIPT~~~
# with open('zResources-ignore/Mar-19-12am-Sony.csv') as f:
#     admin = User.objects.filter(username='admin').first()
#     reader = csv.reader(f)
#     for row in reader:
#         _, created = Game.objects.get_or_create(
#             id=row[0],
#             name=row[1],
#             platform=row[2],
#             author=admin,
#         )


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
users = User.objects.all()
games = Game.objects.all()
num_non_matches = 420

userid = 1
owned_game_id = 4
desired_game_id = 5

while userid < 410:
    a = 0
    while a < 10:
        user = users.filter(id=userid).first()
        if user is None:
            userid += 1
            continue
        owned_game = games.filter(id=owned_game_id).first()
        desired_game = games.filter(id=desired_game_id).first()
        trade = Trade(user_who_posted = user, owned_game=owned_game, desired_game=desired_game)
        trade.save()
        owned_game_id += 1
        desired_game_id += 1
        a += 1
    userid += 1

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
