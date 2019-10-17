#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd

def read_logfile(filename):

    vmstat_raw = pd.read_csv(filename, sep="\n", header=None, skiprows=1, names=["raw"])
    vmstat_temp = vmstat_raw['raw'].str.split().apply(pd.Series)
    vmstat_temp.columns =  vmstat_temp.iloc[0]
    vmstat_temp = vmstat_temp.dropna().reset_index(drop=True)
    vmstat = vmstat_temp.iloc[:,:-2].apply(pd.to_numeric)
    vmstat['UTC'] = pd.to_datetime(vmstat_temp['UTC'] + " " + vmstat_temp.iloc[:,-1])
    return vmstat.set_index('UTC')
