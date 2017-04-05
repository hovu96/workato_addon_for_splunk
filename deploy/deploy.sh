#!/bin/sh

# Remove old package
rm -f workato_addon_for_splunk.spl

# Increase build number
BUILD_NUMBER=$(cat .build)
BUILD_NUMBER=$((BUILD_NUMBER + 1))
echo $BUILD_NUMBER > .build

# Ask for new version number
VERSION=$(cat .version)
read -p "Version ($VERSION): " NEW_VERSION
echo $NEW_VERSION

if [ -z "$NEW_VERSION" ]
then
    echo "Version number not changed"
else
    VERSION="$NEW_VERSION"
    echo $VERSION > .version
fi

# Update app config
sed -i -- "s/^build\s*=.*/build = $BUILD_NUMBER/g" ../default/app.conf
sed -i -- "s/^version\s*=.*/version = $VERSION/g" ../default/app.conf

cd ../..
export COPYFILE_DISABLE=true
tar -zcf workato_addon_for_splunk/deploy/workato_addon_for_splunk.spl --exclude='workato_addon_for_splunk/private' --exclude='workato_addon_for_splunk/deploy' --exclude='workato_addon_for_splunk/.git' --exclude='workato_addon_for_splunk/.git' --exclude='workato_addon_for_splunk/.gitignore' --exclude='README.md' --exclude='.[^/]*' -X workato_addon_for_splunk/.gitignore workato_addon_for_splunk
