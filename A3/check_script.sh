python3 150050061_17V051001.py $1
./A3-reference-implementation/Parser $1
diff -B $1.ast $1.ast.1
diff -B $1.cfg $1.cfg.1