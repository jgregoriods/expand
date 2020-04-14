import matplotlib.pyplot as plt
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
import numpy as np 
import tkinter as tk
import tqdm

from model_mx import Model
from params import arawak, tupi, carib, je
from utils import write_results, get_dates, to_lonlat, transform_coords
from utils import to_canvas


sites = {'la gruta': {'coords': (-65.77, 7.82), 'date': 4591},
         'corporito': {'coords': (-61.81, 8.99), 'date': 5133},
         'abraham': {'coords': (-50.5414, -5.8059), 'date': 2411},
         'sao bento': {'coords': (-53.1869, -3.5514), 'date': 2787},
         'grajau': {'coords': (-45.3701, -4.2532), 'date': 2849},
         'bela vista': {'coords': (-48.5534, -5.1164), 'date': 2410},
         'gentio': {'coords': (-46.8958, -16.3792), 'date': 3513},
         'salitre': {'coords': (-49.9500, -18.1400), 'date': 4202},
         'GOCP02': {'coords': (-51.5753, -16.9612), 'date': 3128},
         'saladero': {'coords': (-62.2009, 8.6817), 'date': 1782},
         'panela': {'coords': (-55.014, -16.3788), 'date': 3073},
         'corozal': {'coords': (-65.697, 7.92), 'date': 1623}}

tolerance = {'arawak': 0.168, 'carib': 0.413, 'tupi': 0.442, 'je': 0.275}

class App:
    def __init__(self, master):
        self.master = master
        master.title('ExPaND')

        # Model visualization
        self.figure = mplfig.Figure(figsize=(7, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = tkagg.FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().grid(row=2, column=2, columnspan=9,
                                         rowspan=9)

        self.toolbar_frame = tk.Frame(self.master)
        self.toolbar_frame.grid(row=11, column=2, columnspan=7)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas,
                                                  self.toolbar_frame)

        self.points = []
        self.pop = []

        # Parameters

        self.breed = tk.StringVar(master)
        self.breed.set('arawak')
        self.menu = tk.OptionMenu(master, self.breed, 'arawak', 'carib', 'tupi', 'je')
        self.menu.grid(row=2, column=1)

        self.orig = tk.StringVar(master)
        self.orig.set('la gruta')
        self.origins= tk.OptionMenu(master, self.orig, 'la gruta', 'corporito',
                                    'abraham', 'sao bento', 'bela vista',
                                    'grajau', 'gentio', 'salitre', 'saladero',
                                    'corozal', 'GOCP02', 'panela')
        self.origins.grid(row=3, column=1)

        self.k = tk.Scale(master, label='K', from_=10, to=100, orient=tk.HORIZONTAL)
        self.k.grid(row=4, column=1)

        self.fiss = tk.Scale(master, label='fission', from_=50, to=300,
                             orient=tk.HORIZONTAL)
        self.fiss.grid(row=5, column=1)

        self.catch = tk.Scale(master, label='catchment', from_=1, to=3,
                              orient=tk.HORIZONTAL)
        self.catch.grid(row=6, column=1)

        self.leap = tk.Scale(master, label='leap', from_=0, to=25,
                             orient=tk.HORIZONTAL)
        self.leap.grid(row=7, column=1)

        self.perm = tk.Scale(master, label='permanence', from_=10, to=30,
                            orient=tk.HORIZONTAL)
        self.perm.grid(row=8, column=1)

        # Controls
        self.setup_button = tk.Button(master, text='Setup',
                                      command=self.setup_model)
        self.setup_button.grid(row=1, column=2)

        self.n_iter = tk.Entry(master)
        self.n_iter.grid(row=1, column=3)

        self.iter_button = tk.Button(master, text='Iterate',
                                     command=self.iterate_model)
        self.iter_button.grid(row=1, column=4)

        self.run_button = tk.Button(master, text='Run',
                                    command=self.run_model)
        self.run_button.grid(row=1, column=5)

        self.stop_button = tk.Button(master, text='Stop',
                                     command=self.stop)
        self.stop_button.grid(row=1, column=6)
        """
        self.year_entry = tk.Entry(master)
        self.year_entry.insert(tk.END, '4600')
        self.year_entry.grid(row=1, column=7)
        """
        self.year_label = tk.Label(master, text='')
        self.year_label.grid(row=1, column=8)
 
        self.write_button = tk.Button(master, text='Write',
                                      command=self.write_model)
        self.write_button.grid(row=1, column=9)

        self.eval_button = tk.Button(master, text='Evaluate',
                                     command=self.eval_model)
        self.eval_button.grid(row=1, column=10)
        """
        # Model parameters
        self.has_arawak = tk.IntVar()
        self.has_arawak.set(1)
        self.arawak_check = tk.Checkbutton(master, text='Arawak',
                                           variable=self.has_arawak)
        self.arawak_check.grid(row=2, column=1)

        self.has_carib = tk.IntVar()
        self.has_carib.set(1)
        self.carib_check = tk.Checkbutton(master, text='Carib',
                                          variable=self.has_carib)
        self.carib_check.grid(row=3, column=1)

        self.has_tupi = tk.IntVar()
        self.has_tupi.set(1)
        self.tupi_check = tk.Checkbutton(master, text='Tupi',
                                         variable=self.has_tupi)
        self.tupi_check.grid(row=4, column=1)

        self.has_je = tk.IntVar()
        self.has_je.set(1)
        self.je_check = tk.Checkbutton(master, text='Je', variable=self.has_je)
        self.je_check.grid(row=5, column=1)

        self.leapfrogging = tk.IntVar()
        self.leapfrogging.set(0)
        self.leapfrog_check = tk.Checkbutton(master, text='Leapfrogging',
                                             variable=self.leapfrogging)
        self.leapfrog_check.grid(row=7, column=1)
        """
        # South America elevation map as a background
        self.basemap = np.vstack(np.loadtxt('./layers/eleAlbers.asc',
                                            skiprows=6).astype(float))
        self.basemap[self.basemap == -9999] = np.nan

        self.setup_model()

    def setup_model(self):
        self.params = [to_canvas(*sites[self.orig.get()]['coords']),
                       self.breed.get(), sites[self.orig.get()]['date'],
                       self.k.get(), self.fiss.get(), self.catch.get(),
                       self.leap.get(), self.perm.get(), tolerance[self.breed.get()]]
        self.running = True
        self.model = Model(params=self.params)
        self.plot_model()
        self.stop_button.configure(text='Stop')

    def get_breeds(self):
        breeds = []
        if self.has_arawak.get():
            breeds.append(arawak)
        if self.has_carib.get():
            breeds.append(carib)
        if self.has_tupi.get():
            breeds.append(tupi)
        if self.has_je.get():
            breeds.append(je)

        return breeds

    def run_model(self):
        if self.running:
            self.model.step()
            self.plot_model()
            self.master.after(1, self.run_model)

    def iterate_model(self):
        for i in tqdm.tqdm(range(int(self.n_iter.get()))):
            self.model.step()
        self.plot_model()
        plt.show()

    def stop(self):
        if self.running:
            self.running = False
            self.stop_button.configure(text='Continue')
        else:
            self.running = True
            self.stop_button.configure(text='Stop')
            self.run_model()

    def write_model(self):
        self.model.write()

    def write_agents(self):
        with open('./results/agents.csv', 'w') as file:
            file.write('x,y,pop\n')
            for _id in self.model.agents:
                pop = self.model.agents[_id].population
                coords = self.model.agents[_id].coords
                x, y = to_lonlat(transform_coords(coords))
                file.write(str(x) + ',' + str(y) + ',' + str(pop) + '\n')

    def eval_model(self):
        print(self.model.eval())

    def plot_model(self):
        self.points = [self.model.agents[_id].coords for
                       _id in self.model.agents]
        self.pop = [self.model.agents[_id].population for
                    _id in self.model.agents]
        # self.owned = [(x, y) for (x, y) in self.model.grid if
        #              self.model.grid[(x, y)]['agent'] > 0]
        self.year_label.configure(text='{} bp'.format(self.model.bp))
        self.ax.cla()
        self.ax.set_facecolor('black')
        self.ax.imshow(self.basemap, cmap='cividis')
        """
        self.arawakpts = [self.model.agents[_id].coords for
                          _id in self.model.agents if
                          self.model.agents[_id].breed == 'arawak']

        self.caribpts = [self.model.agents[_id].coords for
                          _id in self.model.agents if
                          self.model.agents[_id].breed == 'carib']
        
        self.tupipts = [self.model.agents[_id].coords for
                          _id in self.model.agents if
                          self.model.agents[_id].breed == 'tupi']
        
        self.jepts = [self.model.agents[_id].coords for
                          _id in self.model.agents if
                          self.model.agents[_id].breed == 'je']
        if self.owned:
        """
        #self.ax.scatter(*zip(*self.owned), s=4, color='black', marker='s')
        
        self.ax.scatter(*zip(*self.points), s=0.1, c=self.pop, cmap='autumn_r',
                        vmin=100, vmax=500)
        """
        if self.arawakpts:
            self.ax.scatter(*zip(*self.arawakpts), s=0.1, color='magenta')
        if self.caribpts:
            self.ax.scatter(*zip(*self.caribpts), s=0.1, color='green')
        if self.tupipts:
            self.ax.scatter(*zip(*self.tupipts), s=0.1, color='red')
        if self.jepts:
            self.ax.scatter(*zip(*self.jepts), s=0.1, color='yellow')
        """

        self.canvas.draw()


root = tk.Tk()
app = App(root)
root.mainloop()
