from enum import Enum
import random
import tkinter
import statistics

CELL_SIZE = 18
GENERATION_TIME = 30
CELL_DATA_FILE_PATH = 'cell_data.dat'
MAX_WIND_SPEED = 3
POLUTION_THREASHOLD = 0.4
POLLUTION_TEMPRATURE_DIFF = 1.0
RAIN_TEMPRATURE_DIFF = 2
RAIN_POLLUTION_FACTOR = 1.5
DEATH_TEMPRATURE = 60
DEATH_POLLUTION = 1.0
CHANCE_TO_CHANGE_WIND_DIRECTION = 0.4
CHANCE_TO_INCREASE_CHANCE_OF_RAIN = 0.5
CHANCE_OF_RAIN_DIFF = 0.1
RAIN_WILL_FALL = 0.5

CELL_TEMPRATURES = []
CELL_AIR_POLLUTIONS = []

PER_GENERATION_TEMPRATURE_AVG = []
PER_GENERATION_POLLUTION_AVG = []


class CellType(Enum):
    """
        Basic cell type
    """

    def __init__(self, min_temp, max_temp, color, air_pollution_factor):
        # Minimum starting temprature
        self.min_temp = min_temp
        # Maxsimum starting temprature
        self.max_temp = max_temp
        self.color = color                                  # Color to dispaly
        # Air pollution to be added/deleted each generation
        self.air_pollution_factor = air_pollution_factor

    LAND = 20, 40, '#f5a142', 0
    CITY = 20, 35, '#615f5b', 0.01
    FOREST = 20, 30, '#3f9949', -0.2
    SEA = 15, 20, '#4d53c4', 0
    ICEBERG = -7, -3, '#e6e7f0', 0

    @classmethod
    def get_by_letter(self, cell_type_letter):
        """
            Returns the cell type by letter that had been read from the input file
        """
        return list(filter(lambda cell_type: cell_type.name.startswith(cell_type_letter), list(CellType)))[0]

    def normal_temrature(self):
        """
            Returns the normal temprature of the cell type
        """
        return (self.min_temp + self.max_temp) / 2


class WindDirection(Enum):
    NORTH = 0   # UP
    EAST = 1    # RIGHT
    SOUTH = 2   # DOWN
    WEST = 3    # LEFT


class CellState:
    """
        Class that holds the cell state
    """

    def __init__(self, cell_type, temprature, wind_direction, wind_speed, chance_of_rain, air_pollution):
        self.cell_type = cell_type
        self.temprature = temprature
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed
        self.chance_of_rain = chance_of_rain
        self.air_pollution = air_pollution


class Cell:
    """
        Encapsulated Cell operations, current and next cell state and cell visual data

    """

    def __init__(self, x, y, cell_type_letter, wind_direction=WindDirection.NORTH, wind_speed=1, chance_of_rain=0.3, air_pollution=0):
        cell_type = CellType.get_by_letter(cell_type_letter)
        self.current_cell_state = CellState(cell_type, random.randint(cell_type.min_temp, cell_type.max_temp),
                                            wind_direction, wind_speed, chance_of_rain, air_pollution)
        self.next_generation_cell_state = self.current_cell_state
        self.x = x
        self.y = y
        self.rect = None
        self.text = None

    def commit_next_generation(self):
        self.current_cell_state = self.next_generation_cell_state

    def get_color(self):
        return self.current_cell_state.cell_type.color

    def calculate_cell_next_state(self, neighbors):
        self._calculate_next_gen_temprature()
        self._calculate_next_gen_cell_type()
        self._calculate_next_gen_pollution(neighbors)
        self._calculate_next_gen_winds(neighbors)
        self._calculate_next_gen_rain()

        # Makes sure we don't underflow or overflow the cell's next state air pollution
        if self.next_generation_cell_state.air_pollution > 1.0:
            self.next_generation_cell_state.air_pollution = 1.0
        elif self.next_generation_cell_state.air_pollution < -1.0:
            self.next_generation_cell_state.air_pollution = -1.0

    def _calculate_next_gen_temprature(self):
        """
            Calculates the cell's next generation temprature, affected by the cell's current air pollution.
            If it's over the threashhold, the temprature goes up. 
            If under, the temprature gets closer (lower or higher) to the cell's type's normal temprature
        """
        if self.current_cell_state.air_pollution >= POLUTION_THREASHOLD:
            self.next_generation_cell_state.temprature = self.current_cell_state.temprature + \
                POLLUTION_TEMPRATURE_DIFF
        else:
            if self.current_cell_state.temprature > self.current_cell_state.cell_type.normal_temrature():
                self.next_generation_cell_state.temprature = self.current_cell_state.temprature - \
                    POLLUTION_TEMPRATURE_DIFF
            elif self.current_cell_state.temprature < self.current_cell_state.cell_type.normal_temrature():
                self.next_generation_cell_state.temprature = self.current_cell_state.temprature + \
                    POLLUTION_TEMPRATURE_DIFF

    def _calculate_next_gen_cell_type(self):
        """
            Calculates the cell's next cell type. Depending on the cell's current temprature and pollution 
        """
        if self.current_cell_state.cell_type == CellType.SEA:
            if self.current_cell_state.temprature > 100:
                self.next_generation_cell_state.cell_type = CellType.LAND
            elif self.current_cell_state.temprature < 0:
                self.next_generation_cell_state.cell_type = CellType.ICEBERG

        elif self.current_cell_state.cell_type == CellType.ICEBERG:
            if self.current_cell_state.temprature > 0:
                self.next_generation_cell_state.cell_type = CellType.SEA

        if self.current_cell_state.cell_type in [CellType.FOREST, CellType.CITY]:
            if self.current_cell_state.temprature >= DEATH_TEMPRATURE or self.current_cell_state.air_pollution >= DEATH_POLLUTION:
                self.next_generation_cell_state.cell_type = CellType.LAND

    def _calculate_next_gen_rain(self):
        """
            Calculates cell's next chance of rain depending on random chance and the current chance of rain.
            If it currently rains, the temprature and pollution goes down
        """
        if self.current_cell_state.chance_of_rain >= RAIN_WILL_FALL:
            self.next_generation_cell_state.air_pollution = self.next_generation_cell_state.air_pollution / \
                RAIN_POLLUTION_FACTOR
            self.next_generation_cell_state.temprature = self.next_generation_cell_state.temprature - \
                RAIN_TEMPRATURE_DIFF
            self.next_generation_cell_state.chance_of_rain = 0

        elif random.random() > CHANCE_TO_INCREASE_CHANCE_OF_RAIN:
            self.next_generation_cell_state.chance_of_rain = self.current_cell_state.chance_of_rain + \
                CHANCE_OF_RAIN_DIFF

    def _calculate_next_gen_pollution(self, neighbors):
        """
            Calculates cell's next air pollution depending on neighbors' pollution.
            The current cell "takes" all his neighbors pollution
        """
        # Add or subtract air pollution as a dependance of current cell type
        total_pollution = self.current_cell_state.air_pollution + \
            self.current_cell_state.cell_type.air_pollution_factor

        if neighbors:
            for neighbour in neighbors:
                if neighbour.current_cell_state.wind_speed > 0:
                    total_pollution += neighbour.current_cell_state.air_pollution / \
                        neighbour.current_cell_state.wind_speed

            if self.current_cell_state.wind_speed > 2:
                total_pollution = 0

            total_pollution = (total_pollution / len(neighbors))

        self.next_generation_cell_state.air_pollution = total_pollution

    def _calculate_next_gen_winds(self, neighbors):
        """
            Calculates cell's next wind speed and direction. 
            Depending on the temprature change between the previous and next temprature and the neighbors' winds.
            In random chance the wind changes direction.
        """
        self.next_generation_cell_state.wind_speed = abs(
            self.current_cell_state.temprature - self.next_generation_cell_state.temprature) * 1.0

        if not neighbors:
            return

        total_wind_speed = 0

        for neighbour in neighbors:
            total_wind_speed = total_wind_speed + neighbour.current_cell_state.wind_speed

        self.next_generation_cell_state.wind_speed = round(
            self.next_generation_cell_state.wind_speed + int(total_wind_speed / len(neighbors)))

        if self.next_generation_cell_state.wind_speed > MAX_WIND_SPEED:
            self.next_generation_cell_state.wind_speed = MAX_WIND_SPEED

        if random.random() <= CHANCE_TO_CHANGE_WIND_DIRECTION:
            new_wind_directions = list(WindDirection)
            new_wind_directions.remove(self.current_cell_state.wind_direction)

            self.next_generation_cell_state.wind_direction = random.choice(
                new_wind_directions)


class CellGrid:
    """
        The grid holding all of the cells of the automata.
    """

    def __init__(self, height, width, cells_data_file_path):
        self.height = height
        self.width = width

        # Creates an empty self.length * self.length matrix
        self.cells = [[0]*self.width for i in range(self.height)]
        self._init_automata_cells(cells_data_file_path)

    def _init_automata_cells(self, cells_data_file_path):
        """
            Reads initial data file and inites the grid's cells accordingly.
        """
        with open(cells_data_file_path, 'r') as cells_data_file:
            cells_data_rows = cells_data_file.readlines()
            for row_index, row in enumerate(cells_data_rows):
                for cell_index, single_cell_data in enumerate(row.strip()):
                    self.cells[row_index][cell_index] = Cell(
                        row_index, cell_index, single_cell_data, random.choice(list(WindDirection)), random.randint(1, MAX_WIND_SPEED))

    def _get_neighbors_in_radius(self, cell, radius):
        """
            Returns the cell's neighbors in all directions in a certain distance from the cell
        """
        return [
            # NORTH neighbor at given radius
            self.cells[cell.x][(cell.y + radius) % self.width],
            # EAST neighbor at given radius
            self.cells[(cell.x + radius) % self.height][cell.y],
            # SOUTH neighbor at given radius
            self.cells[cell.x][(cell.y - radius) % self.width],
            # WEST neighbor at given radius
            self.cells[(cell.x - radius) % self.height][cell.y]
        ]

    def _are_cell_neighbors(self, affected_cell, affecting_cell):
        """
            Filter function to verify that the wind in a potential neighboring cell reaches the current cell and deserves to be call it's neighbor
        """
        incoming_wind_direction = affecting_cell.current_cell_state.wind_direction
        incoming_wind_speed = affecting_cell.current_cell_state.wind_speed

        if incoming_wind_direction == WindDirection.NORTH:
            return (affecting_cell.y - affected_cell.y) % self.height <= incoming_wind_speed and affected_cell.x == affecting_cell.x

        if incoming_wind_direction == WindDirection.EAST:
            return (affecting_cell.x + affecting_cell.x) % self.width <= incoming_wind_speed and affected_cell.y == affecting_cell.y

        if incoming_wind_direction == WindDirection.SOUTH:
            return (affected_cell.y + affecting_cell.y) % self.height <= incoming_wind_speed and affected_cell.x == affecting_cell.x

        if incoming_wind_direction == WindDirection.WEST:
            return (affected_cell.x - affecting_cell.x) % self.width <= incoming_wind_speed and affected_cell.y == affecting_cell.y

    def _get_cell_neighborhood(self, cell):
        """
            Depending on the neighboring cells' wind directions and speed, returns the cells around the current cell that affect it.
            e.g: 
                If the wind speed of the cell below me is 1 and it's wind direction is N, it affects me.
                If the wind speed of the cell two cells to my right me is 2 and it's wind direction is W, it affects me.
                If the wind speed of the cell above me is 1 and it's wind direction is N, it doesn't affects me.
        """
        cell_neighborhood = []
        for radius in range(MAX_WIND_SPEED):
            cell_neighborhood.extend(
                list(filter(lambda potential_neighbor: self._are_cell_neighbors(cell, potential_neighbor),
                            self._get_neighbors_in_radius(cell, radius + 1))))
        return cell_neighborhood

    def run_generation(self):
        """
            Calculates the next generation for all cells and commits them after all of the cells' generation is calculated
        """

        temp_gen_temp_sum = 0.0
        temp_gen_pollution_sum = 0.0

        for row in self.cells:
            for cell in row:
                cell.calculate_cell_next_state(
                    self._get_cell_neighborhood(cell))

                CELL_TEMPRATURES.append(cell.current_cell_state.temprature)
                CELL_AIR_POLLUTIONS.append(
                    cell.current_cell_state.air_pollution)

                temp_gen_temp_sum += cell.current_cell_state.temprature
                temp_gen_pollution_sum += cell.current_cell_state.air_pollution

        PER_GENERATION_TEMPRATURE_AVG.append(
            temp_gen_temp_sum / (self.height * self.width))
        PER_GENERATION_POLLUTION_AVG.append(
            temp_gen_pollution_sum / (self.height * self.width))

        for row in self.cells:
            for cell in row:
                cell.commit_next_generation()


class CellularAutomata:
    """
        Holds the cell grid, runs and displays the generations of the automata
    """

    def __init__(self, cells_data_file_path, height=50, width=50, generation_count=365):
        self.height = height
        self.width = width
        self.cell_grid = CellGrid(
            self.height, self.width, cells_data_file_path)
        self.generation_count = generation_count
        self.current_generation = 0

    def start(self):
        self.root = tkinter.Tk()
        self.root.title("Maman 11 - Edoe Tsur")
        self.label = tkinter.Label(self.root)
        self.label.pack()
        self.canvas = tkinter.Canvas(
            self.root, height=self.height*CELL_SIZE, width=self.width*CELL_SIZE)
        self.canvas.pack()
        self.root.after(GENERATION_TIME, self._update_generation_visual)
        self.root.mainloop()

    def _update_generation_visual(self):
        for row in self.cell_grid.cells:
            for cell in row:
                self._generate_cell_visual(cell)

        if (self.current_generation < self.generation_count):
            self.cell_grid.run_generation()
            self.current_generation = self.current_generation + 1
            self.label.config(
                text="Generation {}".format(self.current_generation))
            self.root.after(GENERATION_TIME, self._update_generation_visual)

        else:
            self.label.config(
                text="Last Generation Reached: {}".format(self.current_generation))

    def _generate_cell_visual(self, cell):
        if not cell.rect:
            cell.rect = self.canvas.create_rectangle(
                cell.x * CELL_SIZE,
                cell.y * CELL_SIZE,
                (cell.x + 1) * CELL_SIZE,
                (cell.y + 1) * CELL_SIZE,
                fill=cell.get_color())
        else:
            self.canvas.itemconfig(cell.rect, fill=cell.get_color())

        if not cell.text:
            cell.text = self.canvas.create_text(
                (cell.x + 0.5) * CELL_SIZE,
                (cell.y + 0.5) * CELL_SIZE,
                text=int(cell.current_cell_state.temprature),
                font=("Comic Sans MS", 6, "bold"))
        else:
            self.canvas.itemconfig(
                cell.text, text=int(cell.current_cell_state.temprature))


def main():
    cellular_automata = CellularAutomata(CELL_DATA_FILE_PATH)
    cellular_automata.start()

    print("Air pollution factor: {}".format(
        CellType.CITY.air_pollution_factor))
    print("Temprature Data:\n\tMax: {:.2f}\n\tMin: {:.2f}\n\tAvg: {:.2f}\n\tStdev: {:.2f}".format(
        max(CELL_TEMPRATURES), min(CELL_TEMPRATURES), sum(CELL_TEMPRATURES) / float((len(CELL_TEMPRATURES))), statistics.stdev(CELL_TEMPRATURES)))

    print("Air Pollution Data:\n\tMax: {:.2f}\n\tMin: {:.2f}\n\tAvg: {:.2f}\n\tStdev: {:.2f}".format(
        max(CELL_AIR_POLLUTIONS), min(CELL_AIR_POLLUTIONS), sum(CELL_AIR_POLLUTIONS) / float((len(CELL_AIR_POLLUTIONS))), statistics.stdev(CELL_AIR_POLLUTIONS)))

    with open("tempratures.dat", "w") as tempratures_file:
        tempratures_file.write(str(PER_GENERATION_TEMPRATURE_AVG))

    with open("pollution.dat", "w") as pollutions_file:
        pollutions_file.write(str(PER_GENERATION_POLLUTION_AVG))


if __name__ == '__main__':
    main()
