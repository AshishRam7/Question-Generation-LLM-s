import os
import re
import shutil
from pathlib import Path

def convert_latex_to_markdown(text):
    """
    Convert LaTeX notation to markdown equivalent symbols.
    Skip checking or modifying image descriptions and figure descriptions.
    """
    parts = []
    last_end = 0
    
    # Pattern to match both image and figure descriptions (preserve as-is)
    combined_pattern = r'(\*\*Image Description:\*\*.*?(?=\n\n|\Z))|(Figure \d+:.*?(?=\n\n|\Z))'
    
    for match in re.finditer(combined_pattern, text, flags=re.DOTALL):
        if match.start() > last_end:
            parts.append(('process', text[last_end:match.start()]))
        parts.append(('preserve', match.group(0)))
        last_end = match.end()
    
    if last_end < len(text):
        parts.append(('process', text[last_end:]))
    
    processed_parts = []
    for part_type, part_text in parts:
        if part_type == 'preserve':
            processed_parts.append(part_text)
        else:
            processed_parts.append(process_latex_part(part_text))
    
    result = ''.join(processed_parts)
    
    # Post-processing substitutions for overall document improvements
    
    # Fix header: change "Graphs I: Breadth First Search" to "Graphs I – Breadth-First Search"
    result = re.sub(r'^(#\s*Lecture\s+13:\s*Graphs I):\s*Breadth\s+First\s+Search', r'\1 – Breadth-First Search', result, flags=re.MULTILINE)
    
    # Fix common spacing issues, e.g. "A d j" should be "Adj"
    result = re.sub(r'\bA\s+d\s+j\b', 'Adj', result)
    
    return result

def process_latex_part(text):
    """
    Process a part of the text that should have LaTeX converted to markdown.
    """
    # Dictionary of LaTeX to markdown symbol conversions
    latex_to_markdown = {
        # Operators
        r'\\times': '×',
        r'\\div': '÷',
        r'\\dfrac\{([^}]*)\}\{([^}]*)\}': r'\1/\2',  # Simple fraction replacement
        r'\\frac\{([^}]*)\}\{([^}]*)\}': r'\1/\2',
        r'\\sqrt\{([^}]*)\}': r'√\1',
        
        # Pseudocode conversion: convert aligned environment to pseudo-code block
        r'\\begin\{aligned\}(.*?)\\end\{aligned\}': r'```pseudo\n\1\n```',
        
        # Special characters and formatting
        r'\\textbf\{([^}]*)\}': r'**\1**',
        r'\\textit\{([^}]*)\}': r'*\1*',
        r'\\emph\{([^}]*)\}': r'*\1*',
        r'\\underline\{([^}]*)\}': r'_\1_',
        
        # Common math operations
        r'\\sum': '∑',
        r'\\prod': '∏',
        r'\\int': '∫',
        
        # Symbols
        r'\\pi': 'π',
        r'\\approx': '≈',
        r'\\pm': '±',
        r'\\neq': '≠',
        r'\\infty': '∞',
        r'\\in': '∈',
        r'\\notin': '∉',
        r'\\subset': '⊂',
        r'\\subseteq': '⊆',
        r'\\cup': '∪',
        r'\\cap': '∩',
        r'\\implies': '⟹',
        r'\\impliedby': '⟸',
        r'\\to': '→',
        r'\\longrightarrow': '⟶',
        r'\\Rightarrow': '⇒',
        r'\\Longrightarrow': '⟹',
        r'\\propto': '∝',
        r'\\bar': '¯',
        r'\\tilde': '~',
        r'\\breve': '˘',
        r'\\hat': '^',
        r'\\prime': '′',
        r'\\dagger': '†',
        r'\\ast': '∗',
        r'\\star': '⋆',
        r'\\cdots': '⋯',
        r'\\vdots': '⋮',
        r'\\ldots': '...',
        
        # Greek letters
        r'\\alpha': 'α',
        r'\\beta': 'β',
        r'\\gamma': 'γ',
        r'\\Gamma': 'Γ',
        r'\\delta': 'δ',
        r'\\Delta': 'Δ',
        r'\\epsilon': 'ϵ',
        r'\\varepsilon': 'ε',
        r'\\zeta': 'ζ',
        r'\\eta': 'η',
        r'\\theta': 'θ',
        r'\\Theta': 'Θ',
        r'\\vartheta': 'ϑ',
        r'\\iota': 'ι',
        r'\\kappa': 'κ',
        r'\\lambda': 'λ',
        r'\\Lambda': 'Λ',
        r'\\mu': 'μ',
        r'\\nu': 'ν',
        r'\\xi': 'ξ',
        r'\\Xi': 'Ξ',
        r'\\omicron': 'ο',
        r'\\pi': 'π',
        r'\\Pi': 'Π',
        r'\\varpi': 'ϖ',
        r'\\rho': 'ρ',
        r'\\varrho': 'ϱ',
        r'\\sigma': 'σ',
        r'\\Sigma': 'Σ',
        r'\\varsigma': 'ς',
        r'\\tau': 'τ',
        r'\\upsilon': 'υ',
        r'\\Upsilon': 'Υ',
        r'\\phi': 'ϕ',
        r'\\Phi': 'Φ',
        r'\\varphi': 'φ',
        r'\\chi': 'χ',
        r'\\psi': 'ψ',
        r'\\Psi': 'Ψ',
        r'\\omega': 'ω',
        r'\\Omega': 'Ω',
        
        # Comparison operators
        r'\\leq': '≤',
        r'\\geq': '≥',
        r'\\forall': '∀',
        r'\\exists': '∃',
        
        # Space commands
        r'\\quad': ' ',
        r'\\qquad': '  ',
        
        # Algorithm related
        r'\\operatorname\{([^}]*)\}': r'\1',
        
        # Common substitutions for grouping symbols
        r'\\left\(': '(',
        r'\\right\)': ')',
        r'\\left\[': '[',
        r'\\right\]': ']',
        r'\\left\{': '{',
        r'\\right\}': '}',
        r'\\{': '{',
        r'\\}': '}',
        r'\\mid': '|',
        r'_\{([^}]*)\}': r'_\1',
        r'\^\{([^}]*)\}': r'^\1',
        
        # Special formatting for lists
        r'\\begin\{itemize\}(.*?)\\end\{itemize\}': lambda match: '\n' + '\n'.join('- ' + item.strip() for item in re.split(r'\\item', match.group(1))[1:]) + '\n',
        r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}': lambda match: '\n' + '\n'.join(f'{i+1}. ' + item.strip() for i, item in enumerate(re.split(r'\\item', match.group(1))[1:])) + '\n',
    }
    
    # Process display equations (wrapped in $$...$$)
    display_pattern = r'\$\$([^\$]+)\$\$'
    display_matches = list(re.finditer(display_pattern, text))
    for match in display_matches:
        original_equation = match.group(0)
        equation_content = match.group(1)
        modified_content = equation_content
        for latex_pattern, markdown_symbol in latex_to_markdown.items():
            try:
                if callable(markdown_symbol):
                    modified_content = re.sub(latex_pattern, markdown_symbol, modified_content, flags=re.DOTALL)
                else:
                    modified_content = re.sub(latex_pattern, markdown_symbol, modified_content)
            except re.error:
                print(f"Warning: Skipping problematic pattern: {latex_pattern}")
                continue
        text = text.replace(original_equation, f"\n```math\n{modified_content}\n```\n")
    
    # Process inline equations (wrapped in $...$) and convert them to inline LaTeX math delimiters \(...\)
    inline_pattern = r'\$([^\$]+)\$'
    inline_matches = list(re.finditer(inline_pattern, text))
    for match in inline_matches:
        original_equation = match.group(0)
        equation_content = match.group(1)
        modified_content = equation_content
        for latex_pattern, markdown_symbol in latex_to_markdown.items():
            try:
                if callable(markdown_symbol):
                    modified_content = re.sub(latex_pattern, markdown_symbol, modified_content, flags=re.DOTALL)
                else:
                    modified_content = re.sub(latex_pattern, markdown_symbol, modified_content)
            except re.error:
                print(f"Warning: Skipping problematic pattern: {latex_pattern}")
                continue
        text = text.replace(original_equation, f"\\({modified_content}\\)")
    
    # Additional post-processing: Fix multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Preserve and restore code blocks
    code_blocks = re.findall(r'```.*?```', text, re.DOTALL)
    for i, block in enumerate(code_blocks):
        text = text.replace(block, f"CODE_BLOCK_{i}")
    text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', '', text)
    for i, block in enumerate(code_blocks):
        text = text.replace(f"CODE_BLOCK_{i}", block)
    
    return text

def process_markdown_file(input_file, output_file):
    """
    Process a markdown file and convert LaTeX notation to markdown equivalents.
    """
    try:
        with open(input_file, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
        
        converted_content = convert_latex_to_markdown(content)
        
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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    input_path = Path(input_dir)
    markdown_files = []
    for extension in ('*.md', '*.markdown'):
        markdown_files.extend(list(input_path.glob(f"**/{extension}")))
    
    if not markdown_files:
        print(f"No markdown files found in {input_dir}")
        return
    
    print(f"Found {len(markdown_files)} markdown files")
    
    successful_conversions = 0
    for md_file in markdown_files:
        try:
            relative_path = md_file.relative_to(input_path)
            output_file = Path(output_dir) / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            if process_markdown_file(md_file, output_file):
                successful_conversions += 1
        except Exception as e:
            print(f"Error processing file {md_file}: {str(e)}")
    
    print(f"Successfully converted {successful_conversions} out of {len(markdown_files)} files")

def main():
    input_dir = "./content/pdf_content/ocr_output/BFS_notespdf"
    output_dir = "./cleaned_md_outputs"
    
    print(f"Processing markdown files from {input_dir} to {output_dir}")
    process_directory(input_dir, output_dir)

if __name__ == "__main__":
    main()
