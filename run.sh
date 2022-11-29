#!/bin/bash

limit=500
offset=0
pow=2

nohup python3 get_new_cars.py > log/get_new_cars.log 2>&1> get_new_cars.out &
nohup python3 update_cars.py > log/update_cars.log 2>&1> update_cars.out &
nohup python3 bot.py > log/bot.log 2>&1> bot.out &


for i in {1..6}
do
   offset=$((offset + limit))
   if(($i % 2 == 0))
   then
      limit=$((limit * pow))
   fi
   nohup python3 update_cars.py $limit $offset > log/"update_cars_$i".log 2>&1> "update_cars_$i".out &
done
