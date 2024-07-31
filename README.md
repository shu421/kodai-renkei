# 高大連携2024年度用リポジトリ

## Build Environment

1. clone this repository
   ```bash
   git clone git@github.com:shu421/kodai-renkei.git
   cd kodai-renkei
   ```
2. install [rye](https://rye-up.com/)
   - install instructions: https://rye-up.com/guide/installation/
3. enable [uv](https://github.com/astral-sh/uv) to speed up dependency resolution.
   ```bash
   rye config --set-bool behavior.use-uv=true
   ```
4. create a virtual environment
   ```bash
   rye sync
   ```

## Run app
```bash
rye run streamlit run app/main.py

or

streamlit run app/main.py
```
