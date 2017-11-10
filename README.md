# tell-tail-script
A script inspired approach to documenting user stories in Confluence and Jira.

This is why I started this project. I never was sure where I supposed to document my Agile User Stories: 

- in Jira issue?
- in Confluence?
- in which format? Docx? Markdown?

And I like following things:

- Git
- Markdown
- Python

So I'm trying to develop a simple python script that helps me to write the story once and post them on Jira and Confluence simultaneously.

# Design

It is assumed that all files are in Markdown format wi TOML header as metadata currently follwoing metadata is needed

- Jira issue id(`jira_id`) : this can be null that means it don't repot to Jira
- Jira description prefix(`jira_prefix`) : use to add something to the description of Jira issue
- Confluence page id(`confluence_id`): this can be null for new pages
- Confluence Parent id(`confluence_parent_id`): This also can be null
- Confluence Space id(`confluence_space`): This cannot be null
- Title(`title`)


There are follwoing cmd options

- jira url
- confluence url
- username
- passowrd
- title-update


