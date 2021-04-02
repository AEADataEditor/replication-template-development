** Code sample with lots of missing packages

** This is a real code snippet I ran for my job- it contains the following missing packages, all of which can be found in the package_list.xlsx file

// Packages: ivreg2 ranktest ftools reghdfe hdfe parmest binscatter estout boottest acreg ivreghdfe


//Figure 3
use "$dta\states.dta", clear 
collapse (mean ) black_totalpop   ME1790_std, by (state post1690)
gen pos=12
replace pos=3 if state=="Connecticut"
replace pos=6 if state=="Massachusetts"
replace pos=3 if state=="Pennsylvania"
replace pos=6 if state=="Virginia"
replace pos=3 if state=="Delaware"
replace pos=6 if state=="South Carolina"
gen pos2=12
replace pos2=8 if state=="South Carolina"
replace pos2=3 if state=="Virginia"
replace pos2=3 if state=="Maryland"
replace pos2=4 if state=="Connecticut"
replace pos2=6 if state=="Massachusetts"
replace pos2=2 if state=="Pennsylvania"
replace pos2=12 if state=="Delaware"
 
set scheme s1mono 
twoway ///
 (qfitci black_totalpop   ME1790_std if post1690==0 , color(gs15) ) ///
(qfitci black_totalpop   ME1790_std if post1690==0 , color(gs14) level(90) ) ///
 (qfit  black_totalpop   ME1790_std if post1690==0 ,  lpattern(dash)  ) ///
 (scatter black_totalpop   ME1790_std if post1690==0, mcolor(emidblue) lcolor(black)  mlabel(state) mlabsize(*.7) msymbol(o) mlabv(pos) )  ///
 , graphregion(fcolor(white))  legend(off order()) ytitle("Blacks to Total Population %") xtitle("Malaria Stability (std)") ///
 yscale(range(-0.1(0.1) 0.7) )  ylabel( -0.1(0.1) 0.7  )   aspect(.5)  title(Before 1690)  ///
  xscale(range(-1.7(0.5) 2.7) )   
graph export "$fig/referee_graph_statenamesA.png", as(png) replace
twoway ///
 (qfitci black_totalpop   ME1790_std if post1690==1 , color(gs15) ) ///
 (qfitci black_totalpop   ME1790_std if post1690==1 , color(gs14) level(90) ) ///
 (qfit  black_totalpop   ME1790_std if post1690==1 , lpattern(dash) ) ///
 (scatter black_totalpop   ME1790_std if post1690==1,  mcolor(emidblue) lcolor(black)  mlabel(state) mlabsize(*.7) msymbol(o) mlabv(pos2) )   ///
, graphregion(fcolor(white))  legend(off order()) ytitle("Blacks to Total Population %") xtitle("Malaria Stability (std)") ///
 yscale(range(-0.1(0.1) 0.7) )  ylabel( -0.1(0.1) 0.7  )   aspect(.5)  title(After 1690) ///
  xscale(range(-1.7(0.5) 2.7) )      
graph export "$fig/referee_graph_statenamesB.png", as(png) replace



//Figure 4
use "$dta\states.dta", clear 
keep if year>=1630 & year<=1750
reghdfe black_totalpop   YEAR1_x_ME1790-YEAR5_x_ME1790 YEAR7_x_ME1790-YEAR13_x_ME1790, absorb(state_g year  ) vce(cluster state_g year)
parmest, level( 99 95) label saving("$dta/temp.dta", replace)
use "$dta/temp.dta", clear
split  parm, p(_)
keep if parm3=="ME1790"
replace label="1630" if parm1=="YEAR1"
replace label="1640" if parm1=="YEAR2"
replace label="1650" if parm1=="YEAR3"
replace label="1660" if parm1=="YEAR4"
replace label="1670" if parm1=="YEAR5"
replace label="1680" if parm1=="YEAR6"
replace label="1690" if parm1=="YEAR7"
replace label="1700" if parm1=="YEAR8"
replace label="1710" if parm1=="YEAR9"
replace label="1720" if parm1=="YEAR10"
replace label="1730" if parm1=="YEAR11"
replace label="1740" if parm1=="YEAR12"
replace label="1750" if parm1=="YEAR13"

set obs 13
replace label = "1680" in 13
replace estimate=0 if label== "1680"
replace max99=0 if label== "1680"
replace min99=0 if label== "1680"
replace max95=0 if label== "1680"
replace min95=0 if label== "1680"


destring label, replace
gen yl=0
sort label
gen n=_n
set scheme s1mono 
twoway ///
(rarea max99 min99 n, lpattern(none)  color(gs15) mcolor(emidblue))   ///
(rarea max95 min95 n, lpattern(none)  color(gs14) mcolor(emidblue))   ///
(connected estimate n , mcolor(gs3) lcolor(gs10) lpattern(dash)  lwidth(thin) msize(medium) msymbol(s)   ) ///
(scatter estimate n  if label==1680, mcolor(maroon)   msize(medium) msymbol(O)   ) ///
  ,  xline(6.5, lstyle(thin))   yline(0, lstyle(thin))  ytitle(Coefficients and Confidence Intervals) xtitle(Year) ///
xscale(range(0.5 13.5) ) ///
graphregion( color(white) ) plotregion(  fcolor(white) ) legend(off)  aspect(.5)  ///
xlabel(1 "1630" 2 "1640" 3 "1650" 4 "1660" 5 "1670" 6 "1680" 7 "1690" 8 "1700" 9 "1710" 10 "1720" 11 "1730" 12 "1740" 13 "1750")  
graph export "$fig/event_study.png", as(png) replace


////Figure 5 a
use "$dta\counties_1860.dta", clear
binscatter sine_IndianPopulation1860    MAL , nq(30) controls( $crop1860 $geo1860 ) absorb(state) xtitle(Malaria Stability (std)) ytitle(Blacks to Total Population %) savedata("$dta/temp") replace
insheet using "$dta/temp.csv", clear
set scheme s1mono 
twoway ///
(qfitci sine_indianpopulation1860    mal , color(gs15) level (95)) ///
(qfitci sine_indianpopulation1860  mal , color(gs14) level (90)) ///
(qfit sine_indianpopulation1860      mal, lcolor(black) lpattern(dash) ) ///
(scatter sine_indianpopulation1860 mal, mcolor(black) lcolor(black)  msymbol(o)) ///
, graphregion(fcolor(white))   ytitle("Native American Population") xtitle("Malaria Stability (std)") leg(off)
graph export "$fig/county1860_scatter_native.png", as(png) replace





////Figure 5 b
use "$dta\counties_18601870dif.dta", clear
binscatter delta_BlackPop18701860 delta_WhitePop18701860   MAL    , nq(30) controls( $crop1860 $geo1860 )   xtitle(Malaria Stability (std)) ytitle(Change White Pop. 1870-1860) savedata("$dta/temp") replace
insheet using "$dta/temp.csv", clear
set scheme s1mono 
twoway ///
(qfitci delta_blackpop18701860    mal , color(gs15) level (90)) ///
(qfitci delta_whitepop18701860    mal , color(gs14) level (90)) ///
(qfit delta_whitepop18701860       mal, lcolor(black) lpattern(dash) ) ///
(qfit delta_blackpop18701860     mal, lcolor(black) lpattern(dash) ) ///
(scatter  delta_blackpop18701860       mal,   mcolor(emidblue) lcolor(black)  msymbol(o) ) ///
(scatter delta_whitepop18701860    mal, mcolor(black) lcolor(black)  msymbol(o)) ///
, graphregion(fcolor(white))   ytitle("Change White/Black Pop. 1870-1860") xtitle("Malaria Stability (std)") leg(off)
graph export "$fig/county1860_scatter_delta.png", as(png) replace



********************************* Table 8 Main *********************************

use "$dta/prices.dta", clear

//main, distances, agri
eststo main_8_1: xi: reg lnpricesale2_NOATL MAL male_slave ///
    age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_8_1
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_8_1

estadd local region "Yes": main_8_1
estadd local document "Yes": main_8_1


eststo main_8_2: xi: reg lnpricesale2_NOATL MAL ///
    voy2imp male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea ///
    LANG* DOCTYPE*, cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_8_2
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_8_2

estadd local region "Yes": main_8_2
estadd local document "Yes": main_8_2


eststo main_8_3: xi: reg lnpricesale2_NOATL MAL ///
    dist_Atmark male_slave age_slave age_slavesq YEAR* ///
     BightBenin  UpperGuinea LANG* DOCTYPE*, cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_8_3
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_8_3

estadd local region "Yes": main_8_3
estadd local document "Yes": main_8_3


eststo main_8_4: xi: reg lnpricesale2_NOATL MAL landsuit ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_8_4
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_8_4

estadd local region "Yes": main_8_4
estadd local document "Yes": main_8_4


eststo main_8_5: xi: reg lnpricesale2_NOATL MAL COricep ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_8_5
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_8_5

estadd local region "Yes": main_8_5
estadd local document "Yes": main_8_5


eststo main_8_6: xi: reg lnpricesale2_NOATL MAL voy2imp ///
    dist_Atmark landsuit COricep male_slave age_slave ///
    age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_8_6
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_8_6

estadd local region "Yes": main_8_6
estadd local document "Yes": main_8_6


esttab main_8* using "$maindir$table/main_8.tex", replace ///
    keep(MAL) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) /*mymat[2](par fmt(%9.3fc))*/ ///
    se(par(( )) fmt(%9.3fc)) ) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot, ///
    labels("\textit{Bootstrap s.e. p-value}") ) ///
    prehead("\begin{threeparttable} \begin{tabular}{l cc cc cc} \hline" ///
    "\hline \noalign{\medskip} & " ///
    "\multicolumn{6}{c}{\textbf{\large{Ln(Slave Price)}}} \\" ) ///
    posthead(" & (1) & (2) & (3) & (4) & (5) & (6) \\" ///
    "\cmidrule(lr){2-7} ") ///
    prefoot("") ///
    postfoot("\\") 


esttab main_8* using "$maindir$table/main_8.tex", append ///
    keep(male_slave age_slave age_slavesq voy2imp dist_Atmark ///
    landsuit COricep) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) /*mymat[2](par fmt(%9.3fc))*/ ///
    se(par(( )) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(region document N r2 ymean, ///
    labels("\noalign{\medskip} Region \& Year FE" ///
	"Document Language \& Type FE" ///
    "\noalign{\medskip} Observations" "R-squared" "Mean Dep. Var." ) ///
    fmt(%9.2f %9.2f %9.0f %9.3f %9.3f )) ///
    prehead(" ") ///
    posthead(" ") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-7}"  ///
    "\hline  \end{tabular} \end{threeparttable}") 




********************************* Table 9 Main *********************************


use "$dta/prices.dta", clear
//other diseases
eststo main_9_1: xi: reg lnpricesale2_NOATL MAL yellowfeversuit male_slave ///
    age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_1
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_1

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_1

eststo main_9_2: xi: reg lnpricesale2_NOATL MAL glossina ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_2
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_2

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_2


//production costs
eststo main_9_3: xi: reg lnpricesale2_NOATL MAL ruggedness ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_3
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_3

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_3

eststo main_9_4: xi: reg lnpricesale2_NOATL MAL temp ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_4
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_4

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_4

//agriculture skills
eststo main_9_5: xi: reg lnpricesale2_NOATL crop1700 MAL ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_5

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_5
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_5

eststo main_9_6: xi: reg lnpricesale2_NOATL transAgri MAL ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_6
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_6

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_6

//human capital
eststo main_9_7: xi: reg lnpricesale2_NOATL lnPop1400 MAL ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_7
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_7

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_7


eststo main_9_8: xi: reg lnpricesale2_NOATL COUNTRYstateK MAL ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_8
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_8

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_8


eststo main_9_9: xi: reg lnpricesale2_NOATL COUNTRYstateK ruggedness ///
    temp crop1700 transAgr lnPop1400 glossina ///
    yellowfeversuit MAL male_slave age_slave age_slavesq YEAR*  BightBenin  ///
    UpperGuinea LANG* DOCTYPE*, cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_9_9
drop sample

local clust_se _se[MAL]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_9_9

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_9_9


label var temp "Avg. Hist. Temperature"

esttab main_9* using "$maindir$table/main_9.tex", replace ///
    keep(MAL) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) ) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(clust_se boot, ///
    labels("Cluster (s.e.)" "\textit{Bootstrap s.e. p-value}") fmt(%9.3f) ) ///
    prehead("\begin{threeparttable} \begin{tabular}{l cc cc cc cc c} \hline" ///
    "\hline \noalign{\medskip} Dependent Variable: & " ///
    "\multicolumn{9}{c}{\textbf{\large{Ln(Slave Price)}}} \\" ) ///
    posthead(" & \multicolumn{2}{c}{PANEL A}" ///
    "& \multicolumn{2}{c}{PANEL B}" ///
    "& \multicolumn{2}{c}{PANEL C}" ///
    "& \multicolumn{2}{c}{PANEL D}" ///
    "& PANEL E \\" ///
    "& \multicolumn{2}{c}{\textbf{Other Deseases}}" ///
    "& \multicolumn{2}{c}{\textbf{Production Costs}}" ///
    "& \multicolumn{2}{c}{\textbf{Agricultural Skills}}" ///
    "& \multicolumn{2}{c}{\textbf{Human Capital}}" ///
    "& \textbf{All} \\ \noalign{\smallskip}" ///
    "\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7}" ///
    "\cmidrule(lr){8-9}\cmidrule(lr){10-10} \\") ///
    prefoot("") ///
    postfoot("\\") 


esttab main_9* using "$table/main_9.tex", append ///
    keep(yellowfeversuit glossina ruggedness temp crop1700 ///yellowfeversuit glossina ruggedness
    transAgri lnPop1400 COUNTRYstateK) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) /*mymat[2](par fmt(%9.3fc))*/ ///
    se(par(( )) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(N r2 ymean, ///
    labels("\noalign{\medskip} Observations" "R-squared" "Mean Dep. Var." ) ///
    fmt(%9.0f %9.3f %9.3f )) ///
    prehead(" ") ///
    posthead(" ") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7}" ///
    "\cmidrule(lr){8-9}\cmidrule(lr){10-10}" ///
    "\hline   \end{tabular} \end{threeparttable}") 





********************************* Table 10 Main ********************************


use "$dta/prices.dta", clear

gen my_mal_var =  MAL_height 
eststo main_10_1: xi: reg lnpricesale2_NOATL my_mal_var male_slave age_slave ///
    age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE* ///
    if BIRTH_COUNTRY_height!=., cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_10_1
drop sample

local clust_se _se[my_mal_var]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_10_1

boottest my_mal_var=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_10_1


eststo main_10_2: xi: reg lnpricesale2_NOATL my_mal_var HEIGHT_precise ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE* ///
    if BIRTH_COUNTRY_height!=., cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_10_2
drop sample

local clust_se _se[my_mal_var]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_10_2

boottest my_mal_var=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_10_2

drop my_mal_var

//size

gen my_mal_var = MAL_Famine
eststo main_10_3: xi: reg lnpricesale2_NOATL my_mal_var male_slave age_slave ///
    age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE* ///
    if TWOy_Famine!=., cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_10_3
drop sample

local clust_se _se[my_mal_var]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_10_3

boottest my_mal_var=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_10_3


eststo main_10_4: xi: reg lnpricesale2_NOATL my_mal_var TWOy_Famine ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_10_4
drop sample

local clust_se _se[my_mal_var]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_10_4

boottest my_mal_var=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_10_4

drop my_mal_var


gen my_mal_var = MAL_Drought

eststo main_10_5: xi: reg lnpricesale2_NOATL my_mal_var TWOy_Drought ///
    male_slave age_slave age_slavesq YEAR*  BightBenin  UpperGuinea LANG* DOCTYPE*, ///
    cluster(country_g)

gen sample = e(sample)
qui sum lnpricesale2_NOATL 
estadd scalar ymean = r(mean) : main_10_5
drop sample

local clust_se _se[my_mal_var]
estadd local clust_se = "(`: display%4.3f `clust_se'')": main_10_5

boottest my_mal_var=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_10_5


label var my_mal_var "Malaria stability"
label var HEIGHT_precise "Slave Height (Country/Ethnic Group)"
label var TWOy_Famine "Famine in Childhood (2 Years)"
label var TWOy_Drought "Drought in Childhood (2 Years)"


esttab main_10* using "$table/main_10.tex", replace ///
    keep(my_mal_var) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) ) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(clust_se boot, ///
    labels("Cluster (s.e.)" "\textit{Bootstrap s.e. p-value}") fmt(%9.3f) ) ///
    prehead("\begin{threeparttable} \begin{tabular}{l cc cc c} \hline" ///
    "\hline \noalign{\medskip} Dependent Variable: & " ///
    "\multicolumn{5}{c}{\textbf{\large{Ln(Slave Price)}}} \\" ) ///
    posthead(" & \multicolumn{2}{c}{PANEL A}" ///
    "& \multicolumn{3}{c}{PANEL B} \\" ///
    "& \multicolumn{2}{c}{\textbf{Height}}" ///
    "& \multicolumn{3}{c}{\textbf{Body Size}} \\" ///
    "\cmidrule(lr){2-3} \cmidrule(lr){4-6} \\") ///
    prefoot("") ///
    postfoot("\\") 


esttab main_10* using "$table/main_10.tex", append ///
    keep(HEIGHT_precise TWOy_Famine TWOy_Drought ) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) /*mymat[2](par fmt(%9.3fc))*/ ///
    se(par(( )) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(N r2 ymean, ///
    labels("\noalign{\medskip} Observations" "R-squared" "Mean Dep. Var." ) ///
    fmt(%9.0f %9.3f %9.3f )) ///
    prehead(" ") ///
    posthead(" ") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-3} \cmidrule(lr){4-6}" ///
    "\hline   \end{tabular} \end{threeparttable}") 


drop my_mal_var


 


********************************* Table 1 Main *********************************

use "$dta/counties_1790.dta", clear

* Specification 1

eststo main_1_1: acreg slaveratio MAL, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_1

acreg slaveratio MAL, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_1

acreg slaveratio MAL, ///
    pfe1(state_g) dist(500) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_1


reghdfe slaveratio MAL, absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_1

qui sum slaveratio
estadd scalar ymean = r(mean) : main_1_1

estadd local crop "No": main_1_1
estadd local dist_geo "No": main_1_1
estadd local stateFE "Yes": main_1_1


* Specification 2

eststo main_1_2: acreg slaveratio MAL $crop1790, ////
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_2

acreg slaveratio MAL $crop1790, ////
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_2

acreg slaveratio MAL $crop1790, ////
    pfe1(state_g) dist(500) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_2


reghdfe slaveratio MAL $crop1790, absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_2

qui sum slaveratio
estadd scalar ymean = r(mean) : main_1_2

estadd local crop "Yes": main_1_2
estadd local dist_geo "No": main_1_2
estadd local stateFE "Yes": main_1_2


* Specification 3

eststo main_1_3: acreg slaveratio MAL $crop1790 $geo1790, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_3


acreg slaveratio MAL $crop1790 $geo1790, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_3

acreg slaveratio MAL $crop1790 $geo1790, ///
    pfe1(state_g) dist(500) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_3

reghdfe slaveratio MAL $crop1790 $geo1790, ///
    absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_3

qui sum slaveratio
estadd scalar ymean = r(mean) : main_1_3

estadd local crop "Yes": main_1_3
estadd local dist_geo "Yes": main_1_3
estadd local stateFE "Yes": main_1_3


* Specification 4

use "$dta/counties_1860.dta", clear

eststo main_1_4: acreg slaveratio MAL, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_4

acreg slaveratio MAL, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_4

acreg slaveratio MAL, ///
    pfe1(state_g) dist(500) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_4


reghdfe slaveratio MAL, absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_4

qui sum slaveratio
estadd scalar ymean = r(mean) : main_1_4

estadd local crop "No": main_1_4
estadd local dist_geo "No": main_1_4
estadd local stateFE "Yes": main_1_4


* Specification 5

eststo main_1_5: acreg slaveratio MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_5


acreg slaveratio MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_5

acreg slaveratio MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(500) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_5


reghdfe slaveratio MAL $crop1860 $geo1860, ///
    absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_5

qui sum slaveratio
estadd scalar ymean = r(mean) : main_1_5

estadd local crop "Yes": main_1_5
estadd local dist_geo "Yes": main_1_5
estadd local stateFE "Yes": main_1_5


* Specification 6

use "$dta/counties_1790.dta", clear

eststo main_1_6: acreg slaveratio MAL $crop1790 $geo1790 ///
    if slave_state==1, pfe1(state_g) dist(100) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_6


acreg slaveratio MAL $crop1790 $geo1790 ///
    if slave_state==1, pfe1(state_g) dist(250) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_6

acreg slaveratio MAL $crop1790 $geo1790 ///
    if slave_state==1, pfe1(state_g) dist(500) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_6

reghdfe slaveratio MAL $crop1790 $geo1790 ///
    if slave_state==1, absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_6

gen slaveratio_slave = slaveratio
replace slaveratio_slave = . if slave_state != 1

qui sum slaveratio_slave
estadd scalar ymean = r(mean) : main_1_6

estadd local crop "Yes": main_1_6
estadd local dist_geo "Yes": main_1_6
estadd local stateFE "Yes": main_1_6


* Specification 7

use "$dta/counties_1860.dta", clear

eststo main_1_7: acreg slaveratio MAL $crop1860 $geo1860 ///
    if slave_state==1, pfe1(state_g) dist(100) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_1_7


acreg slaveratio MAL $crop1860 $geo1860 ///
    if slave_state==1, pfe1(state_g) dist(250) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_1_7

acreg slaveratio MAL $crop1860 $geo1860 ///
    if slave_state==1, pfe1(state_g) dist(500) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

local conley_500 _se[MAL]
estadd local conley_500 = "(`: display%4.3f `conley_500'')": main_1_7

reghdfe slaveratio MAL $crop1860 $geo1860 ///
    if slave_state==1, absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_1_7

gen slaveratio_slave = slaveratio
replace slaveratio_slave = . if slave_state != 1

qui sum slaveratio_slave
estadd scalar ymean = r(mean) : main_1_7

estadd local crop "Yes": main_1_7
estadd local dist_geo "Yes": main_1_7
estadd local stateFE "Yes": main_1_7


label var MAL "Malaria Stability"


esttab main_1_* using "$table/main_1.tex", replace ///
    keep(MAL) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt(3)))  /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(conley_100 conley_250 conley_500 clust_se ///
    crop dist_geo stateFE N r2 ymean, ///
    labels("\textit{Conley s.e. 100km}" "\textit{Conley s.e. 250km}" ///
    "\textit{Conley s.e. 500km}" "\textit{State Cluster} \smallskip" ///
    "Crop Suitability" "Distances \& Geography" ///
    "State Fixed Effects \smallskip" "Observations" "R-squared" ///
    "Mean Dep. Var.") ///
    fmt(%9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.0fc %9.3f %9.3f)) ///
    prehead("\begin{threeparttable} \begin{tabular}{ l ccc cc cc } \hline" ///
    "\hline \noalign{\smallskip} Dependent Variable:" ///
    "& \multicolumn{7}{c}{\large{\textbf{Share of Slaves (\%)}}} \\")  ///
    posthead("Sample: & \multicolumn{3}{c}{\textbf{All States}} " ///
    "& \multicolumn{2}{c}{\textbf{All States}}" ///
    "& \multicolumn{2}{c}{\textbf{Slave States}} \\" ///
    "Year: & \multicolumn{3}{c}{1790} & \multicolumn{2}{c}{1860}" ///
    "& 1790 & 1860 \\" ///
    "& (1) & (2) & (3) & (4) & (5) & (6) & (7) \\" ///
    "\cmidrule(lr){2-4} \cmidrule(lr){5-6} \cmidrule(lr){7-8}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-4} \cmidrule(lr){5-6} \cmidrule(lr){7-8}" ///
    "\hline   \end{tabular} \end{threeparttable}") 




 

********************************* Table 2 Main *********************************

use "$dta/counties_1860.dta", clear

gen my_crop = .
gen my_crop_x_mal = .

* Specification 1

replace my_crop = xGinnedcotton_std
replace my_crop_x_mal = Ginnedcotton_x_x_sachsp


eststo main_2_1 :acreg slaveratio MAL my_crop ///
    my_crop_x_mal $geo1860, pfe1(state_g) dist(100) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2


estadd local crop_type = "\textbf{Cotton}": main_2_1

estadd local crop_suit = "No": main_2_1
estadd local dist = "Yes": main_2_1
estadd local stateFE = "Yes": main_2_1

qui sum slaveratio
estadd scalar ymean = r(mean) : main_2_1

acreg slaveratio MAL my_crop ///
    my_crop_x_mal $geo1860, pfe1(state_g) dist(250) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

matrix mymat = r(table)
estadd matrix mymat = mymat : main_2_1

* Specification 2

replace my_crop = GinnedcottonD
replace my_crop_x_mal = x_sachsp_std_GinnedcottonD

eststo main_2_2: acreg slaveratio MAL my_crop ///
    my_crop_x_mal $geo1860, pfe1(state_g) dist(100) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

estadd local crop_type = "\textbf{Any Cotton}": main_2_2

estadd local crop_suit = "No": main_2_2
estadd local dist = "Yes": main_2_2
estadd local stateFE = "Yes": main_2_2

qui sum slaveratio
estadd scalar ymean = r(mean) : main_2_2

acreg slaveratio MAL my_crop ///
    my_crop_x_mal $geo1860, pfe1(state_g) dist(250) ///
    latitude(lat_deg) longitude(long_deg) spatial correctr2

matrix mymat = r(table)
estadd matrix mymat = mymat : main_2_2


* Specification 3

replace my_crop = slave_crops90
replace my_crop_x_mal = slave_crops90_x_x_sachsp

eststo main_2_3: acreg slaveratio MAL ///
    my_crop my_crop_x_mal $geo1860, pfe1(state_g) ///
    dist(100) latitude(lat_deg) longitude(long_deg) spatial correctr2

estadd local crop_type = "\textbf{Labor-Intensive}": main_2_3

estadd local crop_suit = "No": main_2_3
estadd local dist = "Yes": main_2_3
estadd local stateFE = "Yes": main_2_3

qui sum slaveratio
estadd scalar ymean = r(mean) : main_2_3

acreg slaveratio MAL ///
    my_crop my_crop_x_mal $geo1860, pfe1(state_g) ///
    dist(250) latitude(lat_deg) longitude(long_deg) spatial correctr2

matrix mymat = r(table)
estadd matrix mymat = mymat : main_2_3


* Specification 4

replace my_crop = Top90Wheat
replace my_crop_x_mal = Top90Wheat_mal

eststo main_2_4: acreg slaveratio MAL my_crop ///
    my_crop_x_mal $geo1860, pfe1(state_g) dist(100) latitude(lat_deg) ///
    longitude(long_deg) spatial correctr2

estadd local crop_type = "\textbf{Wheat}": main_2_4

estadd local crop_suit = "No": main_2_4
estadd local dist = "Yes": main_2_4
estadd local stateFE = "Yes": main_2_4

qui sum slaveratio
estadd scalar ymean = r(mean) : main_2_4

acreg slaveratio MAL my_crop ///
    my_crop_x_mal $geo1860, pfe1(state_g) dist(250) latitude(lat_deg) ///
    longitude(long_deg) spatial correctr2

matrix mymat = r(table)
estadd matrix mymat = mymat : main_2_4


* Specification 5

use "$dta/americas.dta", clear

eststo main_2_5: reghdfe coloredratio MAL, noabsorb vce(robust) 

estadd local crop_suit = "No": main_2_5
estadd local dist = "No": main_2_5
estadd local stateFE = "No": main_2_5

qui sum coloredratio
estadd scalar ymean = r(mean) : main_2_5


* Specification 6

eststo main_2_6: reghdfe coloredratio MAL $crop1860 $geo1860_2, ///
    absorb(country) vce(robust) 

estadd local crop_suit = "Yes": main_2_6
estadd local dist = "Yes": main_2_6
estadd local stateFE = "Yes": main_2_6

qui sum coloredratio
estadd scalar ymean = r(mean) : main_2_6


* Table Part 1

label var MAL "Malaria Stability"

esttab main_2* using "$maindir$table/main_2.tex", replace ///
    keep(MAL) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt(3)) se(par fmt(3)) mymat[2](par([ ]) fmt(3)) )  /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(crop_type, labels("Type of Crop:")) ///
    prehead("\begin{threeparttable} \begin{tabular}{m{0.25\textwidth}" ///
    "m{0.1\textwidth}<{\centering} m{0.1\textwidth}<{\centering}" ///
    "m{0.1\textwidth}<{\centering} m{0.1\textwidth}<{\centering}" ///
    "m{0.08\textwidth}<{\centering} m{0.08\textwidth}<{\centering}}" ) ///
    posthead("\hline \hline \noalign{\medskip} \smallskip" ///
    "& \multicolumn{4}{c}{\large{Panel A}} " ///
    "& \multicolumn{2}{c}{\large{Panel B}} \\" ///
    "Sample: & \multicolumn{4}{c}{United States, Counties 1860}" ///
    "& \multicolumn{2}{c}{US, Brazil, Cuba} \\" ///
    " & \multicolumn{4}{c}{All Counties}" ///
    "& \multicolumn{2}{c}{States/Provinces} \\" ///
    "Dependent Variable: & " ///
    "\multicolumn{4}{c}{\textbf{\% Slaves}}" ///
    "& \multicolumn{2}{c}{\textbf{\% Blacks 1872}} \\" ///
    "\cmidrule(lr){2-5} \cmidrule(lr){6-7} \smallskip" ) ///
    prefoot("") ///
    postfoot(" ") 


* Table Part 2
esttab main_2* using "$table/main_2.tex", append ///
    keep(my_crop my_crop_x_mal) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt(3)) se(par fmt(3)) )  /// 
    label nomtitles nonumbers collabels(,none) ///
    coeflabels(my_crop "Crops" ///
    my_crop_x_mal "Crops $\times$ Malaria Stability") ///
    stats(crop_suit dist stateFE N r2 ymean, ///
    labels("\noalign{\smallskip}Crop Suitability" ///
    "Distances \& Geography" "State Fixed Effects" ///
    "\smallskip Observations" "R-squared" "Mean Dep. Var.") ///
    fmt(%9.2f %9.2f %9.3f %9.0fc %9.3f %9.3f )) ///
    prehead(" ") posthead(" ") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-5} \cmidrule(lr){6-7} " ///
    "\hline \end{tabular} \end{threeparttable}") 



 

********************************* Table 3 Main *********************************

* Specification 1

use "$dta/county_convention.dta", clear

eststo main_3_1: acreg proslavery MAL $crop1860 $geo1860 , ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_3_1

qui sum proslavery
estadd scalar ymean = r(mean) : main_3_1

acreg proslavery MAL $crop1860 $geo1860 , ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_3_1

xi: reg proslavery MAL $crop1860 $geo1860 i.state_g, cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_3_1

estadd local crop "Yes": main_3_1
estadd local dist_geo "Yes": main_3_1
estadd local stateFE "Yes": main_3_1
estadd local voteFE "No": main_3_1


* Specification 2

eststo main_3_2: xi: acreg proslavery MAL $crop1860 $geo1860 ///
    i.vote, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_3_2

qui sum proslavery
estadd scalar ymean = r(mean) : main_3_2

xi: acreg proslavery MAL $crop1860 $geo1860 i.vote, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_3_2

xi: reg proslavery MAL $crop1860 $geo1860 i.state_g i.vote, ///
   cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_3_2

estadd local crop "Yes": main_3_2
estadd local dist_geo "Yes": main_3_2
estadd local stateFE "Yes": main_3_2
estadd local voteFE "Yes": main_3_2



* Specification 3
use "$dta/county_votes.dta", clear

eststo main_3_3: acreg vote1860_rep_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_3_3

qui sum vote1860_rep_pres
estadd scalar ymean = r(mean) : main_3_3

acreg vote1860_rep_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_3_3

reghdfe vote1860_rep_pres MAL $crop1860 $geo1860, ///
    absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_3_3

estadd local crop "Yes": main_3_3
estadd local dist_geo "Yes": main_3_3
estadd local stateFE "Yes": main_3_3


* Specification 4

eststo main_3_4: acreg vote1860_demeq_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_3_4

qui sum vote1860_demeq_pres
estadd scalar ymean = r(mean) : main_3_4


acreg vote1860_demeq_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_3_4


reghdfe vote1860_demeq_pres MAL $crop1860 $geo1860, ///
    absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_3_4

estadd local crop "Yes": main_3_4
estadd local dist_geo "Yes": main_3_4
estadd local stateFE "Yes": main_3_4



* Specification 5

eststo main_3_5: acreg vote1868_rep_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_3_5

qui sum vote1868_rep_pres
estadd scalar ymean = r(mean) : main_3_5

acreg vote1868_rep_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_3_5


reghdfe vote1868_rep_pres MAL $crop1860 $geo1860, ///
    absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_3_5


estadd local crop "Yes": main_3_5
estadd local dist_geo "Yes": main_3_5
estadd local stateFE "Yes": main_3_5



* Specification 6

eststo main_3_6: acreg vote1868_dem_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(100) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_100 _se[MAL]
estadd local conley_100 = "(`: display%4.3f `conley_100'')": main_3_6

qui sum vote1868_dem_pres
estadd scalar ymean = r(mean) : main_3_6

acreg vote1868_dem_pres MAL $crop1860 $geo1860, ///
    pfe1(state_g) dist(250) latitude(lat_deg) longitude(long_deg) ///
    spatial correctr2

local conley_250 _se[MAL]
estadd local conley_250 = "[`: display%4.3f `conley_250'']": main_3_6


reghdfe vote1868_dem_pres MAL $crop1860 $geo1860, ///
    absorb(state_g) cluster(state_g)

local clust_se _se[MAL]
estadd local clust_se = "\{`: display%4.3f `clust_se''\}": main_3_6


estadd local crop "Yes": main_3_6
estadd local dist_geo "Yes": main_3_6
estadd local stateFE "Yes": main_3_6


* Table

label var MAL "Malaria Stability"

esttab main_3* using "$table/main_3.tex", replace ///
    keep(MAL) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt(3)))  /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(conley_100 conley_250 clust_se crop dist_geo stateFE voteFE N r2 ///
    ymean, ///
    labels("\textit{Conley s.e. 100 km}" "\textit{Conley s.e. 250 km}" ///
    "\textit{State Cluster} \medskip" "Crop Suitablitiy" ///
    "Distances and Geography" "State Fixed Effects" ///
    "Vote Fixed Effects \medskip" ///
    "Observations" "R-squared" "Mean Dep. Var") ///
    fmt(%9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.2f %9.0fc %9.3f %9.3f)) ///
    prehead("\begin{threeparttable} \begin{tabular}{ l cc cccc } \hline" ///
    "\hline \noalign{\smallskip}" ///
    "& \multicolumn{2}{c}{\textbf{Constitutional Convention}}" ///
    "& \multicolumn{4}{c}{\textbf{Presidential Elections}} \\")  ///
    posthead("& \multicolumn{2}{c}{1787} & \multicolumn{2}{c}{1860} " ///
    "& \multicolumn{2}{c}{1868} \\" ///
    "& \multicolumn{2}{c}{Pro-Slavery Votes} & Lincoln & Breckinridge " ///
    "& Grant & Seymour \\" ///
    "& (1) & (2) & (3) & (4) & (5) & (6)  \\" ///
    "\cmidrule(lr){2-3} \cmidrule(lr){4-7} ") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-3} \cmidrule(lr){4-7} " ///
    "\hline  \end{tabular} \end{threeparttable}") 

 
 
 

********************************* Table 5 Main *********************************

use "$dta/states.dta", clear
 

 
* Specification 1

eststo main_5_1: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    if year<=1750, absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_5_1
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_1

reghdfe black_totalpop mal1690_x_ME1790_std ///
    if year<=1750, absorb(state_g year) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_1

estadd local decade "Yes": main_5_1
estadd local state "Yes": main_5_1


*Specification 2

eststo main_5_2: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    if year>=1650 & year<=1720, absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_5_2
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_2

reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    if year>=1650 & year<=1720, absorb(state_g) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_2

estadd local decade "Yes": main_5_2
estadd local state "Yes": main_5_2


*Specification 3

eststo main_5_3: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    if state!="South Carolina" & year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_5_3
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_3

reghdfe black_totalpop mal1690_x_ME1790_std ///
    if state!="South Carolina" & year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_3

estadd local decade "Yes": main_5_3
estadd local state "Yes": main_5_3


*Specification 4

eststo main_5_4: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    if state!="Virginia" & year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_5_4
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_4

reghdfe black_totalpop mal1690_x_ME1790_std ///
    if state!="Virginia" & year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_4

estadd local decade "Yes": main_5_4
estadd local state "Yes": main_5_4


* Specification 5

eststo main_5_5: reghdfe Dblack_totalpop mal1690_x_ME1790_std i.year ///
    if year<=1750, absorb(state_g) vce(cluster state_g year) 

gen sample = e(sample)
qui sum Dblack_totalpop if sample==1
estadd scalar ymean = r(mean) : main_5_5
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_5

reghdfe Dblack_totalpop mal1690_x_ME1790_std ///
    if year<=1750, absorb(state_g year) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_5

estadd local decade "Yes": main_5_5
estadd local state "Yes": main_5_5


* Specification 6

eststo main_5_6: reghdfe Dblack mal1690_x_ME1790_std i.year ///
    if year<=1750, absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum Dblack if sample==1
estadd scalar ymean = r(mean) : main_5_6
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_6

reghdfe Dblack mal1690_x_ME1790_std i.year ///
    if year<=1750, absorb(state_g) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_6

estadd local decade "Yes": main_5_6
estadd local state "Yes": main_5_6


* Specification 7

eststo main_5_7: reghdfe Dwhite mal1690_x_ME1790_std i.year ///
    if year<=1750, absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum Dwhite if sample==1
estadd scalar ymean = r(mean) : main_5_7
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_5_7

reghdfe Dwhite mal1690_x_ME1790_std ///
    if year<=1750, absorb(state_g year) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_5_7

estadd local decade "Yes": main_5_7
estadd local state "Yes": main_5_7


* Table

label var mal1690_x_ME1790_std "Malaria Stability $\times$ Post-1690"

esttab main_5* using "$table/main_5.tex", replace ///
    keep(mal1690_x_ME1790_std) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc %9.2f %9.0fc %9.3f %9.3f)) mymat[2](par fmt(%9.3fc)) se(par([ ]) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot decade state N r2 N_clust ymean, ///
    labels("\textit{Bootstrap s.e. p-value} \medskip" ///
    "Decade Fixed Effects" ///
    "State Fixed Effects \smallskip" "Observations" "R-squared" ///
    "Number of States" "Mean Dep. Var.") ///
    fmt(%9.2f %9.2f %9.2f %9.0f %9.3f %9.0f %9.3f)) ///
    prehead("\begin{threeparttable} \begin{tabular}{ l ccc cc cc } \hline" ///
    "\hline \noalign{\smallskip} Dependent Variable:" ///
    "& \multicolumn{4}{c}{\large{\textbf{Share of Blacks}}}" ///
    "& \textbf{$\Delta$ Sh. Blacks} & \textbf{$\Delta$ Blacks}" ///
    "& \textbf{$\Delta$ Whites}  \\")  ///
    posthead("& \multicolumn{2}{c}{All Sample} " ///
    "& No South  & No & All Sample & All Sample & All Sample \\" ///
    "& 1630-1750 & 1650-1720 & Carolina & Virginia & 1630-1750 & 1630-1750" ///
    "& 1630-1750 \\" ///
    "& (1) & (2) & (3) & (4) & (5) & (6) & (7) \\" ///
    "\cmidrule(lr){2-5} \cmidrule(lr){6-8}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-5} \cmidrule(lr){6-8}" ///
    " \hline \end{tabular} \end{threeparttable}") 






********************************* Table 6 Main *********************************


use "$dta/states_short.dta", clear 

* Panel A

* Specification a1

eststo main_6_a1: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    mal1690_x_rice1790_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a1
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a1

reghdfe black_totalpop mal1690_x_ME1790_std ///
    mal1690_x_rice1790_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a1

estadd local control "Rice Suit $ \times$ Post-1690": main_6_a1

* Specification a2

eststo main_6_a2: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    mal1690_x_tobacco1790_std  if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a2
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a2

reghdfe black_totalpop mal1690_x_ME1790_std ///
    mal1690_x_tobacco1790_std  if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a2

estadd local control "Tobacco Suit $ \times$ Post-1690": main_6_a2


* Specification a3

eststo main_6_a3: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    mal1690_x_rice1790_std mal1690_x_tobacco1790_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a3
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a3

reghdfe black_totalpop mal1690_x_ME1790_std ///
    mal1690_x_rice1790_std mal1690_x_tobacco1790_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a3

estadd local control "Rice \& Tob. Suit $ \times$ Post-1690": main_6_a3


* Specification a4

eststo main_6_a4: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Ydum*_x_rice1790_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a4
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a4

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Ydum*_x_rice1790_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a4

estadd local control "Rice Suit $ \times$ Decade FE": main_6_a4


* Specification a5

eststo main_6_a5: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Ydum*_x_tobacco1790_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a5
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a5

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Ydum*_x_tobacco1790_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a5

estadd local control "Tobacco Suit $ \times$ Decade FE": main_6_a5


* Specification a6

eststo main_6_a6: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Ydum*_x_rice1790_std Ydum*_x_tobacco1790_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a6
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a6

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Ydum*_x_rice1790_std Ydum*_x_tobacco1790_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a6

estadd local control "Rice \& Tob. Suit $ \times$ Decade FE": main_6_a6


* Specification a7

eststo main_6_a7: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Sdum*_x_Riceprice Sdum*_x_tobaccoprice if year<=1750, ///
    absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_a7
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_a7

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Sdum*_x_Riceprice Sdum*_x_tobaccoprice if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_a7

estadd local control ///
    "Rice \& Tob. Prices $ \times$ State FE": main_6_a7


* Table

label var mal1690_x_ME1790_std "Malaria Stability $\times$ Post-1690"

esttab main_6_a* using "$table/main_6.tex", replace ///
    keep(mal1690_x_ME1790_std) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) mymat[2](par fmt(%9.3fc)) ///
    se(par([ ]) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot control N r2 ymean, ///
    labels("\textit{Bootstrap s.e. p-value} \medskip" ///
    "\cmidrule(lr){2-8} Controls: \smallskip" "Observations" "R-squared" ///
    "Mean Dep. Var.") ///
    fmt(%9.2f %9.2f %9.0f %9.3f %9.3f)) ///
    prehead("\begin{threeparttable} \begin{tabular}{m{0.25\textwidth}" ///
    "m{0.085\textwidth}<{\centering} m{0.085\textwidth}<{\centering}" ///
    "m{0.085\textwidth}<{\centering} m{0.085\textwidth}<{\centering}" ///
    "m{0.085\textwidth}<{\centering} m{0.085\textwidth}<{\centering}" ///
    "m{0.085\textwidth}<{\centering}} \hline" ///
    "\hline \noalign{\smallskip} Dependent Variable:  &" ///
    "\multicolumn{7}{c}{\large{\textbf{Share of Blacks}}} \\") ///
    posthead("\cmidrule(lr){2-8} &" ///
    "\multicolumn{7}{c}{\textbf{PANEL A: CROPS}} \\" ///
    "& (1) & (2) & (3) & (4) & (5) & (6) & (7) \\" ///
    "\cmidrule(lr){2-8}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-8}") 



* Panel B

* Specification b1

eststo main_6_b1: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    yellow_fever if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b1
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b1

reghdfe black_totalpop mal1690_x_ME1790_std ///
    yellow_fever if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b1

estadd local control "Yellow Fever": main_6_b1


* Specification b2

eststo main_6_b2: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    mal1690_x_aedes_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b2
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b2

reghdfe black_totalpop mal1690_x_ME1790_std ///
    mal1690_x_aedes_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b2

estadd local control "Yellow Fever $ \times$ Post-1690": main_6_b2


* Specification b3

eststo main_6_b3: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Ydum*_x_temp50_std if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b3
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b3

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Ydum*_x_temp50_std if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b3

estadd local control "Temp $ \times$ Decade FE": main_6_b3


* Specification b4

eststo main_6_b4: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    black_totalpop1680_post1690 if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b4
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b4

reghdfe black_totalpop mal1690_x_ME1790_std ///
    black_totalpop1680_post1690 if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b4

estadd local control "Sh. Black 1680 $ \times$ Post-1690": main_6_b4


* Specification b5

eststo main_6_b5: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Sdum*_x_wage_eng if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b5
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b5

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Sdum*_x_wage_eng if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b5

estadd local control "English Farm Wage $ \times$ State FE": main_6_b5


* Specification b6

eststo main_6_b6: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    servant_revolt if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b6
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b6

reghdfe black_totalpop mal1690_x_ME1790_std ///
    servant_revolt if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b6

estadd local control "Servants Revolts": main_6_b6


* Specification b7

eststo main_6_b7: reghdfe black_totalpop mal1690_x_ME1790_std i.year ///
    Ydum*_x_South_Nantucket if year<=1750, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_b7
drop sample

boottest mal1690_x_ME1790_std=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_b7

reghdfe black_totalpop mal1690_x_ME1790_std ///
    Ydum*_x_South_Nantucket if year<=1750, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_b7

estadd local control "South Nantucket $ \times$ Decade FE": main_6_b7


* Table

esttab main_6_b* using "$table/main_6.tex", append ///
    keep(mal1690_x_ME1790_std) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) mymat[2](par fmt(%9.3fc)) ///
    se(par([ ]) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot control N r2 ymean, ///
    labels("\textit{Bootstrap s.e. p-value} \medskip" ///
    "\cmidrule(lr){2-8} Controls: \smallskip" "Observations" "R-squared" ///
    "Mean Dep. Var.") ///
    fmt(%9.2f %9.2f %9.0f %9.3f %9.3f)) ///
    prehead(" ") ///
    posthead( ///
    "& \multicolumn{7}{c}{\textbf{PANEL B: OTHER CONTROLS}} \\" ///
    "& (1) & (2) & (3) & (4) & (5) & (6) & (7) \\" ///
    "\cmidrule(lr){2-8}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-8}") 



* Panel C

use "$dta/states_short.dta", clear 

global tdums = "Ydum1 Ydum2 Ydum3 Ydum4 Ydum5 Ydum6 Ydum7 Ydum8 Ydum9 Ydum10 Ydum11 Ydum12 Ydum13 "  
global sdums = "Sdum1 Sdum2  Sdum5 Sdum6 Sdum7 Sdum8 Sdum9 Sdum10 Sdum11 Sdum12  "  
global linear = "  Sdum2_x_t Sdum3_x_t Sdum4_x_t Sdum5_x_t Sdum6_x_t Sdum7_x_t Sdum8_x_t Sdum9_x_t Sdum10_x_t Sdum11_x_t Sdum12_x_t  "  
global quadratic = "  Sdum2_x_tsq Sdum3_x_tsq Sdum4_x_tsq Sdum5_x_tsq Sdum6_x_tsq Sdum7_x_tsq Sdum8_x_tsq Sdum9_x_tsq Sdum10_x_tsq Sdum11_x_tsq Sdum12_x_tsq  "  
global crops = "Ydum*_x_rice1790_std Ydum*_x_tobacco1790_std Sdum*_x_Riceprice Sdum*_x_tobaccoprice"  
global geo = "  Ydum*_x_South_Nantucket Ydum*_x_aedes_std Ydum*_x_temp50_std"  
global all = " Ydum*_x_rice1790_std Ydum*_x_tobacco1790_std Sdum*_x_Riceprice Sdum*_x_tobaccoprice Ydum*_x_South_Nantucket yellow_fever Ydum*_x_aedes_std Ydum*_x_temp50_std Sdum*_x_wage_eng servant_revolt black_totalpop1680_post1690"  
gen MAL=mal1690_x_ME1790_std

//sum   `crops'
reghdfe black_totalpop MAL $all, ///
    absorb(state_g year) vce(cluster state_g year) 
gen sample_all=e(sample)
keep if sample_all==1

//crops lasso  
lassoShooting black_totalpop $crops $linear $quadratic, ///
    controls($tdums $sdums) lasiter(100) verbose(1) fdisplay(1)
local yvSel `r(selected)'   
di "`yvSel'"  
lassoShooting MAL $crops $linear  $quadratic, ///
    controls($tdums $sdums) lasiter(100) verbose(1) fdisplay(1)  
local xvSel `r(selected)'   
di "`xvSel'" 
local list_crops : list yvSel | xvSel
global lasso_crops "`list_crops'" 


//1
eststo main_6_c1: reghdfe black_totalpop MAL i.year if sample_all==1, ///
    absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c1
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c1

reghdfe black_totalpop MAL if sample_all==1, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c1

estadd local type "Baseline": main_6_c1
estadd local decade "Yes": main_6_c1
estadd local state "Yes": main_6_c1


//2
eststo main_6_c2: reghdfe black_totalpop MAL `list_crops' i.year ///
    if sample_all==1, absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c2
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c2

reghdfe black_totalpop MAL `list_crops' i.year if sample_all==1, ///
    absorb(state_g ) vce(cluster state_g year ) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c2

estadd local type "LASSO": main_6_c2
estadd local control "Crops": main_6_c2
estadd local trend "Yes": main_6_c2
estadd local decade "Yes": main_6_c2
estadd local state "Yes": main_6_c2


//3
pca $crops $linear  $quadratic
predict pca_crops  
eststo main_6_c3: reghdfe black_totalpop MAL pca_crops i.year ///
    if sample_all==1, absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c3
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c3

reghdfe black_totalpop MAL pca_crops if sample_all==1, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c3

estadd local type "PCA": main_6_c3
estadd local control "Crops": main_6_c3
estadd local trend "Yes": main_6_c3
estadd local decade "Yes": main_6_c3
estadd local state "Yes": main_6_c3


//4
lassoShooting black_totalpop $geo $linear $quadratic if sample_all==1, ///
    controls($tdums $sdums) lasiter(100) verbose(1) fdisplay(1)  
local yvSel `r(selected)'   
di "`yvSel'"  
lassoShooting MAL $geo $linear $quadratic if sample_all==1, ///
    controls($tdums $sdums) lasiter(100) verbose(1) fdisplay(1)  
local xvSel `r(selected)'   
di "`xvSel'" 
local list_geo : list yvSel | xvSel
global lasso_crops "`xvSel'" 
eststo main_6_c4: reghdfe black_totalpop MAL `list_geo' i.year ///
    if sample_all==1, absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c4
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c4

reghdfe black_totalpop MAL `list_geo' if sample_all==1, ///
    absorb(state_g year) vce(cluster state_g year)

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c4

estadd local type "LASSO": main_6_c4
estadd local control "Geo": main_6_c4
estadd local trend "Yes": main_6_c4
estadd local decade "Yes": main_6_c4
estadd local state "Yes": main_6_c4


//5
pca $geo 
predict pca_geo  

eststo main_6_c5: reghdfe black_totalpop MAL pca_geo i.year ///
    if sample_all==1, absorb(state_g) vce(cluster state_g ) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c5
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c5

reghdfe black_totalpop MAL pca_geo if sample_all==1, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c5

estadd local type "PCA": main_6_c5
estadd local control "Geo": main_6_c5
estadd local trend "Yes": main_6_c5
estadd local decade "Yes": main_6_c5
estadd local state "Yes": main_6_c5


//6
lassoShooting black_totalpop $all $linear $quadratic, ///
    controls($tdums $sdums) lasiter(100) verbose(1) fdisplay(1)  
local yvSel `r(selected)'   
di "`yvSel'"  
lassoShooting MAL $all $linear $quadratic, ///
    controls($tdums $sdums) lasiter(100) verbose(1) fdisplay(1)  
local xvSel `r(selected)'   
di "`xvSel'" 
local list_all : list yvSel | xvSel
global lasso_crops "`xvSel'" 

eststo main_6_c6: reghdfe black_totalpop MAL `list_all' i.year ///
    if sample_all==1, absorb(state_g) vce(cluster state_g  ) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c6
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c6

reghdfe black_totalpop MAL `list_all' if sample_all==1, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c6

estadd local type "LASSO": main_6_c6
estadd local control "All": main_6_c6
estadd local trend "Yes": main_6_c6
estadd local decade "Yes": main_6_c6
estadd local state "Yes": main_6_c6


//7
pca $all
predict pca_all 
eststo main_6_c7: reghdfe black_totalpop MAL pca_all i.year ///
    if sample_all==1, absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_6_c7
drop sample

boottest MAL=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_6_c7

reghdfe black_totalpop MAL pca_all if sample_all==1, ///
    absorb(state_g year) vce(cluster state_g year) 

matrix mymat = r(table)
estadd matrix mymat = mymat : main_6_c7

estadd local type "PCA": main_6_c7
estadd local control "All": main_6_c7
estadd local trend "Yes": main_6_c7
estadd local decade "Yes": main_6_c7
estadd local state "Yes": main_6_c7

 

*Table

label var MAL "Malaria Stability $\times$ Post-1690"

esttab main_6_c* using "$table/main_6.tex", append ///
    keep(MAL) starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) mymat[2](par fmt(%9.3fc)) ///
    se(par([ ]) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot type control trend N r2 ymean N_clust decade state, ///
    labels("\textit{Bootstrap s.e. p-value} \medskip" ///
    "\cmidrule(lr){2-2} \cmidrule(lr){3-8}  " ///
    "LASSO \& PCA Controls: \smallskip" "Linear \& Quadratic Trend" ///
    "Observations" "R-squared" ///
    "Mean Dep. Var." ///
    "\cmidrule(lr){2-2} \cmidrule(lr){3-8} \noalign{\bigskip} Number of States" ///
    "Decade Fixed Effects" "State Fixed Effects") ///
    fmt(%9.2f %9.2f %9.2f %9.2f %9.0f %9.3f %9.3f %9.0f)) ///
    prehead(" ") ///
    posthead( ///
    "& \multicolumn{7}{c}{\textbf{PANEL C: ALL CONTROLS - LASSO AND PCA}}\\" ///
    "& (1) & (2) & (3) & (4) & (5) & (6) & (7) \\" ///
    "\cmidrule(lr){2-2} \cmidrule(lr){3-8}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-8}" ///
    "\hline  \end{tabular} \end{threeparttable}") 


 

********************************* Table 7 Main *********************************


use "$dta/mortality.dta", clear
 


* Panels A and B
* Specification 1

label var ME_std_x_elnino "Malaria Stability $ \times$ \# El Ni\~no Events"


eststo main_7_a1: xi: reg malaria_all_100 ME_std_x_elnino i.state_short ///
    i.year, cluster(state_short)

qui sum malaria_all_100 if sample==1
estadd scalar ymean = r(mean) : main_7_a1

boottest ME_std_x_elnino=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_a1

estadd local state "Yes": main_7_a1
estadd local year "Yes": main_7_a1


eststo main_7_a2: xi: reg malaria_all_100 ME_std_x_elnino ///
    rice1790_std_x_elnino i.state_short i.year, cluster(state_short)

qui sum malaria_all_100 if sample==1
estadd scalar ymean = r(mean) : main_7_a2

boottest ME_std_x_elnino=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_a2

estadd local state "Yes": main_7_a2
estadd local year "Yes": main_7_a2


use "$dta/states.dta", clear

 
eststo main_7_b1: reghdfe endemic_falciparum ME_std_x_elnino i.year, ///
    absorb(state_g) vce(cluster state_g )

boottest ME_std_x_elnino=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_b1

gen sample = e(sample)
qui sum endemic_falciparum if sample==1
estadd scalar ymean = r(mean) : main_7_b1
drop sample

estadd local state "Yes": main_7_b1
estadd local year "Yes": main_7_b1


eststo main_7_b2: reghdfe endemic_falciparum ME_std_x_elnino ///
    rice1790_std_x_elnino i.year, absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum endemic_falciparum if sample==1
estadd scalar ymean = r(mean) : main_7_b2
drop sample

boottest ME_std_x_elnino=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_b2

estadd local state "Yes": main_7_b2
estadd local year "Yes": main_7_b2

label var ME_std_x_elnino "Malaria Stability $ \times$ \# El Ni\~no Events"
label var rice1790_std_x_elnino "Rice Suit. $ \times$ \# El Ni\~no Events"

esttab main_7_a* main_7_b* using "$table/main_7.tex", replace ///
    keep(ME_std_x_elnino rice1790_std_x_elnino) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) /*mymat[2](par fmt(%9.3fc))*/ ///
    se(par(( )) fmt(%9.3fc)) ) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot state year N r2 ymean, ///
    labels("\textit{Bootstrap s.e. p-value}" ///
    "\noalign{\smallskip} State Fixed Effects" ///
    "Year Fixed Effects" "Observations" "R-squared" ///
    "Mean Dep. Var.") ///
    fmt(%9.2f %9.2f %9.2f %9.0f %9.3f %9.3f)) ///
    prehead("\begin{threeparttable} \begin{tabular}{l cc cc} \hline" ///
    "\hline \noalign{\medskip} & \multicolumn{2}{c}{PANEL A}" ///
    " & \multicolumn{2}{c}{PANEL B} \\" ///
    "& \multicolumn{2}{c}{\textbf{OUT OF SAMPLE}}" ///
    " & \multicolumn{2}{c}{\textbf{FIRST STAGE}} \\" ///
    "& \multicolumn{2}{c}{\textbf{EVIDENCE}} \\") ///
    posthead("Dependent Variable: &" ///
    "\multicolumn{2}{c}{\textbf{Malaria Deaths (100s)}}" ///
    " & \multicolumn{2}{c}{\textbf{Falciparum Malaria}} \\" ///
    "\cmidrule(lr){2-3} \cmidrule(lr){4-5}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-3} \cmidrule(lr){4-5}") 


* Panel C

eststo main_7_c1: reghdfe black_totalpop ME_std_x_elnino i.year, ///
    absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_7_c1
drop sample

boottest ME_std_x_elnino=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_c1

estadd local state "Yes": main_7_c1
estadd local year "Yes": main_7_c1


eststo main_7_c2: reghdfe black_totalpop ME_std_x_elnino ///
    rice1790_std_x_elnino i.year, absorb(state_g) vce(cluster state_g) 

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_7_c2
drop sample

boottest ME_std_x_elnino=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_c2

estadd local state "Yes": main_7_c2
estadd local year "Yes": main_7_c2


eststo main_7_c3: reghdfe black_totalpop endemic_falciparum i.year, ///
    absorb(state_g) vce(cluster state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_7_c3
drop sample

boottest endemic_falciparum=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_c3

estadd local state "Yes": main_7_c3
estadd local year "Yes": main_7_c3


eststo main_7_c4: ivreghdfe black_totalpop ///
    (endemic_falciparum=ME_std_x_elnino) i.state_g i.year, ///
    cluster (state_g)

gen sample = e(sample)
qui sum black_totalpop if sample==1
estadd scalar ymean = r(mean) : main_7_c4
drop sample

boottest endemic_falciparum=0, boottype(wild) seed(12345) nograph
estadd local boot = "\textit{`: display%4.3f `r(p)''}": main_7_c4

estadd local state "Yes": main_7_c4
estadd local year "Yes": main_7_c4


label var endemic_falciparum "Falciparum Malaria"
label var ME_std_x_elnino "Malaria Stability $ \times$ \# El Ni\~no Events"
label var rice1790_std_x_elnino "Rice Suit. $ \times$ \# El Ni\~no Events"

esttab main_7_c* using "$table/main_7.tex", append ///
    keep(endemic_falciparum ME_std_x_elnino rice1790_std_x_elnino) ///
    order(endemic_falciparum ME_std_x_elnino rice1790_std_x_elnino) ///
    starlevels(* 0.1 ** 0.05  *** 0.01)  ///
    cells(b(star fmt( %9.3fc)) /*mymat[2](par fmt(%9.3fc))*/ ///
    se(par(( )) fmt(%9.3fc))) /// 
    label nomtitles nonumbers collabels(,none) ///
    stats(boot state year N r2 ymean, ///
    labels("\textit{Bootstrap s.e. p-value}" ///
	"\noalign{\medskip} State Fixed Effects" ///
    "Year Fixed Effects" "Observations" "R-squared" ///
    "Mean Dep. Var." ) ///
    fmt(%9.2f %9.2f %9.2f %9.0f %9.3f %9.3f )) ///
    prehead(" " ///
    " \noalign{\smallskip} & \multicolumn{4}{c}{PANEL C} \\" ///
    "Dependent Variable: & \multicolumn{2}{c}{\textbf{\% Blacks}}" ///
    " & \multicolumn{2}{c}{\textbf{\% Blacks}} \\" ) ///
    posthead("&" ///
    "\multicolumn{2}{c}{\textbf{REDUCED FORM}}" ///
    " & \textbf{OLS} & \textbf{IV} \\" ///
    "\cmidrule(lr){2-3} \cmidrule(lr){4-5}") ///
    prefoot("") ///
    postfoot( "\cmidrule(lr){2-3} \cmidrule(lr){4-5}"  ///
    "\hline   \end{tabular} \end{threeparttable}") 

 
