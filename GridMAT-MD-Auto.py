#!/usr/bin/python
#########################################################################
#       	        GridMAT-MD-Auto version 1.0        		            #
#		    				                                            #
#		For automated python program for running GridMAT-MD on          #
#                trajectory files and obtain plots.                     #
#                                                                       #
#   GridMAT-MD-Auto.py written by:                                      #
#   Abhishek Acharya                                                    #
#   CSIR-Central Food Technological Research Institute                  #
#   Email: abhi117acharya@gmail.com                                     #
#   Release date: 17th May 2017                                         #
#                                                                       #
#########################################################################
#                   GridMAT-MD-parallel version 2.0                     #
#          For bug fixes and release notes on GridMAT-MD                #
#                please see the following site:		                    #
#	    http://www.bevanlab.biochem.vt.edu/GridMAT-MD/bugs.html		    #
#									                                    #
#                                                                       #
#   Parallelized Version Developed by:                                  #
#	Venkatramanan Krishnamani (Univesity of Iowa)                       #
#	venky.krishna@me.com                                                #
#	Release Date: 12th Oct 2014                                         #
#                                                                       #
#########################################################################

#importing necessary modules
import os, time, sys, subprocess, argparse, psutil

# parsing commandline arguments
#########################################################################

parser = argparse.ArgumentParser(description="GridMAT-MD based automated" 
                                             "analysis tool")

parser.add_argument('fa_param', action='store', 
        help="GridMAT parameter file for calculating area-per-lipid")#positional
parser.add_argument('fb_param', action='store', 
	    help='GridMAT parameter file for calculating thickness')     #positional
parser.add_argument('f_traj', action='store',
	    help='trajectory file  Formats:xtc trr')                     #positional
parser.add_argument('f_coord', action='store', 
	    help='(Structure+mass)db file  Format: gro')                 #positional                    
parser.add_argument('-b', '--btime', action='store', type=int,
	    help='starting frame (in ps) Default = None', default=None)  #optional
parser.add_argument('-e', '--etime', action='store', type=int,
	    help='ending frame (in ps) Default = None', default=None)    #optional
parser.add_argument('-s', '--suffix', action='store', type=str,
	    help='ending frame (in ps) Default = None', default='')      #optional
	                    
carg=parser.parse_args()

# function definitons
#########################################################################

def test_exec(cmd):
	#testing presence of a binary (helps in checking for suitable executable).
	return subprocess.call("type " + cmd, 
	        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
	
def detect_gmx(bin_suffix):
#function to check for trjconv executable or modify them with a suitable suffix.
	gmx_list = ['trjconv', 'gmx']
	if bin_suffix != '':
		print "Using executable suffix: "+bin_suffix
		gmx_list.append('trjconv'+bin_suffix)
		gmx_list.append('gmx'+bin_suffix)
	
	for g in gmx_list:
		if test_exec(g)==True:
			gmexec=g
			break
	else:
		raise Exception("""No gromacs executable detected! 
            Please check your gromacs installation.""")
	return gmexec
	
def process_exec(cmd):
#function for processing gmx command for running trjconv.
	print "Checking for presence of GROMACS executable....."
	if 'gmx' in cmd:
		return cmd+' trjconv'
	elif 'trjconv' in cmd:
		return cmd
							   
def traj_dump(args):
#dumps coordinates into output file
	gro_cmd = process_exec(detect_gmx(args.suffix))
	print "Running trjconv...."
	if args.btime==None and args.etime==None:
		cmd = "%s -f %s -s %s -o tmp.gro &>/dev/null" %(gro_cmd, 
		        args.f_traj, args.f_coord)
	elif isinstance(args.btime, int) and isinstance(args.etime, int):
		cmd = '%s -f %s -s %s -o tmp.gro -b %d -e %d &>/dev/null' %(gro_cmd, 
		        args.f_traj, args.f_coord, args.btime, args.etime)
	elif args.etime==None:
		cmd = '%s -f %s -s %s -o tmp.gro -b %d &>/dev/null' %(gro_cmd, 
		        args.f_traj, args.f_coord, args.btime)
	else:
		cmd = '%s -f %s -s %s -o tmp.gro -e %d &>/dev/null' %(gro_cmd, 
		        args.f_traj, args.f_coord, args.etime)
	os.system("printf '0\n' | "+cmd)
	return 0

def gridmat(param_file, num_frames):
#run GridMAT_parallel
	print "\nRunning GridMAT-MD-parallel on trajectory frames."
	print "This may take a while. Go have some coffee.\n"
	print "MAY THE CORES BE WITH YOU!"
	gridmat_cmd = 'perl GridMAT-MD-parallel.pl '\
	        +param_file+' tmp.gro '+str(num_frames)
	t0=time.time()
	os.system(gridmat_cmd)
	print "GridMAT run has finished.\n"
	print "It took %.2f minutes for the run." %((time.time()-t0)/60)
	return None

		

def parse_time():
#extracting the time-stamp for all dumped frames
	time_lst = []
	coord_dat = open('tmp.gro', 'r').readlines()
	for l in coord_dat:
		if 'Generated' in l:
			time_lst.append(float(l.split(' ')[-1]))
	return time_lst
	
def parse_log():
#extracting the list of all apl log files
	os.system('ls output_apl*.log | sort -V > loglist_apl.dat')
	log_lst = open('loglist_apl.dat', 'r').read().split('\n')
	null = log_lst.pop()
	return log_lst
	
def parse_dat():
#extracting the list of all thickness dat files
	os.system('ls output_dpp*average* | sort -V > loglist_dpp.dat')
	log_lst = open('loglist_dpp.dat', 'r').read().split('\n')
	null = log_lst.pop()
	return log_lst

def parse_apl(log_file):
#extracting the apl value GridMAT generated log file
	log_data = open(log_file, 'r').readlines()
	for line in log_data:
		if 'average' in line:
			apl = float(line.split()[-3])
	return apl

def calc_dpp(log_file):
#extracting data from GridMAT generated output and calculating average thickness
	log_data = open(log_file, 'r').read().split('\n')
	log_data.pop()
	tot=0
	for d in log_data:
		tot += float(d)
	return round(tot/len(log_data), 5)
	
def apl_plot(time_list, log_list):
#obtain a dictionary of {time:avg. apl} configuration
	apl_dict = {}
	if len(time_list) == len(log_list):
	    for x in range(0,len(time_list)):
			apl_dict[time_list[x]] = parse_apl(log_list[x])
	else:
		raise ValueError("Something not quite right. The timestamps count \
		does not correspond to the apl count.")
		sys.exit(2)
	return apl_dict

def dpp_plot(time_list, log_list):
#obtain a dictionary of  {time:avg. thickness} configuration
	dpp_dict = {}
	if len(time_list) == len(log_list):
	    for x in range(0,len(time_list)):
			dpp_dict[time_list[x]] = calc_dpp(log_list[x])
	else:
		raise ValueError("Something not quite right. The timestamps count \
		does not correspond to the dpp count.")
		sys.exit(2)
	return dpp_dict

def make_xvg(xy_dict, prop):
#function to print a xy plot in Xmgrace format.
	cmd1= 'touch %s-vs-time.xvg' %(prop)
	os.system(cmd1)
	if prop in ["apl", "APL"]:
		header = """@    title "AVERAGE AREA-PER-LIPID"
		    @    xaxis  label "Time (ps)"
		    @    xaxis  tick major 10000
		    @    xaxis  tick minor 1000
		    @    yaxis  label "Avg. Area per Lipid (sq. Angstrom)"
		    @    yaxis  tick major 10
		    @    yaxis  tick minor 1
		    @TYPE xy
		    @ subtitle "Area/lipid vs Time"
		    
		    """
	elif prop in ['dpp', 'DPP']:
		header = """@    title "AVERAGE BILAYER THICKNESS"
		    @    xaxis  label "Time (ps)"
		    @    xaxis  tick major 10000
		    @    xaxis  tick minor 1000
		    @    yaxis  label "Percentage solvent accessibility"
		    @    yaxis  tick major 1
		    @    yaxis  tick minor 0.1
		    @TYPE xy
		    @ subtitle "Dp-p vs Time"
		    
		    """
	else:
		raise ValueError("Error. Check your input")
		sys.exit(2)
	xvg_file = open(cmd1[6:], 'a')
	xvg_file.write(header)
	key_list = xy_dict.keys()
	key_list.sort()
	for i in key_list:
		cont="\n"+str(i)+" "+ str(xy_dict[i])
		xvg_file.write(cont)
	xvg_file.close()	
	return None
	
def get_trjpid():
#function to obtain trjconv process id.
	cmd='ps -a > ps.log'
	os.system(cmd)
	pslst = open('ps.log', 'r').readlines()
	for l in pslst:
		if "trjconv" in l or "gmx" in l:
			return int(l.split()[0])

	
# main function that calls various subroutines	
#########################################################################			

def main(args):
	print "Starting 'gmx trjconv' for dumping coordinate data into tmp.gro."
	traj_dump(args)
	pid_trjconv = get_trjpid()
	timer = 0
	t0 = time.time()
	while psutil.pid_exists(pid_trjconv):
		continue
	else:
		print "Finished run for trjconv." 
		print "Running time:", round((time.time()-t0)/60), "minutes"
		print "*"*72
		t_list = parse_time()
		print "Commencing APL calculations."
		gridmat(args.fa_param, len(t_list))
		print "APL calculations finished."
		print "*"*72
		print "Commencing Dp-p calculations."
		gridmat(args.fb_param, len(t_list))
		print "Dp-p calculations finished"
		print "Creating xvg output files."
		make_xvg(apl_plot(t_list, parse_log()), "apl")
		make_xvg(dpp_plot(t_list, parse_dat()), "dpp")
		print "Cleaning up temporary files."
		os.system('rm *.log *.dat')
		print "Done."
	
#######################Program End ######################################
	print "\nThank you for using this program.\n"
	print "Please read and cite the following reference:"
	print "W. J. Allen, J. A. Lemkul, and D. R. Bevan. (2009). GridMAT-MD:\
A Grid-based Membrane Analysis Tool for Use With Molecular Dynamics.\
J. Comput. Chem., 30 (12), 1952-1958\n"
#########################################################################   

if __name__=='__main__':
	main(carg)


	
	

	

