#
# Prepare data to show the results after running optimize.py
# Requirement : Need data to be in ../out/optimize/
# 

import sys
import numpy as np
import pandas as pd
import os

BASE = sys.argv[1] if len(sys.argv)>=2 else 'rfc'
M = int(sys.argv[2]) if len(sys.argv)>=3 else 100

RENAME = {"Fashion-MNIST":"Fashion"}
if BASE == 'boost':
    #M = [225, 750, 225, 225, 300]
    DATASETS = [
            'SVMGuide1',
            'Phishing',
            'Mushroom',
            'Splice',
#            'w1a',
#            'Cod-RNA',
            'Adult',
#            'Connect-4',
#            'Shuttle',
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
            'Fashion-MNIST',
            ]


# Prepare data for comparison of MV risk/bounds bewteen \rho=\rho* and \rho=uniform
# The data will be recorded in risk_comparison_optimized/datasets
# Ex. Figure 2 in the NeurIPS 2021 paper
def optimized_comparison(tp='risk', base='rfc'):
    path = "figure/"+base+"/datasets/"
    if not os.path.isdir(path):
        os.makedirs(path)

    opts, baseline = {
        ("risk","boost"): (["prior","unf","lam","tnd","mu","bern"],["ada", "prior"]),
        ("risk","rfc"):   (["lam","tnd","mu","bern"],["unf"]),
        ("risk","mce"):   (["best","lam","tnd","mu","bern"],["unf"]),
        ("bound","boost"):([],[]),
        ("bound","rfc"):  ([("lam","pbkl"),("tnd","tnd"),("mu","MU"),("bern","bern")],[("tnd","tnd")]),
        ("bound","mce"):  ([("lam","pbkl"),("tnd","tnd"),("mu","MU"),("bern","bern")],[("tnd","tnd")])
    }[(tp,base)]
    if tp=='risk':
        opts = [(o,"mv_risk") for o in opts]
        baseline = [(b,"mv_risk") for b in baseline]

    exp_path, smet = {
        "rfc":   ("../out/optimize/","bootstrap"),
        "boost": ("../out/optimize/","boost"),
        "mce":   ("../out/optimizeMCS6/","bootstrap"),
    }[base]

    for bl,blbnd in baseline:
        cols = ["dataset"]
        for opt,_ in opts:
            cols += [opt+suf for suf in ["_diff","_q25","_q75"]]
        rows_bin = []
        rows_mul = []
        blcol = bl+"_"+blbnd
        for ds in DATASETS:
            df = pd.read_csv(exp_path+ds+"-"+str(M)+"-"+smet+"-iRProp.csv",sep=";")
            if (df[blcol]==0).sum() > 0:
                continue
            row = [RENAME.get(ds,ds)]
            for opt,obnd in opts:
                optcol = opt+"_"+obnd
                diff   = df[optcol]/df[blcol]
                med = diff.median()
                row += [med, med-diff.quantile(0.25), diff.quantile(0.75)-med]
            if df["c"].iloc[0]==2:
                rows_bin.append(row)
            else:
                rows_mul.append(row)
        
        pd.DataFrame(data=rows_bin, columns=cols).to_csv(path+tp+"-bin-"+bl + ".csv", sep=";", index_label="idx")
        pd.DataFrame(data=rows_mul, columns=cols).to_csv(path+tp+"-mul-"+bl + ".csv", sep=";", index_label="idx")

optimized_comparison("risk",base=BASE)
optimized_comparison("bound",base=BASE)

PREC = 4

PRETTY_MAP = {
    "best_mv_risk":"$L(h_{best})$",
    "unf_mv_risk":"$L(\\MV_{u})$",
    "lam_mv_risk":"$L(\\MV_{\\rho_\\lambda})$",
    "tnd_mv_risk":"$L(\\MV_{\\rho_{\\TND}})$",
    "mu_mv_risk":"$L(\\MV_{\\rho_{\\CMUTND}})$",
    "bern_mv_risk":"$L(\\MV_{\\rho_{\\COTND}})$",
    "lam_pbkl":"$\\FO(\\rho_\\lambda)$",
    "tnd_tnd":"$\\TND(\\rho_{\\TND})$",
    "mu_MU":"$\\CMUTND(\\rho_{\\CMUTND})$",
    "bern_bern":"$\\COTND(\\rho_{\\COTND})$",
}

# Result tables for NeurIPS 2021 paper
def optimized_comparison_table(tp='risk', base='rfc', hl1="all", hl2=[]):
    path = "table/"+base+"/optimize/"
    out_fname = path+tp+"_table.tex"
    if not os.path.isdir(path):
        os.makedirs(path)

    opts = {
        ("risk","boost"):     ["ada","prior","unf","lam","tnd","mu","bern"],
        ("risk","rfc"):       ["unf","lam","tnd","mu","bern"],
        ("risk","mce"):       ["unf","best","lam","tnd","mu","bern"],
        ("bound","boost"):    [],
        ("bound","rfc"):      [("lam","pbkl"),("tnd","tnd"),("mu","MU"),("bern","bern")],
        ("bound","mce"):      [("lam","pbkl"),("tnd","tnd"),("mu","MU"),("bern","bern")],
    }[(tp,base)]
    if tp=='risk':
        opts = [(o,"mv_risk") for o in opts]
    
    copts = [pre+"_"+suf for pre,suf in opts]
    
    exp_path, smet = {
        "rfc":   ("../out/optimize/","bootstrap"),
        "boost": ("../out/optimize/","boost"),
        "mce":   ("../out/optimizeMCS6/","bootstrap"),
    }[base]
    
    if hl1=="all":
        hl1 = copts

    with open(out_fname, 'w') as fout:
        # Header
        fout.write("\\begin{tabular}{l"+"c"*len(opts)+"}\\toprule\n")
        fout.write("Data set")
        for i,col in enumerate(copts):
            fout.write(" & "+PRETTY_MAP[col])
        fout.write(" \\\\\n")
        fout.write("\\midrule\n")

        for ds in DATASETS:
            df = pd.read_csv(exp_path+ds+"-"+str(M)+"-"+smet+"-iRProp.csv",sep=";")
            df_mean = df.mean()
            df_std  = df.std()
            
            # Highlight indices
            v1 = np.min(df_mean[hl1]) if len(hl1)>0 else -1
            v2 = np.min(df_mean[hl2]) if len(hl2)>0 else -1
            v1 = str(round(v1,PREC))
            v2 = str(round(v2,PREC))

            fout.write("\\dataset{"+RENAME.get(ds,ds)+"}")
            for i,col in enumerate(copts):
                fval = df_mean[col]
                val = str(round(fval,PREC))
                std = str(round(df_std[col],PREC))
                s = val + " ("+std+")"
                if col in hl1 and val==v1:
                    s = "\\textbf{"+s+"}"
                if col in hl2 and val==v2:
                    s = "\\underline{"+s+"}"
                fout.write(" & "+s)
            fout.write(" \\\\\n")

        fout.write("\\bottomrule\n") 
        fout.write("\\end{tabular}\n")
    
optimized_comparison_table('risk', base=BASE, hl2=["lam_mv_risk","tnd_mv_risk","mu_mv_risk","bern_mv_risk"])
optimized_comparison_table('bound', base=BASE, hl2=["tnd_tnd","mu_MU","bern_bern"])


### Old csv table functions below

# Prepare data for the table to compare the results for optimization
def optimized_comparison_table(base='bootstrap'):
    path = "table/"+base+"/optimize/"
    if not os.path.isdir(path):
        os.makedirs(path)
    
    prec = 5
    if base == 'boost':
        opts = ["ada", "prior", "unf", "lam","tnd","mu","bern"]
    else:
        opts = ["unf", "lam","tnd","mu","bern"]
    
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

#optimized_comparison_table(base=BASE)


# Prepare data for the table to compare tnd and Bern
def TND_Ben_comparison_table(base='bootstrap'):
    path = "table/"+base+"/optimize/"
    if not os.path.isdir(path):
        os.makedirs(path)
    
    prec = 5
    opts = ["tnd", "mu", "bern"]
    cols = ["dataset", "c", "d"]
    for opt in opts:
        if opt == "tnd":
            cols += [opt+suf for suf in ["_KL", "_gibbs", "_tandem", "_tnd", "_TandemUB"]]
        elif opt == "mu":
            cols += [opt+suf for suf in ["_KL", "_MU", "_muTandemUB", "_bmu"]]
        elif opt == "bern":
            cols += [opt+suf for suf in ["_KL", "_bern", '_mutandem_risk', '_vartandem_risk', "_varUB", "_bernTandemUB", "_bmu", "_bg", "_bl"]]
    rows = []
    for ds in DATASETS:
        df = pd.read_csv(EXP_PATH+ds+"-"+str(M)+"-"+base+"-iRProp.csv",sep=";")
        df_mean = df.mean()
        df_std  = df.std()
        
        row = [ds, df_mean["c"], df_mean["d"]]
        for opt in opts:
            if opt == "tnd":
                row += [df_mean[opt+suf] for suf in ["_KL", "_gibbs", "_tandem", "_tnd", "_TandemUB"]]
            elif opt == "mu":
                row += [df_mean[opt+suf] for suf in ["_KL", "_MU", "_muTandemUB", "_bmu"]]
            elif opt == "bern":
                row += [df_mean[opt+suf] for suf in ["_KL", "_bern", '_mutandem_risk', '_vartandem_risk', "_varUB", "_bernTandemUB", "_bmu", "_bg", "_bl"]]            
        rows.append(row)
    
    pd.DataFrame(data=rows, columns=cols).round(prec).to_csv(path+"mu_comparison.csv", sep=",", index=False)

#TND_Ben_comparison_table(base=BASE)

# Prepare data for the table to compare the bounds for the optimized rho
def Bounds_optimized_table(base='bootstrap'):
    path = "table/"+base+"/optimize/"
    if not os.path.isdir(path):
        os.makedirs(path)
    
    prec = 5
    if base == 'boost':
        opts = {"ada":'sh', "lam":'pbkl',"tnd":'tnd',"mu":'MU',"bern":'bern'}
    else:
        opts = {"lam":'pbkl',"tnd":'tnd',"mu":'MU',"bern":'bern'}
    
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

#Bounds_optimized_table(base=BASE)
