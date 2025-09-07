import sys
from pathlib import Path
import xmlschema

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_xml.py <xml-file-or-folder> [schema.xsd]")
        sys.exit(1)

    target = Path(sys.argv[1])
    schema_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "AE_XSD_schema.xsd"

    print(f"Loading schema: {schema_path}")
    schema = xmlschema.XMLSchema(schema_path)

    def validate_one(xml_path: Path):
        print(f"\n--- Validating: {xml_path} ---")
        errors = list(schema.iter_errors(xml_path))

        if not errors:
            print(" OK: Schema-valid ")
        else:
            print(f" INVALID: Found {len(errors)} errors")
            for i, err in enumerate(errors, 1):
                print(f"[{i}] Path={err.path} Reason={err.reason}")


    if target.is_dir():
        for xml_file in sorted(target.glob("*.xml")):
            validate_one(xml_file)
    else:
        validate_one(target)

if __name__ == "__main__":
    main()
