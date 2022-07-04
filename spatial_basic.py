# people can be infected if people in the 3x3 square around them are infected
# recover completely with fixed probability each timestep

from enum import Enum, unique, auto
from operator import mod
import pprint as pretty_print
from re import A
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from random import randint
from PIL import Image

pprint = lambda x: pretty_print.pprint(x, width=500, compact=True)

@unique
class PersonState(Enum):
	SUSCEPTIBLE = auto()
	INFECTED = auto()
	RECOVERED = auto()

state_colors: dict[PersonState, tuple[int, int, int]] = {
	PersonState.SUSCEPTIBLE: (0, 255, 0),
	PersonState.INFECTED: (255, 0, 0),
	PersonState.RECOVERED: (0, 0, 255)
}

sir_beta = 0.5
sir_gamma = 1/7

def timestep(in_cells:  list[list[PersonState]]) -> tuple[list[list[PersonState]], tuple[int,int,int]]:
	new_cells = [[PersonState.SUSCEPTIBLE for x in range(len(in_cells))] for y in range(len(in_cells[0]))]

	susceptible_count = 0
	infected_count = 0
	recovered_count = 0

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			if in_cells[x][y] == PersonState.SUSCEPTIBLE:
				susceptible_count += 1
			elif in_cells[x][y] == PersonState.INFECTED:
				infected_count += 1
			elif in_cells[x][y] == PersonState.RECOVERED:
				recovered_count += 1

	total = susceptible_count + infected_count + recovered_count

	transmission_probability = sir_beta
	recovery_probability = sir_gamma

	print(transmission_probability, recovery_probability)

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			if in_cells[x][y] == PersonState.RECOVERED:
				new_cells[x][y] = PersonState.RECOVERED
				continue

			if in_cells[x][y] == PersonState.INFECTED:
				if randint(0, 100) < recovery_probability * 100:
					new_cells[x][y] = PersonState.RECOVERED
				else:
					new_cells[x][y] = PersonState.INFECTED
				continue
			
			surrounding_states = []
			if x == 0:
				if y == 0:
					surrounding_states = [in_cells[x][y+1], in_cells[x+1][y], in_cells[x+1][y+1]]
				elif y == len(in_cells[0]) - 1:
					surrounding_states = [in_cells[x][y-1], in_cells[x+1][y], in_cells[x+1][y-1]]
				else:
					surrounding_states = [in_cells[x][y-1], in_cells[x][y+1], in_cells[x+1][y-1], in_cells[x+1][y], in_cells[x+1][y+1]]
			elif x == len(in_cells) - 1:
				if y == 0:
					surrounding_states = [in_cells[x][y+1], in_cells[x-1][y], in_cells[x-1][y+1]]
				elif y == len(in_cells[0]) - 1:
					surrounding_states = [in_cells[x][y-1], in_cells[x-1][y], in_cells[x-1][y-1]]
				else:
					surrounding_states = [in_cells[x][y-1], in_cells[x][y+1], in_cells[x-1][y-1], in_cells[x-1][y], in_cells[x-1][y+1]]
			else:
				if y == 0:
					surrounding_states = [in_cells[x-1][y], in_cells[x+1][y], in_cells[x][y+1], in_cells[x-1][y+1], in_cells[x+1][y+1]]
				elif y == len(in_cells[0]) - 1:
					surrounding_states = [in_cells[x-1][y], in_cells[x+1][y], in_cells[x][y-1], in_cells[x-1][y-1], in_cells[x+1][y-1]]
				else:
					surrounding_states = [in_cells[x-1][y-1], in_cells[x-1][y], in_cells[x-1][y+1], in_cells[x][y-1], in_cells[x][y+1], in_cells[x+1][y-1], in_cells[x+1][y], in_cells[x+1][y+1]]
			
			total_surrounding_infected = sum(1 if state == PersonState.INFECTED else 0 for state in surrounding_states)
			this_infected_probability = transmission_probability * total_surrounding_infected
			if randint(0, 100) < this_infected_probability * 100:
				new_cells[x][y] = PersonState.INFECTED
	
	return (new_cells, (susceptible_count, infected_count, recovered_count))

def cells_to_image(in_cells: list[list[PersonState]], outfile):
	img = Image.new("RGB", (len(in_cells), len(in_cells[0])))
	data = img.load()

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			data[x, y] = state_colors[in_cells[x][y]]

	img.save(outfile)

def main():
	cell_width = 100
	cell_height = 100

	cells = [[PersonState.SUSCEPTIBLE for x in range(cell_width)] for y in range(cell_height)]
	for i in range(15):
		cells[randint(0, cell_height-1)][randint(0, cell_width-1)] = PersonState.INFECTED

	counts = []

	cells_to_image(cells, "out/basic_spatial/0.png")
	for i in range(0,200):
		cells, count = timestep(cells)
		counts.append(count)
		cells_to_image(cells, f"out/basic_spatial/{i+1}.png")
	
	fig, ax = plt.subplots()
	ax.plot(counts)
	ax.set_ylabel("Number of people")
	fig.legend(("S", "I", "R"))
	plt.savefig("graphs/basic_spatial.png")
	plt.show()

if __name__ == "__main__":
	main()