
API Reference

BIOTICACore

Main class for BIOTICA calculations.

Methods

· compute_vca(ndvi, lai, gpp): Compute Vegetative Carbon Absorption
· compute_mdi(shannon, chao1, otus): Compute Microbial Diversity Index
· compute_ibr(parameters): Compute Integrated Biotic Resilience index

IBRComposite

Class for IBR composite calculations.

Methods

· set_parameter(name, value): Set a parameter
· compute(): Compute IBR score
  EOF

cat > docs/changelog.md << 'EOF'

Changelog

[1.0.0] - 2026-03-01

Added

· Initial release
· Core equations for 9 parameters
· IBR composite index
· Basic documentation
  EOF

إنشاء ملفات docs الإضافية

cat > docs/Makefile << 'EOF'

Minimal makefile for Sphinx documentation

SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

help:
@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

.PHONY: help Makefile

%: Makefile
@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)
