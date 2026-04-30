# ASEAN PPN/VAT/GST Rates

Free, machine-readable, auto-updating dataset of VAT/GST/PPN rates for all 10 ASEAN member states.

## Quick Access (Free API)

Fetch the latest rates as JSON — no API key, no signup:

```
https://raw.githubusercontent.com/faizfadhillah/asean-ppn-rates/main/data/asean-ppn-rates.json
```

### Example: fetch in JavaScript
```js
const res = await fetch('https://raw.githubusercontent.com/faizfadhillah/asean-ppn-rates/main/data/asean-ppn-rates.json');
const { rates } = await res.json();
const indonesia = rates.find(r => r.iso2 === 'ID');
console.log(`Indonesia PPN: ${indonesia.standard_rate}%`);
```

### Example: fetch in Python
```python
import requests
data = requests.get('https://raw.githubusercontent.com/faizfadhillah/asean-ppn-rates/main/data/asean-ppn-rates.json').json()
for r in data['rates']:
    print(f"{r['country']}: {r['standard_rate']}%")
```

## Coverage

| Country | ISO | Tax Type | Standard Rate | Local Name |
|---------|-----|----------|--------------|------------|
| Brunei Darussalam | BN | none | 0% | — |
| Cambodia | KH | VAT | 10% | VAT |
| Indonesia | ID | VAT | 12% | PPN |
| Laos | LA | VAT | 10% | VAT |
| Malaysia | MY | SST | 8% | SST |
| Myanmar | MM | Commercial Tax | 5% | Commercial Tax |
| Philippines | PH | VAT | 12% | VAT |
| Singapore | SG | GST | 9% | GST |
| Thailand | TH | VAT | 7% | VAT |
| Vietnam | VN | VAT | 10% | VAT/GTGT |

## Auto-Update

A GitHub Action runs on the 1st and 15th of every month:

1. Scrapes PwC Tax Summaries for each ASEAN country
2. Compares against the local dataset
3. If changes detected → auto-commits + creates a GitHub Issue for review

You can also trigger it manually from the Actions tab.

## Data Schema

```jsonc
{
  "meta": {
    "title": "string",
    "last_updated": "YYYY-MM-DD",
    "sources": ["url"],
    "version": "semver"
  },
  "rates": [
    {
      "country": "string",       // Full country name
      "iso2": "string",          // ISO 3166-1 alpha-2
      "iso3": "string",          // ISO 3166-1 alpha-3
      "local_name": "string",    // Local name for the tax (e.g., "PPN")
      "tax_type": "string",      // vat | gst | sst | commercial_tax | none
      "standard_rate": 12,       // Percentage (number, not string)
      "reduced_rates": [5, 0],   // Array of reduced rates
      "currency": "string",      // ISO 4217 currency code
      "notes": "string",         // Context and caveats
      "effective_date": "string" // When the current rate took effect
    }
  ]
}
```

## License

MIT
