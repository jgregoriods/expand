# ExPaND
<h2>Simulating demic expansion of farmers in tropical South America</h2>

Jonas Gregorio de Souza<br/>
[![ORCiD](https://img.shields.io/badge/ORCiD-0000--0001--7879--4531-green.svg)](https://orcid.org/0000-0001-6032-4443)<br/>

<p>This is an agent-based model for simulating the demic expansion of tropical forest farmers in late Holocene South America. Over the last 5000 years, archaeological cultures like the Saladoid-Barrancoid and Tupiguarani expanded over different parts of Amazon and beyond, spreading the practice of polyculture agroforestry. Can these archaeological expansions be modelled as demic waves of advance similar to what has been proposed for the Neolithic in Eurasia? Model results are assessed by comparing simulated arrival times with radiocarbon dates. Similar models, where human expansions are determined by population growth, fission and relocation, have been developed for the spread of farming in Europe (<a href="https://doi.org/10.7183/0002-7316.77.2.203">Fort et al. 2012</a>; <a href="https://doi.org/10.1073/pnas.1613413114">Isern et al. 2017</a>). The same concept is adopted here, with the rules of the model informed by the ethnography of tropical forest farmers. For a complete description of the model, see Souza et al. (<a href="https://doi.org/10.1371/journal.pone.0232367">2020</a>).</p>
<h3>Installation</h3>
<p>Clone or download the repository. There are some dependencies that need to be installed:</p>

```
pip3 install -r requirements.txt
```

<h3>Model architecture</h3>

<p>Expansions result from the interaction between population growth, village fission and village relocation. Each village has a territory within a <i>catchment radius</i> and a <i>maximum population density</i> (<i>K*</i>). The population grows at a rate of 2.5% per year. If the population is above the maximum density, more cells (10 x 10 km) are added to its territory. When the village population is above a certain <i>threshold</i> and there are free cells outside of its catchment, it fissions, giving birth to a new village. If a village has been in its location beyond a <i>maximum permanence time</i>, it also looks for free cells outside its catchment to move. Finally, villages have the option to <i>leapfrog</i>: if there are no free cells in the immediate neighbourhood, they can jump over longer distances.</p>
<p>The model starts with a village whose population is at the fission threshold, so that it immediately fissions and starts the expansion.</p>
<p>When fissioning or moving, villages choose the best cell according to a suitability layer. Here, a layer env.asc is provided in the <code>/layers</code> folder for illustrative purposes. The layer was created using MaxEnt. In the code, a parameter <code>tolerance</code> is passed to the agents, determining the minimum value for a cell to be settled. In this version, the value 0.3 was used, based on the max training sensitivity and specificity threshold of the MaxEnt results.</p>

<h3>Running the model</h3>

<p>You must define a start date (BP) and a dictionary with the parameters: the coordinates (lonlat) of the first village, the maximum population density (persons 100 km<sup>-2</sup>), fission threshold, catchment radius (km), leap distance (km) and maximum permanence time (years).</p>

<p>For now, let's set the start date to 4600 BP and the initial coordinates to -65.77 7.82 (approximate coordinates of La Gruta, which potentially contains some of the earliest Saladoid-Barrancoid ceramics).</p>

```python
>>> from model import Model

>>> start_date = 4600
>>> params = {
    'coords': (-65.77, 7.82),
    'k': 30,
    'fission_threshold': 70,
    'catchment': 10,
    'leap_distance': 150,
    'permanence': 15,
    'tolerance': 0.3
}
>>> model = Model(start_date, params)
>>> model.run(4100, show_progress=True)
100%|██████████████████████████████████████| 4100/4100 [00:08<00:00, 507.48it/s]
```

<p>The results of the model can be evaluated by comparing simulated arrival times with radiocarbon dates in different regions. The calibrated dates you want to use for comparison must be placed in the folder <code>/dates</code>. Files must be in .csv format with two columns, one for each date, with a first row containing XY coordinates for the dated site in lonlat format and the remaining rows containing years BP and the respective probability densities.</p>

<p>The result is a score from 0 to 1 obtained by averaging the intercepted normalised probability at each dated site (or 0 if the simulated arrival time is outside of the calibrated distribution).</p>

```python
>>> score = model.eval()
>>> print('score:', round(score, 2))
score: 0.57
```

<p>You can save the results to be used in other software. This creates two files in the <code>/results</code> folder: one starting with <code>sim...</code> containing the simulated arrival times and the other starting with <code>dates...</code> containing the intercepted probability densities.</p>

```python
>>> model.write()
```

You can also run from the command line by using the following arguments:

```
python3 run.py --start=4600 --x=-65.77 --y=7.82 --k=30 --fiss=70 --catch=10 --leap=150 --perm=15 --tol=0.3 --iter=4100 --write --eval --show-bar
```

<img src='img/res.png' width='300' />

<h3>References</h3>

<p>Fort, Joaquim, Toni Pujol, and Marc Vander Linden. 2012. <a href="https://doi.org/10.7183/0002-7316.77.2.203">“Modelling the Neolithic Transition in the Near East and Europe.”</a> American Antiquity 77 (2): 203–19.</p>
<p>Isern, Neus, João Zilhão, Joaquim Fort, and Albert J Ammerman. 2017. <a href="https://doi.org/10.1073/pnas.1613413114">“Modeling the Role of Voyaging in the Coastal Spread of the Early Neolithic in the West Mediterranean.”</a> Proceedings of the National Academy of Sciences 114 (5): 897 LP – 902.</p>
<p>Souza, J.G., Alcaina-Mateos, J., Madella, M. 2020. <a href="https://doi.org/10.1371/journal.pone.0232367">"Archaeological expansions in tropical South America during the late Holocene: Assessing the role of demic diffusion"</a>. PLOS ONE 15(4): e0232367.</p>
