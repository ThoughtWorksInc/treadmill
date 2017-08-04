yum -y install awscli createrepo s3cmd
mkdir s3
cd s3

aws s3 sync s3://yum_repo_dev .
unalias cp
for file in "$@"
do
	cp -f $file ./
done

createrepo .
aws s3 sync . s3://yum_repo_dev
s3cmd setacl s3://yum_repo_dev --acl-public --recursive