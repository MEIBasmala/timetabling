import yaml
import random

# Define the classes and courses
classes = [
    {
        "class": "Y1_S1_G1",
        "courses": [
            {"course": "Foundational Mathematics", "course_year": 1, "lecturer": ["t1", "t2", "t3"], "room_type": "Amphi", "units": 3},
            {"course": "Digital Systems", "course_year": 1, "lecturer": ["t4", "t5"], "room_type": "LAB", "units": 2}
        ]
    },
    {
        "class": "Y1_S1_G2",
        "courses": [
            {"course": "Data Structures and Algorithms 1", "course_year": 1, "lecturer": ["t1", "t4"], "room_type": "Amphi", "units": 3},
            {"course": "English 1", "course_year": 1, "lecturer": ["t3", "t6"], "room_type": "TUTO", "units": 2}
        ]
    }
]

# Sample teacher availability data
teacher_availability = {
    't1': [9.0, 10.5, 14.0],
    't2': [8.0, 9.0, 10.5],
    't3': [9.0, 12.0, 14.0],
    't4': [10.0, 11.0, 15.0],
    't5': [8.0, 11.0, 14.0],
    't6': [9.0, 10.0, 11.0]
}

# Calculate the cost of each timetable
def calculate_cost(timetable):
    cost = 0
    for class_schedule in timetable.values():
        for course_schedule in class_schedule:
            lecturer = course_schedule["lecturer"]
            time = course_schedule["time"]
            room_type = course_schedule["room"]
            # Add your cost calculation logic here
            # For example, checking for violations of constraints and adding to the cost accordingly
            if time not in teacher_availability.get(lecturer, []):
                cost += 100  # Penalty for scheduling a course when the teacher is not available
            if room_type == "LAB":
                cost += 50  # Penalty for scheduling a course in a lab
            # Add more cost calculation rules as needed
    return cost

# Save the timetables and their costs to a YAML file
def save_to_yaml(timetables, filename):
    data = {"timetables": timetables}
    with open(filename, 'w') as file:
        yaml.dump(data, file)

# Generate random timetables
def generate_random_timetables(num_timetables):
    timetables = {}
    for i in range(1, num_timetables + 1):
        timetable = {}
        for class_info in classes:
            class_name = class_info["class"]
            courses = class_info["courses"]
            class_schedule = []
            for course in courses:
                course_schedule = {
                    "course": course["course"],
                    "time": random.choice([9.0, 10.5, 14.0]),  # Randomly select a time
                    "room": random.choice(["RoomA", "RoomB", "RoomC"]),
                    "lecturer": random.choice(course["lecturer"])  # Randomly select a lecturer
                }
                class_schedule.append(course_schedule)
            timetable[class_name] = class_schedule
        cost = calculate_cost(timetable)
        timetables[f"Timetable {i}"] = {"schedule": timetable, "cost": cost}
    return timetables

# Depth-First Search (DFS) to find the best solution
# Depth-First Search (DFS) to find the best solution
def dfs(timetables, current_index, current_cost, best_solution, best_cost):
    if current_index == len(timetables):
        return best_cost, best_solution
    timetable_name, timetable_info = list(timetables.items())[current_index]
    new_cost = current_cost + timetable_info["cost"]
    if new_cost >= best_cost:
        return best_cost, best_solution
    new_best_solution = {}
    new_best_solution.update(best_solution)
    new_best_solution[timetable_name] = timetable_info
    for index in range(current_index + 1, len(timetables) + 1):
        new_best_cost, new_best_solution = dfs(timetables, index, new_cost, new_best_solution, best_cost)
        if new_best_cost < best_cost:
            best_cost = new_best_cost
            best_solution = {}
            best_solution.update(new_best_solution)
    return best_cost, best_solution

# Example usage
# Generate random timetables
num_timetables = 20
generated_timetables = generate_random_timetables(num_timetables)

# Call DFS to find the best solution
best_cost, best_solution = dfs(generated_timetables, 0, 0, {}, float('inf'))

# Print the best solution and its cost
print("Best solution:")
print(best_solution)
print("Cost:", best_cost)
