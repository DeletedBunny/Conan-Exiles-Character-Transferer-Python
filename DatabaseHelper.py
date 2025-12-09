class DatabaseHelper:

    def __init__(self, exilesCursor, siptahCursor, exilesConn, siptahConn):
        self.exilesCursor = exilesCursor
        self.siptahCursor = siptahCursor
        self.exilesConn = exilesConn
        self.siptahConn = siptahConn

    def get(self, cursor, query):
        if query == '':
            return
        cursor.execute(query)
        return cursor.fetchall()

    def update(self, cursor, databaseToWriteTo, query):
        pass
        if query == '':
            return
        cursor.execute(query)
        self.pick_conn(databaseToWriteTo).commit()

    def get_internal_id(self, cursor, account_id):
        return self.get(cursor, 'SELECT id,char_name,level FROM characters WHERE playerId IS ' + str(account_id))[0]

    def get_user_id_pairs(self):
        exiles_accounts = self.get(self.exilesCursor, 'SELECT id,user FROM account')
        siptah_accounts = self.get(self.siptahCursor, 'SELECT id,user FROM account')
        internal_ids = []
        for i in exiles_accounts:
            for j in siptah_accounts:
                if i[1] == j[1]:
                    internal_ids += [(self.get_internal_id(self.exilesCursor, i[0]), self.get_internal_id(self.siptahCursor, j[0]))]
        return internal_ids

    def get_user_stats(self, internal_ids):
        user_stats = []
        for char_internal_id in internal_ids:
            exiles_stats = self.get(self.exilesCursor, 'SELECT char_id,stat_type,stat_id,stat_value FROM character_stats WHERE char_id IS ' + str(char_internal_id[0][0]))
            siptah_stats = self.get(self.siptahCursor, 'SELECT char_id,stat_type,stat_id,stat_value FROM character_stats WHERE char_id IS ' + str(char_internal_id[1][0]))
            user_stats += [(exiles_stats, siptah_stats)]
        return user_stats

    def get_item_inventory(self, internal_ids):
        item_inventory = []
        for char_internal_id in internal_ids:
            exiles_items = self.get(self.exilesCursor, 'SELECT item_id,owner_id,inv_type,template_id,data FROM item_inventory WHERE owner_id IS ' + str(char_internal_id[0][0]))
            siptah_items = self.get(self.siptahCursor, 'SELECT item_id,owner_id,inv_type,template_id,data FROM item_inventory WHERE owner_id IS ' + str(char_internal_id[1][0]))
            item_inventory += [(exiles_items, siptah_items)]
        return item_inventory

    def get_item_properties(self, internal_ids):
        item_properties = []
        for char_internal_id in internal_ids:
            exiles_properties = self.get(self.exilesCursor, 'SELECT item_id,owner_id,inv_type,name,value FROM item_properties WHERE owner_id IS ' + str(char_internal_id[0][0]))
            siptah_properties = self.get(self.siptahCursor, 'SELECT item_id,owner_id,inv_type,name,value FROM item_properties WHERE owner_id IS ' + str(char_internal_id[1][0]))
            item_properties += [(exiles_properties, siptah_properties)]
        return item_properties

    def get_properties(self, internal_ids):
        properties = []
        for char_internal_id in internal_ids:
            exiles_properties = self.get(self.exilesCursor, 'SELECT object_id,name,value FROM properties WHERE object_id IS ' + str(char_internal_id[0][0]))
            siptah_properties = self.get(self.siptahCursor, 'SELECT object_id,name,value FROM properties WHERE object_id IS ' + str(char_internal_id[1][0]))
            properties += [(exiles_properties, siptah_properties)]
        return properties

    def pick_cursor(self, databaseToWriteTo):
        if databaseToWriteTo == "exiles":
            return self.exilesCursor
        elif databaseToWriteTo == "siptah":
            return self.siptahCursor
        else:
            return None

    def pick_conn(self, databaseToWriteTo):
        if databaseToWriteTo == "exiles":
            return self.exilesConn
        elif databaseToWriteTo == "siptah":
            return self.siptahConn
        else:
            return None

    def get_id_account_offset(self, databaseToWriteTo):
        if databaseToWriteTo == "exiles":
            return 0
        elif databaseToWriteTo == "siptah":
            return 1
        else:
            return -1

    def get_inverse_id_account_offset(self, databaseToWriteTo):
        if databaseToWriteTo == "exiles":
            return 1
        elif databaseToWriteTo == "siptah":
            return 0
        else:
            return -1

    def write_data_to_database_accounts(self, databaseToWriteTo, accounts):
        cursor = self.pick_cursor(databaseToWriteTo)
        if cursor is None:
            return 1

        num = self.get_id_account_offset(databaseToWriteTo)
        inverse_num = self.get_inverse_id_account_offset(databaseToWriteTo)
        if num == -1 or inverse_num == -1:
            return 1

        for account in accounts:
            self.update(cursor, databaseToWriteTo, 'UPDATE characters SET level = ' + str(account[inverse_num][2]) + ' WHERE id = ' + str(account[num][0]))

        return 0

    def write_data_to_database_character_stats(self, databaseToWriteTo, accounts, characterStats):
        cursor = self.pick_cursor(databaseToWriteTo)
        if cursor is None:
            return 1

        num = self.get_id_account_offset(databaseToWriteTo)
        inverse_num = self.get_inverse_id_account_offset(databaseToWriteTo)
        if num == -1 or inverse_num == -1:
            return 1

        for account in accounts:
            self.update(cursor, databaseToWriteTo, 'DELETE FROM character_stats WHERE char_id = ' + str(account[num][0]))

        compounded_query = 'INSERT INTO character_stats (char_id,stat_type,stat_id,stat_value) VALUES '
        for i in range(0, len(accounts)):
            for stats in characterStats[i][inverse_num]:
                compounded_query += "('" + str(accounts[i][num][0]) + "','" + str(stats[1]) + "','" + str(stats[2]) + "','" + str(stats[3]) + "'),"
        compounded_query = compounded_query[:-1] + ''
        self.update(cursor, databaseToWriteTo, compounded_query)

    def write_data_to_database_item_inventory(self, databaseToWriteTo, accounts, itemInventory):
        cursor = self.pick_cursor(databaseToWriteTo)
        if cursor is None:
            return 1

        num = self.get_id_account_offset(databaseToWriteTo)
        inverse_num = self.get_inverse_id_account_offset(databaseToWriteTo)
        if num == -1 or inverse_num == -1:
            return 1

        for account in accounts:
            self.update(cursor, databaseToWriteTo, 'DELETE FROM item_inventory WHERE owner_id = ' + str(account[num][0]))

        compounded_query = 'INSERT INTO item_inventory (item_id,owner_id,inv_type,template_id,data) VALUES '
        for i in range(0, len(accounts)):
            for items in itemInventory[i][inverse_num]:
                compounded_query += "('" + str(items[0]) + "','" + str(accounts[i][num][0]) + "','" + str(items[2]) + "','" + str(items[3]) + "',X'" + str(items[4].hex()) + "'),"
        compounded_query = compounded_query[:-1] + ''
        self.update(cursor, databaseToWriteTo, compounded_query)

    def write_data_to_database_item_properties(self, databaseToWriteTo, accounts, itemProperties):
        cursor = self.pick_cursor(databaseToWriteTo)
        if cursor is None:
            return 1

        num = self.get_id_account_offset(databaseToWriteTo)
        inverse_num = self.get_inverse_id_account_offset(databaseToWriteTo)
        if num == -1 or inverse_num == -1:
            return 1

        for account in accounts:
            self.update(cursor, databaseToWriteTo, 'DELETE FROM item_properties WHERE owner_id = ' + str(account[num][0]))

        compounded_query = 'INSERT INTO item_properties (item_id,owner_id,inv_type,name,value) VALUES '
        for i in range(0, len(accounts)):
            for items in itemProperties[i][inverse_num]:
                compounded_query += "('" + str(items[0]) + "','" + str(accounts[i][num][0]) + "','" + str(items[2]) + "','" + str(items[3]) + "',X'" + str(items[4].hex()) + "'),"
        compounded_query = compounded_query[:-1] + ''
        self.update(cursor, databaseToWriteTo, compounded_query)

    def write_data_to_database_properties(self, databaseToWriteTo, accounts, properties, filter):
        cursor = self.pick_cursor(databaseToWriteTo)
        if cursor is None:
            return 1

        num = self.get_id_account_offset(databaseToWriteTo)
        inverse_num = self.get_inverse_id_account_offset(databaseToWriteTo)
        if num == -1 or inverse_num == -1:
            return 1

        for account in accounts:
            self.update(cursor, databaseToWriteTo, 'DELETE FROM properties WHERE object_id = ' + str(account[num][0]) + ' AND name NOT IN ' + str(filter[0]))

        compounded_query = 'INSERT INTO properties (object_id,name,value) VALUES '
        for i in range(0, len(accounts)):
            for prop in properties[i][inverse_num]:
                compounded_query += "('" + str(accounts[i][num][0]) + "','" + str(prop[1]) + "',X'" + str(prop[2].hex()) + "'),"
        compounded_query = compounded_query[:-1] + ''
        self.update(cursor, databaseToWriteTo, compounded_query)