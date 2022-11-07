import io
import os
import json
import traceback
import urllib.parse
import boto3
import copy
import botocore.response as br
import pyodata
import requests
from PIL import Image
import base64

from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

#clients
s3       = boto3.resource('s3')
smclient = boto3.client('secretsmanager')
lookoutvision_client = boto3.client('lookoutvision')
ddb = boto3.resource('dynamodb')
sapauth={}

#constants
#Replace the below variables with the API endpoint if using SAP BTP
#for eg if the API URL is https://359600betrial-trial.integrationsuitetrial-apim.us10.hana.ondemand.com:443/359600betrial/API_DEFECT_SRV
#DEFECT_SERVICE = /359600betrial/API_DEFECT_SRV
#ATTACHMENT_SERVICE = /359600betrial/API_CV_ATTACHMENT_SRV

DEFECT_SERVICE='/sap/opu/odata/sap/API_DEFECT_SRV'
DEFECT_SERVICE_PATH='/sap/opu/odata/sap/ZAPI_QUAL_NOTIFICATION_SRV'
ATTACHMENT_SERVICE='/sap/opu/odata/sap/API_CV_ATTACHMENT_SRV'
NOTIF_SERVICE = '/359600betrial/ZSERVICE_PM_NOTIFICATION_SRV/'

def handler(event,context):
    try:
# Incoming json file
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'],\
             encoding='utf-8')
        # Read the json file   
        print(bucket)
        print(key)
        
        S3client = boto3.client("s3")
        
        fileobj = S3client.get_object(
        Bucket=bucket,
        Key=key
        ) 
        
        
        filedata = json.loads(fileobj['Body'].read().decode('utf-8'))
        print("here")
        if filedata['prediction'] == 1:

            Snotif = getODataClient(NOTIF_SERVICE)
            notif_data = {}
            #If you choose to pass the file data in the long text
            #Longtext = json.dumps(filedata)
            #Longtext = Longtext.replace("\\r\\n  ", " ")
            print("popualre")
            
            ddbConfigTable = ddb.Table(os.environ.get('DDB_CONFIG_TABLE'))
        
            response = ddbConfigTable.query(KeyConditionExpression=Key('equi').eq(os.environ.get('equi')))
            print(response['Items'])
           
            configItem = response['Items']
            print(type(configItem))
            
            notif_data["FunctLoc"] = configItem[0]['location']
            notif_data["Equipment"] = configItem[0]['sapequi']
            notif_data['ShortText'] = 'RUL threshold'
            notif_data['LongText'] = " For detailed diagnostics, check S3  " +bucket+" file "+key
            
            #print(notif_data)
            
            create_request = Snotif.entity_sets.NOTIF_CREATESet.create_entity()
            create_request.set(**notif_data)
            try:
                new_notif_set = create_request.execute()
            except pyodata.exceptions.HttpError as ex:
                 print(ex.response.text)
            print('Notification Number'+new_notif_set.NotifNo)
    except Exception as e:
        traceback.print_exc()
        return e
        
def getODataClient(service,**kwargs):
    try:
        sap_host = os.environ.get('SAP_HOST_NAME')
        sap_port = os.environ.get('SAP_PORT')
        sap_proto = os.environ.get('SAP_PROTOCOL')
        serviceuri = sap_proto + '://' + sap_host + ':' + sap_port + service
       
        print('service call:'+serviceuri)
       #Secret Manager
        authresponse = smclient.get_secret_value(
            SecretId=os.environ.get('SAP_AUTH_SECRET')
        )

        sapauth = json.loads(authresponse['SecretString'])
        
       #Set session headers - Auth,token etc
        session = requests.Session()
        # If using SAP Netweaver Gateway, please uncomment
        #session.auth = (sapauth['user'],sapauth['password'])
        #If using BTP, please uncomment
        session.headers.update({'APIKey': sapauth['APIKey']})
        response = session.head(serviceuri, headers={'x-csrf-token': 'fetch'})
        token = response.headers.get('x-csrf-token', '')
        session.headers.update({'x-csrf-token': token})
        oDataClient = pyodata.Client(serviceuri, session)
        
        return oDataClient

    except Exception as e:
          traceback.print_exc()
          return e        



   




