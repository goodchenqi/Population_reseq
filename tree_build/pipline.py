#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####Import Module#####
import logging
import sys
import os,re
import math
import time
import argparse
import multiprocessing
import glob
from config import *
#####Description####
usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-9-3
Version: v1.0
Description:
    population reseq! 
Example: 
    python %s [-i vcf] [-o path]

''' % (__file__[__file__.rfind(os.sep) + 1:])

#####HelpFormat#####
class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def getopt():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument(
        '-i', '--snpvcf', help='snpvcf', dest='vcf',  type=str)
    parser.add_argument(
        '-o', '--outdir', help='outdir', dest='dir',  type=str)
    args=parser.parse_args()
    if not args.vcf:
        print('snpvcf must be given!')
        sys.exit(0)
    elif not args.dir:
        print('outdir must be given!')
        sys.exit(0)
    return args

def draw_tree(outdir,PopulationEvolution):
    cmd='python %s PhylogeneticTree -o %s -i %s/SNPresult.txt'%(PopulationEvolution,outdir,outdir)
    os.system(cmd)

def other(outdir,vcf,PopulationEvolution):
    path=os.path.abspath(outdir)
    ##############PopulotionStructure#############
    cmd='python %s PopulotionStructure -o %s -i %s/SNPresult.txt'%(PopulationEvolution,outdir,outdir)
    os.system(cmd)
    ##############PrincipalComponentAnalysis#######
    cmd='python %s PrincipalComponentAnalysis -o %s -i %s/SNPresult.txt -g %s/PopulotionStructure/txt/group.txt'%(PopulationEvolution,outdir,outdir,outdir)
    os.system(cmd)
    ###############LD_analysis###############
    os.chdir(path)
    cmd='python %s LD_analysis -i %s/SNPresult.txt -o %s -v %s -g %s/PopulotionStructure/txt/group.txt'%(PopulationEvolution,outdir,outdir,vcf,outdir)
    os.system(cmd)

def main():
    args=getopt()
    name=args.vcf.split('/')[-1].split('.')[0]+'beagle'
    check_dir(args.dir)
    f_out=args.dir+'/Evolution'
    check_dir(f_out)
    soft=Config()
    #############Transe vcf to snplist#########
    vcf=os.path.abspath(args.vcf)
    cmd='python %s vcf2snplist -o %s -i %s'%(soft.PopulationEvolution,f_out,args.vcf)
    os.system(cmd)
    pool=multiprocessing.Pool(processes=2)
    pool.apply_async(draw_tree,(f_out,soft.PopulationEvolution,))
    pool.apply_async(other,(f_out,vcf,soft.PopulationEvolution,))
    pool.close()
    pool.join()


if __name__=='__main__':
    #test infomation:
        #sample size:76G memory size(max):50G run time(total):4h56m44s threading(max):33
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('all_tree Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('all_tree Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)
