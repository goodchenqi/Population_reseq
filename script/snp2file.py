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
from collections import OrderedDict
from config import *
#####Description####
usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-22 16:16:18
Link   : 
Version: v1.0
Description:
    translate snp file to the file can build tree!
Example: 
    python %s 

''' % (__file__[__file__.rfind(os.sep) + 1:])

class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def snp2file(snplist,keys,minInt,minMAF,types,outdir):
    code={
    "A":"A","T":"T","C":"C","G":"G",
    "R":"AG","Y":"CT","M":"AC","K":"GT","S":"CG","W":"AT",
    "H":"ACT","B":"CGT","V":"ACG","D":"AGT","N":"ATCG","-":"ATCG","?":"ATCG"
    }
    code1={
    "A":"AA","T":"TT","C":"CC","G":"GG",
    "R":"AG","Y":"CT","M":"AC","K":"GT","S":"CG","W":"AT","?":"NN",
    "H":"ACT","B":"CGT","V":"ACG","D":"AGT","N":"NN","-":"NN"
    }

    code2={
    "A":"AA","T":"TT","C":"CC","G":"GG",
    "R":"AG","Y":"CT","M":"AC","K":"GT","S":"CG","W":"AT","?":"??",
    "N":"??","-":"??"
    }

    hcode={
    "A":"1 1","C":"2 2","G":"3 3","T":"4 4",
    "R":"1 3","Y":"2 4","M":"1 2","K":"3 4","S":"2 3","W":"1 4",
    "?":"0 0","N":"0 0","-":"0 0","?":"0 0"
    }
    htrans = {
            'A':['A', 'A'], 'C':['C', 'C'], 'G':['G', 'G'], 'T':['T', 'T'],
            'R':['A', 'G'], 'Y':['C', 'T'], 'K':['G', 'T'], 'M':['A', 'C'],
            'S':['C', 'G'], 'W':['A', 'T'], 'N':['0', '0'], '?':['0', '0'],'-':['0', '0']
    }
    tag,hhead,tassel,plink,hapinfo,snpnum,samnum,head,sequence,admixture_ped,happed,plinks=0,OrderedDict(),OrderedDict(),OrderedDict(),OrderedDict(),0,0,[],OrderedDict(),OrderedDict(),OrderedDict(),OrderedDict()
    type_dict={1:'',2:'',3:'',7:'',8:'',9:''}
    if not types:
        w=open('%s/%s.filter.snplist'%(outdir,key),'w')
    if types==10:
        dirs='%s/tassel'%outdir
        check_dir(dirs)
        w=open('%s/%s.haplotype'%(dirs,keys),'w')
        #remember write head of tassle
        w.write('rs#\talleles\tchrom\tpos\tstrand\tassembly#\tcenter\tprotLSID\tassayLSID\tpanelLSID\tQCcode\t')
    for line in open(snplist,'r'):
        if line.startswith('#') and tag==0:
            info=line.strip().split('\t')
            head=info[2:]
            if types==10:w.write('\t'.join(head)+'\n')
            samnum=len(head)
            if types==4 or types==5 or types==6:
                for i in head:
                    if i not in plink:plink[i]=[]
            for i in range(len(info[2:])):
                if head[i] not in hhead:hhead[head[i]]=2+i
            tag=1
            if not types:w.write(line)
            continue
        elif line.startswith('#') and tag==1:
            if not types:w.write(line)
            continue
        line=line.replace('?','N')
        line=line.replace('X','N')
        line=line.replace('-','N')
        info=line.strip().split('\t')
        maf,N=OrderedDict(),0
        for i in info[2:]:
            if i=='N':
                N+=1
            else:
                for s in code1[i]:
                    if s not in maf:maf[s]=0
                    maf[s]+=1
        if N==len(info[2:]):continue
        mafs=sorted(maf.values())
        if len(mafs)!=2:continue
        #maf_rat 代表该位点所有样本突变的个数占总数的比率
        maf_rat=float(mafs[0])/float(mafs[0]+mafs[1])
        #int_rat代表该位点样本已知碱基的个数占总样本的比率
        int_rat=float(len(info[2:])-N)/float(len(info[2:]))
        if maf_rat<minMAF or int_rat<minInt:continue
        #tassel
        if types==10:
            base=[i for i in sorted(maf.keys())]
            tassle_info(w,info,base,hhead,code1)

        #plinc plinkt plink
        if types==4 or types==5 or types==6:
            if info[0] not in plinks:plinks[info[0]]=[]
            plinks[info[0]].append(info[1])
            for key,value in hhead.items():
                for base in htrans[info[value]]:
                    plink[key].append(base)
        #hapmap
        if types==9:
            if info[0] not in hapinfo:hapinfo[info[0]]=[]
            if info[0] not in happed:happed[info[0]]=OrderedDict()
            hapinfo[info[0]].append('%s_%s  %s\n'%(info[0],info[1],info[1]))
        if types in type_dict:
            for i in range(len(info[2:])):
                #hapmap
                if types==9:
                    if head[i] not in happed[info[0]]:happed[info[0]][head[i]]=[]
                    happed[info[0]][head[i]].append(hcode[info[i+2]])
                #phlip mega structure mb
                elif types==2 or types==1 or types==7 or types==3:
                    if head[i] not in sequence:sequence[head[i]]=[]
                    sequence[head[i]].append(info[i+2])
                #admixture
                elif types==8:
                    if head[i] not in admixture_ped:admixture_ped[head[i]]=[]
                    admixture_ped[head[i]].append(info[i+2])
        snpnum+=1
        if types==0:w.write(line)
    if types==0:w.close()
    if types==4:
        plink_info(plink,plinks,outdir,keys)
    elif types==5:
        plinkc(plink,plinks,outdir,keys)
    elif types==6:
        plinkt(plink,plinks,outdir,keys)
    elif types==9:
        hapmap(hapinfo,happed,outdir,keys)
    elif types==2:
        phylip(sequence,snpnum,outdir,keys)
    elif types==10:
        w.close()
    elif types==1:
        mega(sequence,outdir,keys,code2)
    elif types==8:
        admixture(admixture_ped,outdir,keys,code1)
    elif types==7:
        structure(sequence,outdir,keys,hcode)
    elif types==3:
        mrbayes(sequence,outdir,keys)

#snp:0,mega:1,phylip:2,mrbayes:3,plink:4,plinkc:5,plinkt:6,structure:7,admixture:8,hapmap:9,tassel:10

# def check_dir(dirs):
#     os.mkdir(dirs) if not os.path.exists(dirs) else show_info('%s already exists!!'%dirs)

#still need to check
def mrbayes(sequence,outdir,keys):
    dirs='%s/mrbayes'%outdir
    check_dir(dirs)
    w=open('%s/%s.nex'%(dirs,keys),'w')
    w.write(
'''
#NEXUS

[Data from : Structure Molecular phylogeny]
BEGIN DATA;
DIMENSIONS NTAX=586 NCHAR=471294;
FORMAT DATATYPE=DNA  MISSING=N GAP=- ;
MATRIX

''')
    for key,value in sequence.items():
        w.write('\n')
        w.write('%s\n'%key)
        for i in range(0,len(value),5000):
            end=i+5000 if i+5000< len(value) else len(value)
            w.write(''.join(value[i:end])+'\n')
    w.write(
''';
END;

BEGIN mrbayes;
        lset nst=6 rates=gamma;
        mcmc ngen=20000  samplefreq=10;
sumt;
END;


''')
    w.close()

def structure(sequence,outdir,keys,code):
    dirs='%s/structure'%outdir
    check_dir(dirs)
    w=open('%s/%s.structure'%(dirs,keys),'w')
    for key,value in sequence.items():
        line1,line2=['%s 1 0'%key],['%s 1 0'%key]
        for i in value:
            code1,code2=code[i].split(' ')
            line1.append(code1)
            line2.append(code2)
        w.write('%s\n%s\n'%(' '.join(line1),' '.join(line2)))
    w.close()

def admixture(admixture_ped,outdir,keys,code):
    dirs='%s/admixture'%outdir
    check_dir(dirs)
    w=open('%s/%s.ped'%(dirs,keys),'w')
    records=OrderedDict()
    for key,value in admixture_ped.items():
        w.write('%s %s 0 0 0 -9'%(key,key))
        for i in range(len(value)):
            if value[i]=='N':
                w.write(' 0 0')
            else:               
                code1,code2=list(code[value[i]])
                if i not in records:records[i]=code1
                w.write(' 1') if code1 == records[i] else w.write(' 2')
                w.write(' 1') if code2 == records[i] else w.write(' 2')
        w.write('\n')
    w.close()


def mega(sequence,outdir,keys,code):
    dirs='%s/mega'%outdir
    check_dir(dirs)
    w=open('%s/%s.meg'%(dirs,keys),'w')
    w.write(
'''#Mega
!Title %s.meg;
!Format DataType=DNA;
!Description
 Missing Base Symbol = '?'
 Identical Base Symbol = '.'
 Gap Symbol = '-';

'''%keys)
    for key,value in sequence.items():
        count=0
        w.write('#%s\n'%key)
        for s in value:
            count+=1
            w.write(code[s]) if s in code else show_info("ERROR: exists B/D/H/V [%s]"%s)
            if count==50:
                count=0
                w.write('\n')
        w.write('\n') if count!=50 else show_info('there are nothing to say!')
    w.close()



def tassle_info(w,info,base,head,code):
    w.write('rs%s%s\t%s/%s\t%s\t%s\t+\tGENOSEQ\tGENOSEQ\tGENOSEQ\tGENOSEQ\tGENOSEQ\tGENOSEQ'%(info[0],info[1],base[0],base[1],info[0],info[1]))
    for key,value in head.items():
        w.write('\t'+code[info[value]])
    w.write('\n')


def phylip(sequence,snpnum,outdir,keys):
    dirs="%s/phylip"%outdir
    check_dir(dirs)
    w=open('%s/%s.phy'%(dirs,keys),'w')
    w.write('%s\t%s\n'%(len(sequence),snpnum))
    sta,end=0,50
    for key,value in sequence.items():
        w.write(key)
        for i in range(sta,end,10):
            s=i+10 if i+10<len(value) else len(value)
            w.write(' '+''.join(value[i:s]))
        w.write('\n')
    w.write('\n')
    sta+=50
    end+=50
    for i in range(len(value)/50):
        for value in sequence.values():
            # w.write('\t')
            for i in range(sta,end,10):
                s=i+10 if i+10<len(value) else len(value)
                w.write(' '+''.join(value[i:s]))
            w.write('\n')
        w.write('\n')
        sta+=50
        end+=50

    w.close()

def hapmap(hap_info,hap_ped,outdir,keys):
    dirs="%s/hapmap"%outdir
    check_dir(dirs)
    for key,value in hap_info.items():
        info=open('%s/%s.hapmap.info'%(dirs,key),'w')
        ped=open('%s/%s.hapmap.ped'%(dirs,key),'w')
        for i in value:
            info.write(i)
        info.close()
        for key_ped,value_ped in hap_ped[key].items():
            ped.write('HAPMAP%s  %s  0  0  0  0  %s\n'%(keys,key_ped,' '.join(value_ped)))
        ped.close()

def plinkt(data_ped,data_map,outdir,keys):
    dirs='%s/plinkt'%outdir
    check_dir(dirs)
    sta,end,list_base=0,2,[]
    for key,value in data_map.items():
        w_fam=open('%s/%s.tfam'%(dirs,key),'w')
        for key_ped,value_ped in data_ped.items():
            w_fam.write('\t'.join([key_ped,key_ped,'0','0','0','1'])+'\n')
        w_fam.close()
    for key,value in data_ped.items():
        list_base.append(value)
        data_ped.pop(key)
    for key,value in data_map.items():
        w_ped=open('%s/%s.tped'%(dirs,key),'w')
        for i in value:
            records,record='',{}
            w_ped.write('\t'.join([key,i,'0',i]))
            for s in list_base:
                if s[sta:end][0]=='0' and s[sta:end][1]=='0':
                    w_ped.write(' 0 0')
                else:
                    if s[sta:end][0] not in record:
                        record[s[sta:end][0]]=''
                        records=s[sta:end][0]
                    if s[sta:end][0]== records:
                        w_ped.write(' 1')
                    else:
                        w_ped.write(' 2')
                    if s[sta:end][1]==records:
                        w_ped.write(' 1')
                    else:
                        w_ped.write(' 2')
            sta+=2
            end+=2
            w_ped.write('\n')
        w_ped.close()

def plinkc(data_ped,data_map,outdir,keys):
    dirs='%s/plinkc'%outdir
    check_dir(dirs)
    sta,end=0,0
    for key,value in data_map.items():
        w_ped=open('%s/%s.ped'%(dirs,key),'w')
        w_map=open('%s/%s.map'%(dirs,key),'w')
        for i in value:
            end+=2
            w_map.write('\t'.join([key,i,'0',i])+'\n')
        w_map.close()
        for key_ped,value_ped in data_ped.items():
            result='\t'.join(value_ped[sta:end])
            w_ped.write('\t'.join([key_ped,key_ped,'0','0','0','1'])+'\t'+result+'\n')
        sta=end
        w_ped.close()


def plink_info(data_ped,data_map,outdir,key):
    dirs='%s/plink'%outdir
    check_dir(dirs)
    w_ped=open('%s/%s.ped'%(dirs,key),'w')
    w_map=open('%s/%s.map'%(dirs,key),'w')
    for key,value in data_map.items():
        for i in value:
            w_map.write('\t'.join([key,i,'0',i])+'\n')
        # data_map.pop(key)
    w_map.close()
    data_map.clear()
    # print(len(data_ped))
    for key,value in data_ped.items():
        result='\t'.join(value)
        w_ped.write('\t'.join([key,key,'0','0','0','1'])+'\t'+result+'\n')
        # data_ped.pop(key)
    w_ped.close()


def main():
    path=os.path.abspath(os.path.dirname(__file__))
    program_dir=os.path.basename(__file__)
    parser = argparse.ArgumentParser(
        formatter_class=HelpFormatter, description=usage)
    parser.add_argument(
        '-s', '--snplist', help='snplist', dest='snplist', type=str)
    parser.add_argument(
        '-o', '--outdir', help='outdir', dest='outdir', type=str)
    parser.add_argument(
        '-k', '--key', help='preffix ', dest='key', type=str)
    parser.add_argument(
        '-M', '--minMAF', help='minMAF<default is 0.05>', dest='minMAF', type=float,default=0.05)
    parser.add_argument(
        '-I', '--minInt', help='minInt<default is 0.5>', dest='minInt', type=float,default=0.5)
    parser.add_argument(
        '-t', '--type', help='output type<snp:0\nmega:1\nphylip:2\nmrbayes:3\nplink:4\nplinkc:5\nplinkt:6\nstructure:7\nadmixture:8\nhapmap:9\ntassel:10>', dest='type', type=int)
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                        datefmt='%Y-%m-%d  %H:%M:%S',
                        filename="%s/snp2file.log"%args.outdir,
                        filemode='w')
    if not args.snplist:
        print('error:you didn\'t input snplist!!')
        sys.exit(0)
    elif not args.outdir:
        print('error:you did\'t give the outdir !!')
        sys.exit(0)
    elif not args.key:
        print('error:you did\'t input the key!!')
        sys.exit(0)
    elif not args.type:
        print('error:you did\'t chose the format')
        sys.exit(0)
    check_dir(args.outdir)
    snp2file(args.snplist,args.key,args.minInt,args.minMAF,args.type,args.outdir)

if __name__=='__main__':
    try:
        print('###########Transe SNPlist to file is start!##################')
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
