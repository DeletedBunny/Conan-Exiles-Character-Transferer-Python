from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Progressbar


class UiCharacterTransferer:
    def __init__(self, uiRoot, databaseHelper):
        self.bottom_panel_buttons_frame = None
        self.accounts_chosen = []
        self.character_stats = None
        self.item_inventory = None
        self.item_properties = None
        self.properties = None
        self.database_to_write_to = StringVar()
        self.label = None
        self.uiRoot = uiRoot
        self.uiFrameRoot = None
        self.databaseHelper = databaseHelper
        self.page_index = 1
        self.prefiltered_properties_list = [(
            'BasePlayerChar_C.bedID',
            'BasePlayerChar_C.bedrollID',
            'BasePlayerChar_C.BedSpawnTransform',
            'BasePlayerChar_C.lastBoundToBedroll',
            'BasePlayerChar_C.PreSitTransform',
            'CharacterMapMarkerComponent.m_NumDeathMarkerIDsAssigned',
            'CharacterMapMarkerComponent.m_LastLootedDeathMarkerID',
            'CharacterMapMarkerComponent.m_AllMapsDiscoveredMarkers',
            'CharacterMapMarkerComponent.m_PlayerMarkers',
            'BP_FastTravelHandler_C.AllMapsDiscoveredTravelPoints'
        )]

    def switch_page(self):
        self.uiFrameRoot.destroy()
        self.uiFrameRoot = Frame(self.uiRoot)
        self.uiFrameRoot.grid(row=1, columnspan=2)
        if self.page_index == 1:
            self.page_1_accounts()
        elif self.page_index == 2:
            self.page_2_characters()
        elif self.page_index == 3:
            self.page_3_character_stats()
        elif self.page_index == 4:
            self.page_4_item_inventory()
        elif self.page_index == 5:
            self.page_5_item_properties()
        elif self.page_index == 6:
            self.page_6_properties()
        elif self.page_index == 7:
            self.page_7_final_confirmation()
        elif self.page_index == 8:
            self.write_data()

    def check_current_page_data(self):
        if self.page_index == 1 and len(self.accounts_chosen) == 0:
            messagebox.showerror("Error", "An account needs to be chosen.")
            return True

    def next_page(self):
        if self.page_index == 8:
            return
        if self.check_current_page_data():
            return
        self.page_index += 1
        self.switch_page()

    def previous_page(self):
        if self.page_index == 1:
            return
        self.page_index -= 1
        self.switch_page()

    def write_data(self):
        self.label.config(text="Writing to database please don't close the window")
        self.uiRoot.config(menu=NONE)
        self.bottom_panel_buttons_frame.destroy()
        progressLabel = Label(self.uiFrameRoot)
        progressLabel.grid(row=2, columnspan=2)
        pb = Progressbar(self.uiFrameRoot, orient=HORIZONTAL,
                    length=100, mode='determinate')
        pb.grid(row=1, columnspan=2)
        database_selection = self.database_to_write_to.get()
        progressLabel.config(text="Writing character level")
        self.databaseHelper.write_data_to_database_accounts(database_selection, self.accounts_chosen)
        pb['value'] = 10
        progressLabel.config(text="Writing character stats")
        self.databaseHelper.write_data_to_database_character_stats(database_selection, self.accounts_chosen, self.character_stats)
        pb['value'] = 30
        progressLabel.config(text="Writing character inventory")
        self.databaseHelper.write_data_to_database_item_inventory(database_selection, self.accounts_chosen, self.item_inventory)
        pb['value'] = 65
        progressLabel.config(text="Writing item properties")
        self.databaseHelper.write_data_to_database_item_properties(database_selection, self.accounts_chosen, self.item_properties)
        pb['value'] = 70
        progressLabel.config(text="Writing character properties")
        self.databaseHelper.write_data_to_database_properties(database_selection, self.accounts_chosen, self.properties, self.prefiltered_properties_list)
        pb['value'] = 100
        progressLabel.config(text="Finished")

    def init_common_components(self):
        self.uiRoot.geometry("800x600")
        self.uiRoot.title("Character Transferer")
        self.uiFrameRoot = Frame(self.uiRoot)
        self.uiFrameRoot.grid(row=1, columnspan=2)
        ui_menu = Menu(self.uiRoot)
        file_menu = Menu(ui_menu, tearoff=0)
        ui_menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Overwrite to Siptah (Experimental)')
        file_menu.add_command(label='Overwrite to Exiles (Experimental)')
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.uiRoot.destroy)
        self.uiRoot.config(menu=ui_menu)

        self.bottom_panel_buttons_frame = Frame(self.uiRoot)
        self.bottom_panel_buttons_frame.grid(row=3, columnspan=2, pady=30)

        next_button = Button(self.bottom_panel_buttons_frame, text="Next >", command=self.next_page)
        next_button.grid(row=0, column=1, padx=10)

        back_button = Button(self.bottom_panel_buttons_frame, text="< Back", command=self.previous_page)
        back_button.grid(row=0, column=0, padx=10)

        self.label = Label(self.uiRoot)
        self.label.grid(row=0, columnspan=2, pady=10)

    def move_user_from_list(self, fromListBox, toListBox, indexToInsert, isAdd):
        selected_user_index = fromListBox.curselection()
        if len(selected_user_index) == 0:
            return
        user = fromListBox.get(selected_user_index)
        fromListBox.delete(selected_user_index)
        toListBox.insert(indexToInsert, user)

        if isAdd:
            self.accounts_chosen.insert(len(self.accounts_chosen), user)
        else:
            self.accounts_chosen.remove(user)

    def on_listbox_pressed(self, event, selectedListbox, lastSelectedListbox):
        w = event.widget
        try:
            idx = int(w.curselection()[0])
        except IndexError:
            return
        lastSelectedListbox.clear()
        lastSelectedListbox.append(selectedListbox)

    def remove_property(self, lastSelectedListbox):
        if len(lastSelectedListbox) == 0:
            return
        listbox = lastSelectedListbox.pop()
        num = -1
        if listbox.widgetName == "exiles":
            num = 0
        elif listbox.widgetName == "siptah":
            num = 1
        else:
            return
        chosen_property = listbox.get(listbox.curselection())
        listbox.delete(listbox.curselection())
        lastSelectedListbox.clear()
        self.properties[0][num].remove(chosen_property)

    def page_1_accounts(self):
        self.label.config(text="Pick the account pairs exiles/siptah that were detected which you would like transferred.")
        user_id_pairs_and_names = self.databaseHelper.get_user_id_pairs()

        for user in user_id_pairs_and_names:
            for account in self.accounts_chosen:
                if user == account:
                    user_id_pairs_and_names.remove(user)

        left_side_frame = Frame(self.uiFrameRoot)
        left_side_frame.grid(row=1, column=0, padx=10)

        right_side_frame = Frame(self.uiFrameRoot)
        right_side_frame.grid(row=1, column=1, padx=10)

        selected_users_list_box = Listbox(left_side_frame,
                                          height=25,
                                          width=50)
        selected_users_list_box.grid(row=0, column=0)

        selected_users_list_scrollbar = Scrollbar(left_side_frame)
        selected_users_list_scrollbar.grid(row=0, column=1, sticky='ns')
        selected_users_list_box.config(yscrollcommand=selected_users_list_scrollbar.set)

        users_list_box = Listbox(right_side_frame,
                                 height=25,
                                 width=50)
        users_list_box.grid(row=0, column=0)

        users_list_scrollbar = Scrollbar(right_side_frame)
        users_list_scrollbar.grid(row=0, column=1, sticky='ns')
        users_list_box.config(yscrollcommand=users_list_scrollbar.set)

        for user in user_id_pairs_and_names:
            users_list_box.insert(END, user)

        for user in self.accounts_chosen:
            selected_users_list_box.insert(END, user)

        selected_users_remove_button = Button(left_side_frame, text="Remove User >",
                                              command=lambda: self.move_user_from_list(selected_users_list_box, users_list_box, END, False))
        selected_users_remove_button.grid(row=1, column=0, pady=5)

        users_add_button = Button(right_side_frame, text="< Add User",
                                  command=lambda: self.move_user_from_list(users_list_box, selected_users_list_box, END, True))
        users_add_button.grid(row=1, column=0, pady=5)

    def page_2_characters(self):
        self.label.config(text="These are the users and their levels on their respective databases.")
        left_side_frame = Frame(self.uiFrameRoot)
        left_side_frame.grid(row=1, column=0, padx=10)

        right_side_frame = Frame(self.uiFrameRoot)
        right_side_frame.grid(row=1, column=1, padx=10)

        exiles_label = Label(left_side_frame, text="Exiles character (id, name, level)")
        exiles_label.grid(row=0, columnspan=2, pady=5)

        siptah_label = Label(right_side_frame, text="Siptah character (id, name, level)")
        siptah_label.grid(row=0, columnspan=2, pady=5)

        exiles_list_box = Listbox(left_side_frame,
                                          height=25,
                                          width=50)
        exiles_list_box.grid(row=1, column=0)

        exiles_list_scrollbar = Scrollbar(left_side_frame)
        exiles_list_scrollbar.grid(row=1, column=1, sticky='ns')
        exiles_list_box.config(yscrollcommand=exiles_list_scrollbar.set)

        siptah_list_box = Listbox(right_side_frame,
                                 height=25,
                                 width=50)
        siptah_list_box.grid(row=1, column=0)

        siptah_list_scrollbar = Scrollbar(right_side_frame)
        siptah_list_scrollbar.grid(row=1, column=1, sticky='ns')
        siptah_list_box.config(yscrollcommand=siptah_list_scrollbar.set)

        for user in self.accounts_chosen:
            exiles_list_box.insert(END, user[0])
            siptah_list_box.insert(END, user[1])

    def page_3_character_stats(self):
        self.label.config(text="These are the character stats found, you should be able to safely copy them all.")
        self.character_stats = self.databaseHelper.get_user_stats(self.accounts_chosen)
        left_side_frame = Frame(self.uiFrameRoot)
        left_side_frame.grid(row=1, column=0, padx=10)

        right_side_frame = Frame(self.uiFrameRoot)
        right_side_frame.grid(row=1, column=1, padx=10)

        exiles_label = Label(left_side_frame, text="Exiles char stats (char_id, stat_type, stat_id, stat_value)")
        exiles_label.grid(row=0, columnspan=2, pady=5)

        siptah_label = Label(right_side_frame, text="Siptah char stats (char_id, stat_type, stat_id, stat_value)")
        siptah_label.grid(row=0, columnspan=2, pady=5)

        exiles_list_box = Listbox(left_side_frame,
                                        height=25,
                                        width=50)
        exiles_list_box.grid(row=1, column=0)

        exiles_list_scrollbar = Scrollbar(left_side_frame)
        exiles_list_scrollbar.grid(row=1, column=1, sticky='ns')
        exiles_list_box.config(yscrollcommand=exiles_list_scrollbar.set)

        siptah_list_box = Listbox(right_side_frame,
                                        height=25,
                                        width=50)
        siptah_list_box.grid(row=1, column=0)

        siptah_list_scrollbar = Scrollbar(right_side_frame)
        siptah_list_scrollbar.grid(row=1, column=1, sticky='ns')
        siptah_list_box.config(yscrollcommand=siptah_list_scrollbar.set)

        for user_stat in self.character_stats:
            for stat in user_stat[0]:
                exiles_list_box.insert(END, stat)
            for stat in user_stat[1]:
                siptah_list_box.insert(END, stat)

    def page_4_item_inventory(self):
        self.label.config(text="These are the items found in the inventory, you should be able to safely copy them all.")
        self.item_inventory = self.databaseHelper.get_item_inventory(self.accounts_chosen)
        left_side_frame = Frame(self.uiFrameRoot)
        left_side_frame.grid(row=1, column=0, padx=10)

        right_side_frame = Frame(self.uiFrameRoot)
        right_side_frame.grid(row=1, column=1, padx=10)

        exiles_label = Label(left_side_frame, text="Exiles inventory (item_id, owner_id, inv_type, template_id, data)")
        exiles_label.grid(row=0, columnspan=2, pady=5)

        siptah_label = Label(right_side_frame, text="Siptah inventory (item_id, owner_id, inv_type, template_id, data)")
        siptah_label.grid(row=0, columnspan=2, pady=5)

        exiles_list_box = Listbox(left_side_frame,
                                  height=25,
                                  width=50)
        exiles_list_box.grid(row=1, column=0)

        exiles_list_scrollbar = Scrollbar(left_side_frame)
        exiles_list_scrollbar.grid(row=1, column=1, sticky='ns')
        exiles_list_box.config(yscrollcommand=exiles_list_scrollbar.set)

        siptah_list_box = Listbox(right_side_frame,
                                  height=25,
                                  width=50)
        siptah_list_box.grid(row=1, column=0)

        siptah_list_scrollbar = Scrollbar(right_side_frame)
        siptah_list_scrollbar.grid(row=1, column=1, sticky='ns')
        siptah_list_box.config(yscrollcommand=siptah_list_scrollbar.set)

        for inventory in self.item_inventory:
            for item in inventory[0]:
                exiles_list_box.insert(END, item)
            for item in inventory[1]:
                siptah_list_box.insert(END, item)

    def page_5_item_properties(self):
        self.label.config(text="These are the item properties found, you should be able to safely copy them all.")
        self.item_properties = self.databaseHelper.get_item_properties(self.accounts_chosen)
        left_side_frame = Frame(self.uiFrameRoot)
        left_side_frame.grid(row=1, column=0, padx=10)

        right_side_frame = Frame(self.uiFrameRoot)
        right_side_frame.grid(row=1, column=1, padx=10)

        exiles_label = Label(left_side_frame, text="Exiles properties (item_id, owner_id, inv_type, template_id, data)")
        exiles_label.grid(row=0, columnspan=2, pady=5)

        siptah_label = Label(right_side_frame, text="Siptah properties (item_id, owner_id, inv_type, template_id, data)")
        siptah_label.grid(row=0, columnspan=2, pady=5)

        exiles_list_box = Listbox(left_side_frame,
                                  height=25,
                                  width=50)
        exiles_list_box.grid(row=1, column=0)

        exiles_list_scrollbar = Scrollbar(left_side_frame)
        exiles_list_scrollbar.grid(row=1, column=1, sticky='ns')
        exiles_list_box.config(yscrollcommand=exiles_list_scrollbar.set)

        siptah_list_box = Listbox(right_side_frame,
                                  height=25,
                                  width=50)
        siptah_list_box.grid(row=1, column=0)

        siptah_list_scrollbar = Scrollbar(right_side_frame)
        siptah_list_scrollbar.grid(row=1, column=1, sticky='ns')
        siptah_list_box.config(yscrollcommand=siptah_list_scrollbar.set)

        for item_property in self.item_properties:
            for item in item_property[0]:
                exiles_list_box.insert(END, item)
            for item in item_property[1]:
                siptah_list_box.insert(END, item)

    def page_6_properties(self):
        self.label.config(text="These are the character properties found, you should be able to safely copy them all.")
        self.properties = self.databaseHelper.get_properties(self.accounts_chosen)
        for item in self.prefiltered_properties_list[0]:
            for i in range(0, len(self.properties)):
                for prop in self.properties[i][0]:
                    if prop[1] == item:
                        self.properties[i][0].remove(prop)
                for prop in self.properties[i][1]:
                    if prop[1] == item:
                        self.properties[i][1].remove(prop)
        left_side_frame = Frame(self.uiFrameRoot)
        left_side_frame.grid(row=1, column=0, padx=10)

        right_side_frame = Frame(self.uiFrameRoot)
        right_side_frame.grid(row=1, column=1, padx=10)

        exiles_label = Label(left_side_frame, text="Exiles properties (object_id, name, value)")
        exiles_label.grid(row=0, columnspan=2, pady=5)

        siptah_label = Label(right_side_frame, text="Siptah properties (object_id, name, value)")
        siptah_label.grid(row=0, columnspan=2, pady=5)

        exiles_list_box = Listbox(left_side_frame,
                                  height=25,
                                  width=50)
        exiles_list_box.grid(row=1, column=0)

        exiles_list_scrollbar = Scrollbar(left_side_frame)
        exiles_list_scrollbar.grid(row=1, column=1, sticky='ns')
        exiles_list_box.config(yscrollcommand=exiles_list_scrollbar.set)

        siptah_list_box = Listbox(right_side_frame,
                                  height=25,
                                  width=50)
        siptah_list_box.grid(row=1, column=0)

        siptah_list_scrollbar = Scrollbar(right_side_frame)
        siptah_list_scrollbar.grid(row=1, column=1, sticky='ns')
        siptah_list_box.config(yscrollcommand=siptah_list_scrollbar.set)

        exiles_list_box.widgetName = "exiles"
        siptah_list_box.widgetName = "siptah"
        listbox_last_selected = []
        exiles_list_box.bind('<<ListboxSelect>>', lambda e: self.on_listbox_pressed(e, exiles_list_box, listbox_last_selected))
        siptah_list_box.bind('<<ListboxSelect>>', lambda e: self.on_listbox_pressed(e, siptah_list_box, listbox_last_selected))
        remove_button = Button(self.uiFrameRoot, text="Remove property",
                                              command=lambda: self.remove_property(listbox_last_selected))
        remove_button.grid(row=2, columnspan=2, pady=5)

        for char_property in self.properties:
            for item in char_property[0]:
                exiles_list_box.insert(END, item)
            for item in char_property[1]:
                siptah_list_box.insert(END, item)

    def page_7_final_confirmation(self):
        self.label.config(text="Final screen, choose where you want to write the changes to.")
        radio_selection_exiles = Radiobutton(self.uiFrameRoot, text="Write to Exiles", value="exiles", variable=self.database_to_write_to)
        radio_selection_siptah = Radiobutton(self.uiFrameRoot, text="Write to Siptah", value="siptah", variable=self.database_to_write_to)
        radio_selection_exiles.grid(row=0, column=0)
        radio_selection_siptah.grid(row=0, column=1)
        self.database_to_write_to.set("siptah")