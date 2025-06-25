def print_data_to_txt_file(data, filepath):
    with open(filepath, 'w') as f:
        for line in data:
            f.write(f"{line}\n")
            
def read_txt_file(filepath):
    l = []
    with open(filepath, "r") as f:
        for line in f.readlines():
            l.append(line.strip())
    return l