<h1 align="center">Steal My Neko🐈</h1>

<div align="center">
  <a href="#installation">Installation</a> •
  <a href="https://t.me/nekosv/3">Changelog</a> •
  <a href="#contributing">Contributing</a><br><br>
  <a href="https://t.me/nekosv"><img alt="Telegram - Channel" src="https://img.shields.io/badge/Telegram-Channel-blue?style=flat-square&logo=telegram"></img></a>
</div>

## About
Awesome Telegram parser & poster configured to steal nekos.  
Script uses web and telegram parsers. Telegram parser requires user account to receive and use file_id directly.
Telegram parser supports ad block which automatically detects ad links and mentions. Unfortunately, ad blocking also blocks any album for now.

Started in June 2021
## Installation
1. Clone repository:  
```git clone https://github.com/unxho/steal-my-neko && cd steal-my-neko```  
2. Install requirements:  
```pip install -r requirements.txt```  
You can additionaly install `optional-requirements.txt` which will make the script faster, but also may cause os-related bugs.  
3. Rename example config:  
```mv {example.,}config.ini```  
And fill it in.
4. Start the script:  
```python -m smn```

## Contributing
<details>
<summary>Please read before contributing.</summary>

#### Tools
**Formatter:** [`yapf`](https://github.com/google/yapf)  
**Linter:** [`pylint`](https://github.com/PyCQA/pylint)

#### Always test your changes.  
Do not submit something without at least running the module.  

#### Do not make large changes before discussing them first.
We want to know what exactly you are going to make to give you an advice and make sure you are not wasting your time on it.

#### Do not make formatting PRs.  
We know that our code might be not clean enough, but we don't want to merge, view or get notified about 1-line PR which fixes trailing whitelines. Please don't waste everyone's time with pointless changes.
</details>
