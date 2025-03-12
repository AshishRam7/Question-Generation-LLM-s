import os
import re
import shutil
from pathlib import Path

def convert_latex_to_markdown(text):
    """
    Convert LaTeX notation to markdown equivalent symbols.
    """
    # Dictionary of LaTeX to markdown symbol conversions
    latex_to_markdown = {
        # Operators
        r'\times': '×',
        r'\div': '÷',
        r'\dfrac{([^}]*)}{([^}]*)}': r'\1/\2',  # Simple fraction replacement
        r'\sqrt{([^}]*)}': r'√\1',
        
        # Symbols
        r'\pi': 'π',
        r'\approx': '≈',
        r'\pm': '±',
        r'\neq': '≠',
        r'\infty': '∞',
        r'\\in': '∈',
        r'\\notin': '∉',
        r'\subset': '⊂',
        r'\subseteq': '⊆',
        r'\cup': '∪',
        r'\cap': '∩',
        r'\implies': '⟹',
        r'\impliedby': '⟸',
        r'\\to': '→',
        r'\longrightarrow': '⟶',
        r'\Rightarrow': '⇒',
        r'\Longrightarrow': '⟹',
        r'\propto': '∝',
        r'\bar': '¯',
        r'\tilde': '~',
        r'\breve': '˘',
        r'\hat': '^',
        r'\prime': '′',
        r'\dagger': '†',
        r'\ast': '∗',
        r'\star': '⋆',
        r'\cdots': '⋯',
        r'\vdots': '⋮',
        
        # Greek letters
        r'\alpha': 'α',
        r'\beta': 'β',
        r'\gamma': 'γ',
        r'\Gamma': 'Γ',
        r'\delta': 'δ',
        r'\Delta': 'Δ',
        r'\epsilon': 'ϵ',
        r'\varepsilon': 'ε',
        r'\zeta': 'ζ',
        r'\eta': 'η',
        r'\theta': 'θ',
        r'\Theta': 'Θ',
        r'\vartheta': 'ϑ',
        r'\iota': 'ι',
        r'\kappa': 'κ',
        r'\lambda': 'λ',
        r'\Lambda': 'Λ',
        r'\mu': 'μ',
        r'\nu': 'ν',
        r'\xi': 'ξ',
        r'\Xi': 'Ξ',
        r'\omicron': 'ο',
        r'\pi': 'π',
        r'\Pi': 'Π',
        r'\varpi': 'ϖ',
        r'\rho': 'ρ',
        r'\varrho': 'ϱ',
        r'\sigma': 'σ',
        r'\Sigma': 'Σ',
        r'\varsigma': 'ς',
        r'\tau': 'τ',
        r'\upsilon': 'υ',
        r'\Upsilon': 'Υ',
        r'\phi': 'ϕ',
        r'\Phi': 'Φ',
        r'\varphi': 'φ',
        r'\chi': 'χ',
        r'\psi': 'ψ',
        r'\Psi': 'Ψ',
        r'\omega': 'ω',
        r'\Omega': 'Ω',
        
        # Comparison operators
        r'\leq': '≤',
        r'\geq': '≥',
        r'\forall': '∀',
        r'\exists': '∃',
        
        # Space commands
        r'\\quad': ' ',
        r'\\qquad': '  ',
    }
    
    # Regular expression patterns for inline and display equations
    inline_pattern = r'\$([^\$]+)\$'
    display_pattern = r'\$\$([^\$]+)\$\$'
    
    # Process display equations first
    display_matches = re.finditer(display_pattern, text)
    for match in display_matches:
        original_equation = match.group(0)
        equation_content = match.group(1)
        
        # Apply conversions to the equation content
        for latex_pattern, markdown_symbol in latex_to_markdown.items():
            equation_content = re.sub(latex_pattern, markdown_symbol, equation_content)
        
        # Replace the original equation with the converted one
        text = text.replace(original_equation, f"\n\n{equation_content}\n\n")
    
    # Process inline equations
    inline_matches = re.finditer(inline_pattern, text)
    for match in inline_matches:
        original_equation = match.group(0)
        equation_content = match.group(1)
        
        # Apply conversions to the equation content
        for latex_pattern, markdown_symbol in latex_to_markdown.items():
            equation_content = re.sub(latex_pattern, markdown_symbol, equation_content)
        
        # Replace the original equation with the converted one
        text = text.replace(original_equation, equation_content)
    
    return text

def process_markdown_file(input_file, output_file):
    """
    Process a markdown file and convert LaTeX notation to markdown equivalents.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Convert LaTeX to markdown
        converted_content = convert_latex_to_markdown(content)
        
        # Write converted content to output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(converted_content)
        
        print(f"Successfully converted {input_file} to {output_file}")
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return False

def process_directory(input_dir, output_dir):
    """
    Process all markdown files in the input directory and save converted files to the output directory.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get all markdown files in the input directory
    input_path = Path(input_dir)
    markdown_files = list(input_path.glob('*.md')) + list(input_path.glob('*.markdown'))
    
    if not markdown_files:
        print(f"No markdown files found in {input_dir}")
        return
    
    print(f"Found {len(markdown_files)} markdown files")
    
    # Process each markdown file
    successful_conversions = 0
    for md_file in markdown_files:
        relative_path = md_file.relative_to(input_path)
        output_file = Path(output_dir) / relative_path
        
        # Create any necessary subdirectories
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if process_markdown_file(md_file, output_file):
            successful_conversions += 1
    
    print(f"Successfully converted {successful_conversions} out of {len(markdown_files)} files")

# Main function with hardcoded paths
def main():
    # Hardcoded input and output directories
    input_dir = "./markdown_input"
    output_dir = "./markdown_output"
    
    print(f"Processing markdown files from {input_dir} to {output_dir}")
    process_directory(input_dir, output_dir)

# Run the main function when the script is executed
if __name__ == "__main__":
    main()