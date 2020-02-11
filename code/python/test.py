from db import Database
import datetime
now = datetime.datetime.now()

def break_down_message(message):
	ret_dict = {}
	tvps = message.split("|")
	for tvp in tvps:
		tvp_no_equals = tvp.split("=")
		# Check if entry for tag exists
		if tvp_no_equals[0] in ret_dict:
			# If it does, get list associated with it and add element to it
			ret_dict[tvp_no_equals[0]].append(tvp_no_equals[1])
		else:
			# If it doesn't, create new list with element in it associated with tag
			if len(tvp_no_equals) is 2:
				ret_dict[tvp_no_equals[0]] = [tvp_no_equals[1]]
	return ret_dict

message = '1=(52.281799, -1.532315)|2=B8:27:EB:E7:B4:70|'

breakdown = break_down_message(message)
coords = breakdown['1']
addresses = breakdown['2']
print(coords)
print(addresses)
values = []
if len(coords) == len(addresses):
	for i in range(0, len(coords)):
		values.append((addresses[i], coords[i].strip('()'), now))
print(values)
data = Database('find.db')
data.insert(values)
print(data.select(50))