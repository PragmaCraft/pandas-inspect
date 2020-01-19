echo "running tests"

rm -rf heads;
mkdir heads;

echo "basic:" &&
mkdir heads/basic &&
python3 -m pandas_inspect --heads heads/basic/ -i test/testcases/basic.py --output-excel basic.xlsx -o basic.csv test/testcases/basic.py &&
diff -bq basic.csv test/outputs/basic.csv &&
echo "success!";


echo "overwriting:" &&
mkdir heads/overwriting &&
python3 -m pandas_inspect --heads heads/overwriting/ -i test/testcases/overwriting.py -o overwriting.csv test/testcases/overwriting.py &&
diff -bq overwriting.csv test/outputs/overwriting.csv &&
echo "success!";

echo "functions:" &&
mkdir heads/functions &&
python3 -m pandas_inspect --heads heads/functions/ -i test/testcases/functions.py -o functions.csv test/testcases/functions.py &&
diff -bq functions.csv test/outputs/functions.csv &&
echo "success!";

echo "exclude:" &&
python3 -m pandas_inspect -i test/testcases/ -e test/testcases/functions.py -o functions.csv test/testcases/functions.py &&
[ "$(cat functions.csv | wc -l)" -eq 1 ] &&
echo "success!";