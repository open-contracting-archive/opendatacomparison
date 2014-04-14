opendatacomparison
==================

Django application for comparing datsets, built on Open Comparison


install
=======

To create your database MySQL with utf-8:

    CREATE DATABASE opendatacomparison CHARACTER SET utf8

Get everything setup on most systems:

    cd deploy
    ./bootstrap.py
    ./tasks.py deploy:dev

On OSX, using CLANG for compilation (CLANG throws errors on unexpected arguments by default):

    cd deploy
    ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future ./bootstrap
    ./tasks.py deploy:dev
