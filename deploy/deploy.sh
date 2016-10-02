#!/bin/sh

# Cd to deploy directory
cd "$(dirname "$0")"

# Remove old package
rm -f workato_addon_for_splunk.spl

# Increase build number
let BUILD=`cat .build`
let BUILD=BUILD+1
echo $BUILD > .build

# Ask for new version number
VERSION=`cat .version`
read -p "Version ($VERSION): " NEW_VERSION
[[ ! -z "$NEW_VERSION" ]] && VERSION="$NEW_VERSION"
echo $VERSION > .version

# Update app config
perl -i -pe "s/^build\s*=.*/build = $BUILD/g" ../default/app.conf
perl -i -pe "s/^version\s*=.*/version = $VERSION/g" ../default/app.conf

cd ../..
tar -zcf workato_addon_for_splunk/deploy/workato_addon_for_splunk.spl --exclude='workato_addon_for_splunk/private' --exclude='workato_addon_for_splunk/deploy' --exclude='workato_addon_for_splunk/.git' --exclude='workato_addon_for_splunk/.git' --exclude='workato_addon_for_splunk/.gitignore' --exclude='README.md' -X workato_addon_for_splunk/.gitignore workato_addon_for_splunk
