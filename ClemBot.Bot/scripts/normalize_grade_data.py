# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "numpy",
#     "pandas",
# ]
# ///

"""
Script to normalize csv file exported via tabula from clemsons PDF grade listings
Not a complete reference of possible invalid data

Commands run:
java -jar target/tabula-1.0.6-SNAPSHOT-jar-with-dependencies.jar "202201.pdf" --pages all -o 2022Spring.csv -g
uv run normalize_grade_data.py 2022Spring.csv
"""

import re
import sys

import numpy as np
import pandas as pd

file = sys.argv[1]

if ".csv" not in file:
    exit("File must be a csv")

if "2020" in file or "2021" in file or "2022" in file:
    # Fall 2020 and spring 2021 added some course designations to account for online learning so we need to make extra columns
    columns = [
        "Course",
        "Number",
        "Section",
        "Title",
        "A",
        "B",
        "C",
        "D",
        "F",
        "P",
        "F(P)",
        "W",
        "I",
        "SCP",
        "SCN",
        "SCD",
        "Instructor",
        "Honors",
    ]
else:
    columns = [
        "Course",
        "Number",
        "Section",
        "Title",
        "A",
        "B",
        "C",
        "D",
        "F",
        "P",
        "F(P)",
        "W",
        "Instructor",
        "Honors",
    ]

with open(file, 'r') as f:
    first_line = f.readline().strip().split(',') 

    # already-processed CSVs have a header row with CourseId
    if "CourseId" in first_line:
        data = pd.read_csv(file, header=0)
    else:
        data = pd.read_csv(file, names=columns)

try:
    data = data.drop(columns=["I", "SCP", "SCN", "SCD"])
except KeyError:
    pass

for grade in ["A", "B", "C", "D", "F", "P", "F(P)", "W"]:
    data[grade] = (
        data[grade]
        .astype(str)
        # #### means 100% pass in P/F columns
        .str.replace("####", "100%", regex=False)
        .str.replace("%", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype(float)
    )
    data.loc[data[grade] > 1, grade] = data.loc[data[grade] > 1, grade] / 100.0


# some of the Courses have floats instead of ints as a column type, handle that here
data.Number = data.Number.fillna(0).astype(int)

data.Instructor = data.Instructor.str.lower()

# Create course id field to query on
data["CourseId"] = data.Course + "-" + data.Number.astype(str)

# create year field from the file name
# data.Year = file[:4]
r = re.findall(r"([0-9][0-9][0-9][0-9])", file)
data["Year"] = r[0]

# Change honors H --> True or NaN --> False
data.Honors = data.Honors.apply(lambda x: x is True or x == "H")

if "2018" in file or "2020" in file:
    if "NameProcessed" not in data.columns:
        data.Instructor = (
            data.Instructor.str.split(" ").str[1::].str.join(" ")
            + " "
            + data.Instructor.str.split(" ").str[::3].str.join(" ")
        )
        data["NameProcessed"] = True
else:
    data.Instructor = data.Instructor.str.split(", ").str[::-1].str.join(" ")

data.Instructor = data.Instructor.str.replace(r"\b\w\b", "", True).str.replace(r"\s+", " ", True)

data.Course.replace("", np.nan, inplace=True)

# some of the names have random ' . ' in them, remove that
data.Instructor = data.Instructor.replace(" . ", " ", regex=True)


data.dropna(subset=["Course"], inplace=True)


print(data.info())
print(data)

title = file
# Try to derive the semester from the title
if "Fall" in file:
    title = f"{r[0]}_Fall.csv"
elif "Spring" in file:
    title = f"{r[0]}_Spring.csv"
else:
    print("Could not find semester in file title! Rewriting original file...")

data.to_csv(f"{title}", index=False)
