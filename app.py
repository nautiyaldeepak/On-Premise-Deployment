import ptvsd
import os

print("Waiting to attach")

address = ('0.0.0.0', 3000)
ptvsd.enable_attach(address)
ptvsd.wait_for_attach()

print("Chnages made")

print("DEBUGGER ATTACHED")
