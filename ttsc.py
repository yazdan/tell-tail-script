#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from jira import JIRA
from PythonConfluenceAPI import ConfluenceAPI
import json
import frontmatter
import markdown
import logging

g_jira_url = ''
g_confluence_url = ''
g_user = ''
g_pass = ''
g_fileName = ''
g_update_title = False
g_add_rtl = False

def parseArgs(args):
    global g_jira_url
    global g_confluence_url
    global g_user
    global g_pass
    global g_fileName
    global g_update_title
    parser = argparse.ArgumentParser(description='Sends markdown text to jira and confluence.')
    parser.add_argument('-j','--jira', help='Jira URL', required=True)
    parser.add_argument('-c','--confluence', help='Confluence URL', required=True)
    parser.add_argument('-u','--user', help='Confluence and Jira username', required=True)
    parser.add_argument('-p','--password', help='Confluence and Jira password', required=True)
    parser.add_argument('-tu','--title-update', help='update if title is not unique', action='store_true')
    parser.add_argument('-rtl','--add-rtl', help='Add rtl related things to markdown', action='store_true')
    parser.add_argument('filename', help='Markdown Filename to process')
    

    args = parser.parse_args()
    
    g_jira_url = args.jira
    g_confluence_url = args.confluence
    g_user = args.user
    g_pass = args.password
    g_fileName = args.filename
    g_update_title = args.title_update
    g_add_rtl = args.add_rtl

def jira(url, metadata):
    if metadata['jira_id'] is None:
        return
    options = {
    'server': g_jira_url}
    jira = JIRA(options,basic_auth=(g_user, g_pass))    # a username/password tuple

    # Get an issue.
    issue = jira.issue(metadata['jira_id'])
    
    addedContent = metadata['jira_prefix'] + ' ' + url

    new_description = addedContent

    if issue.fields.description is not None:
        new_description = issue.fields.description + '\n' + addedContent
    #jira.add_comment(issue, addedContent)
    issue.update(notify=False, description=new_description)


def confluence(html, metadata):
    # Create API object.
    api = ConfluenceAPI(g_user, g_pass, g_confluence_url)
    update_content = False
    url = ''
    current_history = 0
    update_content_id = ''
    
    # Check if confluence_id is not null and refer to a valid post
    if metadata['confluence_id'] is not None:
        content = api.get_content_by_id(metadata['confluence_id'])
        if content is not None:
            update_content = True
            current_history = content['version']['number']
            update_content_id = metadata['confluence_id']
            logging.info('updating post with given id')

    # Check if space is available
    if (metadata['confluence_space'] is not None) and (not update_content):
        space = api.get_space_information(metadata['confluence_space'])
        if space is None:
            raise Exception('Space not found')
    
    # Check if title is unique
    if (metadata['title'] is not None) and (not update_content):
        content = api.get_content(title = metadata['title'])
        if content is not None:
            if content['size'] > 0:
                if g_update_title:
                    update_content = True
                    found_id = content['results'][0]['id']
                    found_post = api.get_content_by_id(found_id)
                    if found_post is not None:
                        current_history = found_post['version']['number']
                        update_content_id = found_id
                    logging.info('Updating duplicate Title')
                else:
                    raise Exception('Title is found but not updating')
    
    if not update_content:
        post_content = {
            "type": "page",
            "title": metadata['title'],
            "space": {
                "key": metadata['confluence_space']
            },
            "body": {
                "storage": {
                    "value": html,
                    "representation": "storage"
                }
            },
            "ancestors":[{
                "id":metadata['confluence_parent_id']
            }]
        }
        res = api.create_new_content(post_content)
        links = res['_links']
        url = links['base']+links['webui']
    else:
        post_content = {
            "id": update_content_id,
            "type": "page",
            "title": metadata['title'],
            "space": {
                "key": metadata['confluence_space']
            },
            "version": {
                "number": current_history + 1,
                "minorEdit": False
            },
            "body": {
                "storage": {
                    "value": html,
                    "representation": "storage"
                }
            }
        }
        res = api.update_content_by_id(post_content, update_content_id)
        links = res['_links']
        url = links['base']+links['webui']
    return url
    
def main(args):
    
    parseArgs(args)
    
    post = frontmatter.load(g_fileName)
    
    if post.metadata is None or len(post.metadata) == 0:
        logging.critical('File must start with front matter')
        return 1

    if g_add_rtl:
        post.content = '<div style="direction: rtl;" markdown="1">' + post.content + '</div>'

    html = markdown.markdown(post.content,['markdown.extensions.extra'])
    
    try:
        url = confluence(html, post.metadata)
    except Exception as inst:
        logging.critical('Confluence error')
        logging.critical(inst)
        return 1
    
    try:
        jira(url, post.metadata)
    except Exception as inst:
        logging.critical('Jira error')
        logging.critical(inst)
        return 1

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
