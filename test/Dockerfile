#this is new begin
FROM docker.io/r-base:latest

COPY ./vcftools /usr/bin/vcftools

COPY ./site_package/pip /usr/lib/python3.6/pip/

COPY ./pip /usr/bin/pip

COPY ./tree_build/ /population_analysis/

COPY ./package/ /usr/software/

RUN mv /usr/bin/python3 /usr/bin/python \
    && Rscript -e "install.packages(\"ggplot2\")" \
    && pip install matplotlib \
    && cd /usr/software \
    && tar -zxvf jre-1.8.0.tar.gz \
    && echo "export PATH=/usr/software/jre-1.8.0-openjdk-1.8.0.161-0.b14.el7_4.x86_64/bin:${PATH}">>/etc/profile \
    && tar -zxvf PopLDdecay.tar.gz \
    && tar -zxvf beagle.tar.gz \
    && tar -zxvf svg.tar.gz \
    && tar -zxvf plink.tar.gz \
    && tar -zxvf gcta.tar.gz \
    && tar -zxvf muscle.tar.gz \
    && tar -zxvf admixture.tar.gz \
    && tar -zxvf FastTree.tar.gz \
    && tar -zxvf Haploview.tar.gz \
    && rm /usr/software/*.tar.gz
