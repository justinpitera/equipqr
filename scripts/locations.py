import csv

# Read raw data from file
input_file = "file.txt"
with open(input_file, mode="r") as file:
    raw_data = file.read()

# Parse the data
lines = raw_data.splitlines()
data = []

for i in range(0, len(lines), 2):  # Assuming every 2 lines form one record
    if i + 1 < len(lines):
        location_type = lines[i].split("\t")
        location = location_type[0].strip()
        location_type_value = location_type[1].strip() if len(location_type) > 1 else "Unknown"
        aircraft_list = lines[i + 1].strip()
        data.append({
            "Location": location,
            "Type": location_type_value,
            "Aircraft": aircraft_list
        })

# Write to a CSV file
output_file = "aircraft_locations.csv"

with open(output_file, mode="w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["Location", "Type", "Aircraft"])
    writer.writeheader()
    writer.writerows(data)

print(f"Data successfully written to {output_file}")
