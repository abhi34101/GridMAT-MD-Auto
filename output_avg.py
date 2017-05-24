#!/usr/bin/python
########################################################################
#    This is a helper script for calculating average area/lipid and    #
#    bilayer thickness by taking the respective .xvg file as input.    #
#                                                                      #
#  Usage:    python out_avg.py <input_file>                            #
#                                                                      #
#  Written by: Abhishek Acharya                                        #
#              CSIR-Central Food Technological Research Institute      #
#       Email: abhi117acharya@gmail.com                                #
#                                                                      #
########################################################################

import argparse, sys

########################################################################
# Parsing input arguments
parser = argparse.ArgumentParser(description='Script for calculating average'
        ' membrane properties')
parser.add_argument('input_file', action='store',
        help='Input .xvg file for calculating average values')
parser.add_argument('--iacm', action='store_const', const='',
        help='flag to calculate isothermal area compressibility modulus \
        (requires additional input values for the flags --temp and --nl )' )
parser.add_argument('--temp', action='store', type=int, default=None,
        help='Simulation Temperature (in Kelvin)')
parser.add_argument('--nl', action='store', type=int, default=None,
        help='Number of lipids')
        


inparg = parser.parse_args()

#define the calculation functions

def cal(prop_list):
    mean = sum(prop_list)/len(prop_list)
    sumofsq = 0
    for i in prop_list:
        sumofsq += (mean-i)**2
    return mean, sumofsq/len(prop_list)

def iacmcalc(mean_apl, variance, temp, nl):
    kb=1.38*(10**-23)
    apl=mean_apl*(10**-20)
    var = variance*(10**-40)
    return (2*kb*temp*apl)/(nl*var)


print 'Reading input file....'

inp = open(inparg.input_file, 'r').readlines()
#create a hash table to save xy-table data and initialize variables
cal_dict = {}
title = ''          
subtitle = ''
val_list = []

    
#loop to extract plot xy values and the plot title and subbtitle
for l in inp:
    if '@' not in l and '#' not in l:
        if '&' not in l:
            i = l.split()
            cal_dict[int(i[0])] = float(i[1])
    else:
        if 'title' in l and title=='':
            title = l.split('"')[1]
        elif 'subtitle' in l and subtitle=='':
            subtitle = l.split('"')[1]


time_list = cal_dict.keys() #obtain the list of keys and sort
time_list.sort()
step=time_list[2] - time_list[1]  #obtain the step size

#print information
print """ Analysis done:

Plot title = %s \n %s

Trajectory information:
Starting frame = %d ps
Ending frame = %d ps
Step size = %d ps


Please input the range (in ps) separated by a space
for calculating the average properties. 
""" %(title, subtitle, time_list[0], time_list[-1], step)

#user input for starting and ending frame for calculations
t_range = raw_input('Enter: <beginning_frame> <ending_frame> \n')
first_last = t_range.split()
btime, etime = int(first_last[0]), int(first_last[1])
 
#running checks
if btime in time_list and etime in time_list:
    if etime > btime:
        sel_list = time_list[time_list.index(btime):     #selected frame range
                time_list.index(etime)+1]
    else:
        raise Exception('Ending frame number >= Beginning frame number')
        sys.exit(2)
else:
    raise Exception('Error in input. Frame(s) with specified timestamp'
            ' NOT FOUND!!!')
    sys.exit(2)

#collect the values corresponding to selected keys in sel_list
for t in sel_list:
    val_list.append(cal_dict[t])
#calculate mean and variance values
mean, variance = cal(val_list)


if 'area' in str.lower(title):
    prop='Average area per lipid'
    units="Angstrom square"
else:
    prop='Average Bilayer Thickness'
    units='nm'

print 'The %s is %.4f %s. The variance is %.4f.' %(prop, mean, units, variance)

if inparg.iacm != None:
    if isinstance(inparg.temp, int) and isinstance(inparg.nl, int):
        cm = iacmcalc(mean, variance, inparg.temp, inparg.nl)
        print 'The Isothermal Area Compressibility Modulus is %f N/m' %cm
    else:
        raise ValueError('Please provide correct input values for temperature'
                ' (--temp) and number of lipids (--nl).')
        sys.exit(2)

print "Done"



            
        

