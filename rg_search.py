# -*- coding: utf-8 -*-
"""
list out all the sub-directories and files

2021.abr  1.0  mlabru  initial version (Linux/Python)
"""
# < imports >--------------------------------------------------------------------------------------

# python library
import logging
import os
import pathlib
import subprocess
import sys

# < defines >--------------------------------------------------------------------------------------

# directory to start from
DS_DIR_BASE = "./GNSS"

# directory to start from
DS_DIR_CRUX = "./Crux"

# GFX RINEX program 
DS_PATH_GFZRNX = "./gfzrnx/gfzrnx_lx64"

# -------------------------------------------------------------------------------------------------
def find_crux_file(fs_stat):
    """
    find crux file for station

    :param fs_stat (str): station id
    """
    # crux file name
    ls_crux_fn = "{}_crux.txt".format(fs_stat.lower())

    # try path 1
    l_path = pathlib.Path(DS_DIR_BASE) / "RINEX" / fs_stat.upper() / ls_crux_fn

    # crux file exists ?
    if not l_path.exists():
        # try path 2
        l_path = pathlib.Path(DS_DIR_CRUX) / ls_crux_fn

        # crux file exists ?
        if not l_path.exists():
            # logger
            logging.critical(">> crux file for station %s not found. Aborting...", fs_stat)

            # abend  
            sys.exit(-1)
 
    # return path      
    return l_path

# -------------------------------------------------------------------------------------------------
def trata_data(f_date, fs_stat, fs_crux_fn):
    """
    splice files of this date

    :param f_date (PurePath): observation date
    :param fs_stat (str): station id
    :param fs_crux_fn (str): crux filename
    """
    # station name
    print("date:", str(f_date))

    # list navigation data files
    llst_nav = [str(f) for f in f_date.glob("*N.gz")]

    # not an empty list ?
    if llst_nav:
        # remove navigation data
        subprocess.call(["rm", "-r"] + llst_nav)
    
    # list observation data files
    llst_obs = [str(f) for f in f_date.glob("*O.gz")]

    # not an empty list 
    if llst_obs:
        # decompress observation data
        subprocess.call(["gzip", "-d"] + llst_obs)
    
    # split year
    ls_year = f_date.name[0:2]

    # split D-O-Y
    ls_doy = f_date.name[2:]

    # input file
    ls_finp = "{}/{}{}{{A..X}}.{}O".format(str(f_date), fs_stat.upper(), ls_doy, ls_year)

    # output file
    ls_fout = "{}/{}{}0.{}o".format(str(f_date.parent), fs_stat.lower(), ls_doy, ls_year)

    # build command line
    ls_cmd = "{} -finp {} -fout {} -crux {} -kv".format(DS_PATH_GFZRNX, ls_finp, ls_fout, fs_crux_fn)
    print(ls_cmd)

    # splice files
    subprocess.call(["/bin/bash", "-c", ls_cmd])

    # compress data
    subprocess.call(["gzip", ls_fout])

    # remove directory
    subprocess.call(["rm", "-rf", str(f_date)])

# -------------------------------------------------------------------------------------------------
def trata_ismr(f_path):
    """
    compress ISMR files

    :param f_path (PurePath): path where ISMR files are 
    """
    # ISMR path exists ?
    if not f_path.exists():
        # logger
        logging.critical(">> ISMR path %s not found. Aborting...", str(f_path))

        # abend  
        sys.exit(-1)

    # for all dirs in root path...
    for l_path in pathlib.Path(f_path).iterdir():
        # is a directory ?
        if l_path.is_dir():
            # for all ismr files in dir...
            for ls_ismr in list(l_path.glob("*.ismr")):
                try:
                    print("gzip -f", ls_ismr)
                    # compress ismr file
                    subprocess.check_call(["gzip", "-f", ls_ismr])

                # em caso de erro...
                except subprocess.CalledProcessError as lerr:
                    # logger
                    logging.error("> compress error for %s: %s", ls_ismr, lerr)
            
# -------------------------------------------------------------------------------------------------
def trata_rinex(f_path, fs_stat):
    """
    splice RINEX data

    :param f_path (PurePath): path where ISMR files are 
    :param fs_stat (str): station id
    """
    # RINEX path exists ?
    if not f_path.exists():
        # logger
        logging.critical(">> RINEX path %s not found. Aborting...", str(f_path))

        # abend  
        sys.exit(-1)

    # find crux file for station
    ls_crux_file = find_crux_file(fs_stat)

    # for all dirs in root path...
    for l_path in pathlib.Path(f_path).iterdir():
        # is a directory ?
        if l_path.is_dir():
            # splice files of this date
            trata_data(l_path, fs_stat, ls_crux_file)

# -------------------------------------------------------------------------------------------------
def main(f_path):
    """
    drive program

    :param f_path (PurePath): root path
    """
    # for all dirs in root path...
    for l_path in pathlib.Path(f_path).iterdir():
        # is a directory ?
        if l_path.is_dir():
            print(str(l_path.name), " - ISMR")
            # deal with ISMR files
            trata_ismr(l_path / "ISMR")

            print(str(l_path.name), " - RINEX")
            # deal with RINEX files
            trata_rinex(l_path / "RINEX", l_path.name)

# -------------------------------------------------------------------------------------------------
# this is the bootstrap process

if "__main__" == __name__:

    # logger
    logging.basicConfig(level=logging.WARNING)

    # disable logging
    # logging.disable(sys.maxsize)

    # run application
    sys.exit(main(DS_DIR_BASE))

# < the end >--------------------------------------------------------------------------------------
