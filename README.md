# Public Sector Code Observatory

We are collecting the software listed on Developers Italia as a first step
towards studying dependencies and known vulnerabilities in public sector software.

For now, `catalogue.py` downloads catalogue entries, repository URLs and the
original publiccode.yml metadata. It does not analyse the repositories.

```sh
python3 catalogue.py --limit 10
```

The output is saved to `catalogue.json`. Python 3.10 or later is required;
there are no additional Python dependencies.

Omit `--limit` to collect all pages. Inactive entries are skipped by default;
use `--include-inactive` to include them.

On macOS, if Python reports a certificate verification error, try:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem python3 catalogue.py --limit 10
```

Source: [Developers Italia catalogue API](https://api.developers.italia.it/v1/software).
