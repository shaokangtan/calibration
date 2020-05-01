import pyqtgraph.exporters
import pyqtgraph as pg

# generate something to export
plt = pg.plot([1, 5, 2, 4, 3])

# create an exporter instance, as an argument give it
# the item you wish to export
exporter = pg.exporters.ImageExporter(plt.plotItem)

# set export parameters if needed
exporter.parameters()['width'] = 100   # (note this also affects height parameter)

# save to file
exporter.export('fileName.png')