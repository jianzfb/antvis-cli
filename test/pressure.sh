#!/usr/bin/env bash

for((i=0;i<=20;i++));
do
nohup python main2.py > "$i".log 2>&1 &
done