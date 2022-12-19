#!/bin/bash

set -e

project_path="/etc/opt/star-burger"
python_path="./venv/bin/python"

cd $project_path
source venv/bin/activate
git pull -q
$python_path -m pip install -r requirements.txt
npm install --dev
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
$python_path manage.py collectstatic
$python_path manage.py migrate
systemctl restart star-burger.service
systemctl restart nginx.service
curl -X POST https://api.rollbar.com/api/1/deploy -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" -d "environment=production&revision=$(git rev-parse HEAD)"
echo 'Done'