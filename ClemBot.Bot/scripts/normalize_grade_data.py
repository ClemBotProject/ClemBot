import pandas as pd
import numpy as np
import sys, re

"""
Script to normalize csv file exported via tabula from clemsons PDF grade listings
Not a complete reference of possible invalid data
"""

file = sys.argv[1]

if '.csv' not in file:
    exit('File must be a csv')

if '2020' in file or '2021' in file:
    # Fall 2020 and spring 2021 added some course designations to account for online learning so we need to make extra columns
    columns = ['Course', 'Number', 'Section', 'Title', 'A', 'B', 'C', 'D', 'F', 'P', 'F(P)', 'W', 'I', 'SCP', 'SCN', 'SCD', 'Instructor', 'Honors']
    data = pd.read_csv(file, names=columns)
    data = data.drop(['I', 'SCP', 'SCN', 'SCD'], 1)
else:
    columns = ['Course', 'Number', 'Section', 'Title', 'A', 'B', 'C', 'D', 'F', 'P', 'F(P)', 'W', 'Instructor', 'Honors']
    data = pd.read_csv(file, names=columns)

for grade in ['A', 'B', 'C', 'D', 'F', 'P', 'F(P)', 'W']:
    try:
        data[grade] = data[grade].str.rstrip('%').astype(float) / 100.0
    except:
        pass


#some of the Courses have floats instead of ints as a column type, handle that here
data.Number = data.Number.fillna(0).astype(int)

data.Instructor = data.Instructor.str.lower()

# Create course id field to query on
data['CourseId'] = data.Course + '-' + data.Number.astype(str)

# create year field from the file name
#data.Year = file[:4]
r = re.findall(r"([0-9][0-9][0-9][0-9])", file)
data['Year'] = r[0]

# Change honors H --> True or NaN --> False
data.Honors = data.Honors.apply(lambda x: True if x == 'H' else False)

if '2018' in file or '2020' in file:
    data.Instructor = data.Instructor.str.split(' ').str[1::].str.join(' ') + ' ' + data.Instructor.str.split(' ').str[::3].str.join(' ')
else:
    data.Instructor = data.Instructor.str.split(', ').str[::-1].str.join(' ')

data.Instructor = data.Instructor.str.replace(r'\b\w\b', '', True).str.replace(r'\s+', ' ', True)

data.Course.replace('', np.nan, inplace=True)

# some of the names have random ' . ' in them, remove that
data.Instructor = data.Instructor.replace(' . ', ' ', regex=True)


data.dropna(subset=['Course'], inplace=True)


print(data.info())
print(data)

title = file
# Try to derive the semester from the title
if 'Fall' in file:
    title = f'{r[0]}_Fall.csv'
elif 'Spring' in file:
    title = f'{r[0]}_Spring.csv'
else:
    print('Could not find semester in file title! Rewriting original file...')

data.to_csv(f'{title}', index=False)
