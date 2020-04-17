import matplotlib.pyplot as plt
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
import numpy as np
import tkinter as tk
import tkinter.font as font
from tqdm import tqdm

from model import Model
from utils import get_dates, to_canvas, to_lonlat, transform_coords


class App:
    def __init__(self, master):
        self.master = master
        master.title('ExPaND')
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=8)

        # Model visualization
        self.figure = mplfig.Figure(figsize=(7, 7), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.tick_params(axis='both', which='both', bottom=False,
                            labelbottom=False, left=False, labelleft=False)
        self.figure.subplots_adjust(left=0, bottom=0.02, right=1, top=0.98,
                                    wspace=0, hspace=0)
        self.canvas = tkagg.FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().grid(row=1, column=4, columnspan=1,
                                         rowspan=10)

        self.toolbar_frame = tk.Frame(self.master)
        self.toolbar_frame.grid(row=12, column=4, columnspan=1)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas,
                                                  self.toolbar_frame)

        # Parameters
        # Start date
        self.start = tk.IntVar()
        self.start.set(4500)

        self.start_label = tk.Label(master, text='Start date (BP):')
        self.start_label.grid(row=3, column=1)

        self.start_entry = tk.Entry(master, textvariable=self.start)
        self.start_entry.config(width=10)
        self.start_entry.grid(row=3, column=2, columnspan=2)

        # Start coordinates
        self.lon = tk.DoubleVar()
        self.lon.set(-65.77)

        self.lat = tk.DoubleVar()
        self.lat.set(7.82)

        self.coords_label = tk.Label(master, text='Origin (Lon/Lat):')
        self.coords_label.grid(row=4, column=1)

        self.lon_entry = tk.Entry(master, textvariable=self.lon)
        self.lon_entry.config(width=5)
        self.lon_entry.grid(row=4, column=2)

        self.lat_entry = tk.Entry(master, textvariable=self.lat)
        self.lat_entry.config(width=5)
        self.lat_entry.grid(row=4, column=3)

        # K*
        self.k = tk.Scale(master, label='K* (persons/100 km2)', from_=20,
                          to=100, resolution=20, orient=tk.HORIZONTAL,
                          length=200)
        self.k.grid(row=5, column=1, columnspan=3)

        # Fission threshold
        self.fiss = tk.Scale(master, label='Fission threshold', from_=50,
                             to=300, resolution=50, orient=tk.HORIZONTAL,
                             length=200)
        self.fiss.grid(row=6, column=1, columnspan=3)

        # Catchment
        self.catch = tk.Scale(master, label='Catchment (km)', from_=10, to=30,
                              resolution=10, orient=tk.HORIZONTAL, length=200)
        self.catch.grid(row=7, column=1, columnspan=3)

        # Leap distance
        self.leap = tk.Scale(master, label='Leap distance (km)', from_=0,
                             to=300, resolution=50, orient=tk.HORIZONTAL,
                             length=200)
        self.leap.grid(row=8, column=1, columnspan=3)

        # Permanence
        self.perm = tk.Scale(master, label='Permanence (years)', from_=10,
                             to=30, resolution=10, orient=tk.HORIZONTAL,
                             length=200)
        self.perm.grid(row=9, column=1, columnspan=3)

        # Controls
        self.setup_button = tk.Button(master, text='Setup', width=10,
                                      command=self.setup_model)
        self.setup_button.grid(row=1, column=1)

        self.run_button = tk.Button(master, text='Run', width=10,
                                    command=self.run_model)
        self.run_button.grid(row=1, column=2)

        self.stop_button = tk.Button(master, text='Stop', width=10,
                                     command=self.stop)
        self.stop_button.grid(row=1, column=3)

        self.iter_thousand_button = tk.Button(master, text='▶ 1000 yrs',
                                              width=10,
                                              command=self.iter_thousand)
        self.iter_thousand_button.grid(row=2, column=1)

        self.write_button = tk.Button(master, text='Write', width=10,
                                      command=self.write_model)
        self.write_button.grid(row=2, column=2)

        self.eval_button = tk.Button(master, text='Evaluate', width=10,
                                     command=self.eval_model)
        self.eval_button.grid(row=2, column=3)

        # South America elevation map as a background
        self.basemap = np.vstack(np.loadtxt('./layers/ele.asc',
                                            skiprows=6).astype(float))
        self.basemap[self.basemap == -9999] = np.nan

        self.setup_model()

    def setup_model(self):
        self.params = {'coords': to_canvas(self.lon.get(), self.lat.get()),
                       'k': self.k.get(), 'fission_threshold': self.fiss.get(),
                       'catchment': self.catch.get() // 10,
                       'leap_distance': self.leap.get() // 10,
                       'permanence': self.perm.get(), 'tolerance': 0.4}

        self.running = True
        self.model = Model(start=self.start.get(),
                           params=self.params)
        self.plot_model()
        self.stop_button.configure(text='Stop')

    def run_model(self):
        if self.running:
            self.model.step()
            self.plot_model()
            self.master.after(1, self.run_model)

    def iter_thousand(self):
        for i in tqdm(range(1000)):
            self.model.step()
        self.plot_model()

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

    def eval_model(self):
        print(self.model.eval())

    def plot_model(self):
        self.points = [self.model.agents[_id].coords for
                       _id in self.model.agents]
        self.pop = [self.model.agents[_id].population for
                    _id in self.model.agents]

        self.ax.cla()
        self.ax.set_xlim(45, 600)
        self.ax.set_ylim(800, 10)
        self.ax.set_facecolor('black')
        self.ax.imshow(self.basemap, cmap='cividis')

        # Color scale for villages based on population
        self.ax.scatter(*zip(*self.points), s=1, c=self.pop, cmap='Wistia',
                        vmin=0, vmax=self.fiss.get())

        self.ax.text(580, 50, 'yr BP', color='white',
                     horizontalalignment='right')
        self.ax.text(580, 70, str(self.model.bp), color='white',
                     horizontalalignment='right')

        self.canvas.draw()
