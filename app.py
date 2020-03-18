import requests
import json


urls = {
    'token_url': 'https://global.edge.bamgrid.com/token',
    'collection_url': 'https://search-api-disney.svcs.dssott.com/svc/search/v2/graphql/persisted/query/core/CollectionBySlug',
    'section_url': 'https://search-api-disney.svcs.dssott.com/svc/search/v2/graphql/persisted/query/core/SetBySetId'
}


def get_auth_token():
    payload = {
        'grant_type': 'refresh_token',
        'latitude': 0,
        'longitude': 0,
        'platform': 'browser',
        'refresh_token': 'eyJraWQiOiJlNzRlOTlhNy04NDNlLTQ2NmEtOTVhMS02YjA0MjYwNThlNmYiLCJhbGciOiJFZERTQSJ9.eyJhdWQiOiJ1cm46YmFtdGVjaDpzZXJ2aWNlOnRva2VuIiwic3ViamVjdF90b2tlbl90eXBlIjoidXJuOmJhbXRlY2g6cGFyYW1zOm9hdXRoOnRva2VuLXR5cGU6ZGV2aWNlIiwibmJmIjoxNTg0MzQxMDc3LCJncmFudF90eXBlIjoidXJuOmlldGY6cGFyYW1zOm9hdXRoOmdyYW50LXR5cGU6dG9rZW4tZXhjaGFuZ2UiLCJpc3MiOiJ1cm46YmFtdGVjaDpzZXJ2aWNlOnRva2VuIiwiY29udGV4dCI6ImV5SmhiR2NpT2lKdWIyNWxJbjAuZXlKemRXSWlPaUptT0RObE1qQXdZUzA0WmpFMExUUXpZbVF0T0RObE1pMHlaV1EzTmpJeE56VXdZemdpTENKaGRXUWlPaUoxY200NlltRnRkR1ZqYURwelpYSjJhV05sT25SdmEyVnVJaXdpYm1KbUlqb3hOVGcwTXpJNU1EVXpMQ0pwYzNNaU9pSjFjbTQ2WW1GdGRHVmphRHB6WlhKMmFXTmxPbVJsZG1salpTSXNJbVY0Y0NJNk1qUTBPRE15T1RBMU15d2lhV0YwSWpveE5UZzBNekk1TURVekxDSnFkR2tpT2lJMU1HRTBNMlU1WkMweU1tRmtMVFJoTldZdE9HUmpNaTB4TUdZMU5HVXhPR00xT0RjaWZRLiIsImV4cCI6MTU5OTg5MzA3NywiaWF0IjoxNTg0MzQxMDc3LCJqdGkiOiI3NzI0NDY1OS04NzBiLTQ4ZTEtYmY4Yi00NmQ2NmE1MTk2MDcifQ.EWn4KXvf3xgYb9gDSNbcD3xN4qcQVwiEUd45q2sfG9_Zcy06OnTzfIokWAAuNUQzc9Fm6bpEh7__D7M8KZ_IBw'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'authorization': 'Bearer ZGlzbmV5JmJyb3dzZXImMS4wLjA.Cu56AgSfBTDag5NiRA81oLHkDZfu5L3CKadnefEAY84'
    }

    token = requests.post(
        urls['token_url'], data=payload, headers=headers).json()
    return token


def get_section_info():
    section_info_dict = {}

    token_data = get_auth_token()
    auth_token = token_data['access_token']

    params = {
        'variables': '{"preferredLanguage":["en"],"contentClass":"home","slug":"home","contentTransactionId":"2c278173-12a7-4bb6-85c0-13c23cd93370"}'
    }

    headers = {
        'authorization': "Bearer " + auth_token,
    }

    data = requests.get(urls['collection_url'],
                        params=params, headers=headers).json()

    index = 0
    sections = data['data']['CollectionBySlug']['containers']

    for i in range(2, len(sections)):
        section_info_dict[index] = {}
        if 'refId' in sections[i]['set'].keys():
            section_info_dict[index] = {
                'setId': sections[i]['set']['refId'], 'setType': sections[i]['set']['refType']}
        elif 'setId' in sections[i]['set'].keys():
            section_info_dict[index] = {
                'setId': sections[i]['set']['setId'], 'setType': sections[i]['set']['type']}

        index = index + 1

    return section_info_dict


def get_section_data(section_info):
    result_data = {}

    token_data = get_auth_token()
    auth_token = token_data['access_token']
    
    params = {
        'variables': '{"preferredLanguage": ["en"], "setId":"' + section_info['setId'] + '",'
                    '"setType":"' + section_info['setType'] + '", "contentTransactionId": "a099f643-6021-4b28-a687-512bbe546e0d"}'
    }

    headers = {
        'authorization': "Bearer " + auth_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = requests.get(urls['section_url'], 
                        params=params, headers=headers).json()

    result_data['Name'] = data['data']['SetBySetId']['texts'][0]['content']
    result_data['Items'] = []

    for i in range(len(data['data']['SetBySetId']['items'])):
        result_name = data['data']['SetBySetId']['items'][i]['texts'][0]['content']
        if(result_data['Name'] == "Collections"):
            result_image = data['data']['SetBySetId']['items'][i]['images'][4]['url']
        else:
            result_image = data['data']['SetBySetId']['items'][i]['images'][9]['url']

        result_data['Items'].append({'Name': result_name, 'Image': result_image})
    print(result_data)
    return result_data

open('data.json', 'w').close()

for key, value in get_section_info().items():   
    section_data = get_section_data(value)

    with open('data.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(section_data))
