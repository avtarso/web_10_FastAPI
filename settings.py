# CHOICE_BASE_MESSAGE = '''Basic setup for postgres completed
# Press any key to continue
# To continue with SQLite database - input "lite"'''

# base_choice = input(CHOICE_BASE_MESSAGE)

# if base_choice == "lite":
#     FILE_SQLITE_BASE = "contacts_database.db"

#     DATABASE = f'sqlite:///{FILE_SQLITE_BASE}'

# else:

#     DATABASE = "postgresql+psycopg2://postgres:242419@localhost:5432/web07"


DATABASE = 'sqlite:///contacts_database.db'

