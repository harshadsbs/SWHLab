rm ./dist/*.zip
python "_ newversion.py"
python setup.py sdist upload
pause