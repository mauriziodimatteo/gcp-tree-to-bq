# GCP resource hierarchy to BigQuery

## Introduction
With this script you can export your Google Cloud resource hierarchy to a BigQuery parent-child table with the following schema:

```
{
    "mode": "NULLABLE",
    "name": "name",
    "type": "STRING"
},
{
    "mode": "NULLABLE",
    "name": "display_name",
    "type": "STRING"
},
{
    "mode": "NULLABLE",
    "name": "parent_name",
    "type": "STRING"
}
```

Final result will look something like this:

| name                     | display_name | parent_name              |
|--------------------------|--------------|--------------------------|
| organizations/0123456789 | example.com  | null                     |
| folders/11111111111      | Folder A     | organizations/0123456789 |
| folders/22222222222      | Subfolder A1 | folders/11111111111      |
| projects/333333333333    | Project X    | folders/22222222222      |


## Required permissions

In order for you, or the service account, to have visibility of the full resource hierarchy and write the results to BigQuery, you should have the following roles:

Organization:
- `roles/resourcemanager.organizationViewer`
- `roles/resourcemanager.folderViewer`

Project:
- `roles/bigquery.jobUser`
- `roles/bigquery.dataEditor`

If you are willing to create Custom Roles, you can (and should) further restrict access. For more details read [Listing all resources in your hierarchy](https://cloud.google.com/resource-manager/docs/listing-all-resources).

## Running the script
Fill in `set_env.sh` with your values and run it before running the python script.