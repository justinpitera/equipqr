# Scripts

```bash
cd scripts
```

## QR Generator

```shell
pip install qrcode jinja2 pandas "qrcode[pil]" tqdm
```

```shell
python qrgen.py ../api/database.csv ./logo.png ./star.png
```

## Unique Patterns

```shell
pip install jinja2 tqdm
```

```shell
python unique-finder.py ../api/database.csv
```
