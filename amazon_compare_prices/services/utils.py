from itertools import islice

def chunk_list(data, chunk_size=20):
    for i in range(0, len(data), chunk_size):
        yield list(islice(data, i, i + chunk_size))

