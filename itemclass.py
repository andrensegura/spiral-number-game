import spongedb

class Item:

    # "signifier" can be an int or a string
    def __init__(self, signifier):
        db         = spongedb.SpongeDB()
        db_entry   = db.get_item(signifier)
        self._id   = db_entry['primary_key']
        self._name = db_entry['name']
        self._description = db_entry['description']
        self._price = db_entry['price']
        self._unlimited = db_entry['unlimited']
        self._stock = db_entry['stock']
        self._forsale = db_entry['forsale']
        self._tags = db_entry['tags'].split(',') if db_entry['tags'] else []
        db.close()

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def price(self) -> int:
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError(' value must be positive.')
        self._price = value

    @property
    def description(self) -> str:
        return self._description

    @property
    def is_for_sale(self) -> bool:
        return bool(self._forsale)

    @property
    def is_unlimited(self) -> bool:
        return bool(self._unlimited)

    @property
    def is_limited(self) -> bool:
        return not bool(self._unlimited)

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, value: int):
        if value < 0:
            raise spongedb.OutOfStockError(f"Not enough stock for item '{self._name}'.")
        self._stock = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, list):
            raise ValueError(f"Item.tags must be a list")
        self._tags = value

    def save(self):
        tags = ",".join(self._tags)

        db = spongedb.SpongeDB()
        db.update_item(self._id, self._name, self._price, self._description,
                       self._stock, self._unlimited, self._forsale, tags)
        db.save()
        db.close()

    def ownedby(self):
        db = spongedb.SpongeDB()
        return db.get_player_with_item(self._name)
        db.close()

class NewItem(Item):

    def __init__(self, name, price, desc, stock=1, unlimited=0, save=True, tags=[]):
        tags = ','.join(tags)
        db = spongedb.SpongeDB()
        db.add_item(name, price, desc, stock, unlimited, tags)
        db_entry = db.get_item(name)
        if save:
            db.save()
        db.close()

        super().__init__(name)

if __name__ == "__main__":
    sword = Item("sword of regret")
    print(f'ID:   {sword.id}\nName: {sword.name}')
    print(f'Ownd: {sword.ownedby()}')
    print(f'Unlt: {sword.is_limited}')

    print()

    sword = NewItem("Cute Piglet", 600, "It's too cute to eat.", unlimited=1)
    print(f'ID:   {sword.id}\nName: {sword.name}')
    print(f'Ownd: {sword.ownedby()}')
    print(f'Unlt: {sword.is_limited}')
