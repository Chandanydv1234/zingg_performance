# Zingg 30M Performance Run (Snowflake)

Zingg OSS 0.7.0 entity-resolution run on a 30M-record synthetic FEBRL dataset via Snowflake.

> Files are on the `snowflake-30m-config` branch, not `main`.

## Contents
| Folder | What it is |
|---|---|
| `config/` | Zingg config used for the run (credentials redacted) |
| `model/301/` | Trained Zingg model |
| `input/` | Input data — `FEBRL_NONULL`, 29.3M rows (gzip CSV parts) |
| `output/` | Match output — 29.3M rows (gzip CSV parts) |

## Run summary
- Input: 29,307,273 records (30M minus 692,727 blank-name records, which were excluded)
- Training: 52 matching + 52 non-matching pairs
- Train ~14 min, match ~12 h
- Output: 24,953,722 clusters; largest 453
- Accuracy vs `rec_id` ground truth: **precision ~81%, recall ~31%**

## Usage
Fill in your own Snowflake credentials in `config/config_snow_full.json`, then:
```bash
zingg.sh --phase match --conf config_snow_full.json
```

Reassemble `input/` or `output/` (split into ~90 MB gzip parts):
```bash
gunzip -c data_0_*.csv.gz > full.csv
```
