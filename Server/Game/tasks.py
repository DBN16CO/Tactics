from __future__ import absolute_import

from celery import shared_task
import celery
import datetime
import random
from Game.models import Game, Game_Queue, Game_User
from Static.models import Version

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=5))
def processMatchmakingQueue():

    # Get the matchmaking queue
    queue = Game_Queue.objects.filter()

    # Get the latest version to use for creating games
    version = Version.objects.filter(name=version).first()

    # If there isn't at least 2 players in the queue then exit
    if len(queue) < 2:
        return

    # Take the first player of the queue
    first_player = queue[0]

    # Randomly choose a second player from the remaining players on the queue
    index = random.randint(1, len(queue) - 1)
    second_player = queue[index]

    player_turn_index = random.randint(1, 2)

    # Randomly choose which player will start first
    player_turn = None
    if player_turn_index == 1:
        player_turn = first_player.user
    elif player_turn_index == 2:
        player_turn = second_player.user

    # Create the game
    game = Game(user_turn=player_turn, version=version)
    game.save()

    # Link the game to the first player's game entry
    game_user1 = Game_User.objects.filter(user=first_player.user, game=None).first()
    game_user1.game = game
    game_user1.save()

    # Link the game to the second player's game entry
    game_user2 = Game_User.objects.filter(user=second_player.user, game=None).first()
    game_user2.game = game
    game_user2.save()

    # Delete the first player from the queue
    first_player.delete()

    # Delete the second player from the queue
    second_player.delete()