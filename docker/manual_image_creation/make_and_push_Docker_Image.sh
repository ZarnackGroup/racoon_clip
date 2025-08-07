#! /bin/bash

cd /Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/docker/manual_image_creation

# Replace VERSION_PLACEHOLDER in Dockerfile with actual version
VERSION=$(awk -F'"' '/__version__/ {print $2}' ../../racoon_clip/__init__.py)
echo $VERSION

cp Dockerfile Dockerfile.old
cp ../Dockerfile Dockerfile
sed -i '' "s/VERSION_PLACEHOLDER/$VERSION/g" Dockerfile

# Replace 'yourusername' with your actual Docker Hub username
DOCKER_USERNAME="melinak"

docker build -t racoon_clip:latest .
docker tag racoon_clip:latest $DOCKER_USERNAME/racoon_clip:latest
docker tag racoon_clip:latest $DOCKER_USERNAME/racoon_clip:$VERSION

# Push to Docker Hub 
docker push $DOCKER_USERNAME/racoon_clip:latest
docker push $DOCKER_USERNAME/racoon_clip:$VERSION

