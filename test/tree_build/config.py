#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####Import Module#####
import logging
import sys
import os
import math
import time
import argparse
import glob

class Config():
    def __init__(self):
        #########major soft##########
        self.PopulationEvolution='/population_analysis/PopulationEvolution.py'

        self.beagle='/usr/software/beagle/beagle.jar'
        self.svg='/usr/software/svg/svg2xxx'
        self.plink='/usr/software/plink/plink'
        self.gcta='/usr/software/gcta/gcta64'
        self.muscle='/usr/software/muscle/muscle'
        self.admixture='/usr/software/admixture/admixture'
        self.vcftools='/usr/bin/vcftools'
        ########draw tree##############
        self.FastTree='/usr/software/FastTree/FastTreeMP'
        ######################
        
        self.R='/population_analysis/PCA.ggplot.R'
        self.Rscript='Rscript'
        self.python='python'
        
        ######LD_analysis#######
        self.plink2genotype='/usr/software/PopLDdecay/bin/mis/plink2genotype.pl'
        self.PopLDdecay='/usr/software/PopLDdecay/bin/PopLDdecay'
        self.Plot_OnePop='/usr/software/PopLDdecay/bin/Plot_OnePop.pl'
        self.Plot_MultiPop='/usr/software/PopLDdecay/bin/Plot_MultiPop.pl'
        self.haploview='/usr/software/Haploview/Haploview.jar'
        ###########################

        self.color=["blue",
                                "red",
                                "green",
                                "#FF950c",
                                "#C71585",
                                "#DDA0DD",
                                "#BA55D3",
                                "#483D8B",
                                "#34ECA4",
                                "#0000CD",
                                "#9932CC",
                                "#DA70D6",
                                "#D2691E",
                                "#F0E68C",
                                "#F4A460",
                                "#CC0000",
                                "#CC00CC",
                                "#3333CC",
                                "#003300",
                                "#0099FF",
                                "#FF6633",
                                "#FF3399",
                                "#00CCFF"]

def check_dir(dirs):
    if not os.path.exists(dirs):os.mkdir(dirs) 

def check_run(files):
    if os.path.exists(files):
        show_info('----- !Attention: File %s exist, so this step is skipped ------'%files)
        return 0
    else:
        return 1

def check_software(software_path):
    if os.path.exists(software_path):
        logging.debug("Choose software:" + software_path + "!")
    else:
        output = os.popen('which ' + software_path)
        software_temp = output.read().strip()
        if os.path.exists(software_temp):
            software_path = software_temp
            logging.debug("Choose software:" + software_path + "!")
        else:
            logging.error("Can't locate the " + software_path + "!")
            exit(1)
    return software_path


def show_info(text):
    now_time = time.time()
    logging.info(text)
    return now_time


def run_cmd(cmd):
    logging.info(cmd)
    flag = os.system(cmd)
    if flag != 0:
        logging.error("Command fail: " + cmd)
        exit(2)
    return 0


def run_time(start_time):
    spend_time = time.time() - start_time
    logging.info("Total  spend time : " + fmt_time(spend_time))
    return 0


def fmt_time(spend_time):
    spend_time = int(spend_time)
    day = 24 * 60 * 60
    hour = 60 * 60
    min = 60
    if spend_time < 60:
        return "%ds" % math.ceil(spend_time)
    elif spend_time > day:
        days = divmod(spend_time, day)
        return "%dd%s" % (int(days[0]), fmt_time(days[1]))
    elif spend_time > hour:
        hours = divmod(spend_time, hour)
        return '%dh%s' % (int(hours[0]), fmt_time(hours[1]))
    else:
        mins = divmod(spend_time, min)
        return "%dm%ds" % (int(mins[0]), math.ceil(mins[1]))
