#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####Import Module#####
import random
import time
import sys
import os,re
import multiprocessing
import logging
import math
import argparse
from config import *

####Description####
usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-15 16:16:18
Link   : 
Version: v1.0
Description:
    进化树构建！
Example:
    python %s [-i snp.vcf] [options][-h help]
''' % (__file__[__file__.rfind(os.sep) + 1:])

class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def main():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument('-o','--dir',dest='dir',help='output dir',type=str)
    parser.add_argument('-i','--input',dest='input',help="snplist",type=str)
    parser.add_argument('-t','--type',dest='type',help="mega:0|muscle:1",type=int,default=0)
    args=parser.parse_args()
    soft=Config()
    if not args.input:
        print('SNP vcf file must be given!\n')
        sys.exit(0)
    elif not args.dir:
        print('output dir must be given!')
        sys.exit(0)
    check_dir(args.dir)
    out='%s/PhylogeneticTree'%args.dir
    check_dir(out)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                        datefmt='%Y-%m-%d  %H:%M:%S',
                        filename='%s/PhylogeneticTree.log'%out,
                        filemode='w')
    begin=show_info('##########PhylogeneticTree start!##################')
    meg='%s/mega/MultipleSequenceAlignment.meg'%out
    fa='%s/MultipleSequenceAlignment.fa'%out
    if args.type==0:
        show_info('#####Trans snplist file to MEGA format is start######')      
        cmd='python %s -s %s -o %s -k MultipleSequenceAlignment -t 1'%(soft.snp2xxx,args.input,out)
        run_cmd(cmd)
        cmd='sed \'1,8d\' %s |sed \'s/#/>/g\'>%s'%(meg,fa)
        run_cmd(cmd)
    else:
        show_info('########Multiple Sequence Alignment of input fasta is start#######')       
        cmd='%s -in %s -out %s -quiet'%(soft.muscle,args.input,fa)
        run_cmd(cmd)
    show_info('########draw tree###########')
    cmd='%s -nt %s>%s/PhylogeneticTree.nwk'%(soft.FastTree,fa,out)
    run_cmd(cmd)
    run_time(begin)

if __name__=="__main__":
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('PhylogeneticTree Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('PhylogeneticTree Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)