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
                self._inventory.append(item)

    def set_unlimited_stock(self, amount: int = 10):
        for item in self._inventory:
            if item.is_unlimited:
                item.stock = amount
                item.save()

    @property
    def body(self) -> str:
        unlimited_table = ''
        for item in self._inventory:
            if item.is_unlimited:
                unlimited_table += f"{item.name}|{item.description}|{item.price} o|{item.stock}\n"

        limited_table = ''
        for item in self._inventory:
            if item.is_limited:
                limited_table += f"{item.name}|{item.description}|{item.price} o|{item.stock}\n"

        full_body = self._body.replace('UNLIMITEDITEMS', unlimited_table)
        full_body = full_body.replace('LIMITEDITEMS', limited_table)
        return full_body

    def submit_post(self):
        parlor = r.subreddit(R_SUBREDDIT)
        submission = parlor.submit(title=self._title, selftext=self.body)

        with open(f"{SPONGE_PATH}/text/{self._name}.id", 'w') as file:
            file.write(str(submission))

    def update_post(self):
        post = ''
        with open(f"{SPONGE_PATH}/text/{self._name}.id", 'r') as file:
            submission_id = file.readline()
            post = r.submission(id=submission_id)

        post.edit(body=self.body)
