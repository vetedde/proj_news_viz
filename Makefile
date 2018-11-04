.PHONY: setup n nb

n:
	screen .venv/bin/jupyter notebook --port=8882 --no-browser .

nb:
	screen .venv/bin/jupyter notebook --port=8882 .

setup:
	test -d .venv || virtualenv --python=python3.6 .venv
	sudo pip install poetry
	poetry install
	.venv/bin/jupyter nbextension enable --py widgetsnbextension
