#!/bin/bash

echo -e "n" | ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa >/dev/null
chmod 600 ~/.ssh/authorized_keys
