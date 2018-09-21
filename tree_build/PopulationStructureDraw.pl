#!/usr/bin/perl -w
use strict;
use Getopt::Long;
use File::Basename qw(basename dirname);
############################################
my %opts;
GetOptions(\%opts,"id=s","o=s","svg=s","k=s","h");
if (!defined($opts{id})||!defined($opts{o})||!defined($opts{svg})||defined($opts{h})) {
	print << "	Usage End.";
	Usage:
		-id    in dir                     must be given
		-o     outfile_svg                must be given
		-svg   path svg                   must be given
		-k     k value(defalut is all)    num:Design the num picture
                                          	  sta,end:Design from sta to end picture 
                                          	  num:num:num:.. :Design each \'num\' picture
	Usage End.
		exit;
}
############################################
###############################################Color by Baiqi Fu 2016/7/22
my	$LightPink	="#FFB6C1";	##Ç³·Ûºì
my	$Pink	="#FFC0CB";	##·Ûºì
my	$Crimson	="#DC143C";	##ÐÉºì
my	$LavenderBlush	="#FFF0F5";	##Á³ºìµÄµ­×ÏÉ«
my	$PaleVioletRed	="#DB7093";	##²Ô°×µÄ×ÏÂÞÀ¼ºìÉ«
my	$HotPink	="#FF69B4";	##ÈÈÇéµÄ·Ûºì
my	$DeepPink	="#FF1493";	##Éî·ÛÉ«
my	$MediumVioletRed	="#C71585";	##ÊÊÖÐµÄ×ÏÂÞÀ¼ºìÉ«
my	$Orchid	="#DA70D6";	##À¼»¨µÄ×ÏÉ«
my	$Thistle	="#D8BFD8";	##¼»
my	$plum	="#DDA0DD";	##Àî×Ó
my	$Violet	="#EE82EE";	##×ÏÂÞÀ¼
my	$Magenta	="#FF00FF";	##Ñóºì
my	$Fuchsia	="#FF00FF";	##µÆÁýº£ÌÄ(×ÏºìÉ«)
my	$DarkMagenta	="#8B008B";	##ÉîÑóºìÉ«
my	$Purple	="#800080";	##×ÏÉ«
my	$MediumOrchid	="#BA55D3";	##ÊÊÖÐµÄÀ¼»¨×Ï
my	$DarkVoilet	="#9400D3";	##Éî×ÏÂÞÀ¼É«
my	$DarkOrchid	="#9932CC";	##ÉîÀ¼»¨×Ï
my	$Indigo	="#4B0082";	##µåÇà
my	$BlueViolet	="#8A2BE2";	##Éî×ÏÂÞÀ¼µÄÀ¶É«
my	$MediumPurple	="#9370DB";	##ÊÊÖÐµÄ×ÏÉ«
my	$MediumSlateBlue	="#7B68EE";	##ÊÊÖÐµÄ°åÑÒ°µÀ¶»ÒÉ«
my	$SlateBlue	="#6A5ACD";	##°åÑÒ°µÀ¶»ÒÉ«
my	$DarkSlateBlue	="#483D8B";	##ÉîÑÒ°µÀ¶»ÒÉ«
my	$Lavender	="#E6E6FA";	##Ñ¬ÒÂ²Ý»¨µÄµ­×ÏÉ«
my	$GhostWhite	="#F8F8FF";	##ÓÄÁéµÄ°×É«
my	$Blue	="#0000FF";	##´¿À¶
my	$MediumBlue	="#0000CD";	##ÊÊÖÐµÄÀ¶É«
my	$MidnightBlue	="#191970";	##ÎçÒ¹µÄÀ¶É«
my	$DarkBlue	="#00008B";	##ÉîÀ¶É«
my	$Navy	="#000080";	##º£¾üÀ¶
my	$RoyalBlue	="#4169E1";	##»Ê¾üÀ¶
my	$CornflowerBlue	="#6495ED";	##Ê¸³µ¾ÕµÄÀ¶É«
my	$LightSteelBlue	="#B0C4DE";	##µ­¸ÖÀ¶
my	$LightSlateGray	="#778899";	##Ç³Ê¯°å»Ò
my	$SlateGray	="#708090";	##Ê¯°å»Ò
my	$DoderBlue	="#1E90FF";	##µÀÆæÀ¶
my	$AliceBlue	="#F0F8FF";	##°®ÀöË¿À¶
my	$SteelBlue	="#4682B4";	##¸ÖÀ¶
my	$LightSkyBlue	="#87CEFA";	##µ­À¶É«
my	$SkyBlue	="#87CEEB";	##ÌìÀ¶É«
my	$DeepSkyBlue	="#00BFFF";	##ÉîÌìÀ¶
my	$LightBLue	="#ADD8E6";	##µ­À¶
my	$PowDerBlue	="#B0E0E6";	##»ðÒ©À¶
my	$CadetBlue	="#5F9EA0";	##¾üÐ£À¶
my	$Azure	="#F0FFFF";	##ÎµÀ¶É«
my	$LightCyan	="#E1FFFF";	##µ­ÇàÉ«
my	$PaleTurquoise	="#AFEEEE";	##²Ô°×µÄÂÌ±¦Ê¯
my	$Cyan	="#00FFFF";	##ÇàÉ«
my	$Aqua	="#00FFFF";	##Ë®ÂÌÉ«
my	$DarkTurquoise	="#00CED1";	##ÉîÂÌ±¦Ê¯
my	$DarkSlateGray	="#2F4F4F";	##ÉîÊ¯°å»Ò
my	$DarkCyan	="#008B8B";	##ÉîÇàÉ«
my	$Teal	="#008080";	##Ë®Ñ¼É«
my	$MediumTurquoise	="#48D1CC";	##ÊÊÖÐµÄÂÌ±¦Ê¯
my	$LightSeaGreen	="#20B2AA";	##Ç³º£ÑóÂÌ
my	$Turquoise	="#40E0D0";	##ÂÌ±¦Ê¯
my	$Auqamarin	="#7FFFAA";	##ÂÌÓñ\±ÌÂÌÉ«
my	$MediumAquamarine	="#00FA9A";	##ÊÊÖÐµÄ±ÌÂÌÉ«
my	$MediumSpringGreen	="#F5FFFA";	##ÊÊÖÐµÄ´ºÌìµÄÂÌÉ«
my	$MintCream	="#00FF7F";	##±¡ºÉÄÌÓÍ
my	$SpringGreen	="#3CB371";	##´ºÌìµÄÂÌÉ«
my	$SeaGreen	="#2E8B57";	##º£ÑóÂÌ
my	$Honeydew	="#F0FFF0";	##·äÃÛ
my	$LightGreen	="#90EE90";	##µ­ÂÌÉ«
my	$PaleGreen	="#98FB98";	##²Ô°×µÄÂÌÉ«
my	$DarkSeaGreen	="#8FBC8F";	##Éîº£ÑóÂÌ
my	$LimeGreen	="#32CD32";	##Ëá³ÈÂÌ
my	$Lime	="#00FF00";	##Ëá³ÈÉ«
my	$ForestGreen	="#228B22";	##É­ÁÖÂÌ
my	$Green	="#008000";	##´¿ÂÌ
my	$DarkGreen	="#006400";	##ÉîÂÌÉ«
my	$Chartreuse	="#7FFF00";	##²éÌØ¾ÆÂÌ
my	$LawnGreen	="#7CFC00";	##²ÝÆºÂÌ
my	$GreenYellow	="#ADFF2F";	##ÂÌ»ÆÉ«
my	$OliveDrab	="#556B2F";	##éÏé­ÍÁºÖÉ«
my	$Beige	="#6B8E23";	##Ã×É«(Ç³ºÖÉ«)
my	$LightGoldenrodYellow	="#FAFAD2";	##Ç³Çï÷è÷ë»Æ
my	$Ivory	="#FFFFF0";	##ÏóÑÀ
my	$LightYellow	="#FFFFE0";	##Ç³»ÆÉ«
my	$Yellow	="#FFFF00";	##´¿»Æ
my	$Olive	="#808000";	##éÏé­
my	$DarkKhaki	="#BDB76B";	##Éî¿¨Æä²¼
my	$LemonChiffon	="#FFFACD";	##ÄûÃÊ±¡É´
my	$PaleGodenrod	="#EEE8AA";	##»ÒÇï÷è÷ë
my	$Khaki	="#F0E68C";	##¿¨Æä²¼
my	$Gold	="#FFD700";	##½ð
my	$Cornislk	="#FFF8DC";	##ÓñÃ×É«
my	$GoldEnrod	="#DAA520";	##Çï÷è÷ë
my	$FloralWhite	="#FFFAF0";	##»¨µÄ°×É«
my	$OldLace	="#FDF5E6";	##ÀÏÊÎ´ø
my	$Wheat	="#F5DEB3";	##Ð¡ÂóÉ«
my	$Moccasin	="#FFE4B5";	##Â¹Æ¤Ð¬
my	$Orange	="#FFA500";	##³ÈÉ«
my	$PapayaWhip	="#FFEFD5";	##·¬Ä¾¹Ï
my	$BlanchedAlmond	="#FFEBCD";	##Æ¯°×µÄÐÓÈÊ
my	$NavajoWhite	="#FFDEAD";	##Navajo°×
my	$AntiqueWhite	="#FAEBD7";	##¹Å´úµÄ°×É«
my	$Tan	="#D2B48C";	##É¹ºÚ
my	$BrulyWood	="#DEB887";	##½áÊµµÄÊ÷
my	$Bisque	="#FFE4C4";	##(Å¨ÌÀ)ÈéÖ¬,·¬ÇÑµÈ
my	$DarkOrange	="#FF8C00";	##Éî³ÈÉ«
my	$Linen	="#FAF0E6";	##ÑÇÂé²¼
my	$Peru	="#CD853F";	##ÃØÂ³
my	$PeachPuff	="#FFDAB9";	##ÌÒÉ«
my	$SandyBrown	="#F4A460";	##É³×ØÉ«
my	$Chocolate	="#D2691E";	##ÇÉ¿ËÁ¦
my	$SaddleBrown	="#8B4513";	##Âí°°×ØÉ«
my	$SeaShell	="#FFF5EE";	##º£±´¿Ç
my	$Sienna	="#A0522D";	##»ÆÍÁô÷É«
my	$LightSalmon	="#FFA07A";	##Ç³ÏÊÈâ(öÙÓã)É«
my	$Coral	="#FF7F50";	##Éºº÷
my	$OrangeRed	="#FF4500";	##³ÈºìÉ«
my	$DarkSalmon	="#E9967A";	##ÉîÏÊÈâ(öÙÓã)É«
my	$Tomato	="#FF6347";	##·¬ÇÑ
my	$MistyRose	="#FFE4E1";	##±¡ÎíÃµ¹å
my	$Salmon	="#FA8072";	##ÏÊÈâ(öÙÓã)É«
my	$Snow	="#FFFAFA";	##Ñ©
my	$LightCoral	="#F08080";	##µ­Éºº÷É«
my	$RosyBrown	="#BC8F8F";	##Ãµ¹å×ØÉ«
my	$IndianRed	="#CD5C5C";	##Ó¡¶Èºì
my	$Red	="#FF0000";	##´¿ºì
my	$Brown	="#A52A2A";	##×ØÉ«
my	$FireBrick	="#B22222";	##ÄÍ»ð×©
my	$DarkRed	="#8B0000";	##ÉîºìÉ«
my	$Maroon	="#800000";	##ÀõÉ«
my	$White	="#FFFFFF";	##´¿°×
my	$WhiteSmoke	="#F5F5F5";	##°×ÑÌ
my	$Gainsboro	="#DCDCDC";	##Gainsboro
my	$LightGrey	="#D3D3D3";	##Ç³»ÒÉ«
my	$Silver	="#C0C0C0";	##Òø°×É«
my	$DarkGray	="#A9A9A9";	##Éî»ÒÉ«
my	$Gray	="#808080";	##»ÒÉ«
my	$DimGray	="#696969";	##°µµ­µÄ»ÒÉ«
my	$Black	="#000000";	##´¿ºÚ
#################################################################
my $colume=500;
my $x=50;
my $y=50;
my @color=($Green,$MediumBlue,$Purple,$Orange,$Red,$Yellow,$MediumVioletRed,$Orchid,$Thistle,$Tomato,$Olive,$Wheat,$Peru,$Cyan,$SkyBlue,
           $DarkMagenta,$MediumOrchid,$DarkVoilet,$DarkOrchid,$Indigo,$BlueViolet,$MediumPurple,$MediumSlateBlue,$SlateBlue,$DarkSlateBlue,$Lavender,
		   $GhostWhite,$DarkBlue,$Navy,$RoyalBlue,$HotPink,$CornflowerBlue,$LightSteelBlue,$LightSlateGray,$Violet,$SlateGray,$DoderBlue,$AliceBlue,
		   $SteelBlue,$LightSkyBlue,$Crimson,$LightBLue,$PowDerBlue,$CadetBlue,$Azure,$LightCyan,$PaleTurquoise,$Aqua,$DarkTurquoise,$DarkSlateGray,$Blue,
		   $DarkCyan,$Teal,$DeepSkyBlue,$MediumTurquoise,$DeepPink,$LightSeaGreen,$Fuchsia,$Turquoise,$Auqamarin,$MediumAquamarine,$MediumSpringGreen,$MintCream,$SpringGreen,$SeaGreen,$Honeydew,
		   $LightGreen,$PaleGreen,$LavenderBlush,$DarkSeaGreen,$LimeGreen,$Lime,$ForestGreen,$DarkGreen,$Chartreuse,$LawnGreen,$GreenYellow,$OliveDrab,$Beige,$LightGoldenrodYellow,
		   $Ivory,$LightYellow,$DarkKhaki,$Pink,$LemonChiffon,$PaleGodenrod,$MidnightBlue,$Khaki,$Gold,$Cornislk,$GoldEnrod,$FloralWhite,$OldLace,$plum,$Moccasin,
		   $PapayaWhip,$PaleVioletRed,$BlanchedAlmond,$NavajoWhite,$AntiqueWhite,$Tan,$BrulyWood,$Bisque,$DarkOrange,$Linen,$PeachPuff,$SandyBrown,$Chocolate,$SaddleBrown,$SeaShell,
		   $Sienna,$Magenta,$LightSalmon,$Coral,$OrangeRed,$DarkSalmon,$MistyRose,$Salmon,$Snow,$LightCoral,$RosyBrown,$IndianRed,$Brown,$FireBrick,$DarkRed,$Maroon,$LightPink
);
my $column=16;
# my $svg2xxx="/home/chenqi/tree_soft/software/svg/svg2xxx";
my $svg2xxx=$opts{svg};
#################
#AA      0.000   0.000   0.000   0.602   0.398
#AB      0.000   0.026   0.067   0.515   0.391
#AC      0.000   0.000   0.000   0.565   0.434
#AD      0.000   0.003   0.000   0.592   0.405
#AE      0.000   0.000   0.000   0.581   0.419
#AF      0.000   0.000   0.000   0.607   0.393
#AG      0.000   0.000   0.000   0.636   0.364
my $sample_num=0;
my $out=$opts{o};
my $in_dir=$opts{id};
my $k_picture=$opts{k};
my %strcture;
opendir(DIR,"$in_dir");
my @in_file=grep(!/^\./,readdir(DIR));
my @choice_file=grep /.txt$/,@in_file;
my $FileN=0;
if (not($k_picture)){
	foreach  my $file(sort @choice_file) {
		next if($file =~ /group/);               ## changed by Baiqi Fu2016/7/27
		$FileN++;
		open(IN,"$in_dir/$file")||die"can't open the file [$in_dir/$file]";
		while (<IN>) {
			chomp;next if (/^\</);
			my @line=split(/\s+/,$_);
			my $K_num=$#line;
			my $key="";
			for (my $i=1;$i<=$#line ;$i++) {
				$key.="$line[$i]\t";
			}
			$key=~s/\t$//;
			$strcture{$K_num}{$line[0]}{$key}=$line[0];                    
			$sample_num++ if($FileN==1);
		}
		close IN;
	}
}else{
	# if ($k_picture=!~ /\,/ || $k_picture=!~ /\:/){
	# 	print "good";
	# 	print "only \',\' and \':\' can Identification!!!";
	# 	exit();
	# 	}
	our @test= ($k_picture=~ /\,/) ? split(/\,/,$k_picture) : split(/\:/,$k_picture);
	if(@test==1){
		my @file=grep /k$test[0].txt$/,@in_file;
		$FileN++;
		open(IN,"$in_dir/$file[0]")||die"can't open the file [$in_dir/$file[0]]";
		while (<IN>) {
			chomp;next if (/^\</);
			my @line=split(/\s+/,$_);
			my $K_num=$#line;
			my $key="";
			for (my $i=1;$i<=$#line ;$i++) {
				$key.="$line[$i]\t";
			}
			$key=~s/\t$//;
			$strcture{$K_num}{$line[0]}{$key}=$line[0];                    
			$sample_num++ if($FileN==1);
		}
		close IN;
	}else{
		if ($k_picture=~ /\,/){
			for(my $sta=ord($test[0]);$sta<=ord($test[1]);$sta=$sta+1){
				my $nums_file=chr($sta);
				my @file=grep /k$nums_file.txt$/,@in_file;
				$FileN++;
				open(IN,"$in_dir/$file[0]")||die"can't open the file [$in_dir/$file[0]]";
				while (<IN>) {
					chomp;next if (/^\</);
					my @line=split(/\s+/,$_);
					my $K_num=$#line;
					my $key="";
					for (my $i=1;$i<=$#line ;$i++) {
						$key.="$line[$i]\t";
					}
					$key=~s/\t$//;
					$strcture{$K_num}{$line[0]}{$key}=$line[0];                    
					$sample_num++ if($FileN==1);
				}
				close IN;
				}
		}elsif($k_picture=~ /\:/){
			foreach my $a (sort @test){
				my @file=grep /k$a.txt$/,@in_file;
				$FileN++;
				open(IN,"$in_dir/$file[0]")||die"can't open the file [$in_dir/$file[0]]";
				while (<IN>) {
					chomp;next if (/^\</);
					my @line=split(/\s+/,$_);
					my $K_num=$#line;
					my $key="";
					for (my $i=1;$i<=$#line ;$i++) {
						$key.="$line[$i]\t";
					}
					$key=~s/\t$//;
					$strcture{$K_num}{$line[0]}{$key}=$line[0];                    
					$sample_num++ if($FileN==1);
				}
				close IN;
			}
		}
	}
}
my $num=keys %strcture;
open (OUT,">$out");
###########################start draw
my $out_svg="";
#############paper
my $width=16*$sample_num+100;
my $height=80*$num+130;
$out_svg.=&svg_paper($width,$height);
#############title
$out_svg.="\t".&svg_txt($width/2-100,50,30,$Black,"Population Structure");
my $i=0;
my %sample;
my @sample_name;
my $colum_len=16;
foreach  my $an_num(sort {$a<=>$b} keys %strcture) {
	$i++;
	my $j=0;
	my $t=0;
	$out_svg.="\t".&svg_txt($x-35,$y+80*$i-30,20,$Black,"k=$an_num");
	$out_svg.="\t".&svg_rect($x+9,$y+80*($i-1)-1+10,$colum_len*$sample_num+2,62,"none",1,"white");
	my $yset=$y+80*($i-1)-1+10;
	my @sample_popu=();
	my %column;
	foreach my $sam (keys %{$strcture{$an_num}}) {                               
		foreach my $sampopu(keys %{$strcture{$an_num}{$sam}}) {
			my @max=split(/\s+/,$sampopu);
			@max=sort{$b<=>$a}@max;
			for (my $s=0;$s<$an_num;$s++) {
				my $column=(split/\s+/,$sampopu)[$s];
				if ($column==$max[0]) {
					push @{$column{$s}},$sampopu;
				}
			}
		}
		push @sample_name,$sam;                                           
	}
	foreach  my $num(sort{$a<=>$b}keys %column) {   # $num is column num
		if ($num%2==0) {
			@{$column{$num}}=sort{(split/\s+/,$b)[$num]<=>(split/\s+/,$a)[$num]}@{$column{$num}};
		}
		else{
			@{$column{$num}}=sort{(split/\s+/,$a)[$num]<=>(split/\s+/,$b)[$num]}@{$column{$num}};
		}
#		@sample_popu=(@sample_popu,@{$column{$num}});
		@sample_popu=(@sample_popu,@{$column{$num}},"K$num");
	}

	foreach  my $popu_num(@sample_popu) {
		if ($popu_num =~ /^K/ ) 
		{
			if ($j == $sample_num) { ### remove end of black line by Baiqi Fu 2016/7/21
				next;
			}
			else{
			$out_svg .= "\t".&svg_line($x+10+$colum_len*$j,$y+80*($i-1)-1+10,$x+10+$colum_len*$j,$y+80*($i-1)-1+10+62,$Black,5);
			}
			
			next;
		}
		my @sample=split(/\t/,$popu_num);
		for (my $k=0;$k<=$#sample;$k++) {
			my $Y=0;
			my @tmp=(0,@sample);       #µÚÒ»¸öµÄ¼ä¸ô¸ß¶ÈÎªÁã
			for (my $h=0;$h<=$k ;$h++) {
				$Y+=60*$tmp[$h];
			}
			$Y=$yset+1+$Y;
			#&svg_rest(x,y,width,height,color,[stroke-width],[stroke],[opacity])
			$out_svg.="\t".&svg_rect($x+10+$colum_len*$j,$Y,$colum_len,60*$sample[$k],$color[$k],0.01,$color[$k],1);
		}
		for (my $i=0;$i<=$#sample_name;$i++){                               
			if (exists $strcture{$an_num}{$sample_name[$i]}{$popu_num}) {
				my $name=$strcture{$an_num}{$sample_name[$i]}{$popu_num};
#					$name=~s/\D+//;
				$name="000" if($name eq "");
				$out_svg.="\t".&svg_txt1($x+10+($colum_len)*$j+$colum_len/2,$yset+73,4,$Black,"$name");
				$j++;
				splice (@sample_name,$i,1);
				last;
			}
		}
	}
}

my $X;
foreach  (sort {$a<=>$b} keys %sample) {
	$X+=$sample{$_};
	#print "$X\t$colum_len\n";
	$out_svg.="\t".&svg_txt($x+10+$colum_len*($X-$sample{$_}/2),$y+80*$num+20,20,$Black,"$_");
}

#############close
$out_svg.=&svg_end;
print OUT "$out_svg";
close OUT;
my $dir = dirname "$out" ;
my $name = basename "$out" ;
`cd $dir && perl $svg2xxx -t png $name`;
`cd $dir && perl $svg2xxx -t pdf $name`;
#####################################
sub svg_txt (){#&svg_txt(x,y,size,color,text,[vertical,0/1/2/3]);
	my @svg_x=@_;
	if (!defined $svg_x[5]) {
		$svg_x[5]=0;
	}
	my $svg_matrix='';
	if ($svg_x[5]==0) {
		$svg_matrix="1 0 0 1";
	}
	if ($svg_x[5]==1) {
		$svg_matrix="0 1 -1 0";
	}
	if ($svg_x[5]==2) {
		$svg_matrix="-1 0 0 -1";
	}
	if ($svg_x[5]==3) {
		$svg_matrix="0 -1 1 0";
	}
	my $line="<text fill=\"$svg_x[3]\" transform=\"matrix($svg_matrix $svg_x[0] $svg_x[1])\" font-family=\"ArialNarrow-Bold\" font-size=\"$svg_x[2]\">$svg_x[4]</text>\n";
	return $line;
}

sub svg_txt1 (){#&svg_txt(x,y,size,color,text,[vertical,0/1/2/3]);
	my @svg_x=@_;
	if (!defined $svg_x[5]) {
		$svg_x[5]=0;
	}
	my $svg_matrix='';
	if ($svg_x[5]==0) {
		$svg_matrix="1 0 0 1";
	}
	if ($svg_x[5]==1) {
		$svg_matrix="0 1 -1 0";
	}
	if ($svg_x[5]==2) {
		$svg_matrix="-1 0 0 -1";
	}
	if ($svg_x[5]==3) {
		$svg_matrix="0 -1 1 0";
	}
	my $line="<text fill=\"$svg_x[3]\" transform=\"matrix($svg_matrix $svg_x[0] $svg_x[1])\" text-anchor=\"middle\" font-family=\"ArialNarrow-Bold\" font-size=\"$svg_x[2]\">$svg_x[4]</text>\n";
	return $line;
}

sub svg_line (){#&svg_line(x1,y1,x2,y2,color,[width])
	my @svg_x=@_;
	my $line="<line fill=\"$svg_x[4]\" stroke=\"$svg_x[4]\" x1=\"$svg_x[0]\" y1=\"$svg_x[1]\" x2=\"$svg_x[2]\" y2=\"$svg_x[3]\"/>\n";
	if (defined $svg_x[5]) {
		$line="<line fill=\"$svg_x[4]\" stroke=\"$svg_x[4]\" stroke-width=\"$svg_x[5]\" x1=\"$svg_x[0]\" y1=\"$svg_x[1]\" x2=\"$svg_x[2]\" y2=\"$svg_x[3]\"/>\n";
	}
	return $line;
}

sub svg_rect () {#&svg_rest(x,y,width,height,color,[stroke-width],[stroke],[opacity])
	my @svg_x=@_;
	if (!defined $svg_x[7]) {
		$svg_x[7]=1;
	}
	if (!defined $svg_x[6]) {
		$svg_x[6]=2;
	}
	my $line="<rect x=\"$svg_x[0]\" y=\"$svg_x[1]\" width=\"$svg_x[2]\" height=\"$svg_x[3]\" fill=\"$svg_x[4]\" stroke-width=\"$svg_x[5]\" stroke=\"$svg_x[6]\" opacity=\"$svg_x[7]\"/>\n";
	return $line;
}



sub svg_polygon () {#colorfill,colorstroke,coloropacity,point1,point2,...
	my @svg_x=@_;
	my $svg_color=shift(@svg_x);
	my $svg_color2=shift(@svg_x);
	my $svg_trans=shift(@svg_x);
	my $svg_points=join(" ",@svg_x);
	my $line="<polygon fill=\"$svg_color\" stroke=\"$svg_color2\" opacity=\"$svg_trans\" points=\"$svg_points\"/>\n";
	return $line;
}

sub svg_circle () {#&svg_circle(x,y,r,color,[info])
	my @svg_x=@_;
	my $line="<circle r=\"$svg_x[2]\" cx=\"$svg_x[0]\" cy=\"$svg_x[1]\" fill=\"$svg_x[3]\" />\n";
	if (defined $svg_x[4]) {
		$line="<circle r=\"$svg_x[2]\" cx=\"$svg_x[0]\" cy=\"$svg_x[1]\" fill=\"$svg_x[3]\" onclick=\"alert('$svg_x[4]')\" onmousemove=\"window.status='$svg_x[4]'\" />\n";
	}
	return $line;
}

sub svg_dashed (){#&svg_line(x1,y1,x2,y2,color,"10 5",[width])
	my @svg_x=@_;
	my $line="<line x1=\"$svg_x[0]\" y1=\"$svg_x[1]\" x2=\"$svg_x[2]\" y2=\"$svg_x[3]\" style=\"stroke-dasharray:$svg_x[5];fill:none;stroke:$svg_x[4]\"/>\n";
	if (defined $svg_x[6]) {
		$line="<line x1=\"$svg_x[0]\" y1=\"$svg_x[1]\" x2=\"$svg_x[2]\" y2=\"$svg_x[3]\" style=\"stroke-dasharray:$svg_x[5];fill:none;stroke:$svg_x[4];stroke-width:$svg_x[6]\"/>\n";
	}
	return $line;
}

sub svg_paper (){#&svg_paper(width,height)
	my $svg_drawer = "fubaiqi\@genoseq.cn";
	chomp $svg_drawer;
	my @svg_x=@_;
	my $line="";
	$line.="<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n";
	$line.="<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 20001102//EN\" \"http://www.w3.org/TR/2000/CR-SVG-20001102/DTD/svg-20001102.dtd\">\n\n";
	$line.="<svg width=\"$svg_x[0]\" height=\"$svg_x[1]\">\n";
	$line.="<Drawer>$svg_drawer</Drawer>\n";
	$line.="<Date>".(localtime())."</Date>\n";
	return $line;
}

sub svg_end (){#
	return "</svg>\n";
}

sub max {
	my ($x1,$x2)=@_;
	my $max;
	if ($x1 > $x2) {
		$max=$x1;
	}
	else {
		$max=$x2;
	}
	return $max;
}

sub min {
	my ($x1,$x2)=@_;
	my $min;
	if ($x1 < $x2) {
		$min=$x1;
	}
	else {
		$min=$x2;
	}
	return $min;
}
