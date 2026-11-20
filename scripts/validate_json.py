#!/usr/bin/env python3
"""Yayımlanan tüm JSON'ların sözdizimini, KEV ve haberlerin şemasını kontrol eder."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
SCHEMAS = ROOT / "schemas"


def validate_all(data_dir=DATA, schema_dir=SCHEMAS):
    errors = []
    files = sorted(data_dir.glob("*.json"))
    if not files:
        return ["docs/data içinde JSON bulunamadı"]
    for path in files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{path.name}: geçersiz JSON: {exc}")
    for name, schema_file in (("kev.json", "kev.schema.json"),
                              ("haberler_otomatik.json", "haberler.schema.json")):
        path = data_dir / name
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            schema = json.loads((schema_dir / schema_file).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for issue in validator.iter_errors(data):
                errors.append(f"{name} / {'/'.join(map(str, issue.absolute_path))}: {issue.message}")
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{name}: doğrulanamadı: {exc}")
    return errors


if __name__ == "__main__":
    issues = validate_all()
    if issues:
        raise SystemExit("JSON doğrulama başarısız:\n- " + "\n- ".join(issues))
    print("JSON doğrulama başarılı.")
