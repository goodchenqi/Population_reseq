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
from collections import OrderedDict
from config import *
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.switch_backend('agg')
    from matplotlib.backends.backend_pdf import PdfPages
except:
    print('matplotlib error:may you should check the package!!')
    sys.exit(0)

####Description####
def usages(description):
    usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-09-08 16:16:18
Link   : 
Version: v1.0
Description:
    %s
Example:
    python %s 
''' % (description,__file__[__file__.rfind(os.sep) + 1:])
    return usage

class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

class Tree_bin():
    def __init__(self):
        self.re_digits = re.compile(r'(\d+)')

    def getopt(self):
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
    def admixtureQ(self,admixture,samname,outdir,key):
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

    def value_select(self,qsubfile,outdir,keys):
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

    def kvalue_distr(self,outdir,key,file):
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

    def admixture_group(self,file,outdir):
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

    def emb_numbers(self,s):
        pieces=self.re_digits.split(s)
        pieces[1::2]=map(int,pieces[1::2])    
        return pieces

    def group_allk(self,path):
        data,name={},[]
        w=open('%s/group_all.txt'%path,'w')
        for file in glob.glob('%s/*.admixture_*'%path):
            name.append(file.strip().split('/')[-1])
        name=sorted(name,key=self.emb_numbers)
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

    def main(self):
        args=self.getopt()
        begin=show_info('===== Stat each K-value result and find the best [%s]====='%args.func)
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
            self.admixtureQ(admixture,samname,args.out,args.key)
            self.value_select(qsubfile,args.out,args.key)
        elif args.func=='KvalueDistribution':
            self.kvalue_distr(args.out,args.key,args.file)
        elif args.func=='admixtureGroup':
            self.admixture_group(args.file,args.out)
            self.group_allk(args.out)
        run_time(begin)

class Snp2file():
    def snp2file(self,snplist,keys,minInt,minMAF,types,outdir):
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
                self.tassle_info(w,info,base,hhead,code1)

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
            self.plink_info(plink,plinks,outdir,keys)
        elif types==5:
            self.plinkc(plink,plinks,outdir,keys)
        elif types==6:
            self.plinkt(plink,plinks,outdir,keys)
        elif types==9:
            self.hapmap(hapinfo,happed,outdir,keys)
        elif types==2:
            self.phylip(sequence,snpnum,outdir,keys)
        elif types==10:
            self.w.close()
        elif types==1:
            self.mega(sequence,outdir,keys,code2)
        elif types==8:
            self.admixture(admixture_ped,outdir,keys,code1)
        elif types==7:
            self.structure(sequence,outdir,keys,hcode)
        elif types==3:
            self.mrbayes(sequence,outdir,keys)

    #snp:0,mega:1,phylip:2,mrbayes:3,plink:4,plinkc:5,plinkt:6,structure:7,admixture:8,hapmap:9,tassel:10

    # def check_dir(dirs):
    #     os.mkdir(dirs) if not os.path.exists(dirs) else show_info('%s already exists!!'%dirs)

    #still need to check
    def mrbayes(self,sequence,outdir,keys):
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

    def structure(self,sequence,outdir,keys,code):
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

    def admixture(self,admixture_ped,outdir,keys,code):
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


    def mega(self,sequence,outdir,keys,code):
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



    def tassle_info(self,w,info,base,head,code):
        w.write('rs%s%s\t%s/%s\t%s\t%s\t+\tGENOSEQ\tGENOSEQ\tGENOSEQ\tGENOSEQ\tGENOSEQ\tGENOSEQ'%(info[0],info[1],base[0],base[1],info[0],info[1]))
        for key,value in head.items():
            w.write('\t'+code[info[value]])
        w.write('\n')


    def phylip(self,sequence,snpnum,outdir,keys):
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

    def hapmap(self,hap_info,hap_ped,outdir,keys):
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

    def plinkt(self,data_ped,data_map,outdir,keys):
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

    def plinkc(self,data_ped,data_map,outdir,keys):
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


    def plink_info(self,data_ped,data_map,outdir,key):
        dirs='%s/plink'%outdir
        check_dir(dirs)
        w_ped=open('%s/%s.ped'%(dirs,key),'w')
        w_map=open('%s/%s.map'%(dirs,key),'w')
        for key,value in data_map.items():
            for i in value:
                w_map.write('\t'.join([key,i,'0',i])+'\n')
        w_map.close()
        data_map.clear()
        for key,value in data_ped.items():
            result='\t'.join(value)
            w_ped.write('\t'.join([key,key,'0','0','0','1'])+'\t'+result+'\n')
        w_ped.close()

    def main(self):
        path=os.path.abspath(os.path.dirname(__file__))
        program_dir=os.path.basename(__file__)
        parser = argparse.ArgumentParser(
            formatter_class=HelpFormatter, description=usages('Snp2file!'))
        parser.add_argument(
            'func',choices=['Snp2file'])
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

class LD_analysis():
    def PopLDdecay(self,soft,outdir,file,plink2genotype,PopLDdecay,Plot_OnePop,keys,minInt,minMAF):
        begin=show_info('########PopLDdecay is start!###########')
        out='%s/PopLDdecay'%outdir
        check_dir(out)
        # if check_run('%s/plink/Pop.ped'%out):
        soft.snp2file(file,keys,minInt,minMAF,4,out)
        # cmd='python %s -s %s -o %s -k Pop -t 4'%(snp2file,file,out)
        # os.system(cmd)
        cmd='perl %s -inPED %s/plink/Pop.ped -inMAP %s/plink/Pop.map -outGenotype %s/out.genotype'%(plink2genotype,out,out,out)
        run_cmd(cmd)
        cmd='%s -InGenotype %s/out.genotype -OutStat %s/LDdecay'%(PopLDdecay,out,out)
        run_cmd(cmd)
        cmd='perl %s -inFile %s/LDdecay.stat.gz -output %s/Fig'%(Plot_OnePop,out,out)
        run_cmd(cmd)
        run_time(begin)

    def LD(self,haploview,ped,info,out,args,memory):
        name=ped.split('/')[-1].split('.')[0]
        cmd='java -jar %s -pedfile %s -info %s -out %s/%s -n -compressedpng -check -dprime -memory %s'%(haploview,ped,info,out,name,memory)
        run_cmd(cmd)
        self.dist_sliding(out+'/'+name+'.LD',args.type,args.win,args.step,out,name)

    def LD_new(self,haploview,ped,info,out,args,memory):
        for i in range(len(ped)):
            name=ped[i].split('/')[-1].split('.')[0]
            cmd='java -jar %s -pedfile %s -info %s -out %s/%s -n -compressedpng -check -dprime -memory %s'%(haploview,ped[i],info[i],out,name,memory)
            run_cmd(cmd)
            self.dist_sliding(out+'/'+name+'.LD',args.type,args.win,args.step,out,name)

    def Haploview(self,outdir,haploview,thr,args,tools,memory):
        begin=show_info('##############Haploview is start!################')
        ######LD_analysis#######
        out='%s/Haploview'%outdir
        check_dir(out)
        # if check_run(out+'/hapmap'):
        tools.snp2file(args.snp,args.prefix,args.minInt,args.minMAF,9,out)
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
                pool.apply_async(self.LD,(haploview,ped[i],info[i],out,args,memory,))
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
                pool.apply_async(self.LD_new,(haploview,ped[site[i][0]:site[i][1]],info[site[i][0]:site[i][1]],out,args,memory,))
            pool.close()
            pool.join()
        run_time(begin)

    def dist_sliding(self,file,types,win,step,outdir,name):
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

    ##you have to make sure where you can output fst result,and change the Q*.txt
    def fst(self,vcf,group,outdir,vcftools):
        begin=show_info('##########FST Calculate is start!##########')
        out='%s/FST'%outdir
        check_dir(out)
        data,group_list={},[]
        for i in open(group,'r'):
            info=i.strip().split('\t')
            if info[1] not in data:data[info[1]]=[]
            data[info[1]].append(info[0])
        for key,value in data.items():
            group_list.append(out+'/'+key+'.txt')
            w=open('%s/%s.txt'%(out,key),'w')
            for i in value:
                w.write(i+'\n')
            w.close()
        all_group=' --weir-fst-pop '.join(group_list)
        all_group='--weir-fst-pop '+all_group
        cmd='%s --vcf %s --out %s/fst_result %s --fst-window-size 3000'%(vcftools,vcf,out,all_group)
        run_cmd(cmd)
        for i in group_list:
            os.remove(i)
        cmd='%s --vcf %s --out %s/fst_result --window-pi 3000'%(vcftools,vcf,out)
        run_cmd(cmd)
        run_time(begin)

    def getopt(self):
        parser = argparse.ArgumentParser(
            formatter_class=HelpFormatter, description=usage)
        parser.add_argument('func',choices=['LD_analysis'])
        parser.add_argument(
            '-i', '--snplist', help='snplist', dest='snp',  type=str)
        parser.add_argument(
            '-o', '--outdir', help='outdir', dest='dir',  type=str)
        parser.add_argument(
            '-v','--vcf',help='vcf file',dest='vcf',type=str)
        parser.add_argument(
            '-g','--group',help='group file',dest='group',type=str)
        parser.add_argument(
            '-t','--thr',help='the num of LD threading',type=int,default=10,dest='thr')
        parser.add_argument(
            '-p','--type',help='r^2:1|D:0',dest='type',type=int,default=1)
        parser.add_argument(
            '-w','--window',help='window length(bp)',dest='win',type=int,default=5000)
        parser.add_argument(
            '-s','--stepl',help='step length(bp)',dest='step',type=int,default=100)
        parser.add_argument(
            '-P','--prefix',help='the file of the transe file prefix',dest='prefix',default='Pop',type=str)
        parser.add_argument(
            '-M', '--minMAF', help='minMAF<default is 0.05>', dest='minMAF', type=float,default=0.05)
        parser.add_argument(
            '-I', '--minInt', help='minInt<default is 0.5>', dest='minInt', type=float,default=0.5)
        parser.add_argument('-m','--memory',help='haploview run memory set(Mb)',dest='memory',type=int,default=8100)
        args=parser.parse_args()
        if not args.snp:
            print('snpvcf must be given!')
            sys.exit(0)
        elif not args.dir:
            print('outdir must be given!')
            sys.exit(0)
        elif not args.vcf:
            print('vcf file must be given!')
            sys.exit(0)
        elif not args.group:
            print('group file must be given!')
            sys.exit(0)
        return args

    def main(self):
        args=self.getopt()
        soft=Config()
        out='%s/LD_analysis'%args.dir
        check_dir(out)
        tools=Snp2file()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                            datefmt='%Y-%m-%d  %H:%M:%S',
                            filename="%s/PrincipalComponentAnalysis.log"%out,
                            filemode='w')
        begin=show_info('############LD_analysis is start!############')
        self.PopLDdecay(tools,out,args.snp,soft.plink2genotype,soft.PopLDdecay,soft.Plot_OnePop,args.prefix,args.minInt,args.minMAF)
        self.Haploview(out,soft.haploview,args.thr,args,tools,args.memory)
        self.fst(args.vcf,args.group,out,soft.vcftools)
        run_time(begin)

class PrincipalComponentAnalysis():
    def getopt(self):
        parser = argparse.ArgumentParser(
            formatter_class=HelpFormatter, description=usages('PrincipalComponentAnalysis!'))
        parser.add_argument('func',choices=['PrincipalComponentAnalysis'])
        parser.add_argument(
            '-o', '--out', help='outdir', dest='out', type=str)
        parser.add_argument(
            '-i','--input',help='snplist file',dest='input',type=str)
        parser.add_argument(
            '-g', '--group', help='File samples div into different group like<group.txt>', dest='group', type=str)
        parser.add_argument(
            '-p','--prefix',help='the file of the transe file prefix',dest='prefix',default='pca',type=str)
        parser.add_argument(
            '-M', '--minMAF', help='minMAF<default is 0.05>', dest='minMAF', type=float,default=0.05)
        parser.add_argument(
            '-I', '--minInt', help='minInt<default is 0.5>', dest='minInt', type=float,default=0.5)
        args = parser.parse_args()
        if not args.out:
            print('outdir must be given')
            sys.exit(0)
        elif not args.input:
            print('snplist file must be given')
            sys.exit(0)
        elif not args.group:
            print('<group.txt> must be given')
            sys.exit(0)
        return args

    def TransFile(self,soft,file,outdir,maps,ped,keys,minInt,minMAF):
        begin=show_info('===== Trans snplist file to plink format is start =====')
        if check_run(maps) and check_run(ped):soft.snp2file(file,keys,minInt,minMAF,4,outdir)
        run_time(begin)

    def Analysis(self,plink,outdir,pca,pcl,gcta):
        begin=show_info('===== Calculate with Plink is start =====')
        cmd='cd %s/plink/ && %s --noweb --file pca --maf 0.05 --make-bed --out pca'%(outdir,plink)
        run_cmd(cmd)
        # if check_run(bed):run_cmd(cmd)
        cmd='cd %s/plink/ && %s --bfile pca --make-grm --out pca'%(outdir,gcta)
        run_cmd(cmd)
        cmd='cd %s/plink/ && %s --grm pca --pca 3 --out pca'%(outdir,gcta)
        run_cmd(cmd)
        # if check_run(pca) and check_run(pcl):
        #     cmd="cd %s/plink/ && %s --file pca --pca 3 --out pca --noweb"%(outdir,plink)
        #     run_cmd(cmd)
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
            w.write('\t%.2f'%(float(value)/float(all_num)))
        w.write('\nCumulative Proportion')
        s=0
        for key,value in data.items():
            s+=value/all_num
            w.write('\t%.2f'%s)
        w.close()
        run_time(begin)

    def Matrix(self,matrix,file,pca):
        tmp1=matrix+'.tmp1'
        tmp2=matrix+'.tmp2'
        cmd='echo \"Sample\tGroup\tPC1\tPC2\tPC3\" >%s && sort -k1 %s>%s && sort -k1 %s|sed \'s/ /\t/g\'|cut -f 3->%s && paste %s %s >> %s && rm -f %s %s'%(matrix,file,tmp1,pca,tmp2,tmp1,tmp2,matrix,tmp1,tmp2)
        run_cmd(cmd)

    def DrawPicture(self,outdir,R,Rscript):
        begin=show_info("===== Draw Principal Component Analysis Pictures is start =====")
        #here you can change the Rscript
        cmd='cd %s && %s %s'%(outdir,Rscript,R)
        run_cmd(cmd)
        run_time(begin)

    def nogroup_Matrix(self,outdir):
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

    def main(self):
        args=self.getopt()
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
        tools=Snp2file()
        self.TransFile(tools,args.input,out,maps,ped,args.prefix,args.minInt,args.minMAF)
        self.Analysis(soft.plink,out,pca,pcl,soft.gcta)
        self.Matrix(matrix,args.group,pca)
        self.DrawPicture(out,soft.R,soft.Rscript)
        run_time(begin)

class PopulotionStructure():
    def getopt(self):
        parser = argparse.ArgumentParser(
            formatter_class=HelpFormatter, description=usages('PopulotionStructure!'))
        parser.add_argument('func',choices=['PopulotionStructure'])
        parser.add_argument(
            '-o', '--dir', help='OutputDir  Mapping result  will in OutputDir', dest='dir',  type=str)
        parser.add_argument(
            '-i', '--input', help='Input Files of variation such like snplist', dest='input', type=str)
        parser.add_argument(
            '-p','--picture',help='chose k picture(default is all)[num|num,num|num:num:num:...]',type=str,dest='pic')
        parser.add_argument(
            '-P','--prefix',help='the file of the transe file prefix',dest='prefix',default='Structure',type=str)
        parser.add_argument(
            '-M', '--minMAF', help='minMAF<default is 0.05>', dest='minMAF', type=float,default=0.05)
        parser.add_argument(
            '-I', '--minInt', help='minInt<default is 0.5>', dest='minInt', type=float,default=0.5)
        parser.add_argument(
            '-m', '--process', help='num of process,default is 10', default=10,dest='process', type=int)
        parser.add_argument(
            '-t', '--thread', help='thread to do K Analysis,default is 3', default=3,dest='thread', type=int)
        parser.add_argument(
            '-k', '--value', help='Max K-value to run,default is 10', default=10,dest='value', type=int)
        args = parser.parse_args()
        return args

    def TransFile(self,soft,snpfile,dirs,keys,minInt,minMAF):
        begin=show_info('############Trans snplist file to Admixture format is start!#######')
        if check_run('%s/admixture/Structure.ped'%dirs):
            soft.snp2file(snpfile,keys,minInt,minMAF,8,dirs)
        run_time(begin)

    def admixture(self,pro_num,dirs,soft,ped,thr):
        begin=show_info('##########Calculate each K-value with Admixture is start!#######')
        pool=multiprocessing.Pool(processes=pro_num)
        for i in range(1,pro_num+1):
            # out='%s/admixture/Structure.%s.out'%(dirs,i)
            out='Structure.%s.out'%i
            ped=ped.strip().split('/')[-1]
            cmd="cd %s/admixture && %s --cv %s %s -j%s>%s"%(dirs,soft,ped,i,thr,out)
            pool.apply_async(run_cmd, (cmd,))
        pool.close()
        pool.join()
        run_time(begin)

    def GetAdmixture(self,Bin,indir,file,outdir,tree_bins):
        begin=show_info('##########Stat each K-value result and find the best!###########')
        admixture,samname,qsubfile=[],[],[]
        for i in glob.glob('%s/*.Q'%(indir)):
            admixture.append(i.strip())
        for line in open(file,'r'):
            #here you can change ' ' to '\t'
            # samname.append(line.strip().split(' ')[0])
            samname.append(re.split(r'\s+',line.strip())[0])
        for i in glob.glob('%s/*.out'%indir):
            qsubfile.append(i.strip())
        tree_bins.admixtureQ(admixture,samname,outdir,"Structure")
        tree_bins.value_select(qsubfile,outdir,"Structure")
        run_time(begin)

    def Result(self,Bin,outdir,best,out,svg,k_value,tree_bins):
        begin=show_info('######Find the best K and Draw Map!#######')
        tree_bins.kvalue_distr(outdir,"Structure","%s/Structure.K_value_select"%outdir)
        tree_bins.admixture_group(best,outdir)
        tree_bins.group_allk(outdir)
        k_p='-k %s'%k_value if k_value else ''
        cmd='perl %s/PopulationStructureDraw.pl -id %s -o %s/PopulotionStructure.svg -svg %s %s'%(Bin,outdir,out,svg,k_p)
        run_cmd(cmd)
        run_time(begin)

    def main(self):
        args=self.getopt()
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
                            filename="%s/PopulotionStructure.log"%out,
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
        tools=Snp2file()
        tree_bins=Tree_bin()
        self.TransFile(tools,args.input,out,args.prefix,args.minInt,args.minMAF)
        self.admixture(args.process,out,soft.admixture,ped,args.thread)
        self.GetAdmixture(Bin,out+'/admixture',ped,txt,tree_bins)
        best=glob.glob('%s/txt/*.best_k*'%out)
        self.Result(Bin,txt,best[0],out,soft.svg,args.pic,tree_bins)
        run_time(begin)
        ######################    

class PhylogeneticTree():
    def main(self):
        parser = argparse.ArgumentParser(
            formatter_class=HelpFormatter, description=usages('PhylogeneticTree!'))
        parser.add_argument('func',choices=['PhylogeneticTree'])
        parser.add_argument('-o','--dir',dest='dir',help='output dir',type=str)
        parser.add_argument('-i','--input',dest='input',help="snplist",type=str)
        parser.add_argument('-t','--type',dest='type',help="mega:0|muscle:1",type=int,default=0)
        parser.add_argument(
            '-p','--prefix',help='the file of the transe file prefix',dest='prefix',default='MultipleSequenceAlignment',type=str)
        parser.add_argument(
            '-M', '--minMAF', help='minMAF<default is 0.05>', dest='minMAF', type=float,default=0.05)
        parser.add_argument(
            '-I', '--minInt', help='minInt<default is 0.5>', dest='minInt', type=float,default=0.5)
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
        tools=Snp2file()
        if args.type==0:
            show_info('#####Trans snplist file to MEGA format is start######') 
            tools.snp2file(args.input,args.prefix,args.minInt,args.minMAF,1,out)
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

class vcf2snplist():
    def rand_select(self,file,percent,thr,ref,dep,outdir):
        for line in os.popen('wc -l %s'%file):
            total_line=int(line.split(' ')[0])
        name='_'.join(file.split('/')[-1].split('.')[:-1])
        count_all,count_i=0,0
        w=open('%s/SNPresult.txt'%outdir,'w')
        w.write('#Chr\tPos\t')
        w_i=open('%s/%s_%s.vcf'%(outdir,name,count_i),'w')
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
                    w_i=open('%s/%s_%s.vcf'%(outdir,name,count_i),'w')
                    w_i.write(line)
        w.close()
        w_i.close()
        return table_head

    def run_process(self,num,name,ref,dep,types):
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

    def merge(self,thr,name,suffix):
        w=open('SNPresult.%s'%(suffix),'a')
        for i in range(thr):
            for line in open('%s_%s.%s'%(name,i,suffix),'r'):
                w.write(line)
            os.remove('%s_%s.%s'%(name,i,suffix))
        w.close()

    def main(self):
        parser = argparse.ArgumentParser(
            formatter_class=HelpFormatter, description=usages('vcf2snplist!'))
        parser.add_argument('func',choices=['vcf2snplist'])
        parser.add_argument('-o','--dir',dest='dir',help='output dir',type=str)
        parser.add_argument('-i','--input',dest='input',help="SNP vcf file",type=str)
        parser.add_argument('-r','--ref',dest='ref',help="output ref and alt(0:no; 1:yes)",default=0,type=int)
        parser.add_argument('-d','--dep',dest='dep',help="output depth(0:no; 1:yes)",default=0,type=int)
        parser.add_argument('-s','--type',dest='type',help='type of snp(0:single base; 1:double base)',default=0,type=int)
        parser.add_argument('-t','--threading',dest='thread',help='the num of thread',type=int,default=10)
        parser.add_argument('-p','--percent',dest='perc',help='chose the random position',type=float,default=0.1)
        args=parser.parse_args()
        if not args.input:
            print('SNP vcf file must be given!')
            sys.exit(0)
        elif not args.dir:
            print('output dir must be given!')
            sys.exit(0)
        check_dir(args.dir)
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [line:%(lineno)d][%(levelname)s:] %(message)s',
                            datefmt='%Y-%m-%d  %H:%M:%S',
                            filename='%s/vcf2list.log'%args.dir,
                            filemode='w')
        run_start=show_info("===========vcf2list is start!==============")
        soft=Config()
        thr=args.thread
        name='_'.join(args.input.split('/')[-1].split('.')[:-1])
        table_head=self.rand_select(args.input,args.perc,thr,args.ref,args.dep,args.dir)
        os.chdir(args.dir)
        pool=multiprocessing.Pool(processes=thr)
        for i in range(thr):    
            pool.apply_async(self.run_process, (i,name,args.ref,args.dep,args.type,))
        pool.close()
        pool.join()
        self.merge(thr,name,"txt")
        run_time(run_start)

usage = '''
Author : chenqi
Email  : chenqi@gooalgene.com
Date   : 2018-8-15 16:16:18
Link   : 
Version: v1.0
Description:
    population resequcing!
Example:
    python %s <functions> [options]... 
<functions>
    vcf2snplist                    Transeform vcf file to snplist file
    Snp2file                       Transeform snplist to the file:mega,structure,plink...
    PhylogeneticTree               Construct Phylogenetic Tree
    PopulotionStructure            Populotion Structure computation
    PrincipalComponentAnalysis     PCA analysis
    LD_analysis                    LD analysis
''' % (__file__[__file__.rfind(os.sep) + 1:])

def main():
    if len(sys.argv)==1 or sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print(usage)
        sys.exit(0)
    if sys.argv[1]=='vcf2snplist':
        process=vcf2snplist()
        process.main()
    elif sys.argv[1]=='PhylogeneticTree':
        process=PhylogeneticTree()
        process.main()
    elif sys.argv[1]=='PopulotionStructure':
        process=PopulotionStructure()
        process.main()
    elif sys.argv[1]=='PrincipalComponentAnalysis':
        process=PrincipalComponentAnalysis()
        process.main()
    elif sys.argv[1]=='LD_analysis':
        process=LD_analysis()
        process.main()
    elif sys.argv[1]=='Snp2file':
        process=Snp2file()
        process.main()
    else:
        print('''
sorry! we didn\'t create the function now,please email to my mailbow and may be i will create it

please print \'-h\' or \'--help\' for help,chose function fitst!!!
    
    thank you so much for using it

email:chenqi@gooalgene.com
            ''')
        sys.exit(0)

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
