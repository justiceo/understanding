
# Returns true if number is of the form \d*[st|nd|rd|th], crash or false otherwise.
# See explanation at https://codegolf.stackexchange.com/a/162322
isOrdinalNum = lambda v:'hsnrhhhhhh'[(v[-4:-3]!='1')*int(v[-3])]in v