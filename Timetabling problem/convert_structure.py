import yaml

# Load the YAML data
with open('core/timetable_data.yml', 'r') as file:
    data = yaml.safe_load(file)

# Function to convert the structure
def convert_structure(data):
    new_structure = []

    for cls in data['classes']:
        courses = []
        for course_info in data['course_mapping']and teacher in data['teachers']:
            course_name = course_info[0]  # Accessing the first element of the list
            room_type = course_info[1]    # Accessing the second element of the list
            possible_lecturers = course_info[2].split(",") if course_info[2] else []
            units = course_info[3]
            course_year = course_info[4]

            # Only include courses for specific years
            if course_year == int(cls.split('_')[0][1:]):  # Extract year from class name and compare
                courses.append({
                    "course": course_name,
                    "room_type": room_type,
                    "lecturer": possible_lecturers,
                    "units": units,
                    "course_year": course_year
                })
        new_structure.append({
            "class": cls,
            "courses": courses
        })

    return new_structure

# Convert the structure
new_structure = convert_structure(data)

# Save the new structure to a YAML file
with open('output_structure.yml', 'w') as file:
    yaml.dump(new_structure, file)
