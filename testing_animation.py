import matplotlib.pyplot as plt
import matplotlib.animation as animation

class AnimateGraph:
    def __init__(self):
        self.data = [2 ** i for i in range(5)]
        self.flip = 1
        self.pos = [1]
        self.pos1 = [1]
        self.pos2 = [3]
        self.fig, self.ax = plt.subplots()
        self.animation = animation.FuncAnimation(self.fig, self.update_plot, init_func=self.setup_plot, blit=False)


    def setup_plot(self):

        self.line, = self.ax.plot(self.data)
        self.scat = self.ax.scatter(self.pos, self.pos)

        self.graphs = [self.line, self.scat]

        return self.graphs

    def update_plot(self, i):

        self.update_data()

    
        self.line.set_ydata(self.data)

        self.scat.set_offsets([[self.pos[0], self.pos[0]]])


        return self.graphs

    def update_data(self):

        self.data[2] += self.flip
        self.flip *= -1

        if self.pos[0] == self.pos1[0]:
            self.pos = self.pos2
        else:
            self.pos = self.pos1
        
    
my_animation = AnimateGraph()
plt.show()
