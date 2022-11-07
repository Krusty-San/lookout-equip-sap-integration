from LambdaLayer.LambdaLayers import LambdaLayers
from aws_cdk import ( 
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_s3_notifications as s3_notifications,
    App,
    Stack,
    Duration,
    
    
)
from aws_cdk.aws_lambda_event_sources import S3EventSource
from constructs import Construct

import os
from   os import path

class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        __dirname = (os.path.dirname(__file__))

# set the bucket and inference folder as trigger

        self._function = _lambda.Function(
            self, 'detectAnomalies',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset(path.join(__dirname, './AnomalyDetection')),
            handler='detectAnomalies.handler',
            layers=[props['lambdaLayer']], 
            # props['boto3Layer'],
            # props['pillowLayer'],
            # props['requestsLayer']],
            environment={
                "SAP_AUTH_SECRET": props['config'].sapauth,
                "SAP_HOST_NAME": props['config'].saphost,
                "SAP_PROTOCOL": props['config'].sapprotocol,
                "SAP_PORT": props['config'].sapport,
                "PROJECT_NAME": "",
                "DDB_CONFIG_TABLE": props['config'].ddbtable,
                "BUCKET": props['config'].bucketname,
                "INFERENCEFOLDER": props['config'].inferencefolder,
                "equi": 'Equipment'
            },
            vpc=props['vpc'],
            vpc_subnets=ec2.SubnetSelection(subnets=props['subnet']),
            memory_size=2048,
            timeout=Duration.seconds(props['config'].timeout),
            role=props['lambdarole']
        )

        # self._function.add_event_source(
        #     S3EventSource(bucket=props['bucket'],
        #     events=[s3.EventType.OBJECT_CREATED],
        #     )
        # )
        
        bucket = s3.Bucket.from_bucket_name(self, id="l4ebucket", bucket_name=props['config'].bucketname)
        

        
        #bucket =props['config'].bucketname
        inference = props['config'].inferencefolder

        notification = s3_notifications.LambdaDestination(self._function)
        notification.bind(self, bucket)
        bucket.add_object_created_notification(notification, s3.NotificationKeyFilter(prefix=inference))
        

