min_versions="$(uv run python $GITHUB_WORKSPACE/.github/scripts/get_min_versions.py pyproject.toml release $python_version)"
echo "min-versions=$min_versions" >> "$GITHUB_OUTPUT"