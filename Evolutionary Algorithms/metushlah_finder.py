import random
import tkinter
from bitarray import bitarray
from numpy import random
import uuid
import re

TEST_NAME = uuid.uuid1()
GRID_SIZE = 50
CHROMOSOME_LENGTH = GRID_SIZE**2
CELL_SIZE = 10
MAX_INITIAL_CONFIGURATION_SIZE = 20
POPULATION_SIZE = 100
MUTATION_CHANCE = 0.05
CROSSOVER_CHANCE = 0.90
ELITISEM_PRECENTAGE = 0.1
MAX_GENERATIONS = 1000
GENERATIONS_STALEMATE = 500
ON = 1
OFF = 0


class GameOfLifeSimulator:
    def __init__(self, chromosome):
        self.chromosome = chromosome
        self.cell_grid = [
            chromosome[GRID_SIZE*row: GRID_SIZE * (row+1)] for row in range(GRID_SIZE)]
        self.current_generation = 0
        self.grid_hashes_history = []


    def run(self):
        cell_grid_hash = None
        while cell_grid_hash not in self.grid_hashes_history: 
            self.grid_hashes_history.append(cell_grid_hash)

            self.run_generation()
            cell_grid_hash = hash(
                ''.join([cells_row.to01() for cells_row in self.cell_grid]))


    def run_generation(self):
        new_grid = [bitarray('0' * GRID_SIZE) for _ in range(GRID_SIZE)]
        for row in range(GRID_SIZE):
            for column in range(GRID_SIZE):
                alive_neighbors = 0
                # Checks cell to left
                if (column > 0):
                    if (self.cell_grid[row][column-1] == ON):
                        alive_neighbors += 1
                # Checks cell below
                if (row < GRID_SIZE - 1):
                    if (self.cell_grid[row+1][column] == ON):
                        alive_neighbors += 1
                # Checks cell to bottom right
                if (row < GRID_SIZE - 1 and column < GRID_SIZE - 1):
                    if (self.cell_grid[row+1][column+1] == ON):
                        alive_neighbors += 1
                # Checks cell to bottom left
                if (row < GRID_SIZE - 1 and column > 0):
                    if (self.cell_grid[row+1][column-1] == ON):
                        alive_neighbors += 1
                # Checks cell to right
                if (column < GRID_SIZE - 1):
                    if (self.cell_grid[row][column+1] == ON):
                        alive_neighbors += 1
                # Checks cell to top left
                if (row > 0 and column > 0):
                    if (self.cell_grid[row-1][column-1] == ON):
                        alive_neighbors += 1
                # Checks cell above
                if (row > 0):
                    if (self.cell_grid[row-1][column] == ON):
                        alive_neighbors += 1
                # Checks cell to top right
                if (row != 0 and column != GRID_SIZE - 1):
                    if (self.cell_grid[row-1][column+1] == ON):
                        alive_neighbors += 1

                # Apply Conway's rules
                if self.cell_grid[row][column] == ON:
                    if (alive_neighbors < 2) or (alive_neighbors > 3):
                        new_grid[row][column] = OFF
                    else:
                        new_grid[row][column] = ON
                else:
                    if alive_neighbors == 3:
                        new_grid[row][column] = ON
                    else:
                        new_grid[row][column] = OFF
        
        self.cell_grid = new_grid
        self.current_generation = self.current_generation + 1


class ChromosomeVisualiser:
    def __init__(self, i=''):
        self.grid_visual = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        self.root = tkinter.Tk()

        self.root.title("Maman 12 - Edoe Tsur" + i)
        self.label = tkinter.Label(self.root)
        self.label.pack()
        self.canvas = tkinter.Canvas(
            self.root, height=GRID_SIZE*CELL_SIZE, width=GRID_SIZE*CELL_SIZE)
        self.canvas.pack()


    def generate_grid_visual(self, current_generation, chromosome):
        self.label.config(text="Generation {}".format(current_generation))
        cell_grid = [chromosome[GRID_SIZE*row: GRID_SIZE *
                                (row+1)] for row in range(GRID_SIZE)]

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.grid_visual[x][y]:
                    self.grid_visual[x][y] = self.canvas.create_rectangle(
                        y * CELL_SIZE,
                        x * CELL_SIZE,
                        (y + 1) * CELL_SIZE,
                        (x + 1) * CELL_SIZE,
                        fill=("#FFFFFF" if cell_grid[x][y] else "#000000"))
                else:
                    self.canvas.itemconfig(self.grid_visual[x][y], fill=(
                        "#FFFFFF" if cell_grid[x][y] else "#000000"))

        self.canvas.update()


class MetushelahFinder:
    def __init__(self, show_best_chromosome=False):
        self.show_best_chromosome = show_best_chromosome
        self.visualiser = ChromosomeVisualiser()
        self.generation_fitness_maxs = []
        self.generation_fitness_mins = []
        self.generation_fitness_avgs = []


    def generate_chromosome_and_fitness(self):
        chromosome = bitarray(CHROMOSOME_LENGTH)
        chromosome.setall(0)

        initial_configuration_size = random.randint(
            1, MAX_INITIAL_CONFIGURATION_SIZE)
        for _ in range(initial_configuration_size):
            alive_cell_index = random.randint(0, CHROMOSOME_LENGTH - 1)
            while chromosome[alive_cell_index]:
                alive_cell_index = random.randint(0, CHROMOSOME_LENGTH - 1)
            chromosome[alive_cell_index] = 1

        return (chromosome, 0)


    def generate_initial_population(self):
        return [self.generate_chromosome_and_fitness() for _ in range(POPULATION_SIZE)]


    def calculate_chromosome_fitness(self, chromosome):
        game_of_life_simulator = GameOfLifeSimulator(chromosome)
        game_of_life_simulator.run()
        return game_of_life_simulator.current_generation


    def crossover(self, parents):
        new_chromosome1, new_chromosome2 = self.possible_crossover(parents)
        alive_cells_count1, alive_cells_count2 = new_chromosome1.count(), new_chromosome2.count()

        while alive_cells_count1 > MAX_INITIAL_CONFIGURATION_SIZE or alive_cells_count2 > MAX_INITIAL_CONFIGURATION_SIZE:
            new_chromosome1, new_chromosome2 = self.possible_crossover(parents)
            alive_cells_count1, alive_cells_count2 = new_chromosome1.count(), new_chromosome2.count()
        return new_chromosome1, new_chromosome2


    def possible_crossover(self, parents):
        crossover_position = int(random.random() * CHROMOSOME_LENGTH)
        return (
            parents[0][:crossover_position]+parents[1][crossover_position:],
            parents[1][:crossover_position]+parents[0][crossover_position:])


    def mutate(self, chromosome):
        alive_cells_count = chromosome.count()

        # Making sure not all mutations concentrate in the beggining of the chromosome
        chromosome_mutation_order = [i for i in range(CHROMOSOME_LENGTH)]
        random.shuffle(chromosome_mutation_order)

        for chromosome_mutation_index in chromosome_mutation_order:
            if random.random() < MUTATION_CHANCE:
                if chromosome[chromosome_mutation_index] == ON:
                    chromosome[chromosome_mutation_index] = not chromosome[chromosome_mutation_index]
                    alive_cells_count -= 1
                elif alive_cells_count < MAX_INITIAL_CONFIGURATION_SIZE:
                    # Make sure we don't turn on too many cells
                    chromosome[chromosome_mutation_index] = not chromosome[chromosome_mutation_index]
                    alive_cells_count += 1
        return chromosome


    def calculate_population_fitness(self, current_population):
        population_fitness_map = [(chromosome, self.calculate_chromosome_fitness(
            chromosome)) for chromosome, _ in current_population]
        population_fitness_map.sort(
            key=lambda chromosome_fitness: chromosome_fitness[1], reverse=True)
        return population_fitness_map


    def choose_parents(self, population_fitness_map):
        first_parent = second_parent = None

        # First parent
        total_population_fitness = sum(
            chromosome_with_fitness[1] for chromosome_with_fitness in population_fitness_map)
        selection_probabillities = [chromosome_with_fitness[1] /
                                    total_population_fitness for chromosome_with_fitness in population_fitness_map]
        first_parent = population_fitness_map[random.choice(
            len(population_fitness_map), p=selection_probabillities)]

        population_fitness_map.remove(first_parent)

        # Second parent
        total_population_fitness = sum(
            chromosome_with_fitness[1] for chromosome_with_fitness in population_fitness_map)
        selection_probabillities = [chromosome_with_fitness[1] /
                                    total_population_fitness for chromosome_with_fitness in population_fitness_map]
        second_parent = population_fitness_map[random.choice(
            len(population_fitness_map), p=selection_probabillities)]

        while first_parent == second_parent:
            second_parent = population_fitness_map[random.choice(
                len(population_fitness_map), p=selection_probabillities)]

        # Sort parents by fitness
        return [first_parent[0], second_parent[0]] if first_parent[1] > second_parent[1] else [second_parent[0], first_parent[0]]


    def generate_next_generation_population(self, current_population):
        next_generation_population = []

        # Move ELITISEM_PRECENTAGE of the current population to the next generation
        elitisem_amount = round(ELITISEM_PRECENTAGE * POPULATION_SIZE)
        next_generation_population = current_population[:elitisem_amount]

        for _ in range(int(POPULATION_SIZE/2)):
            parents = self.choose_parents(current_population)

            # If crossover does not happend, choose the fitter parent
            if random.random() < CROSSOVER_CHANCE:
                new_chromosome1, new_chromosome2 = self.crossover(parents)
            else:
                new_chromosome1, new_chromosome2 = parents

            new_chromosome1 = self.mutate(new_chromosome1)
            new_chromosome2 = self.mutate(new_chromosome2)

            next_generation_population.append(
                (new_chromosome1, self.calculate_chromosome_fitness(new_chromosome1)))
            next_generation_population.append(
                (new_chromosome2, self.calculate_chromosome_fitness(new_chromosome2)))

        # Keeping only fittest chromosomes
        next_generation_population.sort(
            key=lambda chromosome: chromosome[1], reverse=True)
        next_generation_population = next_generation_population[:POPULATION_SIZE]

        return next_generation_population


    def handle_statistics(self, current_generation, max_fitness, min_fitness, avg_fitness):
        # Calc statistics
        self.generation_fitness_maxs.append((current_generation, max_fitness))
        self.generation_fitness_mins.append((current_generation, min_fitness))
        self.generation_fitness_avgs.append((current_generation, avg_fitness))


    def run(self):
        print("Running initial generation")
        current_population = self.calculate_population_fitness(
            self.generate_initial_population())

        best_fitness = 0
        same_fitness_count = 0

        for current_generation in range(1, MAX_GENERATIONS):
            print("Running generation {}".format(current_generation))

            # Stop if we're in stalemate
            new_best_fitness = current_population[0][1]
            if best_fitness == new_best_fitness:
                same_fitness_count += 1
            else:
                # Write every new record to a file using the format of golly pattern files
                with open('{}_{}.txt'.format(TEST_NAME, new_best_fitness), 'w') as f:
                    f.write('x={},y={}\n'.format(GRID_SIZE, GRID_SIZE) + re.sub("(.{"+str(GRID_SIZE) + "})", "\\1$\\n", current_population[0][0].to01().replace('0', 'b').replace('1', 'o'), 0, re.DOTALL))
                same_fitness_count = 0
            if same_fitness_count >= GENERATIONS_STALEMATE:
                print("Stopping after {} generations without any improvement (stalemate).".format(
                    same_fitness_count))
                break

            best_fitness = new_best_fitness

            current_population = self.generate_next_generation_population(
                current_population)

            self.handle_statistics(current_generation, current_population[0][1], current_population[-1][1],
                                   float(sum([chromosome_with_fitness[1] for chromosome_with_fitness in current_population]))/len(current_population))

            print("Finished Generation {}, Best Fitness: {}".format(
                current_generation, current_population[0][1]))
            if self.show_best_chromosome:
                self.visualiser.generate_grid_visual(
                    current_generation, current_population[0][0])


if __name__ == '__main__':    
    metushelah_finder = MetushelahFinder()
    try:
        metushelah_finder.run()
    finally:
        with open('{}_avg.txt'.format(TEST_NAME), 'w') as f:
            for gen, x in metushelah_finder.generation_fitness_avgs:
                f.write("{}, {}\n".format(gen, x))
        with open('{}_min.txt'.format(TEST_NAME), 'w') as f:
            for gen, x in metushelah_finder.generation_fitness_mins:
                f.write("{}, {}\n".format(gen, x))
        with open('{}_max.txt'.format(TEST_NAME), 'w') as f:
            for gen, x in metushelah_finder.generation_fitness_maxs:
                f.write("{}, {}\n".format(gen, x))
