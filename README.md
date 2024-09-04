# AI Course Creator
## Create upwards of 60 hours of educational content, complete with practice questions, given a topic phrase.

<img src="app/client/public/hero.jpeg" alt="app hero" width="350" style="padding-bottom: 20px;"/>

- [AI Course Creator](#ai-course-creator)
	- [Create upwards of 60 hours of educational content, complete with practice questions, given a topic phrase.](#create-upwards-of-60-hours-of-educational-content-complete-with-practice-questions-given-a-topic-phrase)
	- [System requirements](#system-requirements)
	- [Setup](#setup)
	- [Quick Start](#quick-start)
		- [Open in Browser](#open-in-browser)
	- [Run New Generation](#run-new-generation)
		- [CLI Mode](#cli-mode)
		- [App Mode](#app-mode)
	- [Generation Jobs](#generation-jobs)
		- [Generate Outline](#generate-outline)
		- [Generate Page Material With Interactives](#generate-page-material-with-interactives)
		- [Generate Page Material Only](#generate-page-material-only)
		- [Generate Interactives](#generate-interactives)
		- [Compile Interactives (Optional)](#compile-interactives-optional)
		- [Resume Job](#resume-job)
	- [Adding Topics](#adding-topics)
	- [Prompts](#prompts)
	- [Outlines](#outlines)
	- [Utilities](#utilities)
	- [Under the Hood](#under-the-hood)
	- [Contributing And Bug Fixes](#contributing-and-bug-fixes)


## System requirements
- Ensure Python version of `3.12` or higher. (*I personally recommend [pyenv](https://github.com/pyenv/pyenv) with the [virtualenv](https://github.com/pyenv/pyenv-virtualenv) extension*). Repo contains pyenv `.python-version` file with preferred version.
- Ensure Node is installed with version `18.x` or higher. `app/client` contains `.nvmrc` file with preferred version. 

## Setup
`git clone https://github.com/AlextheYounga/ai-course-creator.git`

`pip install -r requirements.txt` 

## Quick Start
Use the example sqlite database which contains 13 courses on *"Calculus From the Perspective of Python Programming"*

```bash
unzip storage/example/python-calculus.db.zip && mv database.db db/database.db
```

**Run `python run.py`**

Running this command will automatically create default config files including a default `.env` file, which is where we will store variables like our OpenAI API keys. Check this file and add your keys there. 

```bash
APP_ENV=development
LLM_CLIENT=OPENAI
OPENAI_API_KEY=your-open-api-key
DB_URL='sqlite:///db/database.db'
OUTPUT_DIRECTORY='out'
```

### Open in Browser
```
(ai-course-creator) M1:ai-course-creator alexyounger$ python run.py
[?] Select command category:
   Start Course Creator
   Utilities
 > Run App Server
```

This will install the required node packages, build the app, and then open the browser towards the correct localhost server.

**Dashboard View**
<img src="app/client/public/dashboard.jpg" alt="dashboard" style="padding-bottom: 20px;"/>

**Page Content View**
<img src="app/client/public/page.jpg" alt="page" style="padding-bottom: 20px;"/>

**Content Interactive Questions**
<img src="app/client/public/interactives.jpg" alt="interactives" style="padding-bottom: 20px;"/>

## Run New Generation
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
   Compile Interactives
   Resume Job
```

### App Mode
You can also run new generations from the frontend, although bear in mind that the CLI has been prioritized over the frontend application, and there may be some instabilities in this form. There is also currently no way to view the progress of a new generation from the frontend; this can only be viewed from the terminal. 

<img src="app/client/public/new-generation.jpg" alt="interactives" style="width: 50%; padding-bottom: 20px;"/>

## Generation Jobs
> The jobs system was developed with tremendous help from the legend [Billy W. Conn](https://github.com/TheDauthi). I had never built a job queue from scratch, and I had trouble finding a simple Python jobs queue package. Although he didn't commit directly to this repo, he wrote most of the code in `src/jobs`, and I only adjusted the code in a few places, *(and by adjusted I mean butchered his beautiful work)*. The code in that folder generally looks better than all other code in this application, but it looked even better before I got ahold of it. The comments in those files are also his. 

### Generate Outline
Generate an outline of courses, their chapters, and pages, given a single topic. This will create a random number of courses, but can be as high as 25 courses.

### Generate Page Material With Interactives
Generate page material for each page in the course, as well as create interactive question for practice challenges. Interactives will be generated based on the material in each page.
Kinds of interactive questions: 
- Multiple Choice
- Fill in the Blank (this may be broken)
- Code Editor 
  - These are currently not runnable. One item on the TODO list is to add [Judge0](https://judge0.com/) code execution to handle this. All of the information exists to make this runnable, and testable. 
- Codepen Embed
  - Is not runnable but allows for interactive components within programming course content 

### Generate Page Material Only
Generate page material only, without interactives.

### Generate Interactives
This will generate only interactives, but this is only possible if page material has been generated prior to this. Interactives are generated for each page. 

### Compile Interactives (Optional)
Associate interactives with page material. This process happens automatically when generating page material with interactives, but there were times when I needed to run this process by itself, so I kept it. 

### Resume Job
Cut a job short? Here's how you can keep it running where you last left off. (May contain a few bugs)

## Adding Topics
Topics can be added in two places: 
- Topics can be created either from the CLI by doing `Start Course Creator` -> `Create New`
- From the frontend application by going to the `Topics` tab and hitting the `Create New` button

There was a specific emphasis on programming topics, but this can handle technically any topic you can think of. Ideally, the topic is at most a partial sentence. Something like 

**Good topics:**
- "Sailing"
- "Advanced Sailing"
- "Sailing Around the World"
- "sailing around the world"

**Bad Topics:**
- "I want to learn sailing"
- "Yo lemme get that Jack Sparrow aura!"

Topics can also have their own configurations. For instance, maybe you don't want any coding related interactives on a topic about "Sailing". Currently, the only place we can add those topics settings are the in the `configs/topics.yaml`. 

Please see the `topics.example.yaml` file to see an example of the available topic settings. 

This is not ideal, and I have already built out the ability to change these settings from the `Run New Generation` page, but I have yet to hook this up throughout the app. Currently, those settings do nothing. Sorry, it's a WIP people!

## Prompts
> Had a ton of help with the prompts from [Trey Goff](https://github.com/JohnGaltjr), who also helped discover some interesting phenomenon with ChatGPT. Thanks!

Prompts are located in the `storage/prompts` folder, and are broken up into distinct prompt "collections". You can assign a collection to each topic in the topic settings located in `topics.yaml`. If a prompt does not exist in a particular collection, the prompt from `storage/prompts/core` will be used.

If you want to change prompts, you can add a custom prompt collection by making a new folder in the `storage/prompts` folder and then assign that collection to a topic in the `configs/topics.yaml` file. Copy the specific prompt you want to 
edit into this folder. 

## Outlines 
All course generations require an initial outline. The LLM will output a yaml structure of courses, with chapters and pages.

Example output from the LLM that will be used to create courses, chapters, and pages. By default, you'll get an output with approximately 25 objects shaped like the following. 
```yaml
- courseName: "An Intriguing Course Name"
  chapters:
    - name: "An Interesting Chapter Name"
      pages:
        - "First Page of Chapter"
        - "Second Page of Chapter"
        - "Third Page of Chapter, and so on"
    - name: "Another Interesting Chapter Name"
      pages:
        - "First Page of Chapter"
```

These outlines can also be edited from the frontend App Mode under the `Outlines` tab. You can also create a new outline from scratch. 

<img src="app/client/public/outlines.jpg" alt="interactives" style="padding-bottom: 20px;"/>

## Utilities
```
[?] Select utility command:
 > Backup Database
   Dump Content From Existing Outline
   Run DB Migrations
```

- Backup Database
  - Will create a zipped backup of your database in the storage folder. Very useful
- Dump Content From Existing Outline
  - Will dump all content from a particular outline in the `out/` folder in markdown format. 
- Run DB Migrations
  - This is used for making database changes. I had to write my own SQLite migrations system; it actually works surprisingly well. 

## Under the Hood
The Course Creator uses an event/handler architecture, events are associated with event handlers, and all managed in Redis queues. All event handlers are processed by Redis as if they are a distinct job with no knowledge of each other. This creates a kind of "state machine" system, where every single action can be accounted for. This is a very practical system for any complex AI-based architecture, and allows for easy maintenance as well as a near-infinite number of configurations and flows. 

The one tradeoff of this system: more code. More code is generally considered a no-no, but if you value *clarity above all, as I do, then this is an acceptable tradeoff. There is a lot of code, but it is very simple. If you want to create a new event-handler flow in order to facilitate a new feature, you can copy 80% of the code from another handler. 

Example Event: 
```python
# src/events/events.py
class GenerateSomethingFromLLMRequested(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data

class ProcessResponseFromLLM(Event):
    def __init__(self, data, id=cuid()):
        super().__init__()
        self.id = id
        self.data = data
```

Example Handler:
```python
# src/handlers/generate_something_from_llm_handler.py
from src.events.events import ProcessResponseFromLLM

class GenerateSomethingFromLLMHandler:
    def __init__(self, data: dict):
        self.data = data
        self.db = DB()

    def handle(self) -> Outline:
		response = self._get_response_from_llm()
		# call another event
		return ProcessResponseFromLLM(self.data) 

    def _get_response_from_llm(self) -> dict:
		pass
```

Event Registry:
```python
# src/events/events_registry.py
# EventRegistry.register(event, handler)
EventRegistry.register(GenerateSomethingFromLLMRequested, GenerateSomethingFromLLMHandler)
EventRegistry.register(ProcessResponseFromLLM, ProcessResponseFromLLMHandler)
```

[Excalidraw of Event Handler Flow](https://excalidraw.com/#json=phzY33DD563eCRY5Du_kK,G0ozwD2bo2nOf1l8doX9eA)
<img src="app/client/public/graph.jpg" alt="interactives" style="padding-bottom: 20px;"/>

## Contributing And Bug Fixes
I keep a running [TODO list (docs/todo.md)](https://github.com/AlextheYounga/ai-course-creator/blob/3394aa96fba3a764b10f33e84f16e7c92d5f7010/docs/todo.md) of things I'd like to do. I am also willing to add to that todo list if there's something you want to see. 

I will always read pull requests. I may not always merge pull requests.
I definitely would love some help improving this. I will attempt to improve the documentation as time goes on. 