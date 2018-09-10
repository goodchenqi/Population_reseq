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
    LD analysis!
Example: 
    python %s

''' % (__file__[__file__.rfind(os.sep) + 1:])


#####HelpFormat#####
class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def PopLDdecay(snp2file,outdir,file,plink2genotype,PopLDdecay,Plot_OnePop):
    out='%s/PopLDdecay'%outdir
    check_dir(out)
    # if check_run('%s/plink/Pop.ped'%out):
    cmd='python %s -s %s -o %s -k Pop -t 4'%(snp2file,file,out)
    os.system(cmd)
    cmd='perl %s -inPED %s/plink/Pop.ped -inMAP %s/plink/Pop.map -outGenotype %s/out.genotype'%(plink2genotype,out,out,out)
    os.system(cmd)
    cmd='%s -InGenotype %s/out.genotype -OutStat %s/LDdecay'%(PopLDdecay,out,out)
    os.system(cmd)
    cmd='perl %s -inFile %s/LDdecay.stat.gz -output %s/Fig'%(Plot_OnePop,out,out)
    os.system(cmd)

def LD(haploview,ped,info,out,args):
    name=ped.split('/')[-1].split('.')[0]
    cmd='java -jar %s -pedfile %s -info %s -out %s/%s -n -compressedpng -check -dprime -memory 8100'%(haploview,ped,info,out,name)
    run_cmd(cmd)
    dist_sliding(out+'/'+name+'.LD',args.type,args.win,args.step,out,name)

def LD_new(haploview,ped,info,out,args):
    for i in range(len(ped)):
        name=ped.split('/')[-1].split('.')[0]
        cmd='java -jar %s -pedfile %s -info %s -out %s/%s -n -compressedpng -check -dprime -memory 8100'%(haploview,ped[i],info[i],out,name)
        run_cmd(cmd)
        dist_sliding(out+'/'+name+'.LD',args.type,args.win,args.step,out,name)

def Haploview(outdir,haploview,thr,args):
    ######LD_analysis#######
    out='%s/LD_analysis'%outdir
    check_dir(out)
    cmd='python %s -s %s/SNPresult.txt -o %s -k structure -t 9'%(soft.snp2xxx,args.dir,out)
    run_cmd(cmd)
    ped,info=[],[]

    for i in glob.glob('%s/hapmap/*.ped'%out):
        ped.append(i.strip())
    for i in glob.glob('%s/hapmap/*.info'%out):
        info.append(i.strip())
    ped=sorted(ped)
    info=sorted(info)
    if len(ped)<=thr:
        pool=multiprocessing.Pool(processes=len(ped))
        for i in range(len(ped)):
            pool.apply_async(LD,(haploview,ped[i],info[i],out,args,))
        pool.close()
        pool.join()
    else:
        pool=multiprocessing.Pool(processes=thr)
        num=len(ped)//thr
        num_yu=len(ped)%thr
        sta,end,site=0,0,[]
        for i in range(0,len(ped),num):
            end=i+num+1 if num_yu>0 else i+num
            site.append([sta,end])
            sta=end
            num_yu-=1
        for i in range(len(site)):
            pool.apply_async(LD_new,(haploview,ped[site[i][0]:site[i][1]],info[site[i][0]:site[i][1]],out,args,))
        pool.close()
        pool.join()

def dist_sliding(file,types,win,step,outdir,name):
    path='/'.join(file.strip().split('/')[:-1]) if len(file.strip().split('/'))>1 else '.'
    for line in open(file,'r'):
        info=line.strip().split('\t')
        nr=info.index('r^2')
        nd=info.index('D\'')
        nDi=info.index('Dist')
        break
    cmd='less %s|sort -n -k %s|cut -f %s|tail -n 1'%(file,nDi+1,nDi+1)
    for i in os.popen(cmd):
        chr_length=int(i.strip())
    hash_v=OrderedDict()
    a=0
    if types:
        for line in open(file,'r'):
            if a==0:
                a+=1
                continue           
            info=line.strip().split('\t')
            dist=int(info[nDi])
            value=info[nr]
            zh=int(dist/win)-2
            if zh<0:
                zh=0
            elif zh%2 == 0:
                zh-=1
            start=zh*win
            for sta in range(start,start+5*win,step):
                end=sta+win
                if dist>=sta and dist<=end:
                    if sta not in hash_v:hash_v[sta]=[]
                    hash_v[sta].append(value)
    else:  
        for line in open(file,'r'):
            if a==0:
                a+=1
                continue           
            info=line.strip().split('\t')
            dist=int(info[nDi])
            value=info[nd]
            zh=int(dist/win)-2
            if zh<0:
                zh=0
            elif zh%2 == 0:
                zh-=1
            start=zh*win
            for sta in range(start,start+5*win,step):
                end=sta+win
                if dist>=sta and dist<=end:
                    if sta not in hash_v:hash_v[sta]=[]
                    hash_v[sta].append(value)
    w=open('%s/%s.txt'%(outdir,name),'w')
    for key in sorted(hash_v.keys()):
        sums,num=0,0
        for value in hash_v[key]:
            num+=1
            sums+=float(value)
        pos=key+win/2
        w.write('%s\t%.2f\n'%(int(pos),float(sums)/float(num)))
    w.close()

def getopt():
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument(
        '-i', '--snplist', help='snplist', dest='snp',  type=str)
    parser.add_argument(
        '-o', '--outdir', help='outdir', dest='dir',  type=str)
    parser.add_argument(
        '-t','--thr',help='the num of LD threading',type=int,default=10,dest='thr')
    parser.add_argument(
        '-p','--type',help='r^2:1|D:0',dest='type',type=int,default=1)
    parser.add_argument(
        '-w','--window',help='window length(bp)',dest='win',type=int,default=5000)
    parser.add_argument(
        '-s','--stepl',help='step length(bp)',dest='step',type=int,default=100)
    args=parser.parse_args()
    if not args.snp:
        print('snpvcf must be given!')
        sys.exit(0)
    elif not args.dir:
        print('outdir must be given!')
        sys.exit(0)
    return args

def main():
    args=getopt()
    soft=Confit()
    out='%s/LD_analysis'%args.dir
    check_dir(out)
    PopLDdecay(soft.snp2xxx,out,args.dir+'/SNPresult.txt',soft.plink2genotype,soft.PopLDdecay,soft.Plot_OnePop)
    Haploview(out,soft.haploview,args.thr,args)

if __name__=='__main__':
    try:
        t1 = time.time()
        time1 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))
        print('LD_analysis Start at : ' + time1)

        main()
        t2 = time.time()
        time2 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t2))
        print('End at : ' + time2)
        t3 = t2 - t1
        print('LD_analysis Spend time: ' + fmt_time(t3))
    except KeyboardInterrupt:
        sys.stderr.write("User interrupt me! ;-) See you!\n")
        sys.exit(0)