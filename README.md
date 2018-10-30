# hunahpy
### Python 3.6 (32 bits only)
ctypes based library for the IDQuantique id800 time-to-digital converter (TDC)

Shared libraries you need:

* nhconnect.dll
* nhconnect.lib
* tdcbase.dll
* tdcbase.lib
* libusb0.dll (32 bit)

## hunahpy package:
`hunahpy` contains one object only: `TDC`

`TDC` is a controller for the id800. Its methods can be access like:
* TDC.getLastTimestamps() (a function)
* TDC.timebase (a value)

`config.py` is the configuration file for `hunahpy`. It allows for two different data saving schemes using the `cont` variable:
* `cont` = True (or `cont`inuous data saving) means it creates _only_ one file and dumps every recorded event there. You need to call the write function again to stop writing.
* `cont` = False means it creates _n_ data files and writes time tags in one until a set buffer size is reached. It then stops and moves on to the next one automatically.

------

Example script to open or create a file `filename.dat` saved in `/data/` and write 10 seconds worth of events in binary format:

````
import time
from hunahpy import TDC

tagger = TDC()
tagger.writeTimestamps('/data/filename.dat',binary=True)
time.wait(10)
tagger.writeTimestamps()
tagger.close()
````

If opening a TDC object don't forget to close connection with TDC.close()

