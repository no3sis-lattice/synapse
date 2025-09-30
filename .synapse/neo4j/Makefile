# Mojo Pattern Search Build System
# Phase 2 Week 3: FFI Integration

MOJO := mojo
MOJO_SRC := pattern_search_mojo.mojo
MOJO_LIB := libpattern_search.so

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    MOJO_LIB := libpattern_search.dylib
endif
ifeq ($(OS),Windows_NT)
    MOJO_LIB := libpattern_search.dll
endif

# Build flags
MOJO_FLAGS := --emit=shared-lib

.PHONY: all build clean check help

# Default target
all: build

# Build Mojo shared library
build: check-mojo
	@echo "Building Mojo pattern search library for $(UNAME_S)..."
	$(MOJO) build $(MOJO_FLAGS) $(MOJO_SRC) -o $(MOJO_LIB)
	@echo "✓ Built $(MOJO_LIB)"
	@ls -lh $(MOJO_LIB)

# Clean build artifacts
clean:
	@echo "Cleaning Mojo build artifacts..."
	rm -f $(MOJO_LIB)
	rm -f libpattern_search.so libpattern_search.dylib libpattern_search.dll
	@echo "✓ Clean complete"

# Check Mojo compiler availability
check-mojo:
	@command -v $(MOJO) >/dev/null 2>&1 || { \
		echo "Error: mojo compiler not found"; \
		echo "Install from: https://www.modular.com/max/install"; \
		exit 1; \
	}
	@echo "✓ Mojo compiler found: $$($(MOJO) --version | head -n1)"

# Verify library was built correctly
verify: $(MOJO_LIB)
	@echo "Verifying $(MOJO_LIB)..."
	@file $(MOJO_LIB)
	@nm -D $(MOJO_LIB) | grep pattern_search_ffi || { \
		echo "Error: pattern_search_ffi symbol not found"; \
		exit 1; \
	}
	@echo "✓ Library verified, FFI symbol exported"

# Rebuild if source is newer
rebuild: clean build

# Help target
help:
	@echo "Mojo Pattern Search Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make build    - Build Mojo shared library"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make rebuild  - Clean and build"
	@echo "  make check    - Verify Mojo compiler"
	@echo "  make verify   - Verify built library"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Platform: $(UNAME_S)"
	@echo "Library:  $(MOJO_LIB)"