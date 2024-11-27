for pkg in $(jq -r '.dependencies + .devDependencies | keys[]' package.json); do
    bun add "$pkg@latest"
done
