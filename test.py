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
	
	


print(break_down_message('1=(52.281807, -1.532221)|2=DC:A6:32:26:CE:70|1=(52.281807, -1.532221)|2=DC:A6:32:26:CE:70|'))
