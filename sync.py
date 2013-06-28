from boto import glacier
import os
import socket
import hashlib
import json
import argparse

ROOT_DIR = '/Users/stewart/Pictures'  # root path to the folder you want to sync to glacier
UPLOADED = set()
REGION = 'us-east-1'  # glacier region for your vault where the archives are to be stored
VAULT_NAME = 'photos'  # name of the vault to store archives into
UPLOADED_FILE_NAME = 'uploaded.log'  # name of local file to track/log files that have been uploaded
HOST_NAME = socket.gethostname()


def connect_to_glacier_get_vault(region=REGION, vault=VAULT_NAME):
    cn = glacier.connect_to_region(region)
    print 'available regions:', glacier.regions()
    vaults = cn.list_vaults()
    print 'available vaults in region:',  vaults
    if not vault in [v.name for v in vaults]:
        print 'vault', vault, 'does not exist, creating it...'
        return cn.create_vault(vault)
    else:
        return cn.get_vault(vault)


def populate_hashes_uploaded():
    if os.path.exists(UPLOADED_FILE_NAME):
        print 'loading previously uploaded file hashes'
        with open(UPLOADED_FILE_NAME, 'r') as f:
            for l in f:
                UPLOADED.add(json.loads(l)['sha1'])


def upload_file_to_vault(v, fd):
    #Upload file to glacier
    return v.upload_archive(fd['file_path'], description=json.dumps(fd))


def process_files():
    v = connect_to_glacier_get_vault()
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            fd = {'machine': HOST_NAME}
            fd['file_path'] = os.path.join(root, f)
            fd['sha1'] = hashlib.sha1(file(fd['file_path'], 'rb').read()).hexdigest()
            if not fd['sha1'] in UPLOADED:
                #fd['archive_id'] = upload_file_to_vault(v, fd)
                UPLOADED.add(fd['sha1'])
                file(UPLOADED_FILE_NAME, 'a').write(json.dumps(fd) + '\n')
                print 'UPLOADED', fd['file_path'], 'with hash', fd['sha1']
            else:
                #file already uploaded according to our records
                print 'ALREADY UPLOADED', fd['file_path'], 'with hash', fd['sha1']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CL utility to sync files to AWS glacier.')
    parser.add_argument('--path', '-p', default=ROOT_DIR, help='Root path to the folder containing the files to sync.')
    parser.add_argument('--region', '-r', default=REGION, help='AWS glacier storage region to use.')
    parser.add_argument('--vault', '-v', default=VAULT_NAME, help='Vault name to store archives[files] in.')
    parser.add_argument('--list', '-l', action='store_true', help='List the files to be sync\'d')
    args = parser.parse_args()
    ROOT_DIR = args.path
    REGION = args.region
    VAULT_NAME = args.vault
    if args.list:
        print 'listiing the files....'
    #populate_hashes_uploaded()
    #process_files()
