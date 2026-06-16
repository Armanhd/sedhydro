#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 12:41:17 2026

@author: armanhaddadchi
"""


#%% import packages
import pandas as pd
import numpy as np
import os
import geopandas as gpd
import scipy
import copy
import tomllib



#%%
# def TempSedRout (river_gdf,reach_bed_calib, sediment_size, config_file, h, q, Q, width, SSC_hru_frac):
def TempSedRout (river_gdf, sediment_size, config_file, h, q, Q, 
                 width, SSC_hru_frac, 
                 dispersion_coeff1,dispersion_coeff2,dispersion_coeff3,
                 median_diam,SF, interpolation_numbers,
                 Fd1_coeff,Fd2_coeff, Fd3_coeff,
                 cr1_coeff,cr2_coeff, cr3_coeff):
     
    #%% read shapefile of river network --> river reach characteristics
    
    river_gdf = (
        river_gdf[["LINKNO", "DSLINKNO", "Slope", "Length"]]
        .copy()
        .astype({
            "LINKNO": "int64",
            "DSLINKNO": "int64",
            "Slope": "float64",
            "Length": "float64",
        })
        .set_index("LINKNO")
    )

    
    #%% add reach characteristics to river_gdf

    # dispersion coefficient
    river_gdf['dispersion1']= dispersion_coeff1
    river_gdf['dispersion2']= dispersion_coeff2
    river_gdf['dispersion3']= dispersion_coeff3
    
    # river bed median diameter
    river_gdf['median_diam']= median_diam
    # river bed sand fraction
    river_gdf['SF']=SF
    # number of interpolation points
    river_gdf['xpoints']=interpolation_numbers
    # F coefficient for each fraction
    river_gdf['Fd1']=Fd1_coeff
    river_gdf['Fd2']=Fd2_coeff
    river_gdf['Fd3']=Fd3_coeff
    
    # critical stream power coefficient
    river_gdf['critical_strmpow_coef_d1']=cr1_coeff
    river_gdf['critical_strmpow_coef_d2']=cr2_coeff
    river_gdf['critical_strmpow_coef_d3']=cr3_coeff
    
    # or for optimisation
    # river_gdf['Fd1']=Fd1
    # river_gdf['Fd2']=Fd2
    # river_gdf['Fd3']=Fd3
    # # or for optimisation
    # river_gdf['critical_strmpow_coef_d1']=cr1
    # river_gdf['critical_strmpow_coef_d2']=cr2
    # river_gdf['critical_strmpow_coef_d3']=cr3
    #%% find outlet reach
    reach_out_id=river_gdf.index[~river_gdf['DSLINKNO'].isin(river_gdf.index)][0]
    
    #%% read config file of TOML (temporary name: constants.toml)
    with open (config_file, 'rb') as f:
        constants=tomllib.load(f)
    
    #%% import constants from TOML file
    Rrho=constants['Rrho']
    g= constants['g']
    mcoef= constants['mcoef']
    kv=constants['kv']
    SF=constants['SF']
    rho=constants['rho']
    rhos=constants['rhos']
    nu=constants['nu']
    ki=constants['ki']
        
    #%% Interpolation of unitflow, flow, depth, width
    # at each river reach using number of points (xpoints)

    # interpolation of depth and unit flow at each river reach using number of points (xpoints)
    # change depth columns to integer
    # h.columns = h.columns.astype("int64")
    # # change unit flow columns to integer
    # q.columns = q.columns.astype("int64")
    # # change flow columns to integer
    # Q.columns = Q.columns.astype("int64")
    # # change width columns to integer
    # width.columns = width.columns.astype("int64")
    # hinterp={}      # empty dictionary for interpolated depth [m]

    # qinterp={}      # empty dictionary for interpolated unit flow [m^2/s]

    # Qinterp={}      # empty dictionary for interpolated flow [m^3/s]

    # widthinterp={}      # empty dictionary for interpolated width [m]

    # xpoints= river_gdf['xpoints'].iloc[0]  #    #int(reach_bed_calib.iloc[0]['xpoints'])
    # for reach_id in river_gdf.index:
    #     ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
    #     # skip if DS reach not in q (as outlet)
    #     if ds_id not in q.columns:
    #         continue
        
    #     q_US=np.array(q[reach_id])
    #     q_DS=np.array(q[ds_id])
    #     qinterptmp=np.zeros((len(q_US), xpoints+2))
    #     qinterp_struct=scipy.interpolate.interp1d([1,xpoints+2], np.vstack([q_US,q_DS]),kind='linear',axis=0)
        
    #     h_US=np.array(h[reach_id])
    #     h_DS=np.array(h[river_gdf.loc[reach_id, 'DSLINKNO']])
    #     hinterptmp=np.zeros((len(h_US), xpoints+2))
    #     hinterp_struct=scipy.interpolate.interp1d([1,xpoints+2], np.vstack([h_US,h_DS]),kind='linear',axis=0)
        
    #     Q_US=np.array(Q[reach_id])
    #     Q_DS=np.array(Q[river_gdf.loc[reach_id, 'DSLINKNO']])
    #     Qinterptmp=np.zeros((len(Q_US), xpoints+2))
    #     Qinterp_struct=scipy.interpolate.interp1d([1,xpoints+2], np.vstack([Q_US,Q_DS]),kind='linear',axis=0)
        
    #     width_US=np.array(width[reach_id])
    #     width_DS=np.array(width[river_gdf.loc[reach_id, 'DSLINKNO']])
    #     widthinterptmp=np.zeros((len(width_US), xpoints+2))
    #     widthinterp_struct=scipy.interpolate.interp1d([1,xpoints+2], np.vstack([width_US,width_DS]),kind='linear',axis=0)

    #     for m in range (xpoints+2):
    #         qinterptmp[:,m]=qinterp_struct(m+1)
    #         hinterptmp[:,m]=hinterp_struct(m+1)
    #         Qinterptmp[:,m]=Qinterp_struct(m+1)
    #         widthinterptmp[:,m]=widthinterp_struct(m+1)
           
    #     qinterp[reach_id]=np.transpose(qinterptmp)
    #     hinterp[reach_id]=np.transpose(hinterptmp)
    #     Qinterp[reach_id]=np.transpose(Qinterptmp)
    #     widthinterp[reach_id]=np.transpose(widthinterptmp)



    # --- make sure time is the index for all wide tables ---
    def prepare_wide_df(df):
        df = df.copy()
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df = df.set_index('time')
        return df
    
    h = prepare_wide_df(h)
    q = prepare_wide_df(q)
    Q = prepare_wide_df(Q)
    width = prepare_wide_df(width)
    
    # convert column names to same type as river_gdf index / DSLINKNO if needed
    # uncomment one of these only if needed in your case:
    # q.columns = q.columns.astype(int)
    # h.columns = h.columns.astype(int)
    # Q.columns = Q.columns.astype(int)
    # width.columns = width.columns.astype(int)
    
    # make everything numeric
    q = q.apply(pd.to_numeric, errors='coerce')
    h = h.apply(pd.to_numeric, errors='coerce')
    Q = Q.apply(pd.to_numeric, errors='coerce')
    width = width.apply(pd.to_numeric, errors='coerce')
    
    # dictionaries for interpolated results
    hinterp = {}
    qinterp = {}
    Qinterp = {}
    widthinterp = {}
    
    xpoints = int(river_gdf['xpoints'].iloc[0])
    
    # positions along reach: 0 = upstream, xpoints+1 = downstream
    n_sections = xpoints + 2
    alpha = np.linspace(0.0, 1.0, n_sections)[:, None]   # shape: (n_sections, 1)
    
    for reach_id in river_gdf.index:
        ds_id = river_gdf.loc[reach_id, 'DSLINKNO']
    
        # skip if DS reach not in q (as outlet)
        if ds_id not in q.columns:
            continue
    
        # extract as 1D float arrays
        q_US = q[reach_id].to_numpy(dtype=float)
        q_DS = q[ds_id].to_numpy(dtype=float)
    
        h_US = h[reach_id].to_numpy(dtype=float)
        h_DS = h[ds_id].to_numpy(dtype=float)
    
        Q_US = Q[reach_id].to_numpy(dtype=float)
        Q_DS = Q[ds_id].to_numpy(dtype=float)
    
        width_US = width[reach_id].to_numpy(dtype=float)
        width_DS = width[ds_id].to_numpy(dtype=float)
    
        # direct linear interpolation in space
        # result shape = (n_sections, n_times)
        qinterp[reach_id]     = (1 - alpha) * q_US[None, :]     + alpha * q_DS[None, :]
        hinterp[reach_id]     = (1 - alpha) * h_US[None, :]     + alpha * h_DS[None, :]
        Qinterp[reach_id]     = (1 - alpha) * Q_US[None, :]     + alpha * Q_DS[None, :]
        widthinterp[reach_id] = (1 - alpha) * width_US[None, :] + alpha * width_DS[None, :]
    #%% import time step
    dt = round(h.index.to_series().diff().mode()[0].total_seconds()) # in seconds
    
    #%% calculate dispersion [m^2/s] and ustar [m/s]

    # ustar={}
    # dispersion={}
    # for reach_id in river_gdf.index:
    #     ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
    #     # skip if DS reach not in q (as outlet)
    #     if ds_id not in q.columns:
    #         continue
    #     ustar[reach_id]=np.sqrt(g*hinterp[reach_id]*river_gdf.loc[reach_id,'Slope'])
    #     # kd=k u* h [m^2/s] as suggested by Fischer et al. (1979), coefficient for dispersion term is considered as k(250)
    #     dispersion[reach_id]=river_gdf.loc[reach_id,'dispersion']*hinterp[reach_id]*ustar[reach_id]
        
    #%% calculate dispersion [m^2/s] and ustar [m/s] for fractions
    #!!!
    ustar={}
    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # skip if DS reach not in q (as outlet)
        if ds_id not in q.columns:
            continue
        ustar[reach_id]=np.sqrt(g*hinterp[reach_id]*river_gdf.loc[reach_id,'Slope'])
        
    # map fraction index to the corresponding dispersion column in river_gdf
    dispersion_cols = {
        0: 'dispersion1',
        1: 'dispersion2',
        2: 'dispersion3'
    }

    dispersion={}

    for i in range (0, len(sediment_size)):
        dispersion[i] = {}
        col = dispersion_cols[i]
        
        for reach_id in river_gdf.index:
            ds_id = river_gdf.loc[reach_id, 'DSLINKNO']
            
            # skip if DS reach not in q (as outlet)
            if ds_id not in q.columns:
                continue
            
            dispersion[i][reach_id] = (
                river_gdf.loc[reach_id, col] *
                hinterp[reach_id] *
                ustar[reach_id]
            )
    
    #%% #%% calculation of alpha, beta, lambda for matrix
    # calculate A(left matrix) and M(right matrix)

    # alpha={}
    # beta={}
    # lamba={}
    # A1={}
    # A2={}
    # A3={}
    # M1={}
    # M2={}
    # M3={}

    # for reach_id in river_gdf.index:
    #     ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
    #     # skip if DS reach not in q (as outlet)
    #     if ds_id not in h.columns:
    #         continue
    #     alpha[reach_id]=hinterp[reach_id]/dt
    #     dx=river_gdf.loc[reach_id,'Length']
    #     beta[reach_id]=qinterp[reach_id]/(4*dx)
    #     lamba[reach_id]=(dispersion[reach_id]*hinterp[reach_id])/(2*(dx**2))
    #     A1[reach_id]=(-1*beta[reach_id])+lamba[reach_id]
    #     A2[reach_id]=alpha[reach_id]+(2*lamba[reach_id])
    #     A3[reach_id]=beta[reach_id]-lamba[reach_id]
    #     M1[reach_id]=beta[reach_id]+lamba[reach_id]
    #     M2[reach_id]=alpha[reach_id]-(2*lamba[reach_id])
    #     M3[reach_id]=lamba[reach_id]-beta[reach_id]
        

    #%% calculation of alpha, beta, lambda for matrix for fractions
    # calculate A(left matrix) and M(right matrix)

    alpha = {}
    beta = {}

    for reach_id in river_gdf.index:
        ds_id = river_gdf.loc[reach_id, 'DSLINKNO']
        
        if ds_id not in h.columns:
            continue
        
        dx = river_gdf.loc[reach_id, 'Length']
        alpha[reach_id] = hinterp[reach_id] / dt
        beta[reach_id] = qinterp[reach_id] / (4 * dx)

    lamba = {}
    A1 = {}
    A2 = {}
    A3 = {}
    M1 = {}
    M2 = {}
    M3 = {}

    for i in range(len(sediment_size)):
        lamba[i] = {}
        A1[i] = {}
        A2[i] = {}
        A3[i] = {}
        M1[i] = {}
        M2[i] = {}
        M3[i] = {}
        
        for reach_id in river_gdf.index:
            ds_id = river_gdf.loc[reach_id, 'DSLINKNO']
            
            if ds_id not in h.columns:
                continue
            
            dx = river_gdf.loc[reach_id, 'Length']
            
            lamba[i][reach_id] = (dispersion[i][reach_id] * hinterp[reach_id]) / (2 * (dx ** 2))
            
            A1[i][reach_id] = -beta[reach_id] + lamba[i][reach_id]
            A2[i][reach_id] = alpha[reach_id] + 2 * lamba[i][reach_id]
            A3[i][reach_id] = beta[reach_id] - lamba[i][reach_id]
            
            M1[i][reach_id] = beta[reach_id] + lamba[i][reach_id]
            M2[i][reach_id] = alpha[reach_id] - 2 * lamba[i][reach_id]
            M3[i][reach_id] = lamba[i][reach_id] - beta[reach_id]
        
    #%% calculate fall velocity
    def fallvelocity (di):
        # function to calculate fall velocity
        # input is diameter in meter [m]
        distar=(((Rrho*g)/(nu**2))**(1/3))*(di)
        falveli= (nu/di)*(((25+(1.2*(distar**2)))**(0.5))-5)**(1.5)     # fall velocity in [m/s]
        # print ('fall velocity(s) are:', falveli)
        return falveli

    # particle size for each size class [m]
    di=sediment_size['size']/1000000

    # fall velocity [m/s]
    falveli=fallvelocity (di)
    # fall velocity multiplied by alpha --> as input of 
    falvel_alphai=falveli*sediment_size['alpha']
    
    #%% calculate unit critical discharge and critical stream power 
        
    tetatau=pd.DataFrame(
        index=river_gdf.index,
        columns=['teta', 'tau'],
        dtype=float
    )

    # calculate teta and tau from Wilcock & Crowe relationship
    tetatau['teta']=0.021+(0.015*np.exp(-20*river_gdf['SF'].reindex(tetatau.index)))
    tetatau['tau']=tetatau['teta']*rho*g*Rrho* river_gdf['median_diam'].reindex(tetatau.index)



    # critical dict (unit critical: stream power (Wcri) / discharge (qcri)) with number of dataframes flexible as number of fractions
    cr_dict = {i: pd.DataFrame(
            index=river_gdf.index,
            columns=['Wcri', 'qcri'],
            dtype=float) for i in range(0, len(di)) }

    for i in range (0, len(di)):
        bfunci=0.67/(1+(np.exp(1.5-(di[i]/river_gdf['median_diam'].reindex(tetatau.index)))))
        tetari=(tetatau['tau'].reindex(tetatau.index))*(((di[i]/river_gdf['median_diam'].reindex(tetatau.index))**bfunci)/(rho*Rrho*g*di[i]))
        Logi=np.log10((30*tetari*Rrho*di[i])/(2.718*mcoef*river_gdf['Slope'].reindex(tetatau.index)*river_gdf['median_diam'].reindex(tetatau.index)))
        # unit critical streampower [w/m2]
        cr_dict[i]['Wcri']=(2.3/kv)*rho*((tetari*Rrho*g*di[i])**1.5)*Logi 
        # unit critical discharge [m^2/s]
        cr_dict[i]['qcri']=cr_dict[i]['Wcri']/(rho*g*river_gdf['Slope'].reindex(tetatau.index))  
        
    #%%    Calculate critical discharge and Stream power
    # note since width is not available critical stream power and critical discharge
    # are not calculated: Strmpowcri_dict, Qcr_dict
    Qcr={}
    widthcr={}
    Strmpowcr={}
    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # skip if DS reach not in q (as outlet)
        if ds_id not in h.columns:
            continue
        
        Qcrtmp_dict={}
        widthcrtmp_dict={}
        Strmpowcrtmp_dict={}
        
        # each fraction
        for i in range (0, len(di)):
            Qcrtmp=np.zeros(len(qinterp[reach_id]))
            widthcrtmp= np.zeros(len(qinterp[reach_id]))
            Strmpowcrtmp= np.zeros(len(qinterp[reach_id]))
            
            sloperegressi= np.zeros(len(qinterp[reach_id]))
            interceptregressi= np.zeros(len(qinterp[reach_id]))
            
            #each interpolation
            for l in range (len(qinterp[reach_id])):
                # calculate regression betwee unit flow (q) and width
                # sloperegressi[l],interceptregressi[l], r_value, p_value, std_err=scipy.stats.linregress (qinterp[reach_id][l],widthinterp[reach_id][l])
                
                x = np.asarray(qinterp[reach_id][l], dtype=float)
                y = np.asarray(widthinterp[reach_id][l], dtype=float)
                
                mask = np.isfinite(x) & np.isfinite(y)
                x = x[mask]
                y = y[mask]
                
                if len(x) < 2 or np.all(x == x[0]):
                    sloperegressi[l] = 0.0
                    interceptregressi[l] = np.nanmean(y) if len(y) > 0 else 0.0
                else:
                    sloperegressi[l], interceptregressi[l], r_value, p_value, std_err = scipy.stats.linregress(x, y)
                
                
                
                widthcrtmp[l]=sloperegressi[l]*cr_dict[i].loc[reach_id,'qcri'] + interceptregressi[l]
                Qcrtmp[l]=widthcrtmp[l]*cr_dict[i].loc[reach_id,'qcri'] 
                Strmpowcrtmp[l]=widthcrtmp[l]*cr_dict[i].loc[reach_id,'Wcri'] 
                
            Qcrtmp_dict[i]=Qcrtmp
            widthcrtmp_dict[i]=widthcrtmp
            Strmpowcrtmp_dict[i]=Strmpowcrtmp
            
        Qcr[reach_id]=Qcrtmp_dict
        widthcr[reach_id]=widthcrtmp_dict
        Strmpowcr[reach_id]=Strmpowcrtmp_dict
    
    #%% calculate unit stream power [W/m2] and Stream power
    Strmpowunit = {}
    Strmpow={}
    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # skip if DS reach not in q (as outlet)
        if ds_id not in h.columns:
            continue
        Strmpowunit[reach_id]=rho*g* river_gdf.loc[reach_id, 'Slope']*qinterp[reach_id]
        Strmpow[reach_id]=rho*g* river_gdf.loc[reach_id, 'Slope']*Qinterp[reach_id]
    
    #%% assign Fi and critical strmpow coefs (cr_coef) from reach_bed_calib (entered into river_gdf)
    Fi_dict = {i: pd.DataFrame(
            index=river_gdf.index,
            columns=['Fi'],
            dtype=float) for i in range(0, len(di)) }

    Fi_dict[0]['Fi'] = river_gdf['Fd1']
    Fi_dict[1]['Fi'] = river_gdf['Fd2']
    Fi_dict[2]['Fi'] = river_gdf['Fd3']

    cr_coef_dict={i: pd.DataFrame(
            index=river_gdf.index,
            columns=['cri'],
            dtype=float) for i in range(0, len(di)) }

    cr_coef_dict[0]['cri']=river_gdf['critical_strmpow_coef_d1']
    cr_coef_dict[1]['cri']=river_gdf['critical_strmpow_coef_d2']
    cr_coef_dict[2]['cri']=river_gdf['critical_strmpow_coef_d3']

    #%% calculate re-entrainment rate [kg/m^2/s] --> using unit critical stream power and unit stream power
    # re-entrainment rate for each reach (n=1,2...), each fraction (i=1,2,3,4) and each interpolated flow timseries

    rydunit={}

    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # skip if DS reach not in q (as outlet)
        if ds_id not in h.columns:
            continue
        rydtmp_dict={}
        for i in range (0, len(di)): # loop for each fraction (i)
            ryd_tmp=np.zeros_like(qinterp[reach_id])
            
            for l in range (len(qinterp[reach_id])):  #loop for each interpolated data array
                ryd_tmp[l,:]=(Fi_dict[i].loc[reach_id,'Fi'] / (ki*g*hinterp[reach_id][l,:]))* (
                    Strmpowunit[reach_id][l,:]-(cr_coef_dict[i].loc[reach_id,'cri']*cr_dict[i].loc[reach_id,'Wcri']))*(rhos/(rhos-rho))
                # change negative ryd to zero (-ryd=0 --> E<0 --> scenario 2, only deposition since critical stream power > stream power)
                ryd_tmp[ryd_tmp<0]=0                                             
            rydtmp_dict[i]=ryd_tmp
            del ryd_tmp
        rydunit[reach_id]=rydtmp_dict # re-entrainment rate  [kg/m^2/s]
        del rydtmp_dict
        
    #%% calculate re-entrainment rate [kg/m^2/s] --> using critical stream power and stream power
    # re-entrainment rate for each reach (n=1,2...), each fraction (i=1,2,3,4) and each interpolated flow timseries

    ryd={}

    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # skip if DS reach not in q (as outlet)
        if ds_id not in h.columns:
            continue
        rydtmp_dict={}
        for i in range (0, len(di)): # loop for each fraction (i)
            ryd_tmp=np.zeros_like(qinterp[reach_id])
            
            for l in range (len(qinterp[reach_id])):  #loop for each interpolated data array
                ryd_tmp[l,:]=(Fi_dict[i].loc[reach_id,'Fi'] / (ki*g*hinterp[reach_id][l,:]))* (
                    Strmpow[reach_id][l,:]-(cr_coef_dict[i].loc[reach_id,'cri']*Strmpowcr[reach_id][i][l]))*(rhos/(rhos-rho))
                # change negative ryd to zero (-ryd=0 --> E<0 --> scenario 2, only deposition since critical stream power > stream power)
                ryd_tmp[ryd_tmp<0]=0                                             
            rydtmp_dict[i]=ryd_tmp
            del ryd_tmp
        ryd[reach_id]=rydtmp_dict # re-entrainment rate  [kg/m^2/s]
        del rydtmp_dict

    #%% generate empty SSC_river_frac 
    SSC_river_frac={}

    #
    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # skip if DS reach not in q (as outlet)
        if ds_id in h.columns:
            
            SSC_river_fractmp_dict={}
            for i in range (0, len(di)): # loop for each fraction (i)
                SSC_river_fractmp=np.zeros((xpoints+2,len(h))) # arrays of nrows: interpolated steps (space), ncols: time steps 
                        
                SSC_river_fractmp_dict[i]=SSC_river_fractmp
                del SSC_river_fractmp
            SSC_river_frac[reach_id]=SSC_river_fractmp_dict
            del SSC_river_fractmp_dict 
            
            
        elif ds_id not in h.columns:
            SSC_river_fractmp_dict={}
            for i in range (0, len(di)): # loop for each fraction (i)
                SSC_river_fractmp=np.zeros((xpoints+2,len(h)))#np.zeros((1,len(q))) # array of one row (and ncolumns of time)
                        
                SSC_river_fractmp_dict[i]=SSC_river_fractmp
                del SSC_river_fractmp
            SSC_river_frac[reach_id]=SSC_river_fractmp_dict
            
    # generate empty deposition rate [kg/m2/s]
    ded = {rid: {k: np.zeros_like(arr) for k, arr in frac.items()}
           for rid, frac in SSC_river_frac.items()}
    # generate empty E=ryd-ded [kg/m2/s]
    E_dict = {rid: {k: np.zeros_like(arr) for k, arr in frac.items()}
              for rid, frac in SSC_river_frac.items()}

    #%% add SSC_hru to upper interpolation reach of each river reach in SSC_river
    for reach_id in river_gdf.index:
        ds_id=river_gdf.loc[reach_id, 'DSLINKNO']
        
        # # skip if DS reach not in q (as outlet)
        # if ds_id not in h.columns:
        #     continue
        for i in range (0, len(di)): # loop for each fraction (i)
            SSC_river_frac[reach_id][i][0,:]=SSC_hru_frac[i].loc[reach_id]
            # add first value from first row to all rows as first time step 
            SSC_river_frac[reach_id][i][:,0]=SSC_river_frac[reach_id][i][0,0]

    SSC_river_frac_base=copy.deepcopy(SSC_river_frac)
    
    #%% Calculate C using Crank-Nicholson Scheme

    # Make sure types match (optional but usually good)
    river_gdf = river_gdf.copy()
    river_gdf.index = river_gdf.index.astype("int64")
    river_gdf["DSLINKNO"] = pd.to_numeric(river_gdf["DSLINKNO"], errors="coerce")


    # 1) Count upstream tributaries (within this subset)
    up_count = river_gdf["DSLINKNO"].value_counts()              # counts for downstream ids
    up_count = up_count.reindex(river_gdf.index, fill_value=0)  # ensure every LINKNO has a count

    # 2) Start from headwaters (0 upstream)
    ready = [int(rid) for rid in river_gdf.index[up_count == 0]]

    order = []
    while ready:
        reach_id = ready.pop()          # pop() keeps it simple (LIFO); use pop(0) for FIFO
        order.append(reach_id)

        ds = river_gdf.at[reach_id, "DSLINKNO"]
        if pd.isna(ds):
            continue
        ds = int(ds)

        # only proceed if downstream is in this subset
        if ds in up_count.index:
            up_count.loc[ds] -= 1
            if up_count.loc[ds] == 0:
                ready.append(ds)
                
    # 3) Your loop in upstream -> downstream order
    n_us1 = n_us2 = None

    for reach_id in order:   # reach_id is ALWAYS a LINKNO in river_gdf.index

        if reach_id == n_us1 or reach_id == n_us2:
            continue

        num_step=xpoints+2 # number of rows on each array
        num_time=len(h) # number of columns on each array
        # num_step, num_time=SSC_river_frac[reach_id][0].shape
        us = river_gdf.index[river_gdf["DSLINKNO"] == reach_id]
        
        # 2-tributaries
        if len(us) == 2:
            # print("2 US tributaries")
            # print("DS (reach_id):", reach_id)
            # print(reach_id)
            n_us1, n_us2 = map(int, us[:2])
            # print("US1:", n_us1, "US2:", n_us2)
            for k in range (0, len(di)):   # loop for each fraction
            # i=0# one fraction
            
                # n_us1
                t_before=0
                for j in range (1, num_time): # loop at each time step
                    ded[n_us1][k][:,t_before]=falvel_alphai[k]*SSC_river_frac[n_us1][k][:,t_before]
                    # change negative ded to zero (-ded=0)
                    ded[n_us1][k][:,t_before][ded[n_us1][k][:,t_before]<0]=0
                    
                    for l in range (len(qinterp[n_us1])): # loop at each space step
                        # using unit stream power for ryd
                        # E_dict[n_us1][k][l,t_before]=rydunit[n_us1][k][l,t_before]-ded[n_us1][k][l,t_before]    
                        # using stream power for ryd
                        E_dict[n_us1][k][l,t_before]=ryd[n_us1][k][l,t_before]-ded[n_us1][k][l,t_before]    
        
                    # matrix solution
                    # making matrix A for time step ahead (t+1)= j
                    A=scipy.sparse.spdiags([np.append(A1[k][n_us1][1:,j],[0]), A2[k][n_us1][:,j], np.append([0],A3[k][n_us1][:-1,j])], (-1,0,1), xpoints+2, xpoints+2).toarray()
                    # making matrix M for current time step (t)=j-1
                    M=scipy.sparse.spdiags([np.append(M1[k][n_us1][1:,j-1],[0]), M2[k][n_us1][:,j-1], np.append([0],M3[k][n_us1][:-1,j-1])], (-1,0,1), xpoints+2, xpoints+2).toarray()
                    
                    MC=np.matmul(M,SSC_river_frac[n_us1][k][:,t_before]) # matrix multiplication for right-hand eqn (M * Cj)
                    MCE= MC+E_dict[n_us1][k][:,t_before]    # MC+E which E is (E=r-d) for one time step back
                    Cleft_array=np.linalg.solve (A, MCE) # solve matrix to find Cj+1
                    # change negative C to zero (-C=0)
                    Cleft_array[Cleft_array<0]=0
                    
                    Cleft_array[0]=SSC_river_frac[n_us1][k][0,j]    # Add boundary condition to each step after solving the matrix
                    SSC_river_frac[n_us1][k][:,j]= Cleft_array
                    t_before=t_before+1                
                    # del Cleft_array, A, M, MC, MCE
                    
                # n_us2
                t_before=0
                for j in range (1, num_time): # loop at each time step
                    ded[n_us2][k][:,t_before]=falvel_alphai[k]*SSC_river_frac[n_us2][k][:,t_before]
                    # change negative ded to zero (-ded=0)
                    ded[n_us2][k][:,t_before][ded[n_us2][k][:,t_before]<0]=0
                    
                    for l in range (len(qinterp[n_us2])): # loop at each space step
                        # using unit stream power for ryd
                        # E_dict[n_us2][k][l,t_before]=rydunit[n_us2][k][l,t_before]-ded[n_us2][k][l,t_before]    
                        # using stream power for ryd
                        E_dict[n_us2][k][l,t_before]=ryd[n_us2][k][l,t_before]-ded[n_us2][k][l,t_before]   
        
                    # matrix solution
                    # making matrix A for time step ahead (t+1)= j
                    A=scipy.sparse.spdiags([np.append(A1[k][n_us2][1:,j],[0]), A2[k][n_us2][:,j], np.append([0],A3[k][n_us2][:-1,j])], (-1,0,1), xpoints+2, xpoints+2).toarray()
                    # making matrix M for current time step (t)=j-1
                    M=scipy.sparse.spdiags([np.append(M1[k][n_us2][1:,j-1],[0]), M2[k][n_us2][:,j-1], np.append([0],M3[k][n_us2][:-1,j-1])], (-1,0,1), xpoints+2, xpoints+2).toarray()
                    MC=np.matmul(M,SSC_river_frac[n_us2][k][:,t_before]) # matrix multiplication for right-hand eqn (M * Cj)
                    MCE= MC+E_dict[n_us2][k][:,t_before]    # MC+E which E is (E=r-d) for one time step back
                    Cleft_array=np.linalg.solve (A, MCE) # solve matrix to find Cj+1
                    # change negative C to zero (-C=0)
                    Cleft_array[Cleft_array<0]=0
                    
                    Cleft_array[0]=SSC_river_frac[n_us2][k][0,j]    # Add boundary condition to each step after solving the matrix
                    SSC_river_frac[n_us2][k][:,j]= Cleft_array
                    t_before=t_before+1
                    del Cleft_array, A, M, MC, MCE
                #BC for Downstream reach
                SSC_river_frac[reach_id][k][0,:]=SSC_river_frac[n_us1][k][num_step-1,:]+SSC_river_frac[n_us2][k][num_step-1,:]+SSC_river_frac_base[reach_id][k][0,:]
                
                # IC for Downstream reach
                SSC_river_frac[reach_id][k][:,0]=SSC_river_frac[n_us1][k][0,0]+SSC_river_frac[n_us2][k][0,0]+SSC_river_frac_base[reach_id][k][0,0] #SSC_river_frac_base[reach_id][k][:,0]
                
        # 1-tributary
        elif len(us) == 1:

            n_us = int(us[0])     # n_us = UPSTREAM reach
            # print("1 US tributary")
            # print("DS (reach_id):", reach_id)
            # print("US (n_us):", n_us)
            for k in range (0, len(di)):   # loop for each fraction
            # i=0# one fraction
            
                t_before=0
                for j in range (1, num_time): # loop at each time step
                    ded[n_us][k][:,t_before]=falvel_alphai[k]*SSC_river_frac[n_us][k][:,t_before]
                    # change negative ded to zero (-ded=0)
                    ded[n_us][k][:,t_before][ded[n_us][k][:,t_before]<0]=0
                    
                    for l in range (len(qinterp[n_us])): # loop at each space step
                        # using unit stream power for ryd
                        # E_dict[n_us][k][l,t_before]=rydunit[n_us][k][l,t_before]-ded[n_us][k][l,t_before]    
                        # using stream power for ryd
                        E_dict[n_us][k][l,t_before]=ryd[n_us][k][l,t_before]-ded[n_us][k][l,t_before]
                        
                    # matrix solution
                    # making matrix A for time step ahead (t+1)= j
                    A=scipy.sparse.spdiags([np.append(A1[k][n_us][1:,j],[0]), A2[k][n_us][:,j], np.append([0],A3[k][n_us][:-1,j])], (-1,0,1), xpoints+2, xpoints+2).toarray()
                    # making matrix M for current time step (t)=j-1
                    M=scipy.sparse.spdiags([np.append(M1[k][n_us][1:,j-1],[0]), M2[k][n_us][:,j-1], np.append([0],M3[k][n_us][:-1,j-1])], (-1,0,1), xpoints+2, xpoints+2).toarray()
                    MC=np.matmul(M,SSC_river_frac[n_us][k][:,t_before]) # matrix multiplication for right-hand eqn (M * Cj)
                    MCE= MC+E_dict[n_us][k][:,t_before]    # MC+E which E is (E=r-d) for one time step back
                    Cleft_array=np.linalg.solve (A, MCE) # solve matrix to find Cj+1
                    # change negative C to zero (-C=0)
                    Cleft_array[Cleft_array<0]=0
                    
                    Cleft_array[0]=SSC_river_frac[n_us][k][0,j]    # Add boundary condition to each step after solving the matrix
                    SSC_river_frac[n_us][k][:,j]= Cleft_array
                    t_before=t_before+1
                    del Cleft_array, A, M, MC, MCE
                #BC for Downstream reach
                SSC_river_frac[reach_id][k][0,:]=SSC_river_frac[n_us][k][num_step-1,:]+SSC_river_frac_base[reach_id][k][0,:]
                    
                # IC for Downstream reach
                SSC_river_frac[reach_id][k][:,0]=SSC_river_frac[n_us][k][0,0]+SSC_river_frac_base[reach_id][k][0,0]
                    
    #%% make output for C with time and reach_id for each fraction and total SSC
    SSC_river_frac_out={}
    for k in range (0, len(di)):
        SSC_river_frac_tmp=pd.DataFrame(0.0, index=h.index, columns=h.columns)
        for reach_id in river_gdf.index:
            
            if reach_id ==reach_out_id:
                SSC_river_frac_tmp[reach_id]=SSC_river_frac[reach_id][k][0,:]
            else:
                SSC_river_frac_tmp[reach_id]=SSC_river_frac[reach_id][k][num_step-1,:]
            
        SSC_river_frac_out[k]=SSC_river_frac_tmp

    # total concentration out (i.e. sum each fraction) for each time and each river reach
    # SSC_river_tot_out=pd.DataFrame(0.0, index=h.index, columns=h.columns)
    SSC_river_tot_out=sum(SSC_river_frac_out.values())                

    return SSC_river_frac_out, SSC_river_tot_out 


