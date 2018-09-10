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
from config import *
try:
    import matplotlib.pyplot as plt
    plt.switch_backend('agg')
    from matplotlib.backends.backend_pdf import PdfPages
except:
    usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-27
Version: v1.0
Description:
    Populotion Structure computation！ 
Example: 
    python %s [func:Getadmixture|KvalueDistribution|admixtureGroup] [-d indir] [-f file] [-o outdir] [-k prefix]

''' % (__file__[__file__.rfind(os.sep) + 1:])
    print(usage)
    sys.exit(0)
#####Description####
usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-27
Version: v1.0
Description:
    Populotion Structure computation！ 
Example: 
    python %s [func:Getadmixture|KvalueDistribution|admixtureGroup] [-d indir] [-f file] [-o outdir] [-k prefix]

''' % (__file__[__file__.rfind(os.sep) + 1:])


#####HelpFormat#####
class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def getopt():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument(
        'func',choices=['Getadmixture','KvalueDistribution','admixtureGroup'])
    parser.add_argument(
        '-d', '--indir', help='indir', dest='dir',  type=str)
    parser.add_argument(
        '-f', '--file', help='infile[key.ped|key.K_value_select|key.best_knum.txt]', dest='file', type=str)
    parser.add_argument(
        '-o', '--outdir', help='infile', dest='out', type=str)
    parser.add_argument(
        '-k', '--key', help='keyname', dest='key', default='Structure',type=str)
    args = parser.parse_args()
    if not args.dir and args.func=='Getadmixture':
        print('indir must be given')
        sys.exit(0)
    elif not args.file:
        print('infile must be given')
        sys.exit(0)
    elif not args.out:
        print('outdir must be given')
        sys.exit(0)
    return args

#here can use mutiprocess 
def admixtureQ(admixture,samname,outdir,key):
    for i in admixture:
        name=i.split('.')[-2]
        w=open('%s/%s.admixture_k%s.txt'%(outdir,key,name),'w')
        w.write('<Covariate>\n<Trait>')
        for num in os.popen('head -1 %s|awk \'{print NF}\''%(i)):
            for s in range(1,int(num)+1):
                w.write('\tQ%s'%s)
        w.write('\n')
        s=0
        for line in open(i,'r'):
            info=line.strip().split(' ')
            w.write('%s\t%s\n'%(samname[s],'\t'.join(info)))
            s+=1
        w.close()

def value_select(qsubfile,outdir,keys):
    k_value={}
    for i in qsubfile:
        k=int(i.split('.')[-2])
        for line in os.popen('tail -2 %s'%i):
            if line.startswith('CV'):
                k_value[k]=line.strip().split(':')[-1]
                break
    w=open('%s/%s.K_value_select'%(outdir,keys),'w')
    best_k=0
    w.write('K_number\tvalue\n')
    for i in sorted(k_value.keys()):
        w.write('%s\t%s\n'%(i,k_value[i]))
        best_k=i if not best_k else best_k
        best_k=i if k_value[best_k] > k_value[i] else best_k
    w.write('\nselect_K_num:\t%s\n'%best_k)
    w.close()

    w=open('%s/%s.best_k%s.txt'%(outdir,keys,best_k),'w')
    for line in open('%s/%s.admixture_k%s.txt'%(outdir,keys,best_k),'r'):
        w.write(line)
    w.close()

def kvalue_distr(outdir,key,file):
    k_value,bestk,mink,maxk,k,value={},0,100,0,[],[]
    for line in open(file,'r'):
        if line.startswith('\n'):continue
        if line.startswith('K_number'):
            head=line.strip().split('\t')
            continue
        if line.startswith('select_K_num'):
            bestk=line.strip().split('\t')[1]
            continue
        info=line.strip().split('\t')
        if info[0] not in k_value:k_value[info[0]]=''
        k_value[info[0]]=info[1]
        k.append(int(info[0]))
        value.append(float(info[1]))
        mink=int(info[0]) if int(info[0])<mink else mink
        maxk=int(info[0]) if int(info[0])>maxk else maxk
    min_value=float(sorted(k_value.values())[0])
    with PdfPages('%s/%s.pdf'%(outdir,key)) as pdf:
        plt.figure(figsize=(10, 6))
        plt.plot(k,value,'ko-')
        plt.plot(int(bestk),float(k_value[bestk]),'ro')
        #here you must figure out if the max_y is 1
        plt.axis([0, maxk+1, min_value/float(1.3), 1])
        plt.xlabel(head[0])
        plt.ylabel(head[1])
        pdf.savefig()
        plt.close()

def admixture_group(file,outdir):
    data={}
    w=open('%s/group.txt'%outdir,'w')
    for line in open(file,'r'):
        if line.startswith('<Covariate>'):continue
        if line.startswith('<Trait>'):
            head=line.strip().split('\t')
            continue
        info=line.strip().split('\t')
        data[info[0]]=head[info.index(max(info[1:]))]
    for i in sorted(data.items(),key=lambda d:d[1]):
        w.write('\t'.join(i)+'\n')
    w.close()

re_digits = re.compile(r'(\d+)')
def emb_numbers(s):
    pieces=re_digits.split(s)
    pieces[1::2]=map(int,pieces[1::2])    
    return pieces

def group_allk(path):
    data,name={},[]
    w=open('%s/group_all.txt'%path,'w')
    for file in glob.glob('%s/*.admixture_*'%path):
        name.append(file.strip().split('/')[-1])
    name=sorted(name,key=emb_numbers)
    w.write('sample')
    for i in range(len(name)):
        w.write('\tk%s'%(i+1))
    w.write('\n')
    for file in name:
        for line in open(path+'/'+file.strip(),'r'):
            if line.startswith('<Covariate>'):continue
            if line.startswith('<Trait>'):
                head=re.split(r'\s+',line.strip())
                continue
            info=re.split(r'\s+',line.strip())
            if info[0] not in data:data[info[0]]=[]
            data[info[0]].append(head[info.index(max(info[1:]))])
    for key,value in data.items():
        w.write('%s\t%s\n'%(key,'\t'.join(value)))
    w.close()

#PopulationStructureDrwa still need time to draw ,wait for a while

def main():
    args=getopt()
    print('===== Stat each K-value result and find the best [%s]====='%args.func)
    check_dir(args.out)
    admixture,samname,qsubfile=[],[],[]
    for i in glob.glob('%s/*.Q'%(args.dir)):
        admixture.append(i.strip())
    for line in open(args.file,'r'):
        #here you can change ' ' to '\t'
        samname.append(line.strip().split(' ')[0])
    for i in glob.glob('%s/*.out'%args.dir):
        qsubfile.append(i.strip())
    if args.func=='Getadmixture':
        admixtureQ(admixture,samname,args.out,args.key)
        value_select(qsubfile,args.out,args.key)
    elif args.func=='KvalueDistribution':
        kvalue_distr(args.out,args.key,args.file)
    elif args.func=='admixtureGroup':
        admixture_group(args.file,args.out)
        group_allk(args.out)

if __name__=='__main__':
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)