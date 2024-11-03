# TMK: Automated System for Clinical Trial Recruitment

### High-Level Design

**Objective:**

- Identify potential participants for a clinical trial on Reddit. Ranked by potential interest.

**The key characteristics of the data are:**

- Data is the comments from users on Reddit.
- Comments is a **conversational** data.
- A user can **comment multiple times** in the same post and participate in **multiple posts**.
- The comments are **hierarchical**. And comments have **scores**.

**Approach(With many assumptions):**

- There are two types of potential participants:
  - Those who express **interest** in the trials for **making money**.
  - Those who are **already suffering from illness** and **want to try new treatments**.
- For the **first type**, we will target those who post about **trials** directly on clinical trial subreddits.
  - We will scrape the subreddits like `clinical_trials` or `passive_income` targeting the questions like "What are the best clinical trials for money making?".
  - Targeting the **positive** sentiment users, especially the posters.
- For the **second type**, we will target those who post about their **dissatisfaction of current treatments** on subreddits related to their illnesses.
  - We will scrape the subreddits like `ChronicPain` targeting the questions like "What are the best treatments for depression?".
  - Targeting the **negative** sentiment users, especially the poseter or frequent commenters.
- Process the raw data to establish a user-centric database to store the user-level features, to support the interest analysis and message generation. Those information needs to be extracted from the comments(it is ok to be null or approximate).
  - The features include:
    - Demographics: Age, Gender, Location, Income, Education, etc.
    - Health-related: Illness type, Treatment history, etc.
    - Interest: Interest in clinical trials, Interest in making money, etc.
    - Sentiment: Sentiment towards clinical trials, Sentiment towards current treatments, etc.
    - Engagement: Number of comments, Number of upvotes, etc.

### Detailed Design

**1. Scraping:**

A simple API tool is enough for scraping. It selects posts based on hotness. It needs to extract all the comments and their scores.

**2. Extracting Features:**

A workflow is designed for this task.

- For each comments, run a feature extract agent.
  - The agents need to extract the features and save it to the database.
  - In this NLP task, GPT api can be used to extract the pre-defined features as a simple solution.
  - Feature list:
    - Demographics: Age(range), Gender(M/F), Location(state,city,rural/urban), Income(high/medium/low), Education(high/medium/low).
    - Health-related: Illness type(need business input), Treatment history(need business input).
    - Interest: Interest in clinical trials(high/medium/low), Interest in making money(high/medium/low).
    - Sentiment: Sentiment towards clinical trials(high/medium/low and positive/negative), Sentiment towards current treatments(high/medium/low and positive/negative).
    - Engagement: Number of comments(numeric), Number of upvotes(numeric).
  - Each agent is a simple prompted GPT for one type of feature. It is asked to reasoning step by step for final assigned label.
  - Another agent is responsible for checking hallucination. It can be designed as a Natural Language Inference task. For example, it can check if the reason given by the feature extraction agent is possible for the user.
  - Use python pandas to mimic the database.

**3. Rank the users:**

As the more data comes, the user information will be more and more accurate. 

- Based on the features and given business rules, we can rank the users.
- For example:
  - Target male users who are interested in clinical trials and making money. Ranked by **Sentiment towards clinical trials** and **Interest in making money** where the gender is **Male**.
  - Target female users who are suffering from depression and dissatisfied with current treatments. Ranked by **Sentiment towards current treatments** and **Interest in clinical trials** where the gender is **Female** and the illness type is **Depression**.


### Run the code

#### 1. Demo

Check **demo.ipynb** for a demo.

#### 2. Or run the code from command line

```bash
pip install -e .
python tmk/main.py --config config/default_config.yaml
```

### Future Work

 - Many many essetial things must be done.
 - ...
