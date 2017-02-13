from __future__ import absolute_import

import os
import celery
import datetime
import random
from Game.models import Game, Game_Queue, Game_User, Unit
from Static.models import Version, Map
from Static.log_uploader import upload_logs
import logging
from Server import config
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
fh = logging.FileHandler('./matchmaking.log', mode='a')
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

@celery.decorators.periodic_task(run_every=datetime.timedelta(days=1))
def uploadServerLogs():
    """
    Celery task to upload the trace and matchmaking logs to Google drive once a day
    """
    try:
        logger.info("Uploading trace and matchmaking logs to Google Drive...")
        upload_logs()
        logger.info("Successfully uploaded trace and matchmaking logs to Google Drive...")
        logger.info("Deleting local log files")
        basepath = os.path.dirname(__file__)
        filepath = os.path.abspath(os.path.join(basepath, "..", "trace.log"))
        os.remove(filepath)
        filepath = os.path.abspath(os.path.join(basepath, "..", "matchmaking.log"))
        os.remove(filepath)
        logger.info("Finished deleting local log files")
    except Exception as e:
        logger.exception(e)

@celery.decorators.periodic_task(run_every=datetime.timedelta(seconds=config.GAME_QUEUE_PROCESS_INTERVAL))
def processMatchmakingQueue():
    """
    This is the entry point for the matchmaking logic. Celery workers will periodically execute
    this logic and match players that were placed in the game queue. All the data needed to setup a game
    will happen here.

    The logging output for the matchmaking logic will be stored in matchmaking.log
    """
    try:
        logger.debug("Processing matchmaking queue")

        # Get the matchmaking queue
        queue = Game_Queue.objects.filter()

        # Get the latest version to use for creating games
        version = Version.objects.latest('pk')

        # If there aren't at least 2 players in the queue then exit
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
        for first_player_game_user in Game_User.objects.filter(user=first_player.user).exclude(game=None):
            game_played = first_player_game_user.game

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

        maps = Map.objects.filter()

        # Randomly choose a map for the game
        index = random.randint(0, maps.count() - 1)
        game_map = maps.filter()[index]

        logger.info("Map chosen for this game: " + str(game_map))

        # Create the game
        game = Game(user_turn=player_turn, version=version, map_path=game_map)
        game.save()

        logger.info("Created game id: " + str(game.id))

        game_users = Game_User.objects

        logger.debug("Updating game_user entries")

        # Link the game to the first player's game entry
        game_user1 = game_users.filter(user=first_player.user, game=None).first()
        game_user1.game = game
        game_user1.name = "vs. " + str(second_player.user.username) + " #" + str(count + 1)
        game_user1.team = 1
        game_user1.save()

        # Link the game to the second player's game entry
        game_user2 = game_users.filter(user=second_player.user, game=None).first()
        game_user2.game = game
        game_user2.name = "vs. " + str(first_player.user.username) + " #" + str(count + 1)
        game_user2.team = 2
        game_user2.save()

        logging.debug("Updating each player's unit entries")

        # Update each player's units
        for unit in Unit.objects.filter(owner__in=[first_player.user, second_player.user], game=None):
            unit.game = game
            unit.save()

        logger.debug("Deleting players from the queue")

        # Delete the first player from the queue
        first_player.delete()

        # Delete the second player from the queue
        second_player.delete()
    except Exception, e:
        logger.error("Exception in the matchmaking logic")
        logger.exception(e)