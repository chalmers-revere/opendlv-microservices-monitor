#!/bin/sh

VERSION=$1

cat <<EOF >/tmp/multi.yml
image: chalmersrevere/opendlv-microservices-monitor-multi:$VERSION
manifests:	
  - image: chalmersrevere/opendlv-microservices-monitor-amd64:$VERSION
    platform:
      architecture: amd64
      os: linux
  - image: chalmersrevere/opendlv-microservices-monitor-armhf:$VERSION
    platform:
      architecture: arm
      os: linux
  - image: chalmersrevere/opendlv-microservices-monitor-aarch64:$VERSION
    platform:
      architecture: arm64
      os: linux
EOF
manifest-tool-linux-amd64 push from-spec /tmp/multi.yml
