# TARDIS Math Translator

A Doctor Who-themed mathematics expression editor designed for students with writing disabilities. This application allows users to write mathematical expressions using simple text commands and see them rendered in proper mathematical notation in real-time, all wrapped in a TARDIS-inspired interface.

## Features

- TARDIS-themed user interface
- Real-time translation of text to mathematical notation
- Support for complex mathematical expressions
- Auto-save functionality
- Modern, accessible interface
- Equation alignment tools
- Support for a wide range of mathematical symbols

## Installation

1. Ensure you have Python 3.7+ installed
2. Clone this repository
3. Install requirements:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Run the application:
```bash
python math_translator.py
```

2. Type in the left panel using simple text commands
3. See the mathematical notation appear in the right panel

## Writing Mathematical Expressions

### Basic Operations

| You Type | You Get |
|----------|---------|
| sqrt(x) | √x |
| 1/2 | ½ |
| x^2 | x² |
| sub(x,1) | x₁ |

### Complex Fractions

For longer expressions, use parentheses:
```
(x + y)/(a + b) becomes:
  x + y
  ─────
  a + b
```

### Greek Letters
- Lowercase: @alpha → α, @beta → β
- Uppercase: @GAMMA → Γ, @DELTA → Δ

### Mathematical Operators
- times → ×
- div → ÷
- <= → ≤
- >= → ≥
- != → ≠

### Set Theory
- in → ∈
- subset → ⊂
- union → ∪
- empty → ∅

### Calculus
- partial → ∂
- integral → ∫
- iintegral → ∬
- iiintegral → ∭

## Features Guide

### Auto-Save
- Files are automatically saved every 5 minutes after the first manual save
- Saves are stored in .math format
- Use File > Save to choose initial save location

### Equation Alignment
1. Write multiple equations with "=" signs
2. Click "Align =" button
3. All equations will align at their equals signs

Example:
```
x = 5
y + 2 = 10
long_variable = 15
```
becomes:
```
x             = 5
y + 2         = 10
long_variable = 15
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Save | Ctrl+S |
| Load | Ctrl+O |
| Show Help | F1 |

## File Format

The .math files are JSON formatted with the following structure:
```json
{
    "input_text": "your math expressions",
    "timestamp": "ISO format timestamp"
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
