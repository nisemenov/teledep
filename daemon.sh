#!/bin/bash

sudo systemctl daemon-reload
sudo systemctl stop teledep
sudo systemctl start teledep
