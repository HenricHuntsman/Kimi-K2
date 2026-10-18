# FORGE Python demonstration prototype
.PHONY: all setup build test test-ui clean install dist run-gui run-server run-cli help

all: build

setup:
	python3 -m pip install -r requirements.txt

# Full media/OS build remains unimplemented and returns nonzero.
build:
	python3 build_system.py

test:
	python3 -m py_compile *.py
	python3 -m unittest discover -s tests -v

test-ui:
	node --check static/js/app.js
	node --test tests/frontend.test.cjs

clean:
	rm -rf build dist __pycache__ tests/__pycache__

install:
	@echo "No system installer is implemented. Create a virtual environment and use make setup."
	@exit 1

# An explicitly labelled source bundle, not an installer or bootable ISO.
dist:
	python3 build_system.py --source-only

run-gui:
	python3 forge_gui.py

run-server:
	python3 forge_server.py

run-cli:
	python3 forge_cli.py

help:
	@echo "setup: install demo dependencies into your active environment"
	@echo "test: syntax and regression checks; dist: prototype source ZIP"
	@echo "run-cli / run-gui / run-server: start demonstration interfaces"
	@echo "build and install: incomplete, return nonzero"
