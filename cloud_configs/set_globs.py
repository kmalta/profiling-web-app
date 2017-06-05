import sys
sys.path.insert(0,'.')

from which_cloud import *
from aws.aws_vars import *
from aws.aws_cfg import *
from aws.aws_node_image import *
if cloud_name == 'aristotle':
    from aristotle.aristotle_vars import *
    from aristotle.aristotle_cfg import *
    from aristotle.aristotle_node_image import *
elif cloud_name != 'aws':
    print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"