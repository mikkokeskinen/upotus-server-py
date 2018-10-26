from django.utils.translation import pgettext_lazy
from enumfields import Enum


class ShipType(Enum):
    CARRIER = 'carrier'
    BATTLESHIP = 'battleship'
    DESTROYER = 'destroyer'
    SUBMARINE = 'submarine'
    PATROL_BOAT = 'patrol_boat'

    class Labels:
        CARRIER = pgettext_lazy('Ship type', 'Carrier')
        BATTLESHIP = pgettext_lazy('Ship type', 'Battleship')
        DESTROYER = pgettext_lazy('Ship type', 'Destroyer')
        SUBMARINE = pgettext_lazy('Ship type', 'Submarine')
        PATROL_BOAT = pgettext_lazy('Ship type', 'Patrol Boat')


class Orientation(Enum):
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

    class Labels:
        HORIZONTAL = pgettext_lazy('Orientation', 'Horizontal')
        VERTICAL = pgettext_lazy('Orientation', 'Vertical')
