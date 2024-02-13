import os
import json
from .files import write_json_file
from collections import OrderedDict
from itertools import islice


def object_sorted_chunks(data, chunk_size):
    # Ensure the dictionary is sorted
    sorted_data = OrderedDict(sorted(data.items()))

    it = iter(sorted_data.items())  # .items() returns tuples of (key, value)

    # 'islice' used in a loop like this will maintain its position in the iterator
    # across different iterations of the loop, effectively chunking the dict
    for _ in range(0, len(sorted_data), chunk_size):
        yield OrderedDict(islice(it, chunk_size))


def chunk_data_file(input_file: str, output_directory: str) -> None:
    data = json.load(open(input_file))
    generate_chunk_files(data, output_directory)


def generate_chunk_files(data: dict, output_directory: str) -> None:
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    chunk_size = 5000
    print(f"Chunking in increments of {chunk_size}")
    data_chunks = object_sorted_chunks(data, chunk_size)

    for i, chunk in enumerate(data_chunks):
        print(f"Chunking data chunk: {i}", end='\r')
        write_json_file(f"{output_directory}/data_chunk_{i}.json", chunk)


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def chunks_list(lst, n):
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def object_chunks(data, chunk_size):
    it = iter(data)
    for i in range(0, len(data), chunk_size):
        yield {k: data[k] for k in islice(it, chunk_size)}
