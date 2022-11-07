#!/usr/bin/env python3
from aws_cdk import App,Environment
from aws_lookout_equip.aws_lookout_equip_stack import AwsLookoutEquipStack
from AppConfig.config import Config

_config = Config()

app = App()

env = Environment(account=_config.account, region=_config.region)

AwsLookoutEquipStack(app,_config.stackname,env=env)

app.synth()
