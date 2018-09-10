#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####Import Module#####
import logging
import sys
import os,re
import math
import time
import argparse
import glob
from collections import OrderedDict
from config import *
#####Description####
usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-27
Version: v1.0
Description:
    PCA analysis
Example: 
    python %s [-o dir] [-i SNP.txt] [-f group.txt]

''' % (__file__[__file__.rfind(os.sep) + 1:])


#####HelpFormat#####
class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def getopt():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument(
        '-o', '--out', help='outdir', dest='out', type=str)
    parser.add_argument(
        '-i','--input',help='snplist file',dest='input',type=str)
    parser.add_argument(
        '-g', '--group', help='File samples div into different group like<group.txt>', dest='group', type=str)
    args = parser.parse_args()
    if not args.out:
        print('outdir must be given')
        sys.exit(0)
    elif not args.input:
        print('snplist file must be given')
        sys.exit(0)
    # elif not args.file:
    #     print('<group.txt> must be given')
    #     sys.exit(0)
    return args

def TransFile(soft,file,outdir,maps,ped):
    begin=show_info('===== Trans snplist file to plink format is start =====')
    print('===== Trans snplist file to plink format is start =====')
    cmd='python %s -s %s -o %s -k pca -t 4'%(soft,file,outdir)
    if check_run(maps) and check_run(ped):run_cmd(cmd)
    run_time(begin)

def Analysis(plink,outdir,pca,pcl):
    begin=show_info('===== Calculate with Plink is start =====')
    print('===== Calculate with Plink is start =====')
    # cmd='cd %s/plink/ && %s --noweb --file pca --maf 0.05 --make-bed --out pca'%(outdir,plink)
    # if check_run(bed):run_cmd(cmd)
    # cmd='cd %s/plink/ && %s --bfile pca --make-grm --out pca'%(outdir,gcta)
    # run_cmd(cmd)
    # cmd='cd %s/plink/ && %s --grm pca --pca 3 --out pca'%(outdir,gcta)
    # run_cmd(cmd)
    if check_run(pca) and check_run(pcl):
        cmd="cd %s/plink/ && %s --file pca --pca 3 --out pca --noweb"%(outdir,plink)
        run_cmd(cmd)
    w=open('%s/pca.contribution_rate.stat'%outdir,'w')
    data,s,all_num=OrderedDict(),0,0
    for i in open(pcl,'r'):
        s+=1
        name='PC'+str(s)
        if name not in data:data[name]=float(i.strip())
        all_num+=float(i.strip())
    for key in data.keys():
        w.write('\t'+key)
    w.write('\n')
    w.write('Proportion of Variance')
    for key,value in data.items():
        w.write('\t%.2f'%(value/all_num))
    w.write('\nCumulative Proportion')
    s=0
    for key,value in data.items():
        s+=value/all_num
        w.write('\t%.2f'%s)
    w.close()
    run_time(begin)

def Matrix(matrix,file,pca):
    tmp1=matrix+'.tmp1'
    tmp2=matrix+'.tmp2'
    cmd='echo \"Sample\tGroup\tPC1\tPC2\tPC3\" >%s && sort -k1 %s>%s && sort -k1 %s|sed \'s/ /\t/g\'|cut -f 3->%s && paste %s %s >> %s && rm -f %s %s'%(matrix,file,tmp1,pca,tmp2,tmp1,tmp2,matrix,tmp1,tmp2)
    run_cmd(cmd)

def DrawPicture(outdir,R,Rscript):
    begin=show_info("===== Draw Principal Component Analysis Pictures is start =====")
    print("===== Draw Principal Component Analysis Pictures is start =====")
    #here you can change the Rscript
    cmd='cd %s && %s %s'%(outdir,Rscript,R)
    run_cmd(cmd)
    run_time(begin)

def nogroup_Matrix(outdir):
    w=open('%s/PrincipalComponentAnalysis.nogroup.matrix'%outdir,'w')
    for i in os.popen('head -1 %s/plink/pca.eigenvec|awk \'{print NF}\''%outdir):
        num=i.strip()
    w.write('Sample')
    for i in range(1,int(num)):
        w.write('\tPC%s'%i)
    w.write('\n')
    for line in open('%s/plink/pca.eigenvec'%outdir):
        info=re.split(r'\s+',line)
        w.write('\t'.join(info[1:])+'\n')
    w.close()

def main():
    args=getopt()
    check_dir(args.out)
    soft=Config()
    out='%s/PrincipalComponentAnalysis'%args.out
    check_dir(out)
    ped='%s/plink/pca.ped'%out
    maps='%s/plink/pca.map'%out
    pcl='%s/plink/pca.eigenval'%out
    pca='%s/plink/pca.eigenvec'%out
    matrix='%s/PrincipalComponentAnalysis.matrix'%out
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                        datefmt='%Y-%m-%d  %H:%M:%S',
                        filename="%s/PrincipalComponentAnalysis.log"%out,
                        filemode='w')
    begin=show_info('###############Principal Component Analysis is Start!!#############')
    TransFile(soft.snp2xxx,args.input,out,maps,ped)
    Analysis(soft.plink,out,pca,pcl)
    if args.group:
        Matrix(matrix,args.file,pca)
        DrawPicture(out,soft.R,soft.Rscript)
    nogroup_Matrix(out)
    run_time(begin)

if __name__=='__main__':
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('PrincipalComponentAnalysis Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('PrincipalComponentAnalysis Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)