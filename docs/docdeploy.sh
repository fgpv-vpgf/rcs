#!/bin/bash

set -e

if [ "$TRAVIS_REPO_SLUG" == "fgpv-vpgf/rcs" ] && [ -n "$TRAVIS_TAG" ]; then
    openssl aes-256-cbc -k "$PW" -out ~/.ssh/id_rsa -in devkey.enc -d
    echo -e "Host *\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config
    chmod 600 ~/.ssh/id_rsa
    eval `ssh-agent -s`
    ssh-add ~/.ssh/id_rsa

    cd docs
    make clean
    make html
    git clone --depth=1 git@github.com:fgpv-vpgf/rcs.git -b gh-pages ghdocs
    mkdir -p ghdocs/$TRAVIS_TAG
    rsync -av --delete _build/html/ ghdocs/$TRAVIS_TAG/
    bash make_doc_index.sh ghdocs/ > ghdocs/index.html

    cd ghdocs
    git add $TRAVIS_TAG
    git add index.html
    git config user.email "glitch.chatbot@gmail.com"
    git config user.name "Glitch Bot"
    git commit -m "Docs for rcs@$TRAVIS_TAG"
    git push
    cd ..
    rm -rf ghdocs
fi
