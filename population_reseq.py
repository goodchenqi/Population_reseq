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

def main():
    args=getopt()
    soft=Config()
    name=args.vcf.split('/')[-1].split('.')[0]+'beagle'
    check_dir(args.dir)
    f_out=args.dir+'/population_reseq'
    check_dir(f_out)
    ######Transe vcf to snplist#####
    cmd='python %s -o %s -i %s'%(soft.vcf2snplist,f_out,args.vcf)
    ####imputation####
    out='%s/imputation'%f_out
    check_dir(out)
    cmd='cmd:java -XX:ParallelGCThreads=4 -Xmx20g -Djava.io.tmpdir=%s/tmp -jar %s gtgl=%s out=%s nthreads=%s impute=true'%(out,soft.beagel,args.vcf,out+'/'+name,30)
    run_cmd(cmd)
    #####PhylogeneticTree###
    cmd='python %s PhylogeneticTree -i %s -o %s'%(soft.PhylogeneticTree,args.vcf,f_out)
    run_cmd(cmd)
    #####PopulotionStructure#####
    cmd='python %s -i %s/SNPresult.txt -o %s'%(soft.PopulotionStructure,f_out,f_out)
    run_cmd(cmd)
    ######PrincipalComponentAnalysis######
    cmd='python %s -o %s -i %s/SNPresult.txt -g %sPopulotionStructure/txt/group.txt'%(soft.PrincipalComponentAnalysis,f_out,f_out,f_out)
    run_cmd(cmd)
    ######LD_analysis#######
    cmd='python %s -i %s/SNPresult.txt -o %s'%(soft.LD_analysis,f_out,f_out)
    run_cmd(cmd)

if __name__=='__main__':
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('PopulotionStructure Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('PopulotionStructure Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)

