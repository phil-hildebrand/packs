#!/usr/bin/env python
import requests
import sys

'''
    Gets the agent count for your organisation broken down by sub-account.
'''

# Set your API key from your user settings page: https://app.dataloop.io/#/user-account/api-tokens
API_KEY = ''
# Set your organisation ID here
ORG = ''
# Only change this if using a different API endpoint (for testing)
API_BASE_URL = "https://api.dataloop.io/v1/orgs/%s" % (ORG)

'''
    Main method. Gets a count of all the agents for an organisation, broken down by sub-account
'''


def get_agent_count():
    count = {'total': 0}

    # List all the accounts for your org
    accounts = make_request('/accounts?view=counts')

    # Loop through all accounts to get no. of agents
    for account in accounts:

        name = account['name']
        agent_count = 0

        # Need to loop through agents to ensure we're not counting docker containers
        agents = make_request('/accounts/' + name + '/agents')

        for agent in agents:
            if ('osName' in agent) and (agent['osName'] != 'docker'):
                agent_count += 1
            elif ('provider' in agent) and (agent['provider']) and (agent['provider']['service'] == 'ec2'):
                agent_count += 1

        count[name] = agent_count
        count['total'] = count['total'] + agent_count

    # Print Nagios output
    output = "OK | "
    for key, value in count.iteritems():
        if key != 'total':
            output += "usage.agents.account." + key + "=" + str(value) + ";;;; "
        else:
            output += "usage.agents.total=" + str(value) + ";;;; "
    print output


'''
    Make a request to the Dataloop.IO API with authentication token
'''


def make_request(url):
    headers = {'authorization': 'Bearer ' + API_KEY}
    resp = requests.get(API_BASE_URL + url, headers=headers)
    if resp.status_code == 200:
        json = resp.json()
        return json
    else:
        print "Error reading URL " + API_BASE_URL + ". Status Code: " + str(resp.status_code)
        sys.exit(2)


get_agent_count()