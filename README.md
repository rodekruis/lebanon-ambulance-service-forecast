# lebanon-ambulance-services-forecast
template and documentation to build an Azure function app in python.

It assumes that the function needs to be triggered at regular intervals; if an HTTP trigger is required see [the Azure documentation](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python#http-trigger-and-bindings).

## Requirements
Locally:
1. Python 3.*
2. [Azure Functions Core Tools and Visual Studio Code](https://docs.microsoft.com/en-us/azure/developer/python/tutorial-vs-code-serverless-python-01#configure-your-environment)

In Azure:
1. An [Azure Resource Group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/overview) for linux resources (BEST PRACTICE: make a new resource group for each project)
2. The role of "Contributor" in that resource group (ask Maarten)

## Basic setup
1. [create an empty python function app with Visual Data Studio](https://docs.microsoft.com/en-us/azure/developer/python/tutorial-vs-code-serverless-python-02)
2. Copy-paste your script into `__init__.py`, see [this template](https://github.com/jmargutt/azure-python-function-app/blob/main/my-function/__init__.py)
3. Copy-paste the modules required to run your python script into `requirements.txt`. BEST PRACTICE: add only what is needed. If in doubt, start a new virtual env for your project, install only what is needed and then get requirements with
```sh 
$ pip freeze > requirements.txt
```
4. Configure how often your function will run in `function.json`: edit the [cron expression](https://crontab.guru/) in the field `schedule`
5. Debug locally. Example: to run the function locally, execute this command from the project root folder
```sh 
$ func start --functions <my-function> --python --verbose --build remote
```
6. [Deploy to Azure using Visual Studio Code](https://docs.microsoft.com/en-us/azure/developer/python/tutorial-vs-code-serverless-python-05)
7. Store your code on [rodekruis' github](https://github.com/rodekruis): create a new repo named `<my-function-app>-function-app` and put your code there

You will now be able to monitor your function in the [Azure portal](https://portal.azure.com/). A new resource of type "Application Insights" will be created, where you can monitor runs, errors, etc. Good to know: in Azure portal you can also check the logs within the Function App (`Functions > <my-function> > Code + Test > Logs`)

## Data
If your function takes data as input/output, the recommended workflow is to store the data in an [Azure storage account](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview) and download/upload it from/to there.

When you create a new function app with Visual Data Studio a new storage account will be created automatically in the same resource group; you can use this one or an existing one. Good to know: individual files in Azure storage are called 'blobs' and directories 'containers'.
1. Create a container within the storage via the Azure portal
2. Configure the function in `__init__.py`

They way your function exchange data with the storage is via [azure-storage-blob](https://pypi.org/project/azure-storage-blob/), which needs the rights credentials. If you are using the default storage that is created with the function, the credentials are already accessible as an environmental variable named `AzureWebJobsStorage`; you can get it with
```
credentials = os.environ['AzureWebJobsStorage']
```
and then get your data with e.g.
```
blob_service_client = BlobServiceClient.from_connection_string(credentials)
blob_client = blob_service_client.get_blob_client(container='<my-container>', blob='<my-data-file>')
data = pickle.loads(blob_client.download_blob().readall())
```
[OPTIONAL] If you are using a different storage account
1. [Copy the credentials from the Azure portal](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python#copy-your-credentials-from-the-azure-portal)
2. [Add them in the function settings](https://docs.microsoft.com/en-us/azure/azure-functions/functions-how-to-use-azure-function-app-settings#settings), so that they will be callable within the function as environmental variables
3. Add them in `local.settings.json`, in order to be able to run the function locally

## Credentials, keys and secrets
If your function needs to use an API (e.g. Google Maps) and requires credentials, **do NOT store them in `__init__.py`**, since this will expose them to whoever has access to the resource group. The recommended workflow is to store them in an [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/general/overview).
1. Create an Azure Key Vault in the same resource group
2. Ask to be given the role of "Key Vault Secrets Officer" in the vault (ask the admin of the resource group)
3. Add your credentials in the vault under `Secrets`, via the Azure portal
4. [Integrate the credentials in your function app](https://daniel-krzyczkowski.github.io/Integrate-Key-Vault-Secrets-With-Azure-Functions/)
