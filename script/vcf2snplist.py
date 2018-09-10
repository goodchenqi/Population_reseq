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
    transe vcf to snplist file!
Example:
    python %s [-i snp.vcf] [-o path] [options][-h help]
''' % (__file__[__file__.rfind(os.sep) + 1:])

class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def rand_select(file,percent,thr,ref,dep):
    for line in os.popen('wc -l %s'%file):
        total_line=int(line.split(' ')[0])
    name='_'.join(file.split('/')[-1].split('.')[:-1])
    count_all,count_i=0,0
    w=open('SNPresult.txt','w')
    w.write('#Chr\tPos\t')
    w_i=open('%s_%s.vcf'%(name,count_i),'w')
    for line in open(file,'r'):
        if line.startswith('##'):
            total_line-=1
            continue
        if line.startswith('#CHROM'):
            each_thr=total_line/thr
            info=line.strip().split('\t')
            if ref:w.write('Ref\tAlt\t')
            if dep:
                w.write('\tDP\tAD'.join(info[9:])+'\n')
                table_head='#Chr\tPos\t'+'\tDP\tAD'.join(info[9:])
            else:
                w.write('\t'.join(info[9:])+'\n')
                table_head='#Chr\tPos\t'+'\t'.join(info[9:])
            count_all+=1
            continue
        count_all+=1
        if random.random()<float(percent):
            if each_thr*count_i<count_all<=each_thr*(count_i+1):
                w_i.write(line)
            elif count_all>each_thr*(count_i+1):
                count_i+=1
                if count_i>=thr:
                    break
                w_i.close()
                w_i=open('%s_%s.vcf'%(name,count_i),'w')
                w_i.write(line)
    w.close()
    w_i.close()
    return table_head

def run_process(num,name,ref,dep,types):
    single={'AG':'R', 'GA':'R', 'CT':'Y', 'TC':'Y', 'GT':'K', 'TG':'K', 'AC':'M', 'CA':'M','CG':'S', 'GC':'S', 'AT':'W', 'TA':'W', 'A':'A', 'C':'C', 'G':'G', 'T':'T','CGT':'B', 'AGT':'D', 'ACT':'H', 'ACG':'V', 'ACGT':'N'}
    double={'AG':'AG', 'GA':'AG', 'CT':'CT', 'TC':'CT', 'GT':'GT', 'TG':'GT', 'AC':'AC', 'CA':'AC','CG':'CG', 'GC':'CG', 'AT':'AT', 'TA':'AT', 'A':'AA', 'C':'CC', 'G':'GG', 'T':'TT','CGT':'CGT', 'AGT':'AGT', 'ACT':'ACT', 'ACG':'ACG', 'ACGT':'NN'}
    code={"A":"AA","T":"TT","C":"CC","G":"GG","R":"AG","Y":"CT","M":"AC","K":"GT","S":"CG","W":"AT","H":"ACT","B":"CGT","V":"ACG","D":"AGT","N":"NN"}
    data,a={},2
    for i in os.popen('head -1 SNPresult.txt'):
        for s in i.strip().split('\t')[2:]:
            data[a]=[s]
            a+=1
    w=open('%s_%s.txt'%(name,num),'w')
    twobase=['','','']
    for line in open('%s_%s.vcf'%(name,num),'r'):
        info=line.strip().split('\t')
        twobase[0],twobase[1],formats,sample=info[3],info[4],info[8],info[9:]
        w.write('\t'.join(info[:2])+'\t')
        if len(twobase[0])!=1:continue
        if re.findall(r'AD',info[8]) and re.findall(r'DP',info[8]):
            if ref:
                w.write('\t'.join(twobase)+'\t')
            if len(twobase[1])!=1:
                bases=twobase[1].split(',')
                flag=0
                for base in bases:
                    if len(base)!=1:
                        flag=1
                        break
                if flag==1:continue
                for i in range(len(bases)):
                    twobase[i+1]=bases[i]
            form=formats.split(':')    
            dp_pos=form.index('DP') if 'DP' in form else "NA"
            gt_pos=form.index('GT') if 'GT' in form else "NA"
            ad_pos=form.index('AD') if 'AD' in form else "NA"
            count_a=2
            for ids in sample:
                sam=ids.split(':')
                try:
                    gt=sam[gt_pos] if gt_pos!="NA" else '.'
                    dp=sam[dp_pos] if dp_pos!="NA" else '.'
                    ad=sam[ad_pos] if ad_pos!="NA" else '.'
                except:
                    show_info('this is normal error,maybe no DP or AD!')
                gt=gt.split('/')
                while '.' in gt:
                    gt.remove('.')
                if gt:
                    match_info=list(set([twobase[int(i)] for i in gt]))
                    match=''.join(match_info)
                    if match not in single or match not in double:
                        start_time=show_info("key %s not exists"%match)
                        run_time(start_time)
                        exit()
                    else:
                        if dep:
                            if types:
                                w.write('\t'.join([double[match],dp,ad])+'\t')
                                data[count_a].append(double[match])
                            else:
                                w.write('\t'.join([single[match],dp,ad])+'\t')
                                data[count_a].append(single[match])

                        else:
                            if types:
                                w.write(double[match]+'\t')
                                data[count_a].append(double[match])
                            else:
                                w.write(single[match]+'\t')
                                data[count_a].append(single[match])
                        count_a+=1
                else:
                    if dep:
                        if types:
                            w.write('NN\t.\t')
                            data[count_a].append('NN')
                        else:
                            w.write('N\t.\t')
                            data[count_a].append('N')
                    else:
                        if types:
                            w.write('NN\t')
                            data[count_a].append('NN')
                        else:
                            w.write('N\t')
                            data[count_a].append('N')
                        count_a+=1
            w.write('\n')
    w.close()
    os.remove('%s_%s.vcf'%(name,num))

def merge(thr,name,suffix):
    w=open('SNPresult.%s'%(suffix),'a')
    for i in range(thr):
        for line in open('%s_%s.%s'%(name,i,suffix),'r'):
            w.write(line)
        os.remove('%s_%s.%s'%(name,i,suffix))
    w.close()

def main():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument('-o','--dir',dest='dir',help='output dir',type=str)
    parser.add_argument('-i','--input',dest='input',help="SNP vcf file",type=str)
    parser.add_argument('-r','--ref',dest='ref',help="output ref and alt(0:no; 1:yes)",default=0,type=int)
    parser.add_argument('-d','--dep',dest='dep',help="output depth(0:no; 1:yes)",default=0,type=int)
    parser.add_argument('-s','--type',dest='type',help='type of snp(0:single base; 1:double base)',default=0,type=int)
    parser.add_argument('-t','--threading',dest='thread',help='the num of thread',type=int,default=10)
    parser.add_argument('-p','--percent',dest='perc',help='chose the random position',type=float,default=0.1)
    args=parser.parse_args()
    if not args.input:
        print('SNP vcf file must be given!\n')
        sys.exit(0)
    elif not args.dir:
        print('output dir must be given!')
        sys.exit(0)
    check_dir(args.dir)
    os.chdir(args.dir)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                        datefmt='%Y-%m-%d  %H:%M:%S',
                        filename='vcf2list.log',
                        filemode='w')
    run_start=show_info("===========vcf2list is start!==============")
    soft=Config()
    thr=args.thread
    name='_'.join(args.input.split('/')[-1].split('.')[:-1])
    table_head=rand_select(os.path.abspath(args.input),args.perc,thr,args.ref,args.dep)
    pool=multiprocessing.Pool(processes=thr)
    for i in range(thr):    
        pool.apply_async(run_process, (i,name,args.ref,args.dep,args.type,))
    pool.close()
    pool.join()
    merge(thr,name,"txt")
    run_time(run_start)

if __name__=="__main__":
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('vcf2list Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('vcf2list Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)