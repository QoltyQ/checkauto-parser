#!/bin/bash

limit=500
offset=0
pow=2

for i in {1..10}
do
   echo "limit: "$limit 
   echo "offset: "$offset
   offset=$((offset + limit))
   if(($i % 2 == 0))
   then
      limit=$((limit * pow))
   fi
done
