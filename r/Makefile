.PHONY: install check test doc clean

install:
R CMD INSTALL .

check:
R CMD check --as-cran biotica_1.0.0.tar.gz

build:
R CMD build .

test:
Rscript -e "devtools::test()"

doc:
Rscript -e "devtools::document()"

clean:
rm -rf biotica.Rcheck/
rm -f biotica_*.tar.gz
