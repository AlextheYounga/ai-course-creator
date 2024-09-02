# AI Course Creator


<img src="app/client/public/hero.jpeg" alt="app hero" width="350" style="padding-bottom: 20px;"/>

- [AI Course Creator](#ai-course-creator)
	- [System requirements](#system-requirements)
	- [Setup](#setup)
	- [Quick Start](#quick-start)
		- [CLI Mode](#cli-mode)
		- [App Mode](#app-mode)


## System requirements
- Ensure Python version of `3.12` or higher. (I personally recommend [pyenv](https://github.com/pyenv/pyenv) with the [virtualenv](https://github.com/pyenv/pyenv-virtualenv) extension). Repo contains pyenv `.python-version` file with preferred version.
- Ensure Node is installed with version `18.x` or higher. `app/client` contains `.nvmrc` file with preferred version. 

## Setup
`git clone https://github.com/AlextheYounga/ai-course-creator.git`

`pip install -r requirements.txt` 

## Quick Start
**Run `python run.py`**

Running this command will automatically create default config files including a default `.env` file, which is where we will store sensitive information such as our OpenAI API keys. Check this file and add your keys there. 

```bash
APP_ENV=development
LLM_CLIENT=OPENAI
OPENAI_API_KEY=your-open-api-key
DB_URL='sqlite:///db/database.db'
OUTPUT_DIRECTORY='out'
```

### CLI Mode
```
(ai-course-creator) ai-course-creator$ python run.py
[?] Select command category:
 > Start Course Creator
   Utilities
   Run App Server

[?] Which topic would you like to generate course material for?:
   Create New
   All
 > Ruby on Rails

[?] Select task:
 > Generate Outline
   Generate Page Material With Interactives
   Generate Page Material Only
   Generate Interactives
   Resume Job
```

### App Mode