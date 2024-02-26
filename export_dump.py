import pandas as pd
import requests
import configparser
import re

policiy_response = {}

def connect_nr():
    config = configparser.ConfigParser()
    config.read('secret.cfg')
    obj = {}
    obj["apiKey"] = config.get('NR_API_DETAILS', 'api_key')
    obj["endpointPolicies"] = config.get('NR_API_DETAILS', 'endpoint_policies')
    obj["endpointNRQLConditions"] = config.get('NR_API_DETAILS', 'endpoint_nrql_alert_condition')
    return obj


api_key = str(connect_nr()["apiKey"])
endpointPolicies = str(connect_nr()["endpointPolicies"])
endpointNRQLConditions = str(connect_nr()["endpointNRQLConditions"])


epr_ids = pd.read_csv("Tier1_EPR.csv")
epr_id_list = list(epr_ids['EPR_ID'])
policies_dump = {} 

def fetch_alert_policies_for_application(epr):
    alert_policies_endpoint = endpointPolicies
    headers = {
        'X-Api-Key': api_key
    }
    response = requests.get(alert_policies_endpoint, headers=headers)
    policy_details = response.json()["policies"]
    policiy_response["message"] = policy_details
    policy_ids = []
 

    for policy in policy_details:
        if policy["name"].split(".")[0].strip() == str(epr):
            policy_ids.append(policy["id"])
    return policy_ids

for epr_id in epr_id_list :
    policies_dump[str(epr_id)] = []
    l = fetch_alert_policies_for_application(epr_id)
    for x in l:
        policies_dump[str(epr_id)].append(x)
# print(policies_dump)

def fetch_event(query):
    query = query.lower()
    pattern = r'from\s+(\w+)'
    match = re.search(pattern, query.replace("`", ""))
    if match:
        word_after_from = match.group(1)
        return word_after_from
    else:
        return "No event"

def fetch_policy_name(policyID, epr):
    policy_details = policiy_response["message"]
    policy_name = []
    for policy in policy_details:
        if str(policy["name"].split(".")[0].strip()) == str(epr) and str(policy["id"]) == policyID:
            policy_name.append(policy["name"])
    return policy_name[0]


def fetch_conditions(policy_id, epr_id):
    url = f'{endpointNRQLConditions}?policy_id={str(policy_id)}'
    headers = {'X-Api-Key': api_key}
    response = requests.get(url, headers=headers)
    data = response.json()

    col = [ "Alert Condition,Policy,Query" ]
    content = []
    content.append(col)

    row_data = {
        "EPR ID" : [],
        "Policy ID" : [],
        "Alert Condition" : [],
        "Policy" : [],
        "Query" : [],
        "Type" : [],
        "Critical Threshold" : [],
        "Warning Threshold" : [],
        "Event" : []
            }
    
    for con in data["nrql_conditions"]:
        row_data["EPR ID"].append(str(epr_id))
        row_data["Policy ID"].append(str(policy_id))
        row_data["Alert Condition"].append(con["name"])
        row_data['Policy'].append(fetch_policy_name(str(policy_id), str(epr_id)))
        row_data["Query"].append(con["nrql"]["query"])
        row_data["Event"].append(str(fetch_event(con["nrql"]["query"])))
        row_data["Type"].append(con["type"])
        priorities = []
        for x in con["terms"]:
            priorities.append(x["priority"])
        
        if len(priorities) == 2:
            for x in con["terms"] :
                if x["priority"] == "critical":
                    row_data["Critical Threshold"].append(f"{x["operator"]} {x["threshold"]} for {x["duration"]} minutes")
                if x["priority"] == "warning":
                    row_data["Warning Threshold"].append(f"{x["operator"]} {x["threshold"]} for {x["duration"]} minutes")
        elif len(priorities) == 1:
             if "critical" in priorities :
                for x in con["terms"] :
                    row_data["Critical Threshold"].append(f"{x["operator"]} {x["threshold"]} for {x["duration"]} minutes")

                    row_data["Warning Threshold"].append(f"NA")
             
             else:

                for x in con["terms"] :
                    row_data["Warning Threshold"].append(f"{x["operator"]} {x["threshold"]} for {x["duration"]} minutes")

                    row_data["Critical Threshold"].append(f"NA")

    return row_data


spreadsheet_obj = {"alerts" : []}

for x in epr_id_list:
    for y in policies_dump[str(x)]:
        spreadsheet_obj["alerts"].append(fetch_conditions(y, x))

alerts_list = spreadsheet_obj["alerts"]

dataframe_obj = {
    "EPR ID" : [],
    "Policy ID" : [],
    "Alert Condition" : [],
    "Policy" : [],
    "Query" : [],
    "Type" : [],
    "Critical Threshold" : [],
    "Warning Threshold" : [],
    "Event" : []
}

for x in alerts_list:
    for i1 in x["EPR ID"]:
        dataframe_obj["EPR ID"].append(i1)
    for i2 in x["Policy ID"]:
        dataframe_obj["Policy ID"].append(i2)
    for i3 in x["Alert Condition"]:
        dataframe_obj["Alert Condition"].append(i3)
    for i4 in x["Policy"]:
        dataframe_obj["Policy"].append(i4)
    for i5 in x["Query"]:
        dataframe_obj["Query"].append(i5)
    for i6 in x["Type"]:
        dataframe_obj["Type"].append(i6)
    for i7 in x["Critical Threshold"]:
        dataframe_obj["Critical Threshold"].append(i7)
    for i8 in x["Warning Threshold"]:
        dataframe_obj["Warning Threshold"].append(i8)
    for i9 in x["Event"]:
        dataframe_obj["Event"].append(i9)

df = pd.DataFrame(dataframe_obj)
df.to_excel("ALERT_DUMP.xlsx", index=False)


print("="*25)
print("EXCEL GENERATED")
print("="*25)



