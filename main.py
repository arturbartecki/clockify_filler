import requests
import payloads

url = "https://api.clockify.me/api/"
headers={"x-api-key" : ''}

def run_clockify_filler():
    print("Hello and welcome to Clockify filler. Please select what you want me to do:")
    get_all_projects()

def get_workspace_name():
    """Future update: add handling multiple workspaces"""
    r = requests.get(url + 'v1/workspaces', headers=headers)
    return r.json()[0]['id']

def get_all_projects():
    """Future update: add handling multiple projects"""
    workspaceId = get_workspace_name()
    r = requests.get(url + f'v1/workspaces/{workspaceId}/projects', headers=headers)
    projectId = None
    for item in r.json():
        if item['name'] == 'Kyriba':
            projectId = item['id']
    return projectId, workspaceId

def post_time_entry():
    projectId, workspaceId = get_all_projects()
    payload = payloads.time_entry_payload
    payload['projectId'] = projectId
    r = requests.post(url + f'v1/workspaces/{workspaceId}/time-entries', headers=headers, json=payload)
    print (r.status_code)

if __name__ == "__main__":
    post_time_entry()