dev:
	conda install ruff mypy debugpy
	conda install coverage matplotlib-base cartopy

check:
	ruff clouddrift tests	
	ruff format clouddrift tests
	mypy --config-file pyproject.toml

test:
	coverage run -m unittest discover -s tests -p "*.py"

clean:
	rm -rf ~/.clouddrift
	rm -rf /tmp/clouddrift
	rm -rf ./data/*