#!/bin/bash
cat homework_links.txt | xargs -I {} python main.py --link {} --req ""