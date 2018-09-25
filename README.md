# Population_reseq
你可以使用该脚本对重测序的vcf结果进行群体分析，有进化树分析，群体结构分析，PCA分析,LD分析，需要的软件可以直接在config脚本里面修改它的路径

usage:  

    python PopulationEvolution.py <functions> [options]...  
    
    
functions：  

    vcf2snplist                    Transeform vcf file to snplist file  
    
    Snp2file                       Transeform snplist to the file:mega,structure,plink...  
    
    PhylogeneticTree               Construct Phylogenetic Tree  
    
    PopulotionStructure            Populotion Structure computation  
    
    PrincipalComponentAnalysis     PCA analysis  
    
    LD_analysis                    LD analysis  
    

PhylogeneticTree:  

    简述：进化树分析，该步骤用于得到群体物种之间的亲缘关系  
    
    算法：距离法（聚类方法），贝叶斯法和最大似然法
    
    软件：FastTree,RAxML,SNPhylo
    
    作图：mega
    
    修图：https://itol.embl.de/login.cgi
    
PopulotionStructure:  

    简述：群体结构又称为群体分层，指所研究的群体中存在基因频率不同的亚群。其基本原理是将群体分成k个服从哈迪温伯格平衡的亚群，将每个材料归到各个亚群并计算每个材料基因组变异源于第k个亚群的可能性，主要是利用Q矩阵进行衡量，一般来说Q值越大，表明每个材料来自于某个亚群的可能性越大  
    
    软件：admixture,Structure  
    
PrincipalComponentAnalysis:  

    简述：是一种数学降维的方法，利用正交变换把一系列可能线性相关的变量转换为一组线性不相关的新变量，也叫主成分，从而利用新变量在更小的维度下展示数据的特征（https://www.plob.org/article/11869.html，详细说明）
    
    软件：gcta,plink
    
LD_analysis:  

    简述：当位于某一座位的特定等位基因与另一座位的某一等位基因同时出现的概率大于群体中因随机分布的两个等位基因同时出现的概率时，就称这两个座位处于连锁不平衡状态(http://www.sohu.com/a/234594093_761120,详细说明)
    
    软件：haploview,PopLDdecay
