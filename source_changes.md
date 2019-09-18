##inputs

On line 2497 in inputs.py package, I added time.sleep(0.001) to fix lag, as per suggestion of 
https://github.com/zeth/inputs/issues/65.

## pyqtgraph
Can be solved by changing line 683 in pyqtgraph/graphicsItems/PlotDataItem.py to:
y = abs(f[1:len(f)//2])
Using the integer division operator works.