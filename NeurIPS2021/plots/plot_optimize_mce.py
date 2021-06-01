#
# Prepare data to show the results after running optimize_mce.py
# Requirement : Need data to be in $EXP_PATH$ folder
#

import sys
import numpy as np
import pandas as pd
import os

BASE = sys.argv[1] if len(sys.argv)>=2 else 'mce'
M = int(sys.argv[2]) if len(sys.argv)>=3 else 7

if BASE == 'boost':
    DATASETS = [
            'SVMGuide1',
            'Phishing',
            'Mushroom',
            'Splice',
            'w1a',
            'Cod-RNA',
            'Adult',
            'Connect-4',
            'Shuttle',
            ]
else:
    DATASETS = [
            'SVMGuide1',
            'Phishing',
            'Mushroom',
            'Splice',
            'w1a',
            'Cod-RNA',
            'Adult',
            'Protein',
            'Connect-4',
            'Shuttle',
            'Pendigits',
            'Letter',
            'SatImage',
            'Sensorless',
            'USPS',
            'MNIST',
            'Fashion-MNIST'
            ]
EXP_PATH  = "../out/optimizeMCS4/"


"""
# Prepare data for plotting error and bounds when \rho=rho^*
# One plot(csv file) for each dataset.
# Ex. Figure 1. in the NeurIPS 2020 paper.
def multi_bounds():
    name = "bounds_optimize"
    path = name+"/datasets/"
    if not os.path.isdir(path):
        os.makedirs(path)
        
    bounds = [("lam_pbkl","FO"),("tnd_tnd","TND"),("mug_mub","MU"),("MUBernsteing_bern","Bern")]
    
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH+"/"+ds+"-"+str(NUM_TREES)+"-bootstrap-iRProp.csv",sep=";")
        df_mean = df.mean()
        df_std  = df.std()**(0.5)
        with open(path+ds+".tex", "w") as f:
            for i,(bnd,cls) in enumerate(bounds):
                f.write("\\addplot["+cls+", Bound]coordinates {("+str(i+1)+","+str(df_mean[bnd])+") +- (0,"+str(df_std[bnd])+")};\n")

#multi_bounds()
"""

# Prepare data for comparison of MV risk bewteen \rho=\rho* and \rho=uniform
# The data will be recorded in risk_comparison_optimized/mce/datasets
# Ex. Figure 2 (a) in the NeurIPS 2020 paper
def optimized_risk_comparison(base='mce'):
    name = "risk_comparison_optimized"
    path = name+"/"+base+"/datasets/"
    if not os.path.isdir(path):
        os.makedirs(path)

    if base == 'boost':
        opts = ["unf","lam","tnd","mu","bern"]
        baseline = "ada_mv_risk"
    else:
        #opts = ["unf", "lam", "tnd", "mu", "bern"]
        #baseline = "best_mv_risk"
        opts = ["best", "lam", "tnd", "mu", "bern"]
        baseline = "unf_mv_risk"
        base='bootstrap'

    cols = ["dataset"]
    for opt in opts:
        cols += [opt+suf for suf in ["_diff","_q25","_q75"]]
    rows_bin = []
    rows_mul = []
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH+ds+"-"+str(M)+"-"+base+"-iRProp.csv",sep=";")
        if (df[baseline]<=0.0).sum() > 0:
            continue
        row = [ds]
        for opt in opts:
            diff   = df[opt+"_mv_risk"]/df[baseline]
            med = diff.median()
            row += [med, med-diff.quantile(0.25), diff.quantile(0.75)-med]
        if df["c"].iloc[0]==2:
            rows_bin.append(row)
        else:
            rows_mul.append(row)
    
    pd.DataFrame(data=rows_bin, columns=cols).to_csv(path+"bin.csv", sep=";", index_label="idx")
    pd.DataFrame(data=rows_mul, columns=cols).to_csv(path+"mul.csv", sep=";", index_label="idx")

optimized_risk_comparison(base=BASE)


# Prepare data for comparison of MV risk bewteen \rho=\rho* and \rho=uniform
# The data will be recorded in risk_comparison_optimized/mce/bounds
# Ex. Figure 2 (a) in the NeurIPS 2020 paper
def optimized_bound_comparison(base='mce'):
    name = "risk_comparison_optimized"
    path = name + "/" + base + "/bounds/"
    if not os.path.isdir(path):
        os.makedirs(path)

    if base == 'boost':
        opts = ["unf", "lam", "tnd", "mu", "bern"]
        baseline = "ada_mv_risk"
    else:
        opts = ["mu", "bern"]
        opts2 = {"mu":"_MU", "bern":"_bern"}
        baseline = "tnd_tnd"
        base='bootstrap'

    cols = ["dataset"]
    for opt in opts:
        cols += [opt + suf for suf in ["_diff", "_q25", "_q75"]]
    rows_bin = []
    rows_mul = []
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH + ds + "-" + str(M) + "-" + base + "-iRProp.csv", sep=";")
        if (df[baseline] <= 0.001).sum() > 0:
            continue
        row = [ds]
        for opt in opts:
            diff = df[opt + opts2[opt]] / df[baseline]
            med = diff.median()
            row += [med, med - diff.quantile(0.25), diff.quantile(0.75) - med]
        if df["c"].iloc[0] == 2:
            rows_bin.append(row)
        else:
            rows_mul.append(row)

    pd.DataFrame(data=rows_bin, columns=cols).to_csv(path + "bin.csv", sep=";", index_label="idx")
    pd.DataFrame(data=rows_mul, columns=cols).to_csv(path + "mul.csv", sep=";", index_label="idx")


optimized_bound_comparison(base=BASE)

# Prepare data for the table to compare the results for optimization
def optimized_comparison_table(base='mce'):
    path = "table/"+base+"/optimize/"
    if not os.path.isdir(path):
        os.makedirs(path)
    
    prec = 5
    if base == 'boost':
        opts = ["ada", "unf", "lam","tnd","mu","bern"]
    else:
        opts = ["best", "unf", "lam","tnd","mu","bern"]
        base='bootstrap'

    cols = ["dataset"] + opts

    rows = []
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH+ds+"-"+str(M)+"-"+base+"-iRProp.csv",sep=";")
        df_mean = df.mean()
        df_std  = df.std()
        
        row = [ds]
        for opt in opts:
            risk = df_mean[opt+"_mv_risk"]
            row += [risk]
        rows.append(row)
    
    pd.DataFrame(data=rows, columns=cols).round(prec).to_csv(path+"test_risk.csv", sep=",", index=False)

optimized_comparison_table(base=BASE)


# Prepare data for the table to compare tnd and Bern
def TND_Ben_comparison_table(base='mce'):
    path = "table/"+base+"/optimize/"
    if not os.path.isdir(path):
        os.makedirs(path)

    if base=='mce':
        base='bootstrap'

    prec = 5
    opts = ["tnd", "mu", "bern"]
    cols = ["dataset", "c", "d"]
    for opt in opts:
        if opt == "tnd":
            cols += [opt+suf for suf in ["_gibbs", "_tandem", "_KL", "_tnd", "_TandemUB", "_bern"]]
        elif opt == "mu":
            cols += [opt+suf for suf in ["_MU", "_muTandemUB", "_bern", "_bmu"]]
        elif opt == "bern":
            cols += [opt+suf for suf in ["_bern", '_mutandem_risk', '_vartandem_risk', "_KL", "_varUB", "_bernTandemUB", "_bmu", "_bg", "_bl"]]
    rows = []
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH+ds+"-"+str(M)+"-"+base+"-iRProp.csv",sep=";")
        df_mean = df.mean()
        df_std  = df.std()
        
        row = [ds, df_mean["c"], df_mean["d"]]
        for opt in opts:
            if opt == "tnd":
                row += [df_mean[opt+suf] for suf in ["_gibbs", "_tandem", "_KL", "_tnd", "_TandemUB", "_bern"]]
            elif opt == "mu":
                row += [df_mean[opt+suf] for suf in ["_MU", "_muTandemUB", "_bern", "_bmu"]]
            elif opt == "bern":
                row += [df_mean[opt+suf] for suf in ["_bern", '_mutandem_risk', '_vartandem_risk', "_KL", "_varUB", "_bernTandemUB", "_bmu", "_bg", "_bl"]]            
        rows.append(row)
    
    pd.DataFrame(data=rows, columns=cols).round(prec).to_csv(path+"mu_comparison.csv", sep=",", index=False)

TND_Ben_comparison_table(base=BASE)

# Prepare data for the table to compare the bounds for the optimized rho
def Bounds_optimized_table(base='mce'):
    path = "table/"+base+"/optimize/"
    if not os.path.isdir(path):
        os.makedirs(path)
    
    prec = 5
    if base == 'boost':
        opts = {"ada":'sh', "lam":'pbkl',"tnd":'tnd',"mu":'MU',"bern":'bern'}
    else:
        opts = {"lam":'pbkl',"tnd":'tnd',"mu":'MU',"bern":'bern'}
        base = 'bootstrap'

    cols = ["dataset"] + list(opts.keys())

    rows = []
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH+ds+"-"+str(M)+"-"+base+"-iRProp.csv",sep=";")
        df_mean = df.mean()
        df_std  = df.std()
        
        row = [ds]
        for key in list(opts.keys()):
            risk = df_mean[key+"_" + opts[key]]
            row += [risk]
        rows.append(row)
    
    pd.DataFrame(data=rows, columns=cols).round(prec).to_csv(path+"bounds_optimized.csv", sep=",", index=False)

Bounds_optimized_table(base=BASE)