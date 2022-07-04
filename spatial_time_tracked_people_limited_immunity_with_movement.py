# 
# recover in random time between 7 and 12 timesteps
# after random time between 5 and 10 timesteps they become susceptible again

# INCOMPLETE

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

class VaccinatedState:
	def __init__(self, days = 1):
		self.day = days
	def color(self):
		return (0, 0, 255)

# 0 - home, 1 - work/school
place_betas = [0.03, 0.00005]
immunity_length = lambda: randint(20, 25)
v_immunity_length = lambda: randint(50, 100)

def timestep_single_place(in_cells, time: int, place_num: int, places):
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

	transmission_probability = place_betas[place_num]

	print(transmission_probability)

	# 2 pass process
	# 1st pass - find all places with infected people and calculate probability of being infected by going to that place
	# 2nd pass - update state for people based on probability of being infected

	# pass 1
	infected_places = [0 for x in range(len(places[place_num]))]

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			match in_cells[x][y]:
				case InfetedState(day=_):
					dist = 100000000
					closest_place = None
					# find closest place
					for (idx, place) in enumerate(places[place_num]):
						dist_to_place = abs(x - place[0]) + abs(y - place[1])
						if dist_to_place < dist:
							dist = dist_to_place
							closest_place = idx
							break
					# update probability of place being 'infected'
					infected_places[closest_place] = 1

	print(infected_places)

	# pass 2
	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			match in_cells[x][y]:
				case RecoveredState(day=days_recovered):
					if place_num == 0:
						if days_recovered > immunity_length():
							new_cells[x][y] = SusceptibleState()
						else:
							new_cells[x][y] = RecoveredState(days_recovered + 1)
					else:
						new_cells[x][y] = RecoveredState(days_recovered)
				
				case VaccinatedState(day=days_recovered):
					if place_num == 0:
						if days_recovered > v_immunity_length():
							new_cells[x][y] = SusceptibleState()
						else:
							new_cells[x][y] = VaccinatedState(days_recovered + 1)
					else:
						new_cells[x][y] = VaccinatedState(days_recovered)

				case InfetedState(day=days_infected):
					if place_num == 0:
						if days_infected < 7:
							new_cells[x][y] = InfetedState(days_infected + 1)
						else:
							days_left_max = 13 - days_infected
							recovery_today_probability = 1 / randint(1, days_left_max)
							if random() < recovery_today_probability:
								new_cells[x][y] = RecoveredState()
							else:
								new_cells[x][y] = InfetedState(days_infected + 1)
					else:
						new_cells[x][y] = InfetedState(days_infected)
				
				case SusceptibleState():
					dist = 100000000
					closest_place = None
					# find closest place
					for (idx, place) in enumerate(places[place_num]):
						dist_to_place = abs(x - place[0]) + abs(y - place[1])
						if dist_to_place < dist:
							dist = dist_to_place
							closest_place = idx
							break
					# calculate probability of being infected by said place
					infection_probability = infected_places[closest_place] * transmission_probability
					if random() < infection_probability:
						new_cells[x][y] = InfetedState()
					else:
						new_cells[x][y] = SusceptibleState()
			
	
	return (new_cells, (susceptible_count, infected_count, recovered_count))

def cells_to_image(in_cells, outfile):
	img = Image.new("RGB", (len(in_cells), len(in_cells[0])))
	data = img.load()

	for x in range(len(in_cells)):
		for y in range(len(in_cells[0])):
			data[x, y] = in_cells[x][y].color()

	img.save(outfile)

def places_to_image(width, height, places, outfile):
	img = Image.new("RGB", (width, height))
	data = img.load()

	for x in range(width):
		for y in range(height):
			data[x, y] = (0, 0, 0)
	
	for place in places[0]:
		data[place[0], place[1]] = (255, 0, 0)

	for place in places[1]:
		data[place[0], place[1]] = (0, 0, 255)

	img.save(outfile)

def setup_herd_immuity(w, h):
	cells = [[VaccinatedState() for x in range(w)] for y in range(h)]
	for i in range(15):
		x = randint(0, w - 1)
		y = randint(0, h - 1)
		cells[x][y] = InfetedState()
	for i in range(5000):
		x = randint(0, w - 1)
		y = randint(0, h - 1)
		cells[x][y] = SusceptibleState()
	
	return cells

def setup_normal(w, h):
	cells = [[SusceptibleState() for x in range(w)] for y in range(h)]
	for i in range(2):
		x = randint(0, w - 1)
		y = randint(0, h - 1)
		cells[x][y] = InfetedState()
	
	return cells

def main():
	cell_width = 100
	cell_height = 100

	cells = setup_normal(cell_width, cell_height)
	
	places = [
		# place 0 - home (1 per group of 4)
		[(i, j) for i in range(0, cell_width, 4) for j in range(0, cell_height, 4)],
		# place 1 - work/school (1 per group of 25)
		[(i+randint(1,10), j+randint(1,10)) for i in range(0, cell_width, 25) for j in range(0, cell_height, 25)]
	]

	counts = []

	places_to_image(cell_width, cell_height, places, f"out/time_tracked_limited_immunity_movement/places.png")

	cells_to_image(cells, "out/time_tracked_limited_immunity_movement/0.png")
	for i in range(0,200):
		for j in range(len(place_betas)):
			cells, count = timestep_single_place(cells, i, j, places)
			counts.append(count)
		cells_to_image(cells, f"out/time_tracked_limited_immunity_movement/{i+1}.png")
	
	fig, ax = plt.subplots()
	ax.plot(counts)
	ax.set_ylabel("Number of people")
	fig.legend(("S", "I", "R"))
	plt.savefig("graphs/time_tracked_limited_immunity_movement.png")
	plt.show()

if __name__ == "__main__":
	main()