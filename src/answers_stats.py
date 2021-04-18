import json
import pandas as pd
import benepar
from progress.bar import Bar
from nltk.tree import *

with open("data/squad-train-trimmed-v2.0.json", "r") as read_file:
    data = json.load(read_file)


df = pd.DataFrame(data=data)
df['word_length'] = df['text'].apply(lambda x: len(x.split(' ')))

print("\ncolumns: ", df.columns, "\n")

# print mode for all the labels
labels_df = df.groupby(['label']).size().reset_index(name='counts')
# df.columns = ['label', 'count']
labels_df = labels_df.sort_values('counts', ascending=False)
print(labels_df.head(10))

print("\nleft sibling:\n")
llabels_df = df.groupby(['left_sibling_label']).size().reset_index(name='counts')
llabels_df = llabels_df.sort_values('counts', ascending=False)
print(llabels_df.head(10))

print("\nleft left sibling:\n")
llabels_df = df.groupby(['left_left_sibling_label']).size().reset_index(name='counts')
llabels_df = llabels_df.sort_values('counts', ascending=False)
print(llabels_df.head(10))

print("\nright sibling:\n")
rlabels_df = df.groupby(['right_sibling_label']).size().reset_index(name='counts')
rlabels_df = rlabels_df.sort_values('counts', ascending=False)
print(rlabels_df.head(10))

print("\nright right sibling:\n")
rlabels_df = df.groupby(['right_right_sibling_label']).size().reset_index(name='counts')
rlabels_df = rlabels_df.sort_values('counts', ascending=False)
print(rlabels_df.head(10))

print("\nparent label:\n")
plabels_df = df.groupby(['parent_label']).size().reset_index(name='counts')
plabels_df = plabels_df.sort_values('counts', ascending=False)
print(plabels_df.head(10))

print("\nmodes:\n")
mode_df = df.groupby([ 'left_sibling_label', 'label', 'right_sibling_label']).size().reset_index(name='counts')
mode_df = mode_df.sort_values('counts', ascending=False)
print(mode_df.head(10))