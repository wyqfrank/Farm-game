import tkinter as tk
from tkinter import filedialog  # For masters task
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *


# Implement your classes here
class InfoBar(AbstractGrid):
    """
    InfoBar is a grid with 2 rows and 3 columns, which displays information to
    the user about the number of days elapsed in the game, as well as the
    player’s energy and money.
    """

    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """
        Sets up this InfoBar to be an AbstractGrid with the appropriate number
        of rows and columns, and the appropriate width and height

        Args:
            master: parent widget for the InfoBar
        """
        super().__init__(master, dimensions=(2, 3),
                         size=(FARM_WIDTH + INVENTORY_WIDTH, INFO_BAR_HEIGHT))

    def redraw(self, day: int, money: int, energy: int) -> None:
        """
        Clears the InfoBar and redraws it to display the provided day, money,
        and energy.

        Args:
            day: The current day
            money: The amount of money the player has
            energy: The amount of energy the player has
        """
        self.clear()

        information = [("Day:", f"{day}"), ("Money:", f"${money}"),
                       ("Energy:", f"{energy}")]
        for i, (info, amount) in enumerate(information):
            self.annotate_position(position=(0, i), text=info,
                                   font=HEADING_FONT)
            self.annotate_position(position=(1, i), text=amount, font=None)


class FarmView(AbstractGrid):
    """
    The FarmView is a grid displaying the farm map, player, and plants.
    """

    def __init__(self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int],
                 size: tuple[int, int], **kwargs) -> None:
        """
        Sets up the FarmView to be an AbstractGrid with the appropriate
        dimensions and size.

        args:
            master: The parent widget for the FarmView.
            dimensions: The dimensions of the FarmView grid in rows and columns.
            size: The size of each grid cell in pixels.
            **kwargs: Additional keyword arguments to be passed to the
                      AbstractGrid initialiser
        """
        super().__init__(master, dimensions, size, **kwargs)

        self._cache = {}

    def redraw(self, ground: list[str], plants: dict[tuple[int, int], 'Plant'],
               player_position: tuple[int, int], player_direction: str) -> None:
        """
        Clears the farm view, then creates (on the FarmView instance) the images
        for the ground, then the plants, then the player.

        Args:
            ground: The list of ground tiles.
            plants: A dictionary mapping positions to plant objects.
            player_position: The current position of the player as a tuple.
            player_direction: The direction the player is facing.
        """
        self.clear()

        # drawing ground
        for row, tiles in enumerate(ground):
            for col, tile in enumerate(tiles):
                position = (row, col)
                if tile in IMAGES:
                    image = get_image(f"images/{IMAGES[tile]}",
                                      self.get_cell_size(), self._cache)
                    self.create_image(self.get_midpoint(position), image=image)

        # drawing plants
        for position in plants:
            plant_name = plants[position].get_name()
            plant_stage = plants[position].get_stage()
            image = get_image(f"images/plants/{plant_name}/stage_"
                              f"{plant_stage}.png",
                              self.get_cell_size(), self._cache)
            self.create_image(self.get_midpoint(position), image=image)

        # drawing player position
        if player_direction in IMAGES:
            image = get_image(f"images/{IMAGES[player_direction]}",
                              self.get_cell_size(), self._cache)
            self.create_image(self.get_midpoint(player_position), image=image)


class ItemView(tk.Frame):
    """
    The ItemView is a frame displaying relevant information and buttons for a
    single item.
    """

    def __init__(self, master: tk.Frame, item_name: str, amount: int,
                 select_command: Optional[Callable[[str], None]] = None,
                 sell_command: Optional[Callable[[str],
                                                 None]] = None,
                 buy_command: Optional[Callable[[str], None]] = None) -> None:
        """
        Sets up ItemView to operate as a tk.Frame, and creates all internal
        widgets.

        Args:
            master: The parent Tk frame in which this ItemView will be placed.
            item_name: name of the item as a string
            amount: the amount of the item in inventory
            select_command: A callback function to execute when the item is
                            selected.
            sell_command: A callback function to execute when the item is sold.
            buy_command: A callback function to execute when the item is bought.
        """
        super().__init__(master)

        self._item_name = item_name

        self._item_label_frame = tk.Frame(self, bg=INVENTORY_COLOUR)
        self._item_label_frame.pack(side=tk.LEFT)

        self._item_label = tk.Label(self._item_label_frame,
                                    text=f"{item_name}: {amount}",
                                    bg=INVENTORY_COLOUR)

        self._item_label.pack(expand=tk.TRUE, fill=tk.BOTH)

        self._sell_price_label = tk.Label(self._item_label_frame,
                                          text=f"Sell price: "
                                               f"${SELL_PRICES[item_name]}",
                                          bg=INVENTORY_COLOUR
                                          )
        self._sell_price_label.pack(expand=tk.TRUE, fill=tk.BOTH)

        buy = BUY_PRICES.get(item_name, "N/A")
        self._buy_price_label = tk.Label(self._item_label_frame,
                                         text=f"Buy price: ${buy}",
                                         bg=INVENTORY_COLOUR
                                         )
        self._buy_price_label.pack(expand=tk.TRUE, fill=tk.BOTH)

        sell_button = tk.Button(self, text="Sell",
                                command=lambda: sell_command(item_name))
        sell_button.pack(side=tk.LEFT, padx=20)

        # Only creates a buy button for items that can be bought
        if self._buy_price_label["text"][-3:] != "N/A":
            buy_button = tk.Button(self, text="Buy",
                                   command=lambda: buy_command(item_name))
            buy_button.pack(side=tk.LEFT)

        self.config(bg=INVENTORY_COLOUR)

        # binds
        widgets = [self._item_label, self._buy_price_label,
                   self._sell_price_label, self._item_label_frame, self]

        for widget in widgets:
            widget.bind("<Button-1>", lambda x: select_command(item_name))

    def update(self, amount: int, selected: bool = False) -> None:
        """
        Updates the text on the label, and the colour of this ItemView
        appropriately.

        Args:
            amount: the new quantity of the item.
            selected: Indicates whether the item is currently selected. Defaults
                      to False.
        """

        self._item_label.config(text=f"{self._item_name}: {amount}")
        if amount == 0:
            new_colour = INVENTORY_EMPTY_COLOUR
        elif selected:
            new_colour = INVENTORY_SELECTED_COLOUR
        else:
            new_colour = INVENTORY_COLOUR

        widgets = [self._item_label, self._buy_price_label,
                   self._sell_price_label, self._item_label_frame, self]
        for widget in widgets:
            widget.config(bg=new_colour,
                          highlightbackground=new_colour)


class FarmGame(object):
    """
    FarmGame is the controller class for the overall game. The controller is
    responsible for creating and maintaining instances of the model and view
    classes, event handling, and facilitating communication between the model
    and view classes.
    """
    def __init__(self, master: tk.Tk, map_file: str) -> None:
        """
        Sets up the FarmGame by creating the banner, the FarmModel instance, the
        view classes, and a button to enable users to increment the day in
        InfoBar.

        Args:
            master: the root Tk window.
            map_file: The file path to the map file.
        """
        master.title("Farm Game")

        # creates the title banner
        self._header = get_image(image_name="images/header.png",
                                 size=(
                                     FARM_WIDTH + INVENTORY_WIDTH,
                                     BANNER_HEIGHT))

        self._header_label = tk.Label(master, image=self._header)
        self._header_label.pack()

        # FarmModel instance
        self._farm = FarmModel(map_file)
        self._inventory = self._farm.get_player().get_inventory()

        # frame containing FarmView and ItemView
        frame = tk.Frame(master)
        frame.pack(expand=tk.TRUE, fill=tk.X)

        # FarmView instance
        self._farm_view = FarmView(frame, self._farm.get_dimensions(),
                                   (FARM_WIDTH, 480))
        self._farm_view.pack(side=tk.LEFT)

        # ItemView instance
        inventory_items = []
        item_frames = []
        self._inventory_frames = {}   # dict[item_name, Frame]

        # Create frames for items in inventory
        for item_name in ITEMS:
            if item_name in self._inventory:
                item_frame = ItemView(frame, item_name=item_name,
                                      amount=self._inventory[item_name],
                                      sell_command=self.sell_item,
                                      select_command=self.select_item,
                                      buy_command=self.buy_item)
                item_frame.config(highlightbackground=INVENTORY_OUTLINE_COLOUR,
                                  highlightthickness=2)
                item_frames.append(item_frame)
                item_frame.pack(expand=tk.TRUE, fill=tk.BOTH)
                inventory_items.append(item_name)

                if self._inventory[item_name] == 0:
                    item_frame.update(0, False)

                self._inventory_frames[item_name] = item_frame

        # Create frames for items not in inventory
        for item in ITEMS:
            if item not in inventory_items:
                item_frame = ItemView(frame, item_name=item, amount=0,
                                      sell_command=self.sell_item,
                                      select_command=self.select_item,
                                      buy_command=self.buy_item)
                item_frame.update(0, False)
                item_frame.pack(expand=tk.TRUE, fill=tk.BOTH)

                self._inventory_frames[item] = item_frame

        # instance of InfoBar
        self._info_bar = InfoBar(master)
        self._info_bar.pack()

        # next day button
        self._day_btn = tk.Button(text="Next day", command=self.next_day)
        self._day_btn.pack()

        # binds
        master.bind("<KeyPress>", self.handle_keypress)

        self.redraw()

    def next_day(self) -> None:
        """
        updates the display and proceeds to the next day in the FarmGame
        """
        self._farm.new_day()
        self.redraw()

    def redraw(self) -> None:
        """
        Redraws the entire game based on the current model state.
        """
        self._info_bar.redraw(self._farm.get_days_elapsed()
                              , self._farm.get_player().get_money()
                              , self._farm.get_player().get_energy())

        self._farm_view.redraw(self._farm.get_map(),
                               self._farm.get_plants(),
                               self._farm.get_player_position(),
                               self._farm.get_player_direction())

    def inspect_ground(self, position: tuple[int, int]) -> str | None:
        """
        Inspects the ground at the given position and returns the tile at
        that position.

        Args:
            position: The position to inspect in the form of (row, col).

        Returns:
            str or None: The tile at the specified position if a match is found,
            otherwise None is returned
        """

        position_tile = {}
        for row, tiles in enumerate(self._farm.get_map()):
            for col, tile in enumerate(tiles):
                tile_position = (row, col)
                if tile in IMAGES:
                    position_tile[tile_position] = tile

        if position in position_tile:
            return position_tile[position]

    @staticmethod
    def create_plants(plant_name: str) -> Plant | None:
        """
         Returns a plant object based on the provided plant name.

        Args:
            plant_name: The name of the plant to create.

        Returns:
            Plant or None: The created plant object if a match is found,
            otherwise None.
        """

        plants = [PotatoPlant(), KalePlant(), BerryPlant()]
        for plant in plants:
            if plant_name == plant.get_name():
                return plant

    def update_inv_frame(self, plant_name: str, selected: bool) -> None:
        """
        Updates the inventory frame of the specified plant with the given
        selection status.

        Args:
            plant_name: The name of the plant.
            selected: The selection status of the frame.
        """
        if plant_name in self._inventory_frames:
            amount = self._inventory[plant_name]
            self._inventory_frames[plant_name].update(amount, selected)

    def handle_keypress(self, event: tk.Event) -> None:
        """
        An event handler to be called when a keypress event occurs.

        Args:
            event: The keypress event object.
        """
        moves = ["w", "a", "s", "d", "t", "u", "p", "r", "h"]
        if event.keysym in moves:
            if event.keysym == "t":
                self._farm.till_soil(self._farm.get_player_position())
                self.redraw()

            elif event.keysym == "u":
                self._farm.untill_soil(self._farm.get_player_position())
                self.redraw()

            elif event.keysym == "p":
                position = self._farm.get_player().get_position()
                plant = self._farm.get_player().get_selected_item()

                if self.inspect_ground(position) == SOIL and plant:
                    # checks if the item is in inventory and a seed
                    if plant in self._inventory and "Seed" in plant:
                        selected_plant = plant.split()[0].lower()
                        created_plant = self.create_plants(selected_plant)

                        if self._farm.add_plant(position, created_plant):
                            self._farm.get_player().remove_item((plant, 1))

                    if plant not in self._inventory:
                        self._inventory_frames[plant].update(0, False)

                    if plant in self._inventory:  # to prevent KeyError
                        self.update_inv_frame(plant, True)

                self.redraw()

            elif event.keysym == "r":
                self._farm.remove_plant(self._farm.get_player().get_position())
                self.redraw()

            elif event.keysym == "h":
                position = self._farm.get_player().get_position()
                plant_harvested = self._farm.harvest_plant(position)
                if plant_harvested:
                    self._farm.get_player().add_item(plant_harvested)
                    self.update_inv_frame(plant_harvested[0], False)
                self.redraw()

            else:
                self._farm.move_player(event.keysym)
                self.redraw()

    def select_item(self, item_name: str) -> None:
        """
        The callback to be given to each ItemView for item selection.

        Args:
            item_name: the name of the selected item
        """
        if item_name in self._inventory_frames and item_name in self._inventory:
            self._farm.get_player().select_item(item_name)

            for item, frame in self._inventory_frames.items():
                if item in self._inventory:
                    frame.update(self._inventory[item], item == item_name)
        self.redraw()

    def buy_item(self, item_name: str) -> None:
        """
        The callback to be given to each ItemView for buying items.

        Args:
            item_name: the name of the item to buy
        """
        self._farm.get_player().buy(item_name, BUY_PRICES[item_name])

        if item_name not in self._inventory:
            self._farm.get_player().add_item((item_name, 0))
        else:
            self.update_inv_frame(item_name, False)
            self._inventory_frames[item_name].config(
                highlightbackground=INVENTORY_OUTLINE_COLOUR,
                highlightthickness=2)
        self.redraw()

    def sell_item(self, item_name: str) -> None:
        """
        The callback to be given to each ItemView for selling items.

        Args:
            item_name: the name of the item to sell
        """
        self._farm.get_player().sell(item_name, SELL_PRICES[item_name])

        if item_name not in self._inventory:
            self._inventory_frames[item_name].update(0, False)
        else:
            self.update_inv_frame(item_name, False)
        self.redraw()


def play_game(root: tk.Tk, map_file: str) -> None:
    """
    Construct the controller FarmGame instance and ensure the root window stays
    open listening for events.

    Args:
        root: the root Tk window
        map_file: The file path to the map file
    """
    FarmGame(root, map_file)
    root.mainloop()


def main() -> None:
    """
    Construct the root tk.Tk instance and calls play_game
    """
    window = tk.Tk()
    play_game(root=window, map_file="maps/map1.txt")


if __name__ == '__main__':
    main()
