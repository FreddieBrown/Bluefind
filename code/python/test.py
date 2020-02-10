from db import Database
import datetime
now = datetime.datetime.now()
values = [("AB:CD:EF:GH:IJ", "55.00, 64.00", now), ("AB:CD:EF:GH:IJ", "55.00, 64.00", now), ("AB:CD:EF:GH:IJ", "55.00, 64.00", now), ("AB:CD:EF:GH:IJ", "55.00, 64.00", now)]

data = Database()
data.insert(values)
print(data.select(50))