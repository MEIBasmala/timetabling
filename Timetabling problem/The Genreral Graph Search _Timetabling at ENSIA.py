
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from collections import deque
from random import choice
from bisect import insort
from colorama import init, Fore, Back, Style
import numpy as np

#________________________________TRANSITION MODEL____________________________________________________________________________________
transtion_mmodel =  {

        "course_conflict": {
            "swap_course": 450,
            "Assign_Teacher": 320,
            "Assign_Course": 80,
            "Assign_Classroom": 700,
            "Move_Course": 200
            "Split_Course" : ,
            "Change_Room" : 
            
        },
        "teacher_conflict": {
           
        },
        "classroom_conflict": {  
        
        },
        "no_launch_break" :{
            
    
        }
        "time_slots < 5" : {}
        
        "work > availability " :{}
        
        "course_unit_not_fullfiled" :{}
        
        "course_unit_more_then_fullfiled " : {}
        "day_is_loaded" :{}
        "day_more_then_two_lectures" :{}
        "teacher_module > limit":{}
        "two_sections != teacher":{}
        "lecture's teacher is not Phd":{}
        
        "groups " : {}
        }

#________________________________TIMETABLE STRUCTURE AND NODE CLASS___________________________________________________________________________________

with open("output_structure.yml", "r") as file:
    Timetable_data = yaml.safe_load(file)
    
    class Node(object):
    """
    A class to represent a node in the search. This node stores state
    information, path to the state, cost of the node, depth of the node, and
    any extra information.
    
    :param state: the state at this node
    :type state: object for tree search and hashable object for graph search
    :param parent: the node from which the current node was generated
    :type parent: :class:`Node`
    :param action: the action performed to transition from parent to current.
    :type action: typically a string, but can be any object
    :param cost: the cost of reaching the current node
    :type cost: float
    :param extra: extra information to store in this node, typically used to
                  store non-hashable information about the state.
    :type extra: object
    """

    def __init__(self, state, parent=None, action=None, node_cost=0,
                 extra=None):
        self.state = state 'must'
        self.parent = parent
        self.action = action
        self.node_cost = node_cost'must'
        self.extra = extra

        if parent is None:
            self.node_depth = 0
        else:
            self.node_depth = parent.depth() + 1

         time_slots = {
                    "Sunday": [8.30 , 10.10 , 11.50 , 13.30 , 15.10 , 16.50 ],
                    "Monday": [8.30 , 10.10 , 11.50 , 13.30 , 15.10 , 16.50 ],
                    "Tuesday": [8.30 , 10.10 , 11.50 , 13.30 , 15.10 , 16.50 ],
                    "Wednesday": [8.30 , 10.10 , 11.50 , 13.30 , 15.10 , 16.50 ],
                    "Thursday": [8.30 , 10.10 , 11.50 , 13.30 , 15.10 , 16.50 ]
                    }
    
    def depth(self):
        """
        Returns the depth of the current node.
        """
        return self.node_depth

    def cost(self):
        """
        Returns the cost of the current node.
        """
        return self.node_cost

    def path(self):
        """
        Returns a path (tuple of actions) from the initial to current node.
        """
        actions = []
        current = self
        while current.parent:
            actions.append(current.action)
            current = current.parent
        actions.reverse()
        return tuple(actions)

    def __str__(self):
#         return "State: %s, Extra: %s" % (self.state, self.extra)
        return "State: %s, Cost: %s" % (self.state, self.node_cost)

    def __repr__(self):
        return "Node(%s, Cost(%s))" % (repr(self.state), repr(self.node_cost))

    def __hash__(self):
        return hash(self.state)
        """Dictionary Keys and Set Elements: By defining a __hash__ method for the Node class, instances
        of Node can be used as keys in dictionaries or elements in sets. This allows for efficient 
        lookup and retrieval based on the state of the node."""

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.cost() < other.cost()

#________________________________TIMETABLE visualisation___________________________________________________________________________________

def visualize_timetable(Timetable_data):
    for class_info in Timetable_data:  # Iterate over each class
        class_name = class_info["class"]
        courses = class_info["courses"]

        # Calculate the total number of slots needed to accommodate all courses
        total_slots_needed = sum(course["units"] for course in courses)

        # Calculate the maximum number of slots to be filled per day
        max_slots_per_day = 5

        # Calculate the number of days needed to accommodate all slots
        days_needed = (total_slots_needed + max_slots_per_day - 1) // max_slots_per_day

        # Initialize the timetable table
        timetable_table = [[""] * 5 for _ in range(days_needed)]

        # Iterate over each course and fill in the timetable
        current_day = 0
        current_slot_count = 0
        for course in courses:
            course_name = course["course"]
            room_type = course["room_type"]
            units = course["units"]

            # Fill in the current slot
            timetable_table[current_day][current_slot_count] = f"{course_name} ({room_type})"
            current_slot_count += 1

            # Move to the next day if the maximum slots per day is reached
            if current_slot_count >= max_slots_per_day:
                current_day += 1
                current_slot_count = 0

        # Print the timetable for the class
        print(f"{class_name}:")
        print(tabulate(timetable_table, headers=["Sun","Mon", "Tue", "Wed", "Thu"], tablefmt="fancy_grid"))
        print("\n")

# Visualize the timetable
visualize_timetable(data)



#________________________________OBJECTIVE FUNCTION____________________________________________________________________________________"

with open('Timetable_data.yml', 'r') as file:
    Timetable_data = yaml.safe_load(file)

def assign_courses_to_teachers(timetable_data):
    teacher_courses_dict = {}

    if 'course_mapping' in timetable_data and 'teachers' in timetable_data:
        course_mapping = timetable_data['course_mapping']
        teachers = timetable_data['teachers']

        # Manually assigning courses to each specialty
        specialty_courses = {
            "Computer Science": ["Data Structures and Algorithms 1", "Digital Systems", "Information Technology Essentials",
                                 "Object Oriented Programming", "Introduction to Linux", "Data Structures and Algorithms 2",
                                 "Databases", "Web Development", "Theory of Computing", "Operating Systems",
                                 "Computer Architecture", "Introduction to AI", "Data Mining", "Operations Research",
                                 "Software Engineering", "Networks and Protocols", "Mobile Development", "Machine Learning",
                                 "Advanced Databases", "Computer and network Security", "Natural Language Processing",
                                 "Deep Learning", "Human Computer Interaction", "Introduction to Mobile Robotics",
                                 "Wireless Communication Networks and Systems", "Selected topics in AI-Technology","Electronic Circuits LABs"],
            "Mathematics": ["Foundational Mathematics", "Linear Algebra", "Mathematical Analysis 1", "Mathematical Analysis 2",
                            "Mathematical Logic", "Mathematical Analysis 3","Time Series Analysis and Classification",
                            "Numerical Methods and Optimisation"],
            "Statistics": ["Statistical Inference","Probability",  "Introduction to Statistics", "Stochastic Modelling and Simulation"],
            "Organizational Psychology": ["Critical Thinking and Creativity Skills"],
            "English": ["English 1","English 2"],
            "Business & Entrepreneurship": ["Entrepreneurship and Innovation","Introduction to Business","Group-Project"]
        }

        # Initialize teacher_courses_dict with empty lists for each teacher
        for teacher_info in teachers:
            teacher_id, teacher_name, grade, specialty, availability, years_responsible_for = teacher_info
            teacher_courses_dict[teacher_name] = []

        # Iterate over course mapping to assign courses to teachers based on specialty
        for course_info in course_mapping:
            course, room_type, lecturers, units, course_year = course_info
            for teacher_info in teachers:
                teacher_id, teacher_name, grade, teacher_specialty, availability, years_responsible_for = teacher_info
                if teacher_specialty in specialty_courses and course in specialty_courses[teacher_specialty]:
                    teacher_courses_dict[teacher_name].append(course)

    return teacher_courses_dict

# Usage example
assigned_courses = assign_courses_to_teachers(timetable_data)
for teacher, courses in assigned_courses.items():
    print(f"Teacher: {teacher}")
    if courses:
        print("Courses taught by this teacher:")
        for course in courses:
            print(f"- {course}")
    else:
        print("This teacher doesn't teach any courses in the provided data.")
  

# def calculate_initial_cost():

def generate_intial_timtable(Timetable_data):
    timetable = {}

    if 'course_mapping' in Timetable_data and 'teachers' in Timetable_data:
        course_mapping = Timetable_data['course_mapping']
        teachers = Timetable_data['teachers']

    for teacher in teachers:
        possible_lecturers = {
            if teachers[3] = 

        } 

    # Now you can iterate over course_mapping and teachers
    for class_info in Timetable_data:  # Iterate over each class
        class_name = class_info["class"]
        courses = class_info["courses"]

        # Calculate the total number of slots needed to accommodate all courses
        total_slots_needed = sum(course["units"] for course in courses)

        # Calculate the maximum number of slots to be filled per day
        max_slots_per_day = 5

        # Calculate the number of days needed to accommodate all slots
        days_needed = (total_slots_needed + max_slots_per_day - 1) // max_slots_per_day

        # Initialize the timetable table
        timetable_table = [[""] * 5 for _ in range(days_needed)]





def objective_fun (Node):

#There must be a limit on the number of modules that can be teached by a single teacher.S
    for each class_info in Node.state[]

#At given time slot , only one subject is tackled.S
#     Distribute teachers evenly between Groups and years S
#     There must be a limit on the number of modules that can be teached by a single teacher.S
#     At given time slot , only one subject is tackled.S
# Respecting the hours given to each course , in terms of lectures , tutorials and labs.S
   
            
#________________________________PROBLEM DEFINTION____________________________________________________________________________________"

    

class Problem(object): "the timetable problem for the general graph search"
 

    def __init__(self, initial, goal=None, initial_cost=0, extra=None):
        self.initial = Node(initial, None, None, initial_cost, extra=extra)
        self.goal = GoalNode(goal)

    def node_value(self, node):
        """
        Returns the value of the current node. This is the value being
        minimized by the search. By default the cost is used, but this
        function can be overloaded to include a heuristic.
        """
        return node.cost()

    def predecessors(self, node):
        """
        An iterator that yields all of the predecessors of the current goal.
        """
        raise NotImplementedError("No predecessors function implemented")

    def successors(self, node):
        """
        An iterator that yields all of the successors of the current node.
        the result of applying the actions to states 
        """
        raise NotImplementedError("No successors function implemented")

    def random_successor(self, node):
        """
        This method should return a single successor node. This is used
        by some of the search techniques. By default, this just computes all of
        the successors and randomly samples one. This default approach is not
        very efficient, but this funciton can be overridden to generate a
        single successor more efficiently.
        """
        return choice([s for s in self.successors(node)])

    def random_node(self):
        """
        This method returns a random node in the search space. This
        is used by some of the local search / optimization techniques to
        randomly restart search.
        """
        raise NotImplementedError("No random node implemented!")

    def goal_test(self, state_node, goal_node=None):
        """
        Returns true if a goal state is found. This is typically not used by
        the local search / optimization techniques, but some of them use the
        goal test to determine if the search should terminate early. By
        default, this checks if the state equals the goal.
        """
        if goal_node is None:
            goal_node = self.goal
        return state_node == goal_node

    
"________________________________OBJECTIVE FUNCTION____________________________________________________________________________________"
       
            

class GoalNode(Node):
    """
    Used to represent goals in the backwards portion of the search.
    """

    def __repr__(self):
        return "GoalNode(%s)" % repr(self.state)

    def path(self):
        """
        Returns a path (tuple of actions) from the initial to current node.

        Similar to Node's path function, but returns the path in the opposite
        order because the goal nodes branch out from the goal (not the start
        state).
        """
        actions = []
        current = self
        while current.parent:
            actions.append(current.action)
            current = current.parent
        return tuple(actions)


class SolutionNode(object):
    """
    A Node class that joins a state (:class:`Node`) and a goal
    (:class:`GoalNode`) in bidirectional search, so that it can be returned and
    the used like other :class:`Node`. In particular it provides an isomorphic
    interface for querying depth, cost, and path.

    The state, parent, action, node_cost, and extra attributes have been
    removed because they are not well defined for a join. The key issue here is
    that the state and goal nodes might not be specified in the same terms. For
    example, goals may be partial states and goal_test might return True when
    the state_node satisfies the goal_node (not when they are strictly equal).

    Thus, to generate the actual state represented by the solution node, the
    returned path needs to be executed from the initial state, which is outside
    the scope of this library since it has no knowledge of how to execute paths
    (it just generates them using the user specified successor/predecessor
    functions).
    """

    def __init__(self, state, goal):
        self.state_node = state
        self.goal_node = goal

    def depth(self):
        return self.state_node.depth() + self.goal_node.depth()

    def cost(self):
        return self.state_node.cost() + self.goal_node.cost()

    def path(self):
        return self.state_node.path() + self.goal_node.path()

    def __str__(self):
        return "StateNode={%s}, GoalNode={%s}" % (self.state_node,
                                                  self.goal_node)

    def __repr__(self):
        return "SolutionNode(%s, %s)" % (repr(self.state_node),
                                         repr(self.goal_node))

    def __hash__(self):
        return hash((self.state_node.state, self.goal_node.state))

    def __eq__(self, other):
        return (isinstance(other, SolutionNode) and
                self.state_node == other.state_node and
                self.goal_node == other.goal_node)

    def __ne__(self, other):
        return not self.__eq__(other)


class Fringe(object):
    """
    A template for a fringe class. Used to control the strategy of different
    search approaches.
    """

    def push(self, node):
        """
        Adds one node to the collection.
        """
        raise NotImplementedError("No push method")

    def extend(self, nodes):
        """
        Given an iterator (`nodes`) adds all the nodes to the collection.
        """
        for n in nodes:
            self.push(n)

    def pop(self):
        """
        Pops a node off the collection.
        """
        raise NotImplementedError("No pop method")

    def __len__(self):
        """
        Returns the length of the fringe.
        """
        raise NotImplementedError("No __len__ method")

    def __iter__(self):
        """
        Returns iterator that yields the elements in the order they would be
        popped.
        """
        raise NotImplementedError("No __iter__ method")


class FIFOQueue(Fringe):
    """
    A first-in-first-out queue. Used to get breadth first search behavior.

    >>> fifo = FIFOQueue()
    >>> fifo.push(0)
    >>> fifo.push(1)
    >>> fifo.push(2)p
    >>> list(fifo)
    [0, 1, 2]
    >>> fifo.remove(2)
    >>> print(fifo.pop())
    0
    >>> print(fifo.pop())
    1
    """

    def __init__(self):
        self.nodes = deque()

    def push(self, node):
        self.nodes.append(node)

    def remove(self, node):
        for i in range(self.nodes.count(node)):
            self.nodes.remove(node)

    def pop(self):
        return self.nodes.popleft()

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)


class LIFOQueue(FIFOQueue):
    """
    A last-in-first-out queue. Used to get depth first search behavior.

    >>> lifo = LIFOQueue()
    >>> lifo.push(0)
    >>> lifo.push(1)
    >>> lifo.push(2)
    >>> list(lifo)
    [2, 1, 0]
    >>> print(lifo.pop())
    2
    >>> print(lifo.pop())
    1
    >>> print(lifo.pop())
    0
    """

    def pop(self):
        return self.nodes.pop()

    def __iter__(self):
        return reversed(self.nodes)


class PriorityQueue(Fringe):
    """
    A priority queue that sorts elements by their value. Always returns the
    minimum value item.  A :class:`PriorityQueue` accepts a node_value
    function, a cost_limit (nodes with a value greater than this limit will not
    be added) and a max_length parameter. If adding an item ever causes the
    size to exceed the max_length then the worst nodes are removed until the
    list is equal to max_length.

    >>> pq = PriorityQueue(node_value=lambda x: x, max_length=3)
    >>> pq.push(6)
    >>> pq.push(0)
    >>> pq.push(2)
    >>> pq.push(6)
    >>> pq.push(7)
    >>> len(pq)
    3
    >>> list(pq)
    [0, 2, 6]
    >>> pq.update_cost_limit(5)
    >>> len(pq)
    2
    >>> pq.peek()
    0
    >>> pq.peek_value()
    0
    >>> print(pq.pop())
    0
    >>> pq.peek()
    2
    >>> pq.peek_value()
    2
    >>> print(pq.pop())
    2
    >>> len(pq)
    0

    :param node_value: The node evaluation function (defaults to
        ``lambda x: x.cost()``)
    :type node_value: a function with one parameter for node
    :param cost_limit: the maximum value for elements in the set, if an item
        exceeds this limit then it will not be added (defaults to
        ``float('inf'))``
    :type cost_limit: float
    :param max_length: The maximum length of the list (defaults to
        ``float('inf')``
    :type max_length: int or ``float('inf')``
    """

    def __init__(self, node_value=lambda x: x, cost_limit=float('inf'),
                 max_length=float('inf')):
        self.nodes = []
        self.max_length = max_length
        self.cost_limit = cost_limit
        self.node_value = node_value

    def clear(self):
        """
        Empties the list.
        """
        self.nodes = []

    def peek(self):
        """
        Returns the best node.
        """
        return self.nodes[-1][1]

    def peek_value(self):
        """
        Returns the value of the best node.
        """
        return -self.nodes[-1][0]

    def update_cost_limit(self, cost_limit):
        """
        Updates the cost limit and removes any nodes that violate the new
        limit.
        """
        self.cost_limit = cost_limit
        for i in range(len(self.nodes)):
            if self.nodes[i][0] >= -self.cost_limit:
                self.nodes = self.nodes[i:]
                break

    def push(self, node):
        """
        Push a node into the priority queue. If the node exceeds the cost limit
        then it is not added. If the max_length is exceeded by
        adding the node, then the worst node is discarded from the set.
        """
        value = self.node_value(node)

        if value > self.cost_limit:
            return

        insort(self.nodes, (-value, node))

        if len(self.nodes) > self.max_length:
            val, node = self.nodes.pop(0)

    def pop(self):
        """
        Pop the best value from the priority queue.
        """
        val, node = self.nodes.pop()
        return node

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        for v, n in reversed(self.nodes):
            yield n


#_________________________________________SEARCH ALGORITHMS____________________________________________________________________________________
def General_Graph_search (self ,problem ,  strategy , intial_timetable, wanted_timetable , state_transition_model):
    
    if strategy == 'DFS'
    
    elif strategy == 'BFS'
    
    elif strategy == 'A*'
    
    elif strategy == 'local hill climbing*'
    
    else 
        print('non valid strategy')

#_________________DFS______________________________________________
    
#_________________BFS_______________________________________________
#_________________A*_________________________________________________

#_________________HILL CLIMBING: random restarts version_____________

"""
This module contains the local search / optimization techniques. Instead of
trying to find a goal state, these algorithms try to find the lowest cost
state.
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from math import exp
from math import log
from random import random

# from py_search.base import PriorityQueue
# from py_search.base import SolutionNode


def branch_and_bound(problem, graph=True, depth_limit=float('inf')):
    """
    An exhaustive optimization technique that is guranteed to give the best
    solution. In general the algorithm starts with some (potentially
    non-optimal) solution. Then it uses the cost of the current best solution
    to prune branches of the search that do not have any chance of being better
    than this solution (i.e., that have a node_value > current best cost).

    In this implementation, node_value should provide an admissible lower bound
    on the cost of solutions reachable from the provided node. If node_value is
    inadmissible, then optimality guarantees are lost.

    Also, if the search space is infinite and/or the node_value function
    provides too little guidance (e.g., node_value = float('-inf')), then
    the search might never terminate. To counter this, a depth_limit can be
    provided that stops expanding nodes after the provided depth. This will
    ensure the search is finite and guaranteed to terminate.

    Finally, the problem.goal_test function can be used to terminate search
    early if a good enough solution has been found. If goal_test(node) return
    True, then search is immediately terminated and the node is returned.

    Note, the current implementation uses best-first search via a priority
    queue data structure.

    :param problem: The problem to solve.
    :type problem: :class:`py_search.base.Problem`
    :param graph: Whether to use graph search (no duplicates) or tree search
                  (duplicates).
    :type graph: Boolean
    """
    b = None
    bv = float('inf')

    fringe = PriorityQueue(node_value=problem.node_value)
    fringe.push(problem.initial)

    if graph:
        closed = set()
        closed.add(problem.initial)

    while len(fringe) > 0:
        pv = fringe.peek_value()

        if bv < pv:
            break

        node = fringe.pop()

        if problem.goal_test(node, problem.goal):
            yield SolutionNode(node, problem.goal)

        if problem.node_value(node) < bv:
            b = node
            bv = problem.node_value(node)
            fringe.update_cost_limit(bv)

        if depth_limit == float('inf') or node.depth() < depth_limit:
            for s in problem.successors(node):
                if not graph:
                    fringe.push(s)
                elif s not in closed:
                    fringe.push(s)
                    closed.add(s)

    yield SolutionNode(b, problem.goal)


def hill_climbing(problem, random_restarts=0, max_sideways=0, graph=True): #random restart version 
    """
    Probably the simplest optimization approach. It expands the list of
    neighbors and chooses the best neighbor (steepest descent hill climbing).

    Default configuration should yield similar behavior to
    :func:`local_beam_search` when it has a width of 1, but doesn't need to
    maintain alternatives, so might use slightly less memory (just stores the
    best node instead of limited length priority queue).

    If graph is true (the default), then a closed list is maintained.  This is
    imporant for search spaces with platues because it keeps the algorithm from
    reexpanding neighbors with the same value and getting stuck in a loop.

    If random_restarts > 0, then search is restarted multiple times. This can
    be useful for getting out of local minimums.

    The problem.goal_test function can be used to terminate search early if a
    good enough solution has been found. If goal_test(node) return True, then
    search is immediately terminated and the node is returned.

    :param problem: The problem to solve.
    :type problem: :class:`py_search.base.Problem`
    :param random_restarts: The number of times to restart search. The
        initial state is used for the first search and subsequent starts begin
        at a random state.
    :type random_restarts: int
    :param max_sideways: Specifies the max number of contiguous sideways moves.
    :type max_sideways: int
    :param graph: Whether to use graph search (no duplicates) or tree search
        (duplicates)
    :type graph: Boolean
    """
    b = problem.initial
    bv = problem.node_value(b)

    if problem.goal_test(b, problem.goal):
        yield SolutionNode(b, problem.goal)

    if graph:
        closed = set()
        closed.add(problem.initial)

    c = b
    cv = bv

    while random_restarts >= 0:
        found_better = True
        sideways_moves = 0
        while found_better and sideways_moves <= max_sideways:
            found_better = False
            prev_cost = cv
            for s in problem.successors(c):
                if graph and s in closed:
                    continue
                elif graph:
                    closed.add(s)
                sv = problem.node_value(s)
                if sv <= bv:
                    b = s
                    bv = sv
                    if problem.goal_test(b, problem.goal):
                        yield SolutionNode(b, problem.goal)
                if sv <= cv:
                    c = s
                    cv = sv
                    found_better = True
            if cv == prev_cost:
                sideways_moves += 1
            else:
                sideways_moves = 0

        random_restarts -= 1
        if random_restarts >= 0:
            c = problem.random_node()
            while graph and c in closed:
                c = problem.random_node()
            cv = problem.node_value(c)

            if graph:
                closed.add(c)
            if cv <= bv:
                b = c
                bv = cv
                if problem.goal_test(b, problem.goal):
                    yield SolutionNode(b, problem.goal)

    yield SolutionNode(b, problem.goal)




#_________________________________________M A I N ____________________________________________________________________________________

#generte the intial timetables seperatly , 1y , 2y , 3y then 4y

#generate succsor and apply objective function to each one for evaluation

#start search using the 4 stratigies :do compare the reunnig time 
#return the best solution 

