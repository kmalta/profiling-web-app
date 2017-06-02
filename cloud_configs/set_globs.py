import sys
sys.path.insert(0,'.')

from which_cloud import *
from aws.aws_regions import *

#CHANGE DEFAULT TO AWS WHEN READY
from aristotle.aristotle_cfg import *
from aristotle.aristotle_node_image import *
if cloud_name == 'aws':
    from aws.aws_cfg import *
    from aws.aws_node_image import *
elif cloud_name != 'aristotle':
    print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"