from __future__ import annotations
import spongedb
from spongelog import SpongeLog
from itemclass import Item
from datetime import datetime as dt
from time import strftime

class Player:

    def __init__(self, username: str):
        # get remaining str after last /
        # functionally removes /u/
        username = username.split('/')[-1]

        db = spongedb.SpongeDB()
        db_entry = db.get_player(username)
        db.close()

        self._name = db_entry['username']
        self._suds = db_entry['suds']
        #self._bonus = db_entry['bonus']
        #self._penalty = db_entry['penalty']
        self._inventory = []
        if db_entry['inventory']:
            self._inventory = [Item(int(x)) for x in db_entry['inventory'].split(',')]
        self._score = db_entry['score_7d'] if db_entry['score_7d'] else 0
        self._score = db_entry['score_7d']
        self._dailysuds = db_entry['dailysuds']
        self._safemode = db_entry['safemode']
        self._safemode_timer = db_entry['safemode_timer']

    @property
    def name(self) -> str:
        return self._name

    @property
    def suds(self) -> int:
        return self._suds

    @property
    def dailysuds(self) -> int:
        return self._dailysuds

    @dailysuds.setter
    def dailysuds(self, value):
        self._dailysuds = value

    @property
    def safemode(self) -> bool:
        # database stores an int, but we'll represent
        # it with a bool for easier reading.
        return bool(self._safemode)

    @safemode.setter
    def safemode(self, switch: bool):
        self._safemode = int(switch)

    @property
    def safemode_timer(self) -> str:
        return self._safemode_timer

    def update_safemode_timer(self):
        self._safemode_timer = strftime("%Y-%m-%d %H:%M:%S")

    @property
    def inventory(self) -> dict:
        return [{'id': x.id, 'name': x.name} for x in self._inventory]

    def inventory_string(self) -> str:
        return ','.join([str(x.id) for x in self._inventory])

    def hours_since_safe_toggle(self) -> int:
        last_change = dt.strptime(self._safemode_timer, "%Y-%m-%d %H:%M:%S")
        cur_date = dt.now()

        hours_since = (cur_date - last_change).total_seconds() / 3600
        return hours_since

    def __add__(self, thing: int | str):
        if isinstance(thing, int):
            self._suds += thing
        elif isinstance(thing, Item):
            self._inventory.append(thing)
        else:
            raise ValueError(f'Player._add__() expects int or Item. Got {type(thing)}.')

    def __sub__(self, thing: int | Item):
        if isinstance(thing, int):
            if self._suds < thing:
                raise spongedb.NotEnoughSudsError(f"/u/{self._name} doesn't have enough pebbles.")
            self._suds -= thing
        elif isinstance(thing, Item):
            if thing.name not in [x.name for x in self._inventory]:
                raise spongedb.ItemNotOwnedError(f"/u/{self._name} doesn't have an item called '{thing.name}'.")
            for index,item in enumerate(self._inventory):
                if item.name == thing.name:
                    del self._inventory[index]
                    break
        else:
            raise ValueError(f'Player._add__() expects int or Item. Got {type(thing)}.')

    def pay(self, amount: int, recipient: Player):
        self - amount
        recipient + amount

    def give(self, gift: Item, recipient: Player):
        self - gift
        recipient + gift

    def buy(self, item: Item):
        if not item.is_for_sale:
            raise NotForSaleError(f"item '{item.name}' is not for sale")
        self - item.price
        self + item
        item.stock -= 1

    def save(self):
        db = spongedb.SpongeDB()
        db.update_player(self._suds, self.inventory_string(), int(self.safemode),
                         self._safemode_timer, self._dailysuds, self._name)
        db.save()
        db.close()

    def flush(self, confirm: bool = False):
        if confirm:
            db = spongedb.SpongeDB()
            db.remove_player(self._name)
            db.save()
            db.close()
        else:
            print(f"Player '{self._name}' not flushed. Player.flush(confirm=True) to flush.")

class NewPlayer(Player):

    def __init__(self, username: str):
        # get remaining str after last /
        # functionally removes /u/
        username = username.split('/')[-1]

        db = spongedb.SpongeDB()
        try:
            db.get_player(username)
            raise spongedb.PlayerExistsError(f"player '{username}' exists. Use class Player('{username}') instead.")
        except spongedb.NoSuchPlayerError as e:
            db.add_player(username)
            db.save()
        db.close()

        super().__init__(username)

if __name__ == "__main__":
    bibs = Player('bibbleskit')
    sinj = NewPlayer('asdf')
    gift = Item('sword of regret')

    bibs + gift
    print(bibs.inventory)
    print(sinj.inventory)
    bibs.give(gift, sinj)
    print()
    print(bibs.inventory)
    print(sinj.inventory)
