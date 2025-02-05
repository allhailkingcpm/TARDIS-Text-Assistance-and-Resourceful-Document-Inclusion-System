import re

class MathParser:
    def __init__(self):
        # Basic symbols and Greek letters
        self.symbols = {
            # Existing symbols
            'sqrt': '√',
            'inf': '∞',
            '<=': '≤',
            '>=': '≥',
            
            # Greek letters (lowercase)
            '@alpha': 'α', '@beta': 'β', '@gamma': 'γ', '@delta': 'δ',
            '@epsilon': 'ε', '@zeta': 'ζ', '@eta': 'η', '@theta': 'θ',
            '@iota': 'ι', '@kappa': 'κ', '@lambda': 'λ', '@mu': 'μ',
            '@nu': 'ν', '@xi': 'ξ', '@pi': 'π', '@rho': 'ρ',
            '@sigma': 'σ', '@tau': 'τ', '@upsilon': 'υ', '@phi': 'φ',
            '@chi': 'χ', '@psi': 'ψ', '@omega': 'ω',
            
            # Greek letters (uppercase)
            '@ALPHA': 'Α', '@BETA': 'Β', '@GAMMA': 'Γ', '@DELTA': 'Δ',
            '@EPSILON': 'Ε', '@THETA': 'Θ', '@LAMBDA': 'Λ', '@PI': 'Π',
            '@SIGMA': 'Σ', '@PHI': 'Φ', '@PSI': 'Ψ', '@OMEGA': 'Ω',
            
            # Mathematical operators
            '+-': '±', '-+': '∓', 'times': '×', 'div': '÷',
            '!=': '≠', '~=': '≈', '<=': '≤', '>=': '≥',
            '<<': '≪', '>>': '≫', '-inf': '-∞', '+inf': '+∞',
            
            # Set theory
            'in': '∈', 'notin': '∉', 'subset': '⊂', 'supset': '⊃',
            'subseteq': '⊆', 'supseteq': '⊇', 'union': '∪', 
            'inter': '∩', 'empty': '∅', 'forall': '∀', 'exists': '∃',
            
            # Calculus and analysis
            'partial': '∂', 'nabla': '∇', 'integral': '∫', 
            'iintegral': '∬', 'iiintegral': '∭', 'oint': '∮',
            'therefore': '∴', 'because': '∵',
            
            # Geometry and angles
            'perp': '⊥', 'parallel': '∥', 'angle': '∠', 
            'triangle': '△', 'square': '□', 'circle': '○',
            'degree': '°',
            
            # Logic
            'and': '∧', 'or': '∨', 'not': '¬', 'implies': '⇒',
            'iff': '⇔', 'xor': '⊕',
        }
        
        # Superscripts (including letters)
        self.superscript_map = {
            '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
            '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
            'n': 'ⁿ', 'i': 'ⁱ', '+': '⁺', '-': '⁻', '=': '⁼',
            '(': '⁽', ')': '⁾'
        }
        
        # Subscripts
        self.subscript_map = {
            '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
            '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
            '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎'
        }
        
        # Common fractions
        self.fraction_map = {
            '1/2': '½', '1/3': '⅓', '2/3': '⅔', '1/4': '¼', 
            '3/4': '¾', '1/5': '⅕', '2/5': '⅖', '3/5': '⅗', 
            '4/5': '⅘', '1/6': '⅙', '5/6': '⅚', '1/8': '⅛', 
            '3/8': '⅜', '5/8': '⅝', '7/8': '⅞'
        }

    def convert_power(self, match):
        base = match.group(1)
        exp = match.group(2)
        exp = ''.join(self.superscript_map.get(c, c) for c in exp.strip())
        return f"{base.strip()}{exp}"

    def convert_sub(self, match):
        base, sub = match.group(1).split(',')
        sub = ''.join(self.subscript_map.get(c, c) for c in sub.strip())
        return f"{base.strip()}{sub}"

    def convert_fraction(self, match):
        """Convert fraction expressions to unicode fraction characters"""
        fraction = match.group(1)
        return self.fraction_map.get(fraction, f"({fraction})")

    def translate(self, text):
        # Replace power expressions using caret notation
        text = re.sub(r'(\w+|\([^)]+\))\^(\w+|\([^)]+\))', self.convert_power, text)
        
        # Replace complex fraction expressions first
        text = re.sub(r'\((.*?)\)/\((.*?)\)', self.convert_complex_fraction, text)  # (a)/(b)
        text = re.sub(r'\((.*?)\)/(\w+)', self.convert_complex_fraction, text)      # (a)/b
        text = re.sub(r'(\w+)/\((.*?)\)', self.convert_complex_fraction, text)      # a/(b)
        
        # Then handle simple fractions
        text = re.sub(r'(\d+)/(\d+)', self.convert_direct_fraction, text)
        
        # Replace power expressions
        text = re.sub(r'pow\((.*?)\)', self.convert_power, text)
        
        # Replace subscript expressions (new)
        text = re.sub(r'sub\((.*?)\)', self.convert_sub, text)
        
        # Replace sqrt expressions with optional nth root
        text = re.sub(r'sqrt\((.*?)\)', r'√\1', text)
        text = re.sub(r'root\((.*?),(.*?)\)', r'∛\2', text)
        
        # Replace symbols
        for symbol, replacement in self.symbols.items():
            text = text.replace(symbol, replacement)
        
        return text

    def convert_direct_fraction(self, match):
        """Convert direct fraction notation (e.g., 1/2) to unicode fraction characters"""
        fraction = f"{match.group(1)}/{match.group(2)}"
        return self.fraction_map.get(fraction, f"({fraction})")

    def convert_complex_fraction(self, match):
        """Convert complex fraction expressions using box-drawing characters"""
        numerator = match.group(1).strip('()')
        denominator = match.group(2).strip('()')
        
        # Get the length of the longer part
        width = max(len(numerator), len(denominator))
        
        # Center-align numerator and denominator
        numerator = numerator.center(width)
        denominator = denominator.center(width)
        
        # Create the fraction line using box-drawing character
        fraction_line = '─' * width
        
        # Construct the vertical fraction
        return f"\n{numerator}\n{fraction_line}\n{denominator}\n"
