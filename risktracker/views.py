from django.shortcuts import render
# import rpy2.robjects as robjects
# from rpy2.robjects import pandas2ri
import pandas as pd
import numpy as np
import geopandas as gpd
from pandas import read_csv
# Create your views here.
# Create your views here.

indo_l0 = None
indo_l1 = None
indo_l2 = None




def home(request):
    return render(request, 'risktracker/home.html', {})


def load_data():
    global indo_l0
    global indo_l1
    global indo_l2
    indo_l0 = gpd.read_file("gadm36_IDN.gpkg", layer=0)
    indo_l1 = gpd.read_file("gadm36_IDN.gpkg", layer=4)  #province
    indo_l2 = gpd.read_file("gadm36_IDN.gpkg", layer=3)  #Regency


def time_filter(data, time):
    if data is None:
        return None
    return data[data['Time'] == time]


# switch statment, it returns the data_frame based on the time input parameter
def switch_filter(argument, query_data):
    switcher = {
        "1": time_filter(query_data,"score_318"),
        "2": time_filter(query_data,"score_118"),
        "3": time_filter(query_data,"score_218"),
        "4": time_filter(query_data,"score_319"),
    }
    return switcher.get(argument, lambda: "Invalid month")

# re-writing the gather function in python
def gather( df, key, value, cols ):
    id_vars = [ col for col in df.columns if col not in cols ]
    id_values = cols
    var_name = key
    value_name = value
    return pd.melt( df, id_vars, id_values, var_name, value_name )

def create_popups(data, unit):
    return "<div style='text-align: center;'>{}<br/><b>{}</b><br/><br/>Composite score:<br/><span style='font-size: 1.5em;'>{}</span><br/></div>".format(unit, data.NAME, round(data.comp_score))

def h_popups(data):
    return "<div style='text-align: center;'><b>HOTEL</b><br/><br/><b>District: </b> { } <br/></b><b>Regency: </b> {} </b><br/><br/>Size:<br/><span style='font-size: 1.5em;'> {}</span><br/></div>".format(data.name_district, data.name_muni, data.h_size.to_upper())

def o_popups(data):
    return "<div style='text-align: center;'><b>OFFICE</b><br/><br/><b>District: </b>{}<br/></b><b>Regency: </b>{}</b><br/><br/>Size:<br/><span style='font-size: 1.5em;'> {}</span><br/></div>".format(data.name_district, data.name_muni, data.o_size.to_upper())

def sd_popups(data):
    return "<div style='text-align: center;'><b>SUPPLIER </b> <br/> <br/><b> District: </b> {} <br/></b><b> Regency: </b>{}</b><br/><br/>Type: {}<br/><br/>Risk score:<br/><span style='font-size: 1.5em;'>{}</span><br/></div>".format(data.name_district, data.name_muni, data.pe, data.risk_score_supp.to_upper())


    # readRDS = robjects.r['readRDS']
    # df_1 = readRDS('phy_da_hotels.RDS')
    # indo_lt = readRDS('indo_l0.RDS')


def get_data(inp_query, inp_unit, inp_time):
    load_data()
    if inp_query == "2":
        physical_data = read_csv('physical_assets_new.txt', delimiter='\t')
        query_result = physical_data[['id_district', 'name_district', 'id_muni', 'name_muni', 'hotel', 'h_size', 'office', 'o_size', 'supply', 'perish', 'essential','score_118', 'score_218', 'score_318', 'score_319']]
        query_result = gather(query_result, "Time", "comp_score", ["score_118","score_218", "score_318", "score_319"])

    elif inp_query == "1":
        supply_data = read_csv('supply_chain_new.txt', delimited='\t')
        query_data =  supply_data[['id_district', 'name_district', 'id_muni', 'name_muni', 'hotel', 'h_size', 'office', 'o_size', 'supply', 'perish', 'essential','score_118', 'score_218', 'score_318', 'score_319']]
        query_result = gather(query_result, "Time", "comp_score", ["score_118","score_218", "score_318", "score_319"])

    elif inp_query == "3":
        query_data = None
        return query_data

    # check out shinny data part later
    # code here

        indo_l0['Popup'] = create_popups(indo_l0, "Country")
        return indo_l0

    elif (inp_unit == "1"):
        query_data.groupby(['id_district', 'name_district'])['comp_score'].agg(['mean'])
        query_data.rename(columns={'mean':'comp_score'}, inplace=True)
        indo_l1  = pd.merge(indo_l1, query_data,
                  left_on='device',
                  right_on='id_district',
                  how='left')

        indo_l1.rename(columns={'NAME_1':'NAME'}, inplace=True)
        indo_l1 = indo_l1['Popup'] = create_popups(indo_l1, "Province")
        return indo_l1

    elif (inp_unit == "2"):
        indo_l2  = pd.merge(indo_l2, query_data,
                  left_on='device',
                  right_on='id_district',
                  how='left')

        indo_l2.rename(columns={'NAME_2':'NAME'}, inplace=True)
        indo_l2 = indo_l2['Popup'] = create_popups(indo_l2, "Regency")
        return indo_l2

def hotels_data():
    readRDS = robjects.r['readRDS']
    hd = readRDS('phy_da_hotels.RDS')
    hd['h_popup'] = h_popups(hd)
    return hd

def office_data():
    readRDS = robjects.r['readRDS']
    od = readRDS('phy_da_offices.RDS')
    od['o_popup'] = o_popups(od)
    return od

def suppliers_data():
    readRDS = robjects.r['readRDS']
    sd = readRDS('supp_da_suppliers.RDS')
    sd['pe'] = np.NaN
    sd.loc[sd.perish == 1, 'pe'] = "Perish"
    sd.loc[sd.essential == 1, 'pe'] ="Essential"
    sd.loc[sd.perish == 0 and sd.essential == 0, 'pe'] ="No Perish and No Essential"
    sd['sd_popup'] = sd_popups(sd)

    sd['icon_name'] = np.NaN

    sd.loc[sd.pe == "No Perish and No Essential" and sd.risk_score_supp == -1, 'icon_name'] = "npe_little_r"
    sd.loc[sd.pe == "No Perish and No Essential" and sd.risk_score_supp == 0, 'icon_name']  = "npe_some_r"
    sd.loc[sd.pe == "No Perish and No Essential" and sd.risk_score_supp == 1, 'icon_name']  = "npe_medium_r"
    sd.loc[sd.pe == "No Perish and No Essential" and sd.risk_score_supp == 2, 'icon_name']  = "npe_significant_r"
    sd.loc[sd.pe == "No Perish and No Essential" and sd.risk_score_supp >= 3, 'icon_name']  =  "npe_high_r"


    sd.loc[sd.pe != "No Perish and No Essential" and sd.risk_score_supp == -1, 'icon_name'] = "pe_little_r"
    sd.loc[sd.pe != "No Perish and No Essential" and sd.risk_score_supp == 0, 'icon_name']  =  "pe_some_r"
    sd.loc[sd.pe != "No Perish and No Essential" and sd.risk_score_supp == 1, 'icon_name']  =  "pe_medium_r"
    sd.loc[sd.pe != "No Perish and No Essential" and sd.risk_score_supp == 2, 'icon_name']  =  "pe_significant_r"
    sd.loc[sd.pe != "No Perish and No Essential" and sd.risk_score_supp >= 3, 'icon_name']  =  "pe_high_r"

    return sd


