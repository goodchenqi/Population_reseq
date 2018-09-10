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
    
