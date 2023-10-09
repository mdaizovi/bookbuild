import boto3
import errno
import os
from shutil import copy, copytree, ignore_patterns, make_archive, rmtree
from django.conf import settings


def copyanything(src, dst):
    try:
        copytree(src, dst, ignore=ignore_patterns("*.DS_Store"))
    except OSError as exc:  # python >2.5
        if exc.errno == errno.ENOTDIR:
            copy(src, dst)
        else:
            raise

def cleanUp(files_to_delete=[], folders_to_delete=[]):
    """
    After epub is written,
    delete files and folders I wrote dynamically to Add2Epub, so won't confuse and conflict.
    NOTES:
            os.remove() will remove a file.
            os.rmdir() will remove an empty directory.
            rmtree() will delete a directory and all its contents.
    """

    for f in files_to_delete:
        os.remove(f)
    for f in folders_to_delete:
        rmtree(f)

def compress(newBookDir, book_dir):
    make_archive(newBookDir, "zip", book_dir)


def download_images_from_aws():
    # connect to the bucket
    s3_resource = boto3.resource("s3", region_name="us-east-1")
    my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    s3_root_folder_prefix = "media"  # bucket inside root folder
    s3_folder_list = ["img"]  # root folder inside sub folders list

    print("About to start downloading images")
    for file in my_bucket.objects.filter(Prefix=s3_root_folder_prefix):
        if any(s in file.key for s in s3_folder_list):
            try:
                path, filename = os.path.split(file.key)
                new_home = os.path.join(settings.BASE_DIR, path)
                if not os.path.exists(new_home):
                    try:
                        os.makedirs(new_home)  # Creates dirs recurcivly
                    except Exception as err:
                        print("exception making directory: ", err)
                full_img_path = os.path.join(new_home, filename)
                s3_resource.meta.client.download_file(
                    settings.AWS_STORAGE_BUCKET_NAME, file.key, full_img_path
                )
                print(file.key, " downloaded ")
            except Exception as err:
                print("exception downloading file: ", err)
    print("Done downloading images")


def download_static_from_aws():

    # TODO i have no idea if this works.

    # connect to the bucket
    s3_resource = boto3.resource("s3", region_name="us-east-1")
    my_bucket = s3_resource.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    s3_root_folder_prefix = "media/bookbuild"  # bucket inside root folder
    s3_folder_list = ["static"]  # root folder inside sub folders list

    print("About to start downloading static")
    for file in my_bucket.objects.filter(Prefix=s3_root_folder_prefix):
        if any(s in file.key for s in s3_folder_list):
            try:
                path, filename = os.path.split(file.key)
                new_home = os.path.join(settings.BASE_DIR, path)
                if not os.path.exists(new_home):
                    try:
                        os.makedirs(new_home)  # Creates dirs recurcivly
                    except Exception as err:
                        print("exception making directory: ", err)
                full_img_path = os.path.join(new_home, filename)
                s3_resource.meta.client.download_file(
                    settings.AWS_STORAGE_BUCKET_NAME, file.key, full_img_path
                )
                print(file.key, " downloaded ")
            except Exception as err:
                print("exception downloading file: ", err)
    print("Done downloading static")
