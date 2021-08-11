import os 
import time
import pandas
import re

array = [[1,2],[3,4],[5,6]]

array = sorted(array,key=lambda x: x[1], reverse=True)

print(array)