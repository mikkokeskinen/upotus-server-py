import pytest


@pytest.mark.django_db
def test_player_are_ships_placed(django_user_model, create_game, create_player):
    user1= django_user_model.objects.create_user(
        username='test1', password='test1')
    game = create_game()
    player1 = create_player(
        game=game,
        user=user1,
    )

    assert player1.are_ships_placed() is False
