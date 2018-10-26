from django.contrib import admin

from game.models import Game, Player, Ship, Turn

admin.site.register(Game)
admin.site.register(Player)
admin.site.register(Ship)
admin.site.register(Turn)
