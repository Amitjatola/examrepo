# SAM invokes this from CodeUri (backend/). Copies only `app/` + pip deps — no venv, scripts, tests, DB files.
# ARTIFACTS_DIR is set by `sam build`.

.PHONY: build-AerogateApiFunction

build-AerogateApiFunction:
	@echo "Building AerogateApiFunction into $(ARTIFACTS_DIR)"
	mkdir -p "$(ARTIFACTS_DIR)/app"
	rsync -a --delete app/ "$(ARTIFACTS_DIR)/app/"
	python3 -m pip install -r requirements.txt -t "$(ARTIFACTS_DIR)" --disable-pip-version-check --no-cache-dir
