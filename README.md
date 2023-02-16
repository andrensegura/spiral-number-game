# Spiral Tower Number Extravaganza

## a.k.a. STONE

### Important Files for Contribution:

* spongedb.py
  - The database API. Fully commented. This is how you will mostly interact with the data.
* check\_for\_commands.py
  - Commands are checked minutely. Any new command currently would get added to this file. However, in the future, it would be nice to have commands be their own module.
* special\_items.py
  - Items that have special properties get added here. Like commands, these should probably be within their own modules.

### Other Files:

* sunday\_shop.py
  - The shop is created using this script.
* check\_for\_purchases.py
  - called every couple minutes and queues up purchases.
* remove\_yeeted.py
  - This file removes non-player users and anyone from the most recent Flush by /r/SpiralFlusher.

### Config Info:

To run anything, you'll need to make sure the following files are set up correctly:

* database\_schema.sql
  - You must use this to create a SQLite database.
* spongeconfig.py
  - spongeconfig\_template.py must be renamed to spongeconfig.py
  - You must set the DB\_PATH variable to match the location of the database you created using the schema.
  - You must put in the proper credentials for your or your bot's reddit account.
