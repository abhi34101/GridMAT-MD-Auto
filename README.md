#GridMAT-MD-Auto

Written by: Abhishek Acharya
            Research Associate
            Structural and Computational Biology Lab
            CSIR-Central Food Technological Research Institute
            Mysuru
            
For any queries and reporting problems with the script, send a mail to:
abhi117acharya@gmail.com

#######################################################################################

This program is an automated version of GridMAT-MD-parallel, a modified version of
GridMAT-MD. This was originally developed by Bevan Lab, Virginia Tech.

Please read and cite the following reference:

W. J. Allen, J. A. Lemkul, and D. R. Bevan. (2009). GridMAT-MD:A Grid-based Membrane 
Analysis Tool for Use With Molecular Dynamics. J. Comput. Chem., 30 (12), 1952-1958

For bug fixes and release notes on GridMAT-MD, please see the following site:
http://www.bevanlab.biochem.vt.edu/GridMAT-MD/bugs.html	

The parallelized version has been written by: Venkatramanan Krishnamani
(Univesity of Iowa).

#######################################################################################

#About GridMAT-MD-Auto

This is a program written in python2 and works as a wrapper for the original program
written in perl.

This program allows the analysis of GROMACS membrane simulation trajectories, similar 
to the original version. Additionally, it also writes the time evolution of APL and
and bilayer thickness over the course of the simulation in standard xmgrace format.

The program takes 4 files as input. Two of them are provided with the package; these 
are input files that specify parameters for running the GridMAT-MD APL and thickness
calculations. First is an input file for APL calculations while the second is for 
calculation of bilayer thickness. Using two seperate input parameter files allows the 
user to specify parameters separately for APL and Bilayer thickness calculation; the
script automatically calculates both the parameters and saves appropriate output files.

Since the analysis requires extracting all the frames as gro file and produces outputs
for each frame analysed, the outputs take much disk space. Therefore, the default beha-
-vior of the program is to delete the frame-by-frame output files. The user can choose
to keep these files by providing the --keep flag.

Additionally, user can choose the start and ending time for running the analysis on a
subsection of the full trajectory file; a -skip flag is also provided to skip frames
during analysis.

#######################################################################################

#Usage


GridMAT-MD-Auto.py [-h] [-b BTIME] [-e ETIME] [-s SUFFIX] [--skip SKIP]
                          [--keep]
                          fa_param fb_param f_traj f_coord

GridMAT-MD based automated analysis tool

positional arguments:
  fa_param              GridMAT parameter file for calculating area/lipid
  fb_param              GridMAT parameter file for calculating thickness
  f_traj                Trajectory file Formats:xtc trr
  f_coord               (Structure+mass)db file Format: gro

optional arguments:
  -h, --help            show this help message and exit
  -b BTIME, --btime BTIME
                        Starting frame (in ps) Default = None
  -e ETIME, --etime ETIME
                        Ending frame (in ps) Default = None
  -s SUFFIX, --suffix SUFFIX
                        Binary suffix for the gromacs installation
  --skip SKIP           Only extract every nr-th frame
  --keep                Keep output and log files produced by GridMAT.Will
                        take addtional space on drive.

######################################################################################

