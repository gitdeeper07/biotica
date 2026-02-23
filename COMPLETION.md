# BIOTICA Shell Completion

BIOTICA provides shell completion for bash, zsh, and fish shells to enhance command-line productivity.

## Installation

### Bash

Add to your `~/.bashrc`:
```bash
eval "$(_BIOTICA_COMPLETE=bash_source biotica)"
```

Zsh

Add to your ~/.zshrc:

```zsh
eval "$(_BIOTICA_COMPLETE=zsh_source biotica)"
```

Fish

Add to your ~/.config/fish/config.fish:

```fish
eval (env _BIOTICA_COMPLETE=fish_source biotica)
```

Available Commands

```bash
biotica --help
```

Core Commands

Command Description
biotica analyze Run bioinformatics analysis
biotica monitor Run monitoring pipeline
biotica dashboard Launch dashboard
biotica sequences List available sequences
biotica alerts Check active alerts
biotica export Export data

Parameter Commands

```bash
biotica analyze protein-structure  # Protein structure prediction
biotica analyze gene-expression    # Gene expression analysis
biotica analyze sequence-alignment # Sequence alignment
biotica analyze phylogeny          # Phylogenetic analysis
biotica analyze crispr-design      # CRISPR design tools
biotica analyze pathway            # Metabolic pathway analysis
biotica analyze network            # Biological network analysis
biotica analyze health-index       # Biotechnology Health Index
```

Options

```bash
--sample SAMPLE         # Specify sample name or ID
--start-date DATE       # Start date (YYYY-MM-DD)
--end-date DATE         # End date (YYYY-MM-DD)
--format FORMAT         # Output format (json, csv, table)
--output FILE           # Output file path
--config FILE           # Configuration file
--verbose               # Verbose output
--debug                 # Debug mode
```

Examples

```bash
# Analyze protein structure
biotica analyze protein-structure --sample sample_001

# Monitor with custom config
biotica monitor --config config/biotica.local.yaml

# Export data as JSON
biotica export --format json --output data.json

# Check alerts
biotica alerts --status active

# List all sequences
biotica sequences --type dna

# Run analysis for specific date
biotica pipeline run --date 2026-02-19
```

Tab Completion Features

The completion system provides:

· Command name completion
· Sample name completion (from config/samples/)
· Date completion (YYYY-MM-DD format)
· File path completion for --output
· Format completion (json, csv, table)

Troubleshooting

If completion isn't working:

1. Ensure biotica is installed: which biotica
2. Reload shell: exec $SHELL
3. Check installation: biotica --version
4. Reinstall completions: re-run the eval command

For more help: biotica help completion
