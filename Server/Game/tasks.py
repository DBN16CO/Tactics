from __future__ import absolute_import

import celery
import datetime
import random
from Game.models import Game, Game_Queue, Game_User, Unit
from Static.models import Version, Map
import logging
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
fh = logging.FileHandler('./matchmaking.log', mode='a')
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=5))
def processMatchmakingQueue():

    logger.debug("Processing matchmaking queue")

    # Get the matchmaking queue
    queue = Game_Queue.objects.filter()

    # Get the latest version to use for creating games
    version = Version.objects.latest('pk')

    # If there isn't at least 2 players in the queue then exit
    if len(queue) < 2:
        logger.debug("Not enough people in the queue to match...Exiting")
        return

    # Take the first player of the queue
    first_player = queue[0]

    # Randomly choose a second player from the remaining players on the queue
    index = random.randint(1, len(queue) - 1)
    second_player = queue[index]

    logger.info("Found a match: " + str(first_player.user.username) + " vs. " + str(second_player.user.username))

    # Determine the number of times these 2 players have played against each other
    count = 0
    for first_player_game_user in Game_User.objects.filter(user=first_player.user):
        game_played = first_player_game_user.game

        if not game_played:
            continue

        is_second_player_in_game = Game_User.objects.filter(user=second_player.user, game=game_played).first()

        if is_second_player_in_game:
            count += 1

    logger.info("Users have played each other " + str(count) + " times.")

    # Randomly choose which player will start first
    player_turn_index = random.randint(1, 2)
    player_turn = None
    if player_turn_index == 1:
        logger.info(str(first_player.user.username) + " will take the first turn")
        player_turn = first_player.user
    elif player_turn_index == 2:
        logger.info(str(second_player.user.username) + " will take the first turn")
        player_turn = second_player.user

    maps = Map.objects

    # Randomly choose a map for the game
    index = random.randint(0, maps.count() - 1)
    game_map = maps.filter()[index]

    logger.info("Map chosen for this game: " + str(game_map))

    # Create the game
    game = Game(user_turn=player_turn, version=version, map_path=game_map)
    game.save()

    logger.info("Created the game: " + str(game))

    game_users = Game_User.objects

    logger.debug("Updating game_user entries")

    # Link the game to the first player's game entry
    game_user1 = game_users.filter(user=first_player.user, game=None).first()
    game_user1.game = game
    game_user1.name = "vs. " + str(second_player.user.username) + " #" + str(count + 1)
    game_user1.save()

    # Link the game to the second player's game entry
    game_user2 = game_users.filter(user=second_player.user, game=None).first()
    game_user2.game = game
    game_user2.name = "vs. " + str(first_player.user.username) + " #" + str(count + 1)
    game_user2.save()

    logging.debug("Updating each player's unit entries")

    # Update each player's units
    for unit in Unit.objects.filter(owner=first_player.user, game=None):
        unit.game = game
        unit.save()

    for unit in Unit.objects.filter(owner=second_player.user, game=None):
        unit.game = game
        unit.save()

    logger.debug("Deleting players from the queue")

    # Delete the first player from the queue
    first_player.delete()

    # Delete the second player from the queue
    second_player.delete()