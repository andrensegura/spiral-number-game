from itemclass import Item
from spongedb import SpongeDB
from reddit_connect import r
from spongeconfig import R_SUBREDDIT, SPONGE_PATH

class Shop:
    def __init__(self, name='general', title='STONE: Sunday Shop Open!',
                 item_signifiers=[], tags=['general']):
        self._name = name
        self._title = title
        self._body = ''
        self._inventory = []

        self._submission_id = ''
        try:
            with open(f"{SPONGE_PATH}/text/{self._name}.id", 'r') as file:
                self._submission_id = file.readline()
        except:
            pass

        # body text with UNLIMITEDITEMS and LIMITEDITEMS placeholders
        with open(f"{SPONGE_PATH}/text/{name}.body", 'r') as file:
            self._body = file.read()

        # add item ids with supplied tags to list of items
        self._tags = tags
        db = SpongeDB()
        for tag in tags:
            item_signifiers += db.get_items_with_tag(tag)
        db.close()
        item_signifiers = set(item_signifiers)
        
        # create inventory of Items
        for signifier in item_signifiers:
            item = Item(signifier)
            if item.is_for_sale:
                # Items that are out of stock should not be for sale.
                #if item.stock == 0:
                #    item._forsale = 0
                #    item.save()
                #    continue
                self._inventory.append(item)

    def clear_out_of_stock(self):
        for item in self._inventory:
            if item.stock == 0:
                item._forsale = 0
                item.save()

    def set_unlimited_stock(self, amount: int = 10):
        for item in self._inventory:
            if item.is_unlimited and item.stock > 10:
                item.stock = amount
                item.save()

    @property
    def inventory(self):
        return sorted(self._inventory, key=lambda x: x.stock, reverse=True)
        

    @property
    def body(self) -> str:
        unlimited_table = ''
        for item in self.inventory:
            if item.is_unlimited:
                name = item.name if item.stock > 0 else f"~~{item.name}~~"
                unlimited_table += f"{name}|{item.description}|{item.price} o|{item.stock}\n"

        limited_table = ''
        for item in self.inventory:
            if item.is_limited:
                name = item.name if item.stock > 0 else f"~~{item.name}~~"
                limited_table += f"{name}|{item.description}|{item.price} o|{item.stock}\n"

        full_body = self._body.replace('UNLIMITEDITEMS', unlimited_table)
        full_body = full_body.replace('LIMITEDITEMS', limited_table)
        return full_body

    def submit_post(self):
        parlor = r.subreddit(R_SUBREDDIT)
        submission = parlor.submit(title=self._title, selftext=self.body)
        self._submission_id = str(submission)

        with open(f"{SPONGE_PATH}/text/{self._name}.id", 'w') as file:
            file.write(self._submission_id)

        with open(f"{SPONGE_PATH}/text/{self._name}.banlist", 'w') as banlist:
            banlist.write('')

    def update_post(self):
        post = ''
        post = r.submission(id=self._submission_id)
        post.edit(body=self.body)

    def is_banned(self, username: str) -> bool:
        with open(f"{SPONGE_PATH}/text/{self._name}.banlist", 'r') as banlist:
            if str(username) in [str(x.strip()) for x in banlist.readlines()]:
                return True
            else:
                return False

    def ban(self, username: str):
        with open(f"{SPONGE_PATH}/text/{self._name}.banlist", 'a') as banlist:
           banlist.write(username + '\n')
