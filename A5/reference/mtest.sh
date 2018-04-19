python3 ../Parser.py $1
cp $1.s $1.s.s
./test.sh $1
diff $1.s $1.s.s

