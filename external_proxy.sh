#!/bin/bash
cd $1 #Navigate to temporary folder
gcloud compute scp $2 --zone "asia-east1-b" --project "tech-essence" nginxstack-mtproxy-vm:/home/stefan #Upload file to VM
gcloud compute ssh --zone "asia-east1-b" "nginxstack-mtproxy-vm" --project "tech-essence" <<EOF #SSH into VM
cd /home/stefan
./test.sh $2 #Send file to ABS
exit
cd ..
EOF