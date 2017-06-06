import sys, os, boto

def start_s3_boto_connection(key_id, secret_key):
    print "Starting Boto S3 Connection."
    s3conn = boto.connect_s3(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key)
    return s3conn

def get_dataset(s3url, s3conn):
    s3url_arr = s3url.split('/')
    dataset = s3url_arr[-1]
    bucket_name = s3url_arr[-2]

    if os.path.exists('/mnt/' + dataset):
        os.system('sudo rm /mnt/' + dataset)

    bucket = s3conn.get_bucket(bucket_name)
    key = bucket.get_key(dataset)
    key.get_contents_to_filename('/mnt/' + dataset)

def main():
    clp = sys.argv
    s3url = clp[1]
    key_id = clp[3]
    secret_key = clp[4]

    while(1):
        try:
            s3conn = start_s3_boto_connection(key_id, secret_key)
            get_dataset(s3url, s3conn)
            break
        except Exception as e:
            print repr(e)

if __name__ == "__main__":
    main()