# Makefile for Corpus Callosum Message Router
# Phase 3: Mojo FFI compilation

# Detect platform
UNAME_S := $(shell uname -s)
MOJO := mojo

# Library name
LIB_NAME := libmessage_router.so

# Source file
SRC := message_router.mojo

# Build directory
BUILD_DIR := .

# Default target
.PHONY: all
all: build

# Build shared library
.PHONY: build
build:
	@echo "Building Corpus Callosum message router..."
	$(MOJO) build $(SRC) --emit shared-lib -o $(BUILD_DIR)/$(LIB_NAME)
	@echo "✓ Built $(LIB_NAME)"
	@ls -lh $(BUILD_DIR)/$(LIB_NAME)

# Verify FFI exports
.PHONY: verify
verify: build
	@echo "Verifying FFI exports..."
	@if command -v nm >/dev/null 2>&1; then \
		echo "Exported symbols:"; \
		nm -D $(BUILD_DIR)/$(LIB_NAME) | grep -E '(create_router|destroy_router|route_message_ffi|get_next_message_ffi|get_queue_depth_ffi|get_total_queue_depth_ffi|get_total_messages_ffi|get_message_loss_count_ffi|reset_stats_ffi)' || echo "⚠️ Warning: Some FFI symbols may not be exported"; \
	else \
		echo "nm not available, skipping symbol verification"; \
	fi

# Run smoke test
.PHONY: test
test: build
	@echo "Running smoke test..."
	python3 test_message_router.py

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(BUILD_DIR)/$(LIB_NAME)
	rm -f *.o
	@echo "✓ Clean complete"

# Help
.PHONY: help
help:
	@echo "Corpus Callosum Message Router Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build message router library (default)"
	@echo "  build      - Build shared library"
	@echo "  verify     - Verify FFI exports"
	@echo "  test       - Run smoke test"
	@echo "  clean      - Remove build artifacts"
	@echo "  help       - Show this message"
