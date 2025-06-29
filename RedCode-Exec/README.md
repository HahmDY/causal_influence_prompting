<h1 align="center"><img src="assets/RedCode-logo-512.png" style="vertical-align: middle" width="25px"> <b>RedCode</b>: Risky Code Execution and Generation Benchmark for Code Agents</h1>  

<p align="center">
  📄 <a href="https://arxiv.org/abs/2411.07781"><b>[Paper]</b></a>
  🌐 <a href="https://redcode-agent.github.io"><b>[Webpage]</b></a>
</p>


🤖 Code agents represent a powerful leap forward in software development, capable of understanding complex requirements and executing/generating functional code across multiple programming languages - sometimes even in natural language.


## 📂 Repository Structure

### Dataset

This directory contains the datasets `RedCode-Exec`, which are used as inputs for the agents.

### Environment

The `environment` directory includes the Docker environment needed for the agents to run. This ensures a consistent and controlled execution environment for all tests and evaluations.

### Result

The `result` directory stores the results of the evaluations.

## 📚 Citation

```
@article{guo2024redcode,
  title={RedCode: Risky Code Execution and Generation Benchmark for Code Agents},
  author={Guo, Chengquan and Liu, Xun and Xie, Chulin and Zhou, Andy and Zeng, Yi and Lin, Zinan and Song, Dawn and Li, Bo},
  booktitle={Thirty-Eighth Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
  year={2024}
}
```