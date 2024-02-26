import configparser
import requests
import pandas as pd

df = pd.read_csv("Tier1_EPR.csv")
epr_id_list = list(df['EPR_ID'])
policies_dump = {}

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


def fetch_alert_policies_for_application(epr):
    alert_policies_endpoint = endpointPolicies
    headers = {
        'X-Api-Key': api_key
    }
    response = requests.get(alert_policies_endpoint, headers=headers)
    policy_details = response.json()["policies"]
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




for eprid in epr_id_list:
    if len(policies_dump[str(eprid)]) == 0:
        print(eprid)