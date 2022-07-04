from enum import Enum, unique, auto
import pprint as pretty_print
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from random import randint

pprint = lambda x: pretty_print.pprint(x, width=500, compact=True)

@unique
class PersonState(Enum):
	SUSCEPTIBLE = auto()
	INFECTED = auto()
	RECOVERED = auto()

TIMESTEP_SIZE_SECONDS = lambda t: 24*60*60
RECOVERY_TIME_SECONDS = lambda t: randint(7, 12) * 60 * 60 * 24
R0 = lambda t: 1.2

def SIR_timestep(S, I, R, beta, gamma):
	N = S + I + R
	ds = -beta * S * I / N
	di = beta * S * I / N - gamma * I
	dr = gamma * I

	return (S + ds, I + di, R + dr)

def main() -> None:
	state = [(10000, 15, 0)]

	t = 0
	#while (state[t//TIMESTEP_SIZE_SECONDS(t)][2] < state[0][0] * 0.95 and t//TIMESTEP_SIZE_SECONDS(t) < 1000):
	#print( TIMESTEP_SIZE_SECONDS(0) /  RECOVERY_TIME_SECONDS(0))
	while (t < 200 * 24 * 3600):
 
		gamma = 1/ (RECOVERY_TIME_SECONDS(t)/TIMESTEP_SIZE_SECONDS(t))
		beta = 0.5

		state.append(SIR_timestep(*state[t//TIMESTEP_SIZE_SECONDS(t)], beta, gamma))
		t += TIMESTEP_SIZE_SECONDS(t)

	#print(state)

	fig, ax = plt.subplots()
	ax.plot(state)
	ax.set_xlabel("Days since start")
	ax.set_ylabel("Number of people")
	fig.legend(("S", "I", "R"))
	plt.savefig("graphs/mathematical_sir.png")
	plt.show()

if __name__ == "__main__":
	main()