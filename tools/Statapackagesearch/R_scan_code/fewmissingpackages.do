
** Code sample with fewer missing packages

** Contrived, shorter code snippet that contains fewer missing packages and less overall noise

// Packages: wyoung carryforward oaxaca


wyoung `v', cmd(regress OUTCOMEVAR hra_c_yr1, vce(robust)) familyp(hra_c_yr1) bootstrap(1000) seed (1234)	

reg family treat, vce(robust)

bysort personid (negyear): carryforward educ2, gen(educ2b) back

reg personid treat, vce(robust)

oaxaca personid educ2 if hra_c_yr1==0