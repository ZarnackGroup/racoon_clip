#!/bin/bash
count="$1"
character="$2"

    for (( i = 0; i < "$count"; ++i ))
    do
        echo -n "$character"
    done
