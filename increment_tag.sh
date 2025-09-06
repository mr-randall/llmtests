#!/bin/bash

#Script courtesy of https://stackoverflow.com/a/27332476

#get highest tag number
VERSION="$(git describe --abbrev=0 --tags || echo "v0.0.0")"

GITHUBREF="$1"

if [[ "$GITHUBREF" == "refs/tags/v"* ]]; then
    GITHUBREF_ARRAY=(${GITHUBREF//\// })
    VERSION="${GITHUBREF_ARRAY[2]}"
fi

#replace . with space so can split into an array
VERSION_BITS=(${VERSION//./ })

#get number parts and increase last one by 1
echo GITHUB_REF $GITHUBREF
echo GITHUB_RUN_NUMBER $GITHUB_RUN_NUMBER
echo GITHUB_RUN_ATTEMPT $GITHUB_RUN_ATTEMPT
VMAJOR=${VERSION_BITS[0]}
VMINOR=${VERSION_BITS[1]}
VPATCH=${VERSION_BITS[2]}
VPRERES="dev${GITHUB_RUN_NUMBER}.${GITHUB_RUN_ATTEMPT}"
VPATCH=$((VPATCH+1))

#create new tag
NEW_TAG="$VMAJOR.$VMINOR.$VPATCH-$VPRERES"

echo "Updating $VERSION to $NEW_TAG"

#get current hash and see if it already has a tag
GIT_COMMIT=`git rev-parse HEAD`
NEEDS_TAG=`git describe --contains $GIT_COMMIT 2>/dev/null`

#only tag if no tag already
if [ -z "$NEEDS_TAG" ]; then
    git tag $NEW_TAG
    echo "Tagged with $NEW_TAG"
    git push --tags
else
    echo "Already a tag on this commit"
fi
