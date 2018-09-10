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
import multiprocessing
from collections import OrderedDict
from config import *
#####Description####
usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-27
Version: v1.0
Description:
    
Example: 
    python %s 

''' % (__file__[__file__.rfind(os.sep) + 1:])


#####HelpFormat#####
class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass



def getopt():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument(
        '-o', '--dir', help='OutputDir  Mapping result  will in OutputDir', dest='dir',  type=str)
    parser.add_argument(
        '-p','--picture',help='chose k picture(default is all)[num|num,num|num:num:num:...]',type=str,dest='pic')
    parser.add_argument(
        '-i', '--input', help='Input Files of variation such like snplist', dest='input', type=str)
    parser.add_argument(
        '-m', '--process', help='num of process,default is 10', default=10,dest='process', type=int)
    parser.add_argument(
        '-t', '--thread', help='thread to do K Analysis,default is 3', default=3,dest='thread', type=int)
    parser.add_argument(
        '-k', '--value', help='Max K-value to run,default is 10', default=10,dest='value', type=int)
    args = parser.parse_args()
    return args

def TransFile(soft,snpfile,dirs):
    begin=show_info('############Trans snplist file to Admixture format is start!#######')
    if os.path.exists('%s/admixture/Structure.ped'%dirs):
        pass
    else:
        cmd='python %s -s %s -o %s -k Structure -t 8'%(soft,snpfile,dirs)
        run_cmd(cmd)
        run_time(begin)

def admixture(pro_num,dirs,soft,ped,thr):
    begin=show_info('##########Calculate each K-value with Admixture is start!#######')
    pool=multiprocessing.Pool(processes=pro_num)
    for i in range(1,pro_num+1):
        out='Structure.%s.out'%i
        ped=ped.strip().split('/')[-1]
        cmd="cd %s/admixture && %s --cv %s %s -j%s>%s"%(dirs,soft,ped,i,thr,out)
        pool.apply_async(run_cmd, (cmd,))
    pool.close()
    pool.join()
    run_time(begin)

def GetAdmixture(Bin,indir,file,outdir):
    begin=show_info('##########Stat each K-value result and find the best!###########')
    #you can change the python version
    cmd='/storage_wut/01Software/Anaconda/anaconda3/bin/python3.6 %s/tree_bin.py Getadmixture -d %s -f %s -o %s'%(Bin,indir,file,outdir)
    run_cmd(cmd)
    run_time(begin)

def Result(Bin,outdir,best,out,k_value,svg):
    begin=show_info('######Find the best K and Draw Map!#######')
    #you can change the python version
    cmd='/storage_wut/01Software/Anaconda/anaconda3/bin/python3.6 %s/tree_bin.py KvalueDistribution -f %s/Structure.K_value_select -o %s'%(Bin,outdir,outdir)
    run_cmd(cmd)
    cmd='/storage_wut/01Software/Anaconda/anaconda3/bin/python3.6 %s/tree_bin.py admixtureGroup -f %s -o %s'%(Bin,best,outdir)
    run_cmd(cmd)
    k_p='-k %s'%k_value if k_value else ''
    cmd='perl %s/PopulationStructureDraw.pl -id %s -o %s/PopulotionStructure.svg %s -svg %s'%(Bin,outdir,out,k_p,svg)
    run_cmd(cmd)
    run_time(begin)

def main():
    args=getopt()
    if not args.dir:
        print('you didn\'t give the output dir!!')
        sys.exit(0)
    if not args.input:
        print('you didn\'t give the input file!!')
        sys.exit(0)
    check_dir(args.dir)
    out='%s/PopulotionStructure'%args.dir
    check_dir(out)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                        datefmt='%Y-%m-%d  %H:%M:%S',
                        filename="%s/PopulationStructure.log"%out,
                        filemode='w')
    soft=Config()
    #####################
    begin=show_info('###########Populotion Structure Analysis is Start!!###########')
    CV=OrderedDict()
    txt='%s/txt'%out
    check_dir(txt)
    ped='%s/admixture/Structure.ped'%out
    file_path=os.path.abspath(sys.argv[0])
    Bin='/'.join(file_path.split('/')[:-1])
    soft_snp2file=soft.snp2xxx
    TransFile(soft_snp2file,args.input,out)
    admixture(args.process,out,soft.admixture,ped,args.thread)
    GetAdmixture(Bin,out+'/admixture',ped,txt)
    best=glob.glob('%s/txt/*.best_k*'%out)
    Result(Bin,txt,best[0],out,args.pic,soft.svg)
    run_time(begin)
    ######################

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
