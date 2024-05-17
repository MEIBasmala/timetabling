import random
from tabulate import tabulate
import yaml

# Load data from the YAML file
with open("output_structure.yml", "r") as file:
    data = yaml.safe_load(file)

def validate_sessions_per_day(timetable):
    # Define the time slots for lunch breaks
    lunch_breaks = [(11, 50), (13, 20)]

    for class_name, class_timetable in timetable.items():
        for day, sessions in class_timetable.items():
            session_count = 0
            last_session_end_time = 0
            for session in sessions:
                session_start_time = session["start_hour"] * 60 + session["start_minute"]
                session_end_time = session["end_hour"] * 60 + session["end_minute"]
                
                # Check if session duration is more than 1 hour and 30 minutes
                if session_end_time - session_start_time > 90:
                    return False
                
                # Check if session overlaps with lunch break
                for lunch_start, lunch_end in lunch_breaks:
                    if lunch_start * 60 <= session_start_time < lunch_end * 60 or \
                       lunch_start * 60 < session_end_time <= lunch_end * 60:
                        return False
                
                # Check if there are more than 5 sessions per day
                if session_count >= 5:
                    return False
                
                # Check if there is at least a 10-minute break between sessions
                if session_start_time - last_session_end_time < 10:
                    return False
                
                session_count += 1
                last_session_end_time = session_end_time
                
    return True

def visualize_timetable(timetable_data):
    for class_info in timetable_data:  # Iterate over each class
        class_name = class_info["class"]
        courses = class_info["courses"]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        # Initialize the timetable table
        timetable_table = [[""] * len(days) for _ in range(5)]

        # Maintain a set of used rooms for each time slot
        used_rooms = {day: set() for day in days}

        # Schedule lectures for each course
        for course in courses:
            course_name = course["course"]
            room_type = course["room_type"]

            # Randomly select a day and time slot
            random_day = random.choice(days)
            random_slot = random.choice([slot for slot in range(len(days)) if len(used_rooms[random_day]) < 5])

            # Update the timetable table
            timetable_table[random_slot][days.index(random_day)] = f"{course_name} ({room_type})"
            used_rooms[random_day].add(random_slot)

        # Schedule launch breaks
        for day in days:
            if day in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
                # Choose a random time slot for launch break
                random_slot = random.choice([2, 3])  # 2 corresponds to 11.50 -> 13.20, 3 corresponds to 13.20 -> 15.10
                timetable_table[random_slot][days.index(day)] = "Launch Break"
                used_rooms[day].add(random_slot)

        # Print the timetable for the class
        print(f"{class_name}:")
        print(tabulate(timetable_table, headers=days, tablefmt="fancy_grid"))
        print("\n")

# Visualize the timetable
visualize_timetable(data)
