from aws_cdk import ( 
    RemovalPolicy,
    aws_dynamodb as ddb
)
from constructs import Construct
class ddbConstruct(Construct):
    def __init__(self, scope: Construct, id: str,props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self._ddb = ddb.Table(self,'configdb', 
                                    table_name=props['config'].ddbtable,
                                    partition_key=ddb.Attribute(name='equi', 
                                                   type=ddb.AttributeType.STRING),
                                    sort_key=ddb.Attribute(name='equipment', 
                                             type=ddb.AttributeType.STRING),
                                    removal_policy=RemovalPolicy.DESTROY )
    

        
        self._ddb.grant_read_write_data(props['ddbrole'])
              
                                    
                                        

        
        
 
