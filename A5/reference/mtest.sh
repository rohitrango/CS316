# For correct
for fi in correct/*.c;
do
	python3 ../Parser.py $fi
	cp $fi.s $fi.s.s
	cp $fi.ast $fi.s.ast
	cp $fi.cfg $fi.s.cfg
	cp $fi.sym $fi.s.sym
	./test.sh $fi
	diff $fi.s $fi.s.s
	# diff -w $fi.ast $fi.s.ast
	# diff -w $fi.cfg $fi.s.cfg
	# diff -w $fi.sym $fi.s.sym
done

# For custom
for fi in custom/*.c;
do
	python3 ../Parser.py $fi
	cp $fi.s $fi.s.s
	./test.sh $fi
	diff $fi.s $fi.s.s
done


