# Ew brother whats this haha just run `bun update --latest` or something lol
for pkg in $(jq -r '.dependencies + .devDependencies | keys[]' package.json); do
    bun add "$pkg@latest"
done
