import yaml
from collections import defaultdict
import random
import time
# Load the YAML file
with open('timetable_data.yml', 'r') as file:
    data = yaml.safe_load(file)

# Data structures to hold timetable information
timetable = defaultdict(lambda: defaultdict(list))
group_sessions_per_day = defaultdict(lambda: defaultdict(int))

# Extract data from YAML
classes = data['timetable_data']['classes']
sessions = data['timetable_data']['session']
days = data['timetable_data']['days']
courses = data['timetable_data']['specialty_courses']
course_mapping = data['timetable_data']['course_mapping']
teachers = data['timetable_data']['teachers']
rooms = data['timetable_data']['rooms']


# Create a mapping of courses to their respective specialties
course_to_specialty = {}
for specialty, course_list in courses.items():
    for course in course_list:
        course_to_specialty[course] = specialty

# Create a mapping of specialties to teachers
specialty_to_teachers = defaultdict(list)
for teacher in teachers:
    teacher_id, teacher_name, grade, *teacher_specialties = teacher
    for specialty in teacher_specialties:
        if isinstance(specialty, list):
            for sub_specialty in specialty:
                specialty_to_teachers[sub_specialty].append(teacher)
        else:
            specialty_to_teachers[specialty].append(teacher)

# Helper function to find a room of a specific type
def find_room(room_type):
    for room in rooms:
        if room[1] == room_type:
            return room
    return None

# Helper function to find a teacher for a specific course based on specialty
def find_teacher(course_name, room_type):
    specialty = course_to_specialty.get(course_name, None)
    if specialty and specialty in specialty_to_teachers:
        eligible_teachers = [teacher for teacher in specialty_to_teachers[specialty] if teacher[2] == 'Professor' or teacher[2] == 'Associate Professor']
        
        # Check if the room type is 'amphi' and filter eligible teachers accordingly
        if room_type.lower() == 'amphi':
            eligible_teachers = [teacher for teacher in eligible_teachers if teacher[2] == 'Professor' or teacher[2] == 'Associate Professor']
        
        if eligible_teachers:
            return random.choice(eligible_teachers)
    return None


# Map session numbers to actual time slots
# Assign courses to classes
for course in course_mapping:
    course_name, room_type, units, course_year = course
    for cls in classes:
        if f'Y{course_year}_' in cls:
            for _ in range(units):
                assigned = False
                attempt_count = 0  # Track the number of attempts
                while not assigned and attempt_count < 100:  # Limit the number of attempts
                    day = random.choice(days)
                    print("Trying to assign session for", cls, "on day", day)  # Moved the day variable definition
                    if group_sessions_per_day[cls][day] < 5:
                        session = random.choice(sessions)
                        time_slot_start, time_slot_end = session  # Extract start and end times
                        if time_slot_start not in ('11:50', '13:30') or group_sessions_per_day[cls][day] < 3:
                            room = find_room(room_type)
                            teacher = find_teacher(course_name, room_type)
                            if teacher:
                                entry = {
                                    'group&year': cls,
                                    'indication': 'study',
                                    'course': course_name,
                                    'teacher': teacher[1] if teacher else 'Unknown',
                                    'classroom': room[3] if room else 'Unknown',
                                    'room_type': room_type
                                }
                                timetable[day][time_slot_start].append(entry)
                                group_sessions_per_day[cls][day] += 1
                                assigned = True
                    attempt_count += 1  # Increment the attempt count

                if not assigned:
                    print(f"Failed to assign session for {cls} after {attempt_count} attempts")

# Ensure each group has a lunch break after the 3rd or 4th timeslot if not already assigned
for cls in classes:
    for d in days:  # Changed the loop variable name to avoid conflict
        if group_sessions_per_day[cls][d] > 0:
            # Determine the lunch break timeslot based on the number of sessions already scheduled
            lunch_timeslot_index = min(group_sessions_per_day[cls][d], 4)  # Ensure lunch after 3rd or 4th session
            lunch_timeslot = sessions[lunch_timeslot_index]  # Assuming sessions is a list, corrected this line
            
            print("Day:", str(d))
            if not any(entry['indication'] == 'lunch break' for entry in timetable[str(d)].get(tuple(lunch_timeslot), [])):


                entry = {
                    'group&year': cls,
                    'indication': 'lunch break',
                    'course': '',
                    'teacher': '',
                    'classroom': '',
                    'room_type': ''
                }
                timetable[d][lunch_timeslot].append(entry)
                group_sessions_per_day[cls][d] += 1
