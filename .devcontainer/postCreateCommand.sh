# Initialize all Git submodules
git config --global --replace-all "safe.directory" "*"
# git submodule update --init

# Setup Python repo
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade --no-warn-script-location --requirement requirements.txt
python3 -m pip install --upgrade --no-warn-script-location --requirement requirements/requirements.build.txt
python3 -m pip install --upgrade --no-warn-script-location --requirement requirements/requirements.dev.txt
python3 -m pip install --upgrade --no-warn-script-location --requirement requirements/requirements.docs.txt
python3 -m pip install --upgrade --no-warn-script-location --requirement requirements/requirements.tests.txt
sh -c "pre-commit install && pre-commit run --all-files"
