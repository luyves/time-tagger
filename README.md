# time-tagger
### Python 3.6 (32 bits only)
ctypes based library for the IDQuantique id800 time-to-digital converter (TDC)

shared libraries you need:

* nhconnect.dll
* nhconnect.lib
* tdcbase.dll
* tdcbase.lib
* libusb0.dll (32 bit)

if opening a TDC object don't forget to close connection to the id800 with TDC.close()
