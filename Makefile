clean:
	@echo "Cleaning up *.pyc files"
	@find . -name "*.pyc" -delete

setup:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@pip install -r requirements_test.txt

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 estester # --ignore=E501,E126,E127,E128

pep8_tests:
	@echo "Checking tests code PEP8 compliance"
	@-pep8 tests # --ignore=E501,E126,E127,E128

lint:
	@echo "Running pylint"
	@pylint estester

tests: clean pep8 pep8_tests
	@echo "Running pep8, unit and integration tests..."
	@nosetests -s  --cover-branches --cover-erase --with-coverage --cover-inclusive --cover-package=estester --tests=tests --with-xunit
