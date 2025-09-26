.PHONY: test_nix_setup clean

LOG_DIR := logs
REPORT_DIR := qa_reports

test_nix_setup:
	@bash scripts/test_nix_setup.sh

clean:
	@rm -rf $(LOG_DIR) $(REPORT_DIR)
