import requests
import payloads

import pandas as pd

from datetime import datetime

url = 'https://api.clockify.me/api/'
headers={'x-api-key' : ''}

actions = {
    1: 'Add time records',
    2: 'Remove time records',
    3: 'List records (To be developed)',
    4: 'Post single time entry',
    5: 'Remove sigle time entry',
}

params = {}

def run_clockify_filler():
    print('Hello and welcome to Clockify filler. Please select what you want me to do')
    for action in actions:
        print(action, '-', actions[action])
    selected_action = input('Action: ')
    api_key = input('Please provide your api key. It can be found in profile settings: ')
    headers['x-api-key'] = api_key
    projectId, workspaceId = get_project()
    
    if selected_action == '1':
        post_time_entry(projectId, workspaceId)
    elif selected_action == '2':
        entries = get_time_entries(workspaceId)
        remove_time_entry(entries, workspaceId, projectId)


def get_workspace_name():
    """Asks user to select workspace if there is more than one found"""
    workspaces = requests.get(url + 'v1/workspaces', headers=headers)
    if len(workspaces.json()) == 1:
        return workspaces.json()[0]['id']
    else:
        for index, item in enumerate(workspaces.json(), start=1):
            print(f'{index} - {item["name"]}')
        workspaceId = int(input('Please select number of the workspace you want to amend time: ')) - 1
        return workspaces.json()[workspaceId]['id']


def get_project():
    """Function asks user to select project"""
    workspaceId = get_workspace_name()
    projects = requests.get(url + f'v1/workspaces/{workspaceId}/projects', headers=headers)
    for index, item in enumerate(projects.json(), start=1):
        print(f'{index} - {item["name"]}')
    projectId = int(input('Please select number of the project you want to amend time: ')) - 1
    projectId = projects.json()[projectId]['id']
    return projectId, workspaceId


def get_and_validate_date(prompt):
    while True:
        try:
            date_value = input(prompt)
            datetime.strptime(date_value, '%Y-%m-%d')
            return date_value
        except ValueError:
            print('Incorrect date format. Please enter date in format YYYY-MM-DD.')


def get_business_days():
    """Refactor to handle incorrect user input"""
    while True:
        start_date = get_and_validate_date('Please provide start date in format YYYY-MM-DD: ')
        end_date = get_and_validate_date('Please provide end date in format YYYY-MM-DD: ')
        user_confirm = str(input(f'Are these dates correct? Start: {start_date} End: {end_date} [y/n]') or 'y')
        if user_confirm[0] in ['y','Y']:
            business_dates = pd.bdate_range(start_date, end_date)
            return business_dates
        else:
            print('Let\'s try again')


def post_time_entry(projectId, workspaceId):
    payload = payloads.time_entry_payload
    payload['projectId'] = projectId
    for date in get_business_days():
        date = date.strftime('%Y-%m-%d')
        payload['start'] = f'{date}T08:00:00Z'
        payload['end'] = f'{date}T16:00:00Z'
        post_request = requests.post(url + f'v1/workspaces/{workspaceId}/time-entries', headers=headers, json=payload)
        print(f'Status code - {post_request.status_code}')

def get_time_entries(workspaceId):
    start_date = input('Please provide start date in format YYYY-MM-DD: ')
    end_date = input('Please provide end date in format YYYY-MM-DD: ')
    params['start'] = f'{start_date}T00:00:00Z'
    params['end'] = f'{end_date}T23:00:00Z'
    user = requests.get(url + f'v1/user', headers=headers)
    userId = user.json()['id']
    entries = requests.get(url + f'v1/workspaces/{workspaceId}/user/{userId}/time-entries', params=params, headers=headers)
    return entries.json()

def remove_time_entry(entries, workspaceId, projectId):
    for entry in entries:
        print(entry)
        if entry.get('projectId') == projectId:
            entryId = entry.get('id')
            del_request = requests.delete(url + f'v1/workspaces/{workspaceId}/time-entries/{entryId}', headers=headers)
            print(f'Status code - {del_request.status_code}')

if __name__ == '__main__':
    run_clockify_filler()
