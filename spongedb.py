import sqlite3
from spongeconfig import DB_PATH

#####################################
# Custom error handling
#####################################

class OutOfStockError(Exception):
    pass

class NotEnoughSudsError(Exception):
    pass

class ItemNonexistantError(Exception):
    pass

class NotForSaleError(Exception):
    pass

#####################################
# SQLite3 API
#####################################

class SpongeDB():
    def __init__(self):
        self.con = sqlite3.connect(DB_PATH)
        self.cur = self.con.cursor()

    def save(self):
        self.con.commit()

    def close(self):
        self.con.close()

    def query(self, statement):
        return self.cur.execute(statement).fetchall()

    # Usage:    show_all(INTEGER)
    # Function: Prints a reddit table formatted list of LIMIT users. If no limit is given,
    #           it will print all users.
    def show_all(self, limit=-1):
        result = self.cur.execute("SELECT * FROM players ORDER BY suds DESC LIMIT {}".format(limit)).fetchall()
        output = ''
        for player in result:
            player = [str(x) for x in player]
            player[0] = '/u/' + player[0] + "^[[I](https://spiral.bibbleskit.com/u/" + player[0] + ")]"
            output += '|'.join(player[:4])
            output += '\n'
        return output

    # Usage:    get_players(INTEGER)
    # Function: Returns a list with all database info for INTEGER players. If no INTEGER is given,
    #           it will return all players in the database.
    def get_players(self, limit=-1):
        if isinstance(limit, int):
	        return self.cur.execute("SELECT * FROM players LIMIT {}".format(limit))
        else:
            raise ValueError('get_players requires an integer value')

    # Usage:    get_player(STRING, COMMA SEPARATED STRING)
    # Function: e.g. get_player('bibbleskit', 'username,suds,inventory')
    #           Returns database info for specified user.
    #           If no string is given for columns parameter, it will return all columns.
    def get_player(self, username, columns='*'):
        # I don't like the string formatting necessary to make this work. Insecurity.
        # I would have like to use ("select ? from ... = ?", (columns, username))
        # but it sanitizes the columns, making it select the literal string.
        result = self.cur.execute("SELECT {} FROM players WHERE username = ?".format(columns), (username,)).fetchone()
        return(result)

    # Usage:    add_player(STRING)
    # Function: This adds the given STRING as a new player into the database. If the user
    #           already exists, then it is ignored.
    def add_player(self, username):
        result = self.cur.execute(
            "INSERT OR IGNORE INTO players (username,suds,bonus,penalty,inventory) VALUES (?,?,?,?,?)",
            (username,0,0,0,'')
        ).fetchone()
        return True if result else False

    # Usage:    remove_player(STRING)
    # Function: Removes the player from the database.
    def remove_player(self, username):
        result = self.cur.execute("DELETE FROM players WHERE username = ?", (username,)).fetchone()
        return True if result else False

    # Usage:    alter_suds(STRING, INTEGER)
    # Function: Sets the players suds to the INTEGER
    def alter_suds(self, username, suds):
        result = self.cur.execute(
            "UPDATE players SET suds = ? WHERE username = ?",
            (suds, username)
        ).fetchone()
        return True if result else False

    # DEPRECATED
    def alter_bonus(self, username, bonus):
        result = self.cur.execute(
            "UPDATE players SET bonus = ? WHERE username = ?",
            (bonus, username)
        ).fetchone()
        return True if result else False

    # DEPRECATED
    def alter_penalty(self, username, penalty):
        result =  self.cur.execute(
            "UPDATE players SET penalty = ? WHERE username = ?",
            (penalty, username)
        ).fetchone()
        return True if result else False

    # Usage:    add_suds(STRING, INTEGER)
    # Function: Increases the players suds count by INTEGER
    #           Can be used to remove suds if INTEGER is negative.
    def add_suds(self, username, amount):
        result = self.cur.execute(
            "UPDATE players set suds = suds + ? WHERE username = ?",
            (amount, username)
        ).fetchone()
        return True if result else False

    # DEPRECATED
    def add_bonus(self, username, amount):
        result = self.cur.execute(
            "UPDATE players set bonus = bonus + ? WHERE username = ?",
            (amount, username)
        ).fetchone()
        return True if result else False

    # DEPRECATED
    def add_penalty(self, username, amount):
        result = self.cur.execute(
            "UPDATE players set penalty = penalty + ? WHERE username = ?",
            (amount, username)
        ).fetchone()
        return True if result else False

    # Usage:    get_item(STRING or INTEGER)
    # Function: Returns the database info for an item.
    #           If the parameter given is a STRING, it will search for the item by name.
    #           If the parameter given is a INTEGER, it will search for the item by ID.
    def get_item(self, item):
        # Returns entire item row
        # e.g. (5, 'Broken Crown', 401, 'I remember this. Those were better days.', 1)
        # 0: id, 1: name, 2: price, 3: description, 4: stock
        if isinstance(item, str):
            query = "SELECT * FROM items WHERE name = ?"
        elif isinstance(item, int):
            query = "SELECT * FROM items WHERE primary_key = ?"
        else:
            raise Exception("item must be type str or int", item)

        item_data = self.cur.execute(query, (item,)).fetchone()
        return item_data

    # Usage:    get_player_with_item(STRING or INTEGER)
    # Function: See get_item() for more info about parameter.
    #           Returns the username of the player who has the specified item.
    def get_player_with_item(self, item):
        item = self.get_item(item)
        usernames = self.cur.execute(
          "SELECT username FROM players WHERE inventory LIKE ? OR inventory LIKE ? OR inventory LIKE ?",
          (str(item[0]) + ",%", "%," + str(item[0]) + ",%", "%," + str(item[0]))
        ).fetchall()
        usernames = [x[0] for x in usernames]
        if len(usernames) == 1:
            usernames = usernames[0]
        return usernames if usernames else None

    # Usage:    __alter_inventory('+' or '-', STRING, STRING)
    # Function: PRIVATE FUNCTION. Adds or removes the requested item from the player's inventory.
    #           Use give_item() or remove_item() instead.
    def __alter_inventory(self, operation, item_name, username):
        item_id = self.get_item(item_name)[0]

        player_items = self.get_player(username, "inventory")[0]
        if player_items == '':
            player_items = []
        else:
            player_items = player_items.split(',')

        if operation == '+':
            player_items.append(str(item_id))
        elif operation == '-':
            player_items.remove(str(item_id))

        player_items = ','.join(player_items)

        self.cur.execute(
            "UPDATE players SET inventory = ? WHERE username = ?",
            (player_items, username)
        )

    # Usage:    give_item(STRING, STRING)
    # Function: Adds item to the user's inventory.
    def give_item(self, item_name, username):
        self.__alter_inventory('+', item_name, username)

    # Usage:    remove_item(STRING, STRING)
    # Function: Removes item to the user's inventory.
    def remove_item(self, item_name, username):
        self.__alter_inventory('-', item_name, username)

    # Usage:    give_item(STRING, STRING)
    # Function: Uses player's suds to purchase the item.
    def purchase_item(self, item, username):
        self.add_player(username)
        # get item data
        item_data  = self.get_item(item)
        if not item_data:
            raise ItemNonexistantError("No item called '{}'.".format(item))
        item_id    = item_data[0]
        item_price = item_data[2]
        item_stock = item_data[4]
        item_forsale = item_data[5]

        # if item not in stock, can't sell it.
        if item_stock <= 0:
            raise OutOfStockError("Item '{}' out of stock".format(item))

        # if user can't afford it
        user_suds = self.get_player(username, 'suds')[0]
        if user_suds < item_price:
            raise NotEnoughSudsError("{} cannot afford item ('{}' {} suds)".format(username, item, item_price))

        # if not for sale:
        if item_forsale == 0:
            raise NotForSaleError("{} is not currently for sale.".format(item))

        # reduce stock
        self.add_stock(item_id, -1)
        # deduct price
        self.add_suds(username, item_price * -1)
        # award item
        self.give_item(item_id, username)
        return True

    # Usage:    add_item(STRING, INTEGER, STRING, INTEGER)
    # Function: Adds a new item to the items database. If no INTEGER for stock is given, it will assume 1.
    def add_item(self, name, price, description, stock = 1):
        if self.get_item(name):
            return False
        result = self.cur.execute(
            "INSERT INTO items (name, price, description, stock) VALUES (?, ?, ?, ?)",
            (name, price, description, stock)
        ).fetchone()
        return True if result else False

    # Usage:     delete_item(STRING or INTEGER)
    # Function:  Removes the requested item from the databse.
    #            Searches by name if given STRING, searches by ID if given INTEGER.
    def delete_item(self, item):
        if isinstance(item, str):
            query = "DELETE FROM items WHERE name = ?"
        elif isinstance(item, int):
            query = "DELETE FROM items WHERE primary_key = ?"
        else:
            raise Exception("item must be type str or int", item)

        result = self.cur.execute(
            query,
            (item,)
        ).fetchone()
        return True if result else False

    # Usage:    add_stock(STRING or INTEGER, INTEGER)
    # Function: Adds INTEGER to the current amount of stock that an item has.
    #           Assumes add 1 stock if none supplied.
    #           Searches for item by name if STRING, ID if INTEGER.
    def add_stock(self, item, amount = 1):
        item_data  = self.get_item(item)
        if not item_data:
            print("No item called '{}'.".format(item))
            return False
        item_id    = item_data[0]
        item_stock = item_data[4]

        result = self.cur.execute(
            "UPDATE items SET stock = ? WHERE primary_key = ?",
            (item_stock + amount, item_id)
        ).fetchone()
        return True if result else False
        
    # Usage:    set_stock(STRING or INTEGER, INTEGER)
    # Function: Sets the stock to the exact number supplied.
    #           Assumes 1 stock if none supplied.
    #           Searches for item by name if STRING, ID if INTEGER.
    def set_stock(self, item, amount = 1):
        item_data  = self.get_item(item)
        if not item_data:
            print("No item called '{}'.".format(item))
            return False
        item_id    = item_data[0]
        item_stock = item_data[4]

        result = self.cur.execute(
            "UPDATE items SET stock = ? WHERE primary_key = ?",
            (amount, item_id)
        ).fetchone()
        return True if result else False

    # Usage:    is_submission_added(STRING)
    # Function: With the given submission ID, checks the database to see if it's been added.
    #           Returns True if so, returns False if not.
    def is_submission_added(self, sub_id):
        result = self.cur.execute(
            "SELECT id FROM submissions WHERE id = ?",
            (sub_id,)
        ).fetchone()
        return True if result else False

    # Usage:    is_comment_added(STRING)
    # Function: With the given comment ID, checks the database to see if it's been added.
    #           Returns True if so, returns False if not.
    def is_comment_added(self, com_id):
        result = self.cur.execute(
            "SELECT id FROM comments WHERE id = ?",
            (com_id,)
        ).fetchone()
        return True if result else False

    # Usage:    add_submission(STRING)
    # Function: Adds the submission ID to the database.
    def add_submission(self, sub_id):
        result = self.cur.execute(
            "INSERT OR IGNORE INTO submissions (id) VALUES (?)",
            (sub_id,)
        ).fetchone()
        return True if result else False

    # Usage:    add_comment(STRING)
    # Function: Adds the comment ID to the database.
    def add_comment(self, com_id):
        result = self.cur.execute(
            "INSERT OR IGNORE INTO comments (id) VALUES (?)",
            (com_id,)
        ).fetchone()
        return True if result else False

    # Usage:    select_store_stock(INTEGER)
    # Function: Returns a list of items available for sale. The integer provided
    #           is the limit for how many items will be sold in the shop.
    #           Assumes 50 if none supplied.
    def select_store_stock(self, limit=50):
        self.cur.execute("UPDATE items SET forsale = 0;")
        result = self.cur.execute(
            "UPDATE items SET forsale = 1 WHERE primary_key in (SELECT primary_key FROM items WHERE stock > 0 ORDER BY primary_key LIMIT ?);",
            (limit,)
        ).fetchone()
        return True if result else False

    # Usage:    get_forsale()
    # Function: Return a list of all of the items available for sale.
    def get_forsale(self):
        result = self.cur.execute(
            "SELECT * FROM items WHERE forsale = 1;"
        ).fetchall()
        return result

    # Usage:    update_stats(STRING, INTEGER)
    # Function: Adds suds to item statistics totals.
    def update_stats(self, item_name, amount):
        result = self.cur.execute(
            "UPDATE stats SET lifetime = lifetime + ?, week = week + ?, day = day + ? WHERE name = ?;",
            (amount, amount, amount, item_name)
        ).fetchone()
        return True if result else False
