from boto import glacier
import os
import socket
import hashlib
import json
import argparse

ROOT_DIR = '/Volumes/Photos/'  # root path to the folder you want to sync to glacier
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
    print 'using', vault, 'vault in region', region
    if not vault in [v.name for v in vaults]:
        print 'vault', vault, 'does not exist, creating it...'
        return cn.create_vault(vault)
    else:
        return cn.get_vault(vault)


def get_file_hashes_uploaded():
    if os.path.exists(UPLOADED_FILE_NAME):
        print 'loading previously uploaded file hashes...'
        with open(UPLOADED_FILE_NAME, 'r') as f:
            for l in f:
                UPLOADED.add(json.loads(l)['sha1'])


def upload_file_to_vault(v, fd):
    #Upload file to glacier
    return v.upload_archive(fd['file_path'], description=json.dumps(fd))


def upload_files(limit=0):
    v = connect_to_glacier_get_vault()
    file_data = get_files_on_machine()
    upload_count = 0
    for fd in file_data:
        if not fd['sha1'] in UPLOADED:
            fd['machine'] = HOST_NAME
            try:
                if limit > 0 and upload_count >= limit:
                    break
                #fd['archive_id'] = upload_file_to_vault(v, fd)
                file(UPLOADED_FILE_NAME, 'a').write(json.dumps(fd) + '\n')
                upload_count  += 1
                UPLOADED.add(fd['sha1'])
                print 'UPLOADED', fd['file_path'], 'with hash', fd['sha1']
            except glacier.exceptions.UploadArchiveError as uae:
                logerror('FAILED to upload %s with hash %s' %(fd['file_path'], fd['sha1']), uae)
        else:
            #file already uploaded according to our records
            print 'ALREADY UPLOADED', fd['file_path'], 'with hash', fd['sha1']


def logerror(msg, ex):
    print msg, str(ex)
    file('error.log', 'a').write(msg + ' exception: ' + str(ex) + '\n')


def get_files_on_machine(echo=False):
    fs = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for f in files:
            fd = {}
            fd['file_path'] = os.path.join(root, f)
            try:
                fd['sha1'] = hashlib.sha1(file(fd['file_path'], 'rb').read()).hexdigest()
            except MemoryError as me:
                fd['sha1'] = hashlib.sha1(HOST_NAME + '-' + fd['file_path']).hexdigest()
                logerror('error hashing file %s using full file path name for hash: %s' %(fd['file_path'], fd['sha1']), me)
            if echo:
                print fd['file_path']
            fs.append(fd)
    if echo:
        print '**', len(fs), 'files on machine under', ROOT_DIR, '**'
    return fs


if __name__ == '__main__':
    try:
        # process arguments
        parser = argparse.ArgumentParser(description='CL utility to sync files to AWS glacier.')
        parser.add_argument('--path', '-p', default=ROOT_DIR, help='Root path to the folder containing the files to sync.')
        parser.add_argument('--region', '-r', default=REGION, help='AWS glacier storage region to use.')
        parser.add_argument('--vault', '-v', default=VAULT_NAME, help='Vault name to store archives[files] in.')
        parser.add_argument('--list', '-ls', action='store_true', help='List the files to be sync\'d')
        parser.add_argument('--limit', '-li', default=0, type=int, help='Limit to archive upload to this number.')
        args = parser.parse_args()
        ROOT_DIR = args.path
        REGION = args.region
        VAULT_NAME = args.vault

        # operate on arguments
        if args.list:
            print 'listiing the files....'
            get_files_on_machine(echo=True)
        else:
            get_file_hashes_uploaded()
            upload_files(args.limit)
    except Exception as ex:
        logerror('Exception occurred running glacier sync script', ex)
