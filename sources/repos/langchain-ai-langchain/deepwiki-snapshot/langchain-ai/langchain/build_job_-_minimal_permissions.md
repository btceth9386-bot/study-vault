jobs:
  build:
    if: github.ref == 'refs/heads/master' || inputs.dangerous-nonmaster-release
    environment: Scheduled testing
    runs-on: ubuntu-latest
    permissions:
      contents: read  # Only read access
    steps:
      # ... build steps with uv build