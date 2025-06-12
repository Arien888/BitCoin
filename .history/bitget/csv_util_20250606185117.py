import csv

def save_dict_to_csv(filename, data):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        for k, v in data.items():
            if isinstance(v, dict):
                v = str(v)
            writer.writerow([k, v])