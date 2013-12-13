import sys
import math
import random
class tiny_gp:
	POPSIZE = 100000
	ADD = 110
	SUB = 111
	MUL = 112
	DIV = 113
	FSET_START = ADD
	FSET_END = DIV
	DEPTH = 15
	MAX_LEN = 10
	GENERATIONS = 10000
	TSIZE = 2
	CROSSOVER_PROB = 0.9
	PMUT_PER_NODE  = 0.05
	
	def __init__(self,fname,s):
		self.fitness  = [0.0]*self.POPSIZE
		self.seed = s
		if self.seed >= 0:
			random.seed(self.seed)
		self.setup_fitness(fname)
		self.x = []
		for i in range(self.FSET_START):
			self.x.append((self.maxrandom-self.minrandom)*random.uniform(0,1)+self.minrandom)
		self.pop = self.create_random_pop(self.POPSIZE,self.DEPTH,self.fitness)
	
	def grow(self, pos, max, depth):
		prim = random.randint(0,1)
		if pos >= max:
			return -1
		if pos == 0:
			prim = 1
		if prim == 0 or depth == 0:
			prim = random.randint(0,self.varnumber+self.randomnumber-1)
			self.buffer.append(prim)
			return pos+1
		else:
			prim = random.randint(0,self.FSET_END-self.FSET_START) + self.FSET_START
			if prim == self.ADD or prim == self.SUB or prim == self.MUL or prim == self.DIV:
				self.buffer.append(prim)
				one_child = self.grow(pos+1,max,depth-1)
				if one_child < 0:
					return -1
				return self.grow(one_child,max,depth-1)
		return 0 #should never get here
		
	def create_random_indiv(self,depth):
		self.buffer = []
		
		len_g = self.grow(0,self.MAX_LEN,depth)
		while(len_g < 0):
			self.buffer = []
			len_g = self.grow(0,self.MAX_LEN,depth)
		ind = []
		for i in range(len_g):
			ind.append(self.buffer[i])
		return ind
	
	def traverse(self,buffer,buffercount):
		if buffer[buffercount] < self.FSET_START:
			return buffercount+1
		if buffer[buffercount] == self.ADD or buffer[buffercount] == self.SUB or buffer[buffercount] == self.MUL or buffer[buffercount] == self.DIV:
			return self.traverse(buffer,self.traverse(buffer,buffercount+1))
		return 0 #should never get here
		
	def run(self):
		primitive = self.program[self.PC]
		self.PC += 1
		if primitive < self.FSET_START:
			return self.x[primitive]
		if primitive == self.ADD:
			return self.run() + self.run()
		if primitive == self.SUB:
			return self.run() - self.run()
		if primitive == self.MUL:
			return self.run() * self.run()
		if primitive == self.DIV:
			num = self.run()
			den = self.run()
			if den <= 0.001:
				return num
			return num/den
		return 0 #should never get here
		
	def fitness_function(self,Prog):
		len = self.traverse(Prog,0)
		
		fit = 0.0
		for i in range(self.fitnesscases):
			for j in range(self.varnumber):
				self.x[j] = self.targets[i][j]
			self.program = Prog
			self.PC = 0
			result = self.run()
			fit += abs(result - self.targets[i][self.varnumber])
		return -1*fit
		
	def create_random_pop(self,n,depth,fitness):
		pop = []
		print "Creating population"
		for i in range(n):
			pop.append(self.create_random_indiv(depth))
			self.fitness[i] = self.fitness_function(pop[i])
			
		return pop
	
	def setup_fitness(self,fname):
		f_in = open(fname,"r")
		line = f_in.readline().strip()
		tokens = line.split()
		self.varnumber = int(tokens[0])
		self.randomnumber = int(tokens[1])
		self.minrandom = int(tokens[2])
		self.maxrandom = int(tokens[3])
		self.fitnesscases = int(tokens[4])
		if self.varnumber+self.randomnumber >= self.FSET_START:
			print "too many variables and constants"
		
		self.targets = []
		for i in range(self.fitnesscases):
			line = f_in.readline().strip()
			tokens = line.split()
			temp = []
			for j in range(self.varnumber+1):
				temp.append(float(tokens[j]))
			self.targets.append(temp)
		
		f_in.close()
		print ""
	
	def print_indiv(self,buffer,buffercounter):
		a1 = 0
		if(buffer[buffercounter] < self.FSET_START):
			if buffer[buffercounter] < self.varnumber:
				sys.stdout.write( "X"+str(buffer[buffercounter]+1)+" ")
			else:
				sys.stdout.write(str(self.x[buffer[buffercounter]]))
			return buffercounter + 1
		if buffer[buffercounter] == self.ADD:
			sys.stdout.write("(")
			a1 = self.print_indiv(buffer,buffercounter+1)
			sys.stdout.write(" + ")
		elif buffer[buffercounter] == self.SUB:
			sys.stdout.write("(")
			a1 = self.print_indiv(buffer,buffercounter+1)
			sys.stdout.write(" - ")
		elif buffer[buffercounter] == self.MUL:
			sys.stdout.write("(")
			a1 = self.print_indiv(buffer,buffercounter+1)
			sys.stdout.write(" * ")
		elif buffer[buffercounter] == self.DIV:
			sys.stdout.write("(")
			a1 = self.print_indiv(buffer,buffercounter+1)
			sys.stdout.write(" / ")
		a2 = self.print_indiv(buffer,a1)
		sys.stdout.write(" ) ")
		return a2
		
	def stats(self, fitness,pop,gen):
		best = random.randint(0,self.POPSIZE-1)
		self.fbestpop = fitness[best]
		self.favgpop = 0.0
		node_count = 0.0
		
		for i in range(self.POPSIZE):
			node_count += self.traverse(pop[i],0)
			self.favgpop += fitness[i]
			if fitness[i] > self.fbestpop:
				best = i
				self.fbestpop = fitness[i]
				
		avg_len = node_count/self.POPSIZE
		self.favgpop = self.favgpop /self.POPSIZE
		print "Generation="+str(gen)+" Avg Fitness="+str(-1*self.favgpop)+" Best Fitness="+str(-1*self.fbestpop)+" Avg Size="+str(avg_len)+"\nBest Individual: "
		self.print_indiv(pop[best],0)
		
	def print_parms(self):
		print "-- TINY GP (Python Version) --"
		print "SEED="+str(self.seed)+"\nMAX_LEN="+str(self.MAX_LEN)+"\nPOPSIZE="+str(self.POPSIZE)+"\nDEPTH="+str(self.DEPTH)+"\nCROSSOVER_PROB="+str(self.CROSSOVER_PROB)+"\nPMUT_PER_NODE="+str(self.PMUT_PER_NODE)+"\nMIN_RANDOM="+str(self.minrandom)+"\nMAX_RANDOM="+str(self.maxrandom)+"\nGENERATIONS="+str(self.GENERATIONS)+"\nTSIZE="+str(self.TSIZE)+"\n----------------------------------"
	
	def tournament (self, fitness, tsize):
		best = random.randint(0,self.POPSIZE-1)
		fbest = -1.0e34
		for i in range(tsize):
			competitor = random.randint(0,self.POPSIZE-1)
			
			if fitness[competitor] > fbest:
				fbest =fitness[competitor]
				best = competitor
		
		return best

	def arraycopy(self, scr,scr_start,dest,dest_start, length):
		for i in range(length):
			dest[dest_start + i] = scr[scr_start+i]
		
	def crossover(self,parent1,parent2):
		offspring  = []
		len1 = self.traverse(parent1,0)
		len2 = self.traverse(parent2,0)
		
		xo1start = random.randint(0,len1-1)
		xo1end = self.traverse(parent1,xo1start)
		
		xo2start = random.randint(0,len2-1)
		xo2end = self.traverse(parent2,xo2start)
		lenoff = xo1start + (xo2end - xo2start) + (len1-xo1end);
		offspring = [1]*lenoff;

		self.arraycopy( parent1, 0, offspring, 0, xo1start );
		self.arraycopy( parent2, xo2start, offspring, xo1start,(xo2end - xo2start) );
		self.arraycopy( parent1, xo1end, offspring,xo1start + (xo2end - xo2start), (len1-xo1end) );
		
		"""for i in range(xo1start):
			offspring.append(parent1[i])
		for i in range(xo2start,xo2end):
			offspring.append(parent2[i])
		for i in range(xo1end,len1):
			offspring.append(parent1[i])"""
		return offspring
	
	def mutation(self,parent,pmut):
		parentcopy = []
		len = self.traverse(parent,0)
		for i in range(len):
			parentcopy.append(parent[i])
		for i in range(len):
			if random.uniform(0.0,1.0) < pmut :
				mutsite = i
				if parentcopy[mutsite] <self.FSET_START:
					parentcopy[mutsite] = random.randint(0,self.varnumber+self.randomnumber-1)
				else:
					if parentcopy[mutsite] == self.ADD or parentcopy[mutsite] == self.SUB or parentcopy[mutsite] == self.MUL or parentcopy[mutsite] == self.DIV:
						parentcopy[mutsite] = random.randint(0,self.FSET_END-self.FSET_START) +self.FSET_START
		
		return parentcopy
	
	def negative_tournament(self,fitness,tsize):
		worst = random.randint(0,self.POPSIZE-1)
		fworst = 1e34
		
		for i in range(tsize):
			competitor = random.randint(0,self.POPSIZE-1)
			if fitness[competitor] < fworst:
				fworst = fitness[competitor]
				worst = competitor
		return worst
		
		
	def evolve(self):
		self.print_parms()
		
		self.stats(self.fitness,self.pop,0)
		#raise KeyboardInterrupt
		for gen in range(1,self.GENERATIONS):
			if self.fbestpop > -0.00005:
				print "PROBLEM SOLVED"
				sys.exit(0)
			for indivs in range(self.POPSIZE):
				if random.uniform(0.0,1.0) < self.CROSSOVER_PROB:
					parent1  = self.tournament(self.fitness,self.TSIZE)
					parent2  = self.tournament(self.fitness,self.TSIZE)
					
					newind = self.crossover(self.pop[parent1],self.pop[parent2])
					max = 0;
					parent1_len = self.traverse(self.pop[parent1],0);
					parent2_len = self.traverse(self.pop[parent2],0);
					max = parent2_len;
					if parent1_len > parent2_len:
						max = parent1_len;
		
					max += 10;
					while self.traverse(newind,0) > max:
						parent1  = self.tournament(self.fitness,self.TSIZE)
						parent2  = self.tournament(self.fitness,self.TSIZE)
						newind = self.crossover(self.pop[parent1],self.pop[parent2])
						max = 0;
						parent1_len = self.traverse(self.pop[parent1],0);
						parent2_len = self.traverse(self.pop[parent2],0);
						max = parent2_len;
						if parent1_len > parent2_len:
							max = parent1_len;
		
						max += 10;
				else:
					parent = self.tournament(self.fitness,self.TSIZE)
					newind = self.mutation(self.pop[parent],self.PMUT_PER_NODE)
				newfit = self.fitness_function(newind)
				offspring = self.negative_tournament(self.fitness,self.TSIZE)
				self.pop[offspring] = newind
				self.fitness[offspring] = newfit
			self.stats(self.fitness,self.pop,gen)
		print "PROBLEM *NOT* SOLVED"
		sys.exit(0)
def main():
	fname = "C:\\Train\\TinyGP\\problem.dat"
	s = -1 
	
	if len(sys.argv) == 3:
		s = int(sys.argv[1])
		fname = sys.argv[2]
	if len(sys.argv) == 2:
		fname = sys.argv[1]
	gp = tiny_gp(fname,s)
	gp.evolve()
if __name__ == '__main__':
	main()
	
	