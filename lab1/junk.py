# def strip_spaces(L):
# 	return list(map(lambda x: x.strip(" "), L))

# # get small numbers within hundred
# def get_small_numbers(text):
# 	if text == "":
# 		return 0
# 	mSum = 0
# 	parts = text.split(" ")
# 	L = len(parts)
# 	if L == 1:
# 		if face_values.has_key(text):
# 			return face_values[text]
# 		elif two_digit_vals.has_key(text):
# 			return two_digit_vals[text]
# 		elif r_values.has_key(text):
# 			return r_values[text]
# 		else:
# 			raise Exception("Error: Token %s not present"%(text))
# 	elif L == 2:
# 		if r_values.has_key(parts[0]) and face_values.has_key(parts[1]):
# 			return (r_values[parts[0]] + face_values[parts[1]])
# 		raise Exception("Error: String %s not identified."%(text))
# 	else:
# 		raise Exception("Error: String %s not identified."%(text))

# def numeric_value_util(text):
# 	# help to get numbers within text of hundred
# 	if text == "":
# 		return 0
# 	mSum = 0
# 	parts = strip_spaces(text.split("hundred"))
# 	L = len(parts)
# 	if L == 1:
# 		mSum = get_small_numbers(parts[0])
# 	elif L == 2:
# 		if parts[0] == "":
# 			raise Exception("Enter a face value of hundred. e.g. one hundred.")
# 		mSum = max(1, get_small_numbers(parts[0]))*100 + get_small_numbers(parts[1])
# 	else:
# 		raise Exception("A number can't have 2 or more instances of the word hundred.")
# 	return mSum		

# def numeric_value(text):
# 	if text == "zero" or text == "":
# 		return 0

# 	parts = strip_spaces(text.split("thousand"))
# 	n = len(parts)
# 	if n == 1:
# 		k = numeric_value_util(parts[0])
# 		return k
# 	elif n == 2:
# 		if parts[0] == "":
# 			raise Exception("Enter a face value of thousand. e.g. one thousand.")
# 		k1 = numeric_value_util(parts[0])
# 		k2 = numeric_value_util(parts[1])
# 		if k1 >= 1000:
# 			raise Exception("Number is above a million, not supported.")
# 		elif k2 >= 1000:
# 			raise Exception("Invalid use of thousand and hundred.")
# 		return (1000*max(1, k1) + k2)
# 	else:
# 		raise Exception("A number can't have 2 or more instances of the word thousand.")

# def changeKeys(data, keys):
# 	keys = sorted(keys, reverse=True, key=lambda x: len(x))
# 	for key in keys:
# 		number = numeric_value(key)
# 		data = data.replace(key, str(number))
# 	return data

# def preprocess(data):
# 	# change all the symbols -> simple find and replace
# 	for key, val in mappings.items():
# 		data = data.replace(key, val)

# 	# change the numbers now
# 	keys = list(map(lambda x: x.strip(" "), re.findall(r'[a-z\ ]+', data)))
# 	keys = list(filter(lambda x: len(x), keys))
# 	# print(keys)
# 	data = changeKeys(data, keys)
# 	return data

