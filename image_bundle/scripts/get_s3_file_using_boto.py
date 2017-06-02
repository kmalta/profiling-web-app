import sys, os, boto


def s3_boto_connection(key_id, secret_key, s3_service_path, s3_host):
    s3conn = boto.connect_s3(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
        is_secure=False,
        port=8773,
        path=s3_service_path,
        host=s3_host)
    return s3conn


def walrus_boto_connection(key_id, secret_key, s3_service_path, s3_host):
    s3conn = boto.connect_walrus(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
        is_secure=False,
        port=8773,
        path=s3_service_path,
        host=s3_host)
    return s3conn


def start_s3_boto_connection(cloud_name, key_id, secret_key, s3_service_path, s3_host):
    if cloud_name == 'aristotle':
        return walrus_boto_connection(key_id, secret_key, s3_service_path, s3_host)
    elif cloud_name == 'aws':
        return s3_boto_connection(key_id, secret_key, s3_service_path, s3_host)
    else:
        print "WE DID NOT RECEIVE AN APPROPRIATE CLOUD NAME"

def get_dataset(s3url, s3conn):
    s3url_arr = s3url.split('/')
    dataset = s3url_arr[-1]
    bucket_name = s3url_arr[-2]

    #Clean Up If Error Occurred.
    if os.path.exists('check_if_file_written'):
        os.system('rm check_if_file_written')
    if os.path.exists('/mnt/' + dataset):
        os.system('sudo rm /mnt/' + dataset)


    f = open('check_if_file_written', 'w')
    f.write(str(0))
    f.close()

    try:
        bucket = s3conn.get_bucket(bucket_name)
        key = bucket.get_key(dataset)
        key.get_contents_to_filename('/mnt/' + dataset)

        f = open('check_if_file_written', 'w')
        f.write(str(1))
        f.close()

    except:

        f = open('check_if_file_written', 'w')
        f.write(str(2))
        f.close()



def main():

    clp = sys.argv
    s3url = clp[1]
    cloud_name = clp[2]
    key_id = clp[3]
    secret_key = clp[4]
    s3_service_path = clp[5]
    s3_host = clp[6]

    s3conn = start_s3_boto_connection(cloud_name, key_id, secret_key, s3_service_path, s3_host)
    get_dataset(s3url, s3conn)

if __name__ == "__main__":
    main()