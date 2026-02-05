from pathlib import Path
import json
import argparse

SCRIPT_DIR = Path(__file__).parent.resolve()

def minify_file(input_path: Path, output_path: Path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))
    
    print(f"Minified {input_path} to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Minify a JSON file.")
    parser.add_argument("input_file", type=Path, help="Path to the input JSON file")
    parser.add_argument("-o", "--output", type=Path, help="Path to output file or directory")

    args = parser.parse_args()
    
    input_path = args.input_file.resolve()
    if not input_path.exists() or not input_path.is_file():
        print(f"Error: Input file '{input_path}' does not exist.")
        return

    output_arg = args.output
    
    if output_arg:
        output_arg = output_arg.resolve()
        if output_arg.is_dir():
            # Output is a directory, use input filename inside that directory
            output_filename = input_path.stem + ".minified" + input_path.suffix
            output_path = output_arg / output_filename
        else:
            # Output is a file path
            output_path = output_arg
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # No output provided, save in same directory with .minified inserted
        output_filename = input_path.stem + ".minified" + input_path.suffix
        output_path = input_path.parent / output_filename

    minify_file(input_path, output_path)

if __name__ == "__main__":
    main()
