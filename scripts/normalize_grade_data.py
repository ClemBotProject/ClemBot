import pandas as pd
import numpy as np
import sys

"""
Script to normalize csv file exported via tabula from clemsons PDF grade listings
Not a complete reference of possible invalid data

"""
file = sys.argv[1]

if '.csv' not in file:
    exit('File must be a csv')

if '2020' in file:
    #2020 added some course designatins so we need to make extra columns
    columns = ['Course', 'Number', 'Section', 'Title', 'A', 'B', 'C', 'D', 'F', 'P', 'F(P)', 'W', 'I', 'SCP', 'SCN', 'SCD', 'Instructor', 'H']
    data = pd.read_csv(file, names=columns)
    data = data.drop(['I', 'SCP', 'SCN', 'SCD'], 1)
else:
    columns = ['Course', 'Number', 'Section', 'Title', 'A', 'B', 'C', 'D', 'F', 'P', 'F(P)', 'W', 'Instructor', 'H']

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
data.CourseId = data.Course + '-' + data.Number.astype(str)

# create year field from the file name
data.Year = file[:4]

del data['H']

if '2018' in file or '2020' in file:
    data.Instructor =data.Instructor.str.split(' ').str[1::].str.join(' ') + ' ' + data.Instructor.str.split(' ').str[::3].str.join(' ')
else:
    data.Instructor = data.Instructor.str.split(', ').str[::-1].str.join(' ')

data.Instructor = data.Instructor.str.replace(r'\b\w\b','', True).str.replace(r'\s+', ' ', True)

data.Course.replace('', np.nan, inplace=True)

# some of the names have random ' . ' in them, remove that
data.Instructor = data.Instructor.replace(' . ', ' ',regex=True)

data.dropna(subset=['Course'], inplace=True)

print(data.info())
print(data)

data.to_csv(f'{file}', index=False)
