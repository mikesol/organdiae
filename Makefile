all: organdiae

organdiae: setup.py
	python setup.py build

install: iorgandiae

iorgandiae : setup.py
	python setup.py install

clean:
	rm -rf build