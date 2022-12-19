#!/bin/bash

set -e

project_path="/etc/opt/star-burger"
python_path="./venv/bin/python"

cd $project_path
source venv/bin/activate
git pull -q
$python_path -m pip install -r requirements.txt
npm install ci --dev --silent
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./" | killall node
$python_path manage.py collectstatic --no-input
$python_path manage.py migrate --no-input
systemctl restart star-burger.service
systemctl restart nginx.service
curl -X POST https://api.rollbar.com/api/1/deploy -H "X-Rollbar-Access-Token: $ROLLBAR_TOKEN" -d "environment=production&revision=$(git rev-parse HEAD)"
echo 'Done'
