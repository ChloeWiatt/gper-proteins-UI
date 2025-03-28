# MOM1-GPER

# GPCR-GPER Data Explorer

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🧬 Overview

GPCR-GPER Data Explorer is a powerful bioinformatics tool for exploring, visualizing, and analyzing G protein-coupled estrogen receptor (GPER) data from multiple biological databases. The application provides an intuitive interface for researchers to filter, search, and visualize protein data with advanced features for structure analysis.

## ✨ Features

- **Multi-database integration**: Query and combine data from UniProt, PDB, and more
- **Advanced filtering**: Filter proteins by multiple attributes including sequence patterns
- **Interactive visualizations**: 3D protein structure visualization
- **Detailed protein information**: View comprehensive protein details including:
  - Sequence data
  - Mutation analysis
  - Disease associations
  - Tissue specificity 
  - Subcellular localization
  - PubMed references
- **Presence-based filtering**: Easily find entries with specific data types available

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gpcr-gper.git
   cd gpcr-gper
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

Run the application by starting both the backend and frontend servers:

1. Start the backend server:
   ```bash
   python back.py
   ```

2. In a separate terminal, start the Streamlit frontend:
   ```bash
   streamlit run front.py
   ```

3. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## 💡 How to Use

1. **Filter data**: Use the sidebar to filter proteins by various attributes
2. **Search sequences**: Enter sequence patterns to find specific protein sequences
3. **View details**: Click on any result to see comprehensive protein information
4. **Explore 3D structures**: View available protein structures in the 3D visualization tab

## 🔬 Technical Details

- **Frontend**: Streamlit
- **Backend**: Python
- **Data Sources**: UniProt, PDB, AlphaFold
- **Visualization**: py3Dmol, Streamlit components

## 👥 Contributors

- Chloé WIATT
- Mohamed Emine BASSOUM
- Arthur JEANNE
- Lucas AUTEF

## 📚 Resources

- [UniProt](https://www.uniprot.org/)
- [PDB](https://www.rcsb.org/)
- [AlphaFold DB](https://alphafold.ebi.ac.uk/)
- [GPER/GPR30 Information](https://www.ncbi.nlm.nih.gov/gene/2852)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔍 Future Improvements

- Integration with additional biological databases
- Advanced statistical analysis of protein features
- Batch processing capabilities
- Export functionality for research papers

## ⚠️ Known Issues

- Some PDB structures may load slowly depending on complexity
- Limited support for very large protein datasets

If you encounter any bugs or have feature requests, please [open an issue](https://github.com/yourusername/gpcr-gper/issues).
