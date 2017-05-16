CC = g++ -O3 -Wall -pthread

cli:
	$(CC) src/bmi_cli.cc src/bmi.cc src/features.cc src/sofiaml/sf-data-set.cc src/sofiaml/sf-sparse-vector.cc src/sofiaml/sf-weight-vector.cc src/scorer.cc src/sofiaml/sofia-ml-methods.cc -o bmi_cli

fcgi:
	$(CC) -lfcgi -lfcgi++ src/bmi_fcgi.cc src/bmi.cc src/features.cc src/sofiaml/sf-data-set.cc src/sofiaml/sf-sparse-vector.cc src/sofiaml/sf-weight-vector.cc src/scorer.cc src/sofiaml/sofia-ml-methods.cc -o bmi_fcgi

clean:
	rm -f bmi_cli
	rm -f bmi_fcgi