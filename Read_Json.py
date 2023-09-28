import json
  
# Opening JSON file
f = open('impacts_DNN_UL2017.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)
  
# Iterating through the json
# list
POI_name = data['POIs'][0]['name']
POI_fit = data['POIs'][0]['fit']
print POI_name
#print POI_fit

r_impact_hi = POI_fit[2] - POI_fit[1]
r_impact_lo = POI_fit[0] - POI_fit[1]

print r_impact_hi, r_impact_lo


params = data["params"]
#print params[0]['fit']

parameter_to_track = ["cons_EWK_bkg", "cons_QCD_bkg","cons_top_bkg"]
parameter_info = {}

parameter_info[POI_name]=[r_impact_lo,POI_fit[1],r_impact_hi]

for i,para in enumerate(data["params"]):
    para_name = params[i]['name']
    if para_name in parameter_to_track:
        print params[i]['name']
        print params[i]['fit']
        parameter_info[para_name]=params[i]['fit']


print(parameter_info)#
print(abs(parameter_info['cons_EWK_bkg'][0]) if abs(parameter_info['cons_EWK_bkg'][0])>abs(parameter_info['cons_EWK_bkg'][2]) else abs(parameter_info['cons_EWK_bkg'][2]))
f.close()
