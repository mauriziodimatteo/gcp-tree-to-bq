from google.cloud import resourcemanager_v3
from google.cloud import bigquery
import os 

# Read from ENV
org_id = os.environ.get('ORG_ID')
bq_project = os.environ.get('BQ_PROJECT')
bq_dataset = os.environ.get('BQ_DATASET')
bq_table = os.environ.get('BQ_TABLE') 

org_name = f'organizations/{org_id}'

class Asset():
    def __init__(self, name, display_name, parent_name):
        self.name = name
        self.display_name = display_name
        self.parent_name = parent_name

    def __repr__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


def get_organization(org_name, org_client):
    """
    Get organization details
    """

    request = resourcemanager_v3.GetOrganizationRequest(name=org_name)
    response = org_client.get_organization(request=request)

    return Asset(response.name, response.display_name, None)


def list_folders(parent_name, folders_client):
    """
    List folders under a folder or organization.
    """

    request = resourcemanager_v3.ListFoldersRequest(parent=parent_name)
    page_result = folders_client.list_folders(request=request)
    folders = [Asset(response.name, response.display_name,
                     response.parent) for response in page_result]

    return folders


def list_projects(parent_name, projects_client):
    """
    List projects under a folder or organization.
    """

    request = resourcemanager_v3.ListProjectsRequest(parent=parent_name)
    page_result = projects_client.list_projects(request=request)
    projects = [Asset(response.name, response.display_name,
                      response.parent) for response in page_result]

    return projects


def write_to_bq(assets, bq_project, bq_dataset, bq_table):
    """
    Write list of assets to BigQuery. 
    Dataset must already exist.
    Table will be created if necessary.
    """
    
    print('Writing to BigQuery')
    # Create BQ client
    bq_client = bigquery.Client()

    # Create job config
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField('name', bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField(
                'display_name', bigquery.enums.SqlTypeNames.STRING),
            bigquery.SchemaField(
                'parent_name', bigquery.enums.SqlTypeNames.STRING)
        ],
        write_disposition="WRITE_TRUNCATE"
    )

    # Run job
    table_id=f'{bq_project}.{bq_dataset}.{bq_table}'
    job=bq_client.load_table_from_json(
        [d.__dict__ for d in assets], table_id, job_config=job_config
    )

    # Wait for the job to complete
    job.result()

# Accumulator
discovered_assets=[]

# Get organization
org_client=resourcemanager_v3.OrganizationsClient()
discovered_assets += [get_organization(org_name, org_client)]

# Explore folders structure
folders_to_explore=[a.name for a in discovered_assets]
folders_client=resourcemanager_v3.FoldersClient()
while (folders_to_explore):
    parent=folders_to_explore.pop()
    print(f'Exploring folders in {parent}')
    children=list_folders(parent, folders_client)
    discovered_assets += children
    folders_to_explore += [c.name for c in children]

# List projects in folders
projects_client=resourcemanager_v3.ProjectsClient()
folders_to_explore=[a.name for a in discovered_assets]
for f in folders_to_explore:
    print(f'Exploring projects in {f}')
    discovered_assets += list_projects(f, projects_client)

write_to_bq(discovered_assets, bq_project, bq_dataset, bq_table)