Welcome to BIOTICA's documentation!
===================================

.. toctree::
:maxdepth: 2
:caption: Contents:

modules

Indices and tables
==================

· :ref:genindex
· :ref:modindex
· :ref:search
  EOF

إنشاء ملفات التكوين الإضافية

cat > .gitlab/merge_request_templates/default.md << 'EOF'

Description

Please include a summary of the changes.

Type of change

· Bug fix
· New feature
· Documentation update

Checklist

· Tests pass
· Code style matches
· Documentation updated
  EOF

cat > .gitlab/issue_templates/bug.md << 'EOF'

Bug Description

Describe the bug.

Steps to Reproduce

1. Step 1
2. Step 2

Expected Behavior

What should happen?

Actual Behavior

What actually happens?
