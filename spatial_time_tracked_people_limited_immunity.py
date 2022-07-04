# people can be infected if people in the 3x3 square around them are infected
# recover in random time between 7 and 12 timesteps
# after random time between 5 and 10 timesteps they become susceptible again

from enum import Enum, unique, auto
from operator import mod
import pprint as pretty_print
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from random import randint, random
from PIL import Image

pprint = lambda x: pretty_print.pprint(x, width=500, compact=True)

class InfetedState:
	def __init__(self, days = 1):
		self.day = days
	def color(self):
		return (255, 0, 0)

class SusceptibleState:
	def __init__(self):
		return
	def color(self):
		return (0, 255, 0)

class RecoveredState:
	def __init__(self, days = 1):
		self.day = days
	def color(self):
		return (0, 0, 255)

sir_beta = lambda t: 0.5
immunity_length = lambda: randint(5, 10)

def timestep(in_cells, time: int):
	new_cells = [[SusceptibleState() for x in range(len(in_cells))] for y in range(len(in_cells[0]))]

	susceptible_count = 0
	infected_count = 0
	recovered_count = 0

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			match in_cells[x][y]:
				case SusceptibleState():
					susceptible_count += 1
				case InfetedState(day=_):
					infected_count += 1
				case RecoveredState():
					recovered_count += 1

	total = susceptible_count + infected_count + recovered_count

	transmission_probability = sir_beta(time)

	print(transmission_probability)

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			match in_cells[x][y]:
				case RecoveredState(day=days_recovered):
					if days_recovered > immunity_length():
						new_cells[x][y] = SusceptibleState()
					else:
						new_cells[x][y] = RecoveredState(days_recovered + 1)

				case InfetedState(day=days_infected):
					if days_infected < 7:
						new_cells[x][y] = InfetedState(days_infected + 1)
					else:
						days_left_max = 13 - days_infected
						recovery_today_probability = 1 / randint(1, days_left_max)
						if random() < recovery_today_probability:
							new_cells[x][y] = RecoveredState()
						else:
							new_cells[x][y] = InfetedState(days_infected + 1)
				
				case SusceptibleState():
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
					
					total_surrounding_infected = sum(1 if isinstance(state, InfetedState) else 0 for state in surrounding_states)
					this_infected_probability = transmission_probability * total_surrounding_infected
					if  random() < this_infected_probability:
						new_cells[x][y] = InfetedState()
			
	
	return (new_cells, (susceptible_count, infected_count, recovered_count))

def cells_to_image(in_cells, outfile):
	img = Image.new("RGB", (len(in_cells), len(in_cells[0])))
	data = img.load()

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			data[x, y] = in_cells[x][y].color()

	img.save(outfile)

def main():
	cell_width = 100
	cell_height = 100

	cells = [[SusceptibleState() for x in range(cell_width)] for y in range(cell_height)]
	for i in range(15):
		x = randint(0, cell_width - 1)
		y = randint(0, cell_height - 1)
		cells[x][y] = InfetedState()

	counts = []

	cells_to_image(cells, "out/time_tracked_limited_immunity/0.png")
	for i in range(0,200):
		cells, count = timestep(cells, i)
		counts.append(count)
		cells_to_image(cells, f"out/time_tracked_limited_immunity/{i+1}.png")
	
	fig, ax = plt.subplots()
	ax.plot(counts)
	ax.set_ylabel("Number of people")
	fig.legend(("S", "I", "R"))
	plt.savefig("graphs/time_tracked_limited_immunity.png")
	plt.show()

if __name__ == "__main__":
	main()