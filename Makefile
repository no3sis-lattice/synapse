.PHONY: test_nix_setup clean corpus_callosum corpus_callosum_test corpus_callosum_clean

LOG_DIR := logs
REPORT_DIR := qa_reports
MOJO := /home/m0xu/.synapse-system/.venv/bin/mojo
CORPUS_DIR := .synapse/corpus_callosum
CORPUS_SRC := $(CORPUS_DIR)/message_router.mojo
CORPUS_LIB := $(CORPUS_DIR)/libmessage_router.so

test_nix_setup:
	@bash scripts/test_nix_setup.sh

clean:
	@rm -rf $(LOG_DIR) $(REPORT_DIR)

# Corpus Callosum Message Router (Phase 3)
corpus_callosum: $(CORPUS_LIB)

$(CORPUS_LIB): $(CORPUS_SRC)
	@echo "Compiling Corpus Callosum message router (Mojo → shared library)..."
	@cd $(CORPUS_DIR) && $(MOJO) build --emit=shared-lib message_router.mojo -o libmessage_router.so
	@echo "✓ Compilation complete: $(CORPUS_LIB)"
	@ls -lh $(CORPUS_LIB)

corpus_callosum_test: $(CORPUS_LIB)
	@echo "Running Corpus Callosum FFI integration test..."
	@python3 -m pytest $(CORPUS_DIR)/test_message_router.py -v
	@echo "✓ FFI integration validated"

corpus_callosum_benchmark: $(CORPUS_LIB)
	@echo "Running Corpus Callosum performance benchmark..."
	@python3 $(CORPUS_DIR)/benchmark_message_router.py
	@echo "✓ Baseline metrics collected"

corpus_callosum_clean:
	@rm -f $(CORPUS_LIB)
	@rm -f $(CORPUS_DIR)/*.mojopkg
	@rm -f $(CORPUS_DIR)/*.pyc
	@rm -rf $(CORPUS_DIR)/__pycache__
	@echo "✓ Corpus Callosum artifacts cleaned"
