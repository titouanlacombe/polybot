def constrain(dict, key, min=None, max=None, default=None):
	if key not in dict:
		dict[key] = default

	if min and dict[key] < min:
		raise Exception(f"Config '{key}' < {min}")

	if max and dict[key] > max:
		raise Exception(f"Config '{key}' > {max}")

def estimate_eta(image_size: int, num_inference_steps: int):
	base_size = 512 * 512
	base_time = 10 # seconds per inference step on 512x512 image
	return base_time * (image_size / base_size) * num_inference_steps

def null_func(*args, **kwargs):
	pass
