# PairCoder Evaluation - Machine Learning in Software Engineering Seminar

This repository contains the evaluation results and presentation materials for the **PairCoder** method, presented as part of the "Machine Learning in Software Engineering" seminar.

## Overview

PairCoder is a pair programming approach that uses large language models (LLMs) to solve coding problems through iterative collaboration between a "navigator" and "driver" agent. This evaluation analyzes the performance of PairCoder on three benchmark datasets commonly used in code generation research.

## Repository Structure

```
├── presentation/                       
│   ├── paircoder_Beamer_presentation.pdf
│   ├── paircoder-architecture.png
│   ├── paircoder-results.png
│   └── mapcoder-architecture.png
├── Examples/PairCoder-main/            
│   └── logs/                          
│       ├── codecontest/
│       ├── humaneval/
│       └── mbpp/
├──eval/
│   ├── paircoder_combined_results.csv    
│   ├── paircoder_detailed_codecontest.csv
│   ├── paircoder_detailed_humaneval.csv 
│   ├── paircoder_detailed_mbpp.csv 
│   └── paircoder_summary.csv    
│              
├── README.md                           
├── evaluate.py                         
└── seminar.pdf                         

```

## Evaluation Results

### Datasets Evaluated

1. **HumanEval**: A collection of 164 programming problems designed to evaluate functional correctness of code synthesis
2. **MBPP (Mostly Basic Python Problems)**: A dataset of around 1,000 crowd-sourced Python programming problems
3. **CodeContest**: A competitive programming dataset with problems from various online judges

### Key Metrics

- **Pass Rate**: Percentage of problems solved correctly
- **Test Coverage**: Number of test cases passed/failed/timeout
- **Execution Analysis**: Error patterns and timeout detection

### Results Summary

The evaluation analyzes the performance of PairCoder using GPT-3.5-turbo across all three benchmark datasets. Detailed results are available in the CSV files:

- `paircoder_summary.csv`: High-level statistics for each dataset
- `paircoder_combined_results.csv`: All results in a single file
- `paircoder_detailed_*.csv`: Problem-by-problem breakdown for each dataset

## Running the Evaluation


change paths:
```bash
base_path = r"/path/to/your/logs"  # Change this to your logs base path
output_dir = r"/path/to/your/output"  # Change this to your output directory
```
To reproduce the evaluation results:
```bash
python evaluate.py
```

This script will:
1. Scan the logs directory for experimental results
2. Parse solutions.json files containing test outcomes
3. Analyze log files for error patterns and execution details
4. Generate comprehensive CSV reports
5. Calculate accuracy and summary statistics

## Key Features of the Evaluation

- **Comprehensive Analysis**: Covers public, private, and generated test cases
- **Error Detection**: Identifies timeouts, exceptions, and failure patterns
- **Multi-Dataset Support**: Handles HumanEval, MBPP, and CodeContest formats
- **Detailed Reporting**: Problem-level and aggregate statistics
- **Execution Metrics**: Runtime analysis and error categorization

## Files Description

### Evaluation Files
- `evaluate.py`: Main evaluation script
- `paircoder_*.csv`: Generated evaluation results

### Presentation Materials
- `seminar.pdf`: Complete seminar paper with methodology and results
- `presentation/paircoder_Beamer_presentation.pdf`: Slide presentation
- `presentation/*.png`: Architecture diagrams and result visualizations

### Source Data
- `Examples/PairCoder-main/logs/`: Raw experimental logs and results
- Each subdirectory contains solutions.json and detailed log files

## Methodology

The evaluation follows these steps:

1. **Data Collection**: Extract results from PairCoder experimental logs
2. **Test Analysis**: Parse test outcomes (passed/failed/timeout) for each problem
3. **Status Determination**: Classify problems as PASSED, FAILED, or NO_TESTS
4. **Accuracy Calculation**: Compute pass rates and success metrics
5. **Report Generation**: Create detailed CSV reports and summary statistics

## Research Context

This work is part of a seminar on **Machine Learning in Software Engineering**, focusing on:
- Automated code generation using large language models
- Pair programming methodologies in AI-assisted development
- Evaluation of code synthesis on standard benchmarks
- Comparative analysis of different prompting strategies

## Citation

If you use these evaluation results or methodology in your research, please cite all included paper works and this evaluation.

PairCoder:
```bibtex
@inproceedings{zhang2024paircoder,
  author    = {Huan Zhang and Wei Cheng and Yuhan Wu and Wei Hu},
  title     = {A Pair Programming Framework for Code Generation via Multi-Plan Exploration and Feedback-Driven Refinement},
  booktitle = {Proceedings of the 39th IEEE/ACM International Conference on Automated Software Engineering (ASE)},
  year      = {2024},
  pages     = {1319--1331},
  publisher = {ACM},
  doi       = {10.1145/3691620.3695506},
  url       = {https://dl.acm.org/doi/10.1145/3691620.3695506}
}
```
Guided Code Generation:
```bibtex
@article{almorsi2025guided,
  author    = {Amr Almorsi and Mohanned Ahmed and Walid Gomaa},
  title     = {Guided Code Generation with LLMs: A Multi-Agent Framework for Complex Code Tasks},
  journal   = {arXiv preprint arXiv:2501.06625},
  year      = {2025},
  url       = {https://arxiv.org/abs/2501.06625}
}
```
Self-Debugging:
```bibtex
@inproceedings{chen2024selfdebugging,
  author    = {Xinyun Chen and Maxwell Lin and Nathanael Schärli and Denny Zhou},
  title     = {Teaching Large Language Models to Self-Debug},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2024},
  url       = {https://openreview.net/forum?id=eO3YzBcD68}
}
```
MetaGPT:
```bibtex
@article{metagpt2023,
  author    = {Sirui Hong and Xinyang Zhang and Yu Gu and Yuzhang Li and Jianye Hao and Yang Yu},
  title     = {MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework},
  journal   = {arXiv preprint arXiv:2308.00352},
  year      = {2023},
  url       = {https://arxiv.org/abs/2308.00352}
}
```
MapCoder:
```bibtex
@inproceedings{islam2024mapcodermultiagentcodegeneration,
      title={MapCoder: Multi-Agent Code Generation for Competitive Problem Solving}, 
      author={Md. Ashraful Islam and Mohammed Eunus Ali and Md Rizwan Parvez},
      year={2024},
      eprint={2405.11403},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2405.11403}
}
```

## Contact

If you have questions about this evaluation, Report or the seminar presentation, feel free to ask.

---

*This repository contains evaluation materials only. The original PairCoder implementation can be found [here](https://github.com/nju-websoft/PairCoder) by Zhang, Huan and Cheng, Wei and Wu, Yuhan and Hu, Wei*
