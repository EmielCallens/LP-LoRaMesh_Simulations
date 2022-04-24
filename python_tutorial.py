import sys
import math
import random
import threading
import time
from functools import reduce
import re
import sqlite3
import csv
'''
print("5 + 2 =", 5+2)
print("5 - 2 =", 5-2)
print("5 / 2 =", 5/2)
print("5 % 2 =", 5%2)
print("5 ** 2 =", 5**2)
print("5 // 2 =", 5//2)
i1 = 2
i1 += 1
print("i1", i1)
print("Random", random.randint(1, 101))
#NaN and inf
<>, <=, >=, ==, !=
print("Enter age: ", end="")
age = int(input())

if age > 18:
    print("you can drink liquor")
elif age >= 16:
    print("you can drink beer")
# and or not
canVote = True if age >= 18 else False
print(canVote)

print(r"I'll be ignored \n")
print("Hello "+ "You")
str3 = "Hello You"
print("Length", len(str3))
print("1st", str3[0])
print("Last", str3[-1])
print("1st 3", str3[0:3])
print("Every other", str3[0:-1:2])
str3 = str3.replace("Hello", "Goodbye")
print(str3)
str3 = str3[:8] + "y" + str3[9:]
print(str3)
print("you" not in str3)
print("You index", str3.find("you"))
print("    Hello    ".strip()) #lstrip rstrip
print(" ".join(["Some", "Words"]))
print("A string".split(" "))

int1 = int2 = 5
print(f"{int1}+{int2} = {int1 + int2}")

print("A String".lower())
print("A String".upper())
print("A String 123".isalnum())
print("AString123".isalnum())
print("A String".isalpha())
print("AString".isalpha())
print("A String".isdigit())
print("123".isdigit())
#Lists
l1 = [1, 3.14, "Derek", True]
print("length", len(l1))
print("1st", l1[0])
print("Last", l1[-1])
l1[0] = 2
l1[2:4] = ["Bob", False]
l1[2:2] = ["Paul", 9]
l1.insert(2, "Paul2")
l2 = l1 + ["Egg", 4]
l2. remove("Paul2")
l2.pop(0)
print("l1", l1)
print("l2", l2)
l2 = ["Egg", 4] + l1
l3 = [[1, 2],[3, 4]]
print("l3[1,1]", l3[1][1])
print("1 Exists", (1 in l1))
print("Min", min([1, 2, 3]))
print("Max", max([1, 2, 3]))
print("1st to 2", l1[0:2])
print("Every other", l1[0:-1:2])
print("Reverse", l1[::-1])

#Loops while
w1 = 1
while w1 < 5:
    print(w1)
    w1 += 1
w2 = 0
while w2 <= 20:
    if w2 % 2 == 0:
        print(w2)
    elif w2 == 9:
        break
    else:
        w2 += 1
        continue
    w2 += 1
l4 = [1, 3.14, "Derek"]
while len(l4):
    print(l4.pop(0))
    
#Loops For
for x in range(0, 10):
    print(x, ' ', end="")
print()
l4 = [1, 3.14, "Derek"]
for x in l4:
    print(x)
for x in [2, 4, 6]:
    print(x)

#Iterating & Ranges
l5 = [6, 9, 12]
itr = iter(l5)
print(next(itr))
print(next(itr))
print(list(range(0, 10, 2)))
num_list = [[1, 2, 3], [10, 20, 30], [100, 200, 300]]
for x in range(0, 3):
    for y in range(0, 3):
        print(num_list[x][y])
#topols? lists that can't be changed
t1 = (1, 3.14, "Derek")
print("Length", len(t1))
print("First", t1[0])
print("Last", t1[-1])
print("1st 2", t1[0:2])
print("Every Other", t1[0:-1:2]) # from 0 to end (-1) with steps of 2
print("Reverse", t1[::-1])
#Dictionairies
heroes = {
    "Superman": "Clark Kent",
    "Batman": "Bruce Wayne"
}
villains = dict([
    ("Lex Luthor", "Lex Luthor"),
    ("Loki", "Loki")
])
print("Length", len(heroes))
print(heroes["Superman"])
heroes["Flash"] = "Barry Allan"
heroes["Flash"] = "Barry Allen"
print(list(heroes.items()))
print(list(heroes.keys()))
print(list(heroes.values()))
del heroes["Flash"]
print(heroes.pop("Batman"))
print("Superman" in heroes)
for k in heroes:
    print(k)
for v in heroes.values():
    print(v)
d1 = {"name": "Bread", "price": .88}
print("%(name)s cost $%(price).2f" % d1)

#Sets
s1 = set(["Derek", 1])
s2 = {"Paul", 1}

print("Length", len(s2))
s3 = s1 | s2
print(s3)
s3.add("Dough")
s3.discard("Derek")
print("Random", s3.pop())
s3 |= s2
print(s1.intersection(s2))
print(s1.symmetric_difference(s2))
print(s1.difference(s2))
s3.clear()
s4 = frozenset(["Paul", 7])
#Functions
def get_sum(num1: int = 1, num2: int = 1):
    return num1 + num2
print(get_sum(5 ,4))

def get_sum2(*args):
    sum = 0
    for arg in args:
        sum += arg
    return sum
print(get_sum2(1, 2, 3, 4))

def next_2(num):
    return num + 1, num +2

i1, i2 = next_2(5)
print(i1, i2)
#nameless function inside of a function
def mult_by(num):
    return lambda x: x * num
print("3*5=", (mult_by(3)(5)))

def mult_list(list, func):
    for x in list:
        print(func(x))
mult_by_4 = mult_by(4)
mult_list(list(range(0, 5)), mult_by_4)
power_list = [lambda x: x ** 2,
              lambda x: x ** 3]
print(power_list[1](2))
#Map
one_to_4 = range(1, 5)
times2 = lambda x: x * 2
print(list(map(times2, one_to_4)))
#Filter
print(list(filter((lambda x: x % 2 == 0), range(1, 11))))
#Reduce
print(reduce((lambda x, y: x + y), range(1, 6)))
#Exception Handling
while True:
    try:
        number = int(input("Please enter a number:"))
        break
    except ValueError:
        print("You didn't enter a number")
    except:
        print("An unknown error occurred")
print("Thank you")
#Files
with open("mydata.txt", mode="w", encoding="utf-8")\
    as my_file:
    my_file.write("Some randomtext\nMore random text\nand more")
with open("mydata.txt", encoding="utf-8") as my_file:
    print(my_file.read())
print(my_file.closed)
#Classes and Objects
class Square:
    def __init__(self):
        self.__width = "0"
        self.__height = "0"
    def __int__(self, height, width):
        self.height = height
        self.width = width
    @property
    def height(self):
        print("Retrieving the height")
        return self.height
    @height.setter
    def height(self, value):
        if value.isdigit():
            self.__height = value
        else:
            print("Please only enter numbers of height")
    @property
    def width(self):
        print("Retrieving the width")
        return self.width
    @width.setter
    def width(self, value):
        if value.isdigit():
            self.__width = value
        else:
            print("Please only enter numbers of width")
    def get_area(self):
        return int(self.__width) * int(self.__height)
square = Square()
square.height = "10"
square.width = "10"
print("Area", square.get_area())
#More functions
class Animal:
    def __init__(self, name="unknown", weight=0):
        self.__name = name
        self.__weight = weight

    @property
    def name(self, name):
        self.__name = name

    def make_noise(self):
        return "Grrrrr"

    def __str__(self):
        return "{} is in a {} and says {}".format(self.__name, type(self).__name__, self.make_noise())

    def __gt__(self, animal2):
        if self.__weight > animal2.__weight:
            return True
        else:
            return False
    #Other Methods
    #__eq__ : Equal
    #__ne__ : Not Equal
    #__lt__ : Less Than
    #__gt__ : Greater Than
    #__le__ : Less Than or Equal
    #__ge__ : Greater Than or Equal
    #__add__ : Addition
    #__sub__ : Substraction
    #__mul__ : Multiplication
    #__div__ : Division
    #__mod__ : Modulus
    #__str__ : String

class Dog(Animal):
    def __init__(self, name="unknown", owner="unknown", weight=0):
        Animal.__init__(self, name, weight)
        self.__owner = owner

    def __str__(self):
        return super().__str__() + " and is owned by " + self.__owner

animal = Animal("Spot", 100)
print(animal)
dog = Dog("Bowser", "Bob", 150)
print(dog)
print(animal > dog)
#Threads = block of code, cyclic execution
def execute_thread(i):
    #time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    print("Thread {} sleeps at {}".format(i, time.strftime("%H:%M:%S", time.gmtime())))
    rand_sleep_time = random.randint(1, 5)
    time.sleep(rand_sleep_time)
    print("Tread {} stops sleeping at {}".format(i, time.strftime("%H:%M:%S", time.gmtime())))

for i in range(10):
    thread = threading.Thread(target=execute_thread, args=(i,))
    thread.start()

    print("Active Thread:", threading.activeCount())
    print("Thread Objects:", threading.enumerate())
#Regular Expressions - locate and change strings
import re
if re.search("ape", "The ape at the apex"):
    print("There is an ape")
allApes = re.findall("ape", "The ape at the apex")
for i in allApes:
    print(i)
the_str = "The ape at the apex"
#ape. means ape followed by a single character
#find iterate or finditer, returns the indexes in the string instead of the word
for i in re.finditer("ape.", the_str):
    loc_tuple = i.span() #span returns the tuple
    print(loc_tuple)
    print(the_str[loc_tuple[0]:loc_tuple[1]]) #use indexes found ith finditer and saved in the tuple to slice the string
#Databases
import sqlite3
import csv
def print_DB():
    try:
        result = theCursor.execute("SELECT id, FName, LName, Age, Address, Salary,  HireDate FROM Employees")
        for row in result:
            print("ID:", row[0])
            print("FName:", row[1])
            print("LName:", row[2])
            print("Age:", row[3])
            print("Address:", row[4])
            print("Salary:", row[5])
            print("HireDate:", row[6])
    except sqlite3.OperationalError:
        print("The table doesn't exist")
    except:
        print("General error")
db_conn = sqlite3.connect('test.db')
print("Database created")
theCursor = db_conn.cursor()
try:
    db_conn.execute("CREATE TABLE Employees(ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, FName TEXT NOT NULL, LName NOT NULL, Age INT NOT NULL, Address TEXT, Salary REAL, HireDate TEXT);")
    db_conn.commit()
    print("Table Created")
except sqlite3.OperationalError:
    print("Table Not Created")
except:
    print("General Error")
db_conn.execute("INSERT INTO Employees (FName, LName, Age, Address, Salary, HireDate)" "VALUES ('Derek', 'Banas', 41, '123 Main st', '500,000', date('now'))")
db_conn.commit()
print_DB()
db_conn.close()
#Call other files and recursive function
import myfunc
print(myfunc.factorial(4))
from myfunc import factorial
print(factorial(4))
'''
#import for gui development
from tkinter import *
from tkinter import ttk

class Calculator:
    calc_value = 0.0
    div_trigger = False
    mult_trigger = False
    add_trigger = False
    sub_trigger = False

    def button_press(self, value):
        entry_val = self.number_entry.get()
        entry_val += value
        self.number_entry.delete(0, "end")
        self.number_entry.insert(0, entry_val)

    def isfloat(self, str_val):
        try:
            float(str_val)
            return True
        except ValueError:
            return False

    def math_button_press(self, value):
        if self.isfloat(str(self.number_entry.get())):
            self.add_trigger = False
            self.sub_trigger = False
            self.mult_trigger = False
            self.div_trigger = False
            self.calc_value = float(self.entry_value.get())
            if value == "/":
                print("/ Pressed")
                self.div_trigger = True
            elif value == "*":
                print("* Pressed")
                self.mult_trigger = True
            elif value == "+":
                print("+ Pressed")
                self.add_trigger = True
            elif value == "-":
                print("- Pressed")
                self.sub_trigger = True
            else:
                print("Operation does not exist")

            self.number_entry.delete(0, "end")

    def equal_button_press(self):
        if self.add_trigger or self.sub_trigger or self.mult_trigger or self.div_trigger:
            if self.add_trigger:
                solution = self.calc_value + float(self.entry_value.get())
            elif self.sub_trigger:
                solution = self.calc_value - float(self.entry_value.get())
            elif self.mult_trigger:
                solution = self.calc_value * float(self.entry_value.get())
            elif self.div_trigger:
                solution = self.calc_value / float(self.entry_value.get())
            else:
                solution = 0.0
            print(self.calc_value, " ", float(self.entry_value.get()), " ", solution)
            self.number_entry.delete(0, "end")
            self.number_entry.insert(0, solution)

    def __init__(self, root):
        self.entry_value = StringVar(root, value="")
        root.title("Calculator")
        root.geometry("600x250")
        root.resizable(width=False, height=False)
        style = ttk.Style()
        style.configure("TButton", font="Serif 15", padding=10)
        style.configure("TEntry", font="Serif 18", padding=10)
        self.number_entry = ttk.Entry(root, textvariable=self.entry_value, width=50)
        self.number_entry.grid(row=0, columnspan=4)
        # ----- 1st Row -----
        self.button7 = ttk.Button(root, text="7", command=lambda: self.button_press('7')).grid(row=1, column=0)
        self.button8 = ttk.Button(root, text="8", command=lambda: self.button_press('8')).grid(row=1, column=1)
        self.button9 = ttk.Button(root, text="9", command=lambda: self.button_press('9')).grid(row=1, column=2)
        self.button_div = ttk.Button(root, text="/", command=lambda: self.math_button_press('/')).grid(row=1, column=3)
        # ----- 2nd Row -----
        self.button4 = ttk.Button(root, text="4", command=lambda: self.button_press('4')).grid(row=2, column=0)
        self.button5 = ttk.Button(root, text="5", command=lambda: self.button_press('5')).grid(row=2, column=1)
        self.button6 = ttk.Button(root, text="6", command=lambda: self.button_press('6')).grid(row=2, column=2)
        self.button_mult = ttk.Button(root, text="*", command=lambda: self.math_button_press('*')).grid(row=2, column=3)
        # ----- 3rd Row -----
        self.button1 = ttk.Button(root, text="1", command=lambda: self.button_press('1')).grid(row=3, column=0)
        self.button2 = ttk.Button(root, text="2", command=lambda: self.button_press('2')).grid(row=3, column=1)
        self.button3 = ttk.Button(root, text="3", command=lambda: self.button_press('3')).grid(row=3, column=2)
        self.button_add = ttk.Button(root, text="+", command=lambda: self.math_button_press('+')).grid(row=3, column=3)
        # ----- 4th Row -----
        self.button_clear = ttk.Button(root, text="AC", command=lambda: self.button_press('AC')).grid(row=4, column=0)
        self.button0 = ttk.Button(root, text="0", command=lambda: self.button_press('0')).grid(row=4, column=1)
        self.button_equal = ttk.Button(root, text="=", command=lambda: self.equal_button_press()).grid(row=4, column=2)
        self.button_sub = ttk.Button(root, text="-", command=lambda: self.math_button_press('-')).grid(row=4, column=3)

# Get the root window object
root = Tk()
# Create the calculator
calc = Calculator(root)
# Run the app until exited
root.mainloop()
































































