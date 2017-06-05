# Profiling Web Application
## Master's Project for UCSB's RACELab

The repository contains a project 

## Building This Project

1. Clone this repository.
2. Change your working directory to the cloned repository.
3. Find the *aws_cfg.py.template* file in the templates directory and copy it to *cloud_configs/aws/aws_cfg.py*
4. Add your AWS Access ID and Secret Key to the file.
5. If your AWS account has a sufficient spot limit, change the *launch_type* variable to *'spot'*.  You will see considerable savings (up to 10x) by using this option.  Otherwise, you must use *'on-demand'*
6. Create a copy of your AWS private key and set it to the path *cloud_configs/aws/aws-key.pem*
7. Build the dependencies with the following command:

```bash
source setup_app.sh
```

8. Note, this will request an instance, build an AWS AMI, and terminate said instance.  The total cost of this is at most **$0.262** if *launch_type = 'on-demand'*.

## Using the Web Application

* To start the node.js server and Flask endpoint:

```bash
source start_script.sh
```

* To stop the node.js server and Flask endpoint:

```bash
source stop_script.sh
```

* To clean the MongoDB database, wipe the synth dataset files, all of the profiles, and all of the logs:

```bash
source clean_files.sh
```

** WARNING: This will delete any data created and start the app from a clean slate.  Only do this if you do not care about the data being lost. **

* To add a dataset:
    1. Upload your data to S3.
    2. Make the dataset readable by all.
    3. Copy the template:
        ```bash
        cp templates/dataset.cfg.template data_configs/aws/<your dataset's name>.cfg
        ```
    4. Fill out the fields for the dataset file.  For an example see _templates/example-dataset.cfg_

