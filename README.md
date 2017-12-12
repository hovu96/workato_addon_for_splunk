![](static/screenshot.png)

# Introduction

Welcome to the Workato Add-on for Splunk. This add-on enables [Splunk](https://www.splunk.com/) to integrate with the [Workato](https://www.workato.com/) platform.

Features:
- Sending alerts from Splunk to Workato
- Sending events from Workato to Splunk
- Running Splunk searches from Workato

# Installation

General information about installing Splunk add-ons, refer to the [Splunk docs](About installing Splunk add-ons). For distributed Splunk Enterprise environment, this add-on has to be installed on a Splunk Search Head *only*.

As this add-on provides Splunk REST API endpoints for Workato, the Splunk Search Head's management port (by default, 8089) must be available for incoming HTTP/S requests.

To allow Splunk to send alerts to Workato (to trigger the execution of Workato recipes), the Splunk Search Head must be allowed to send HTTPS requests on port 443 to www.workato.com.

# Usage

To learn more about Splunk and how to create alerts, refer to [Getting Started with Splunk](https://www.splunk.com/en_us/resources/getting-started.html) and the [Splunk Docs](http://docs.splunk.com/Documentation/Splunk/latest).

To learn more about Workato and how to create Workato recipes using Application Connections, Triggers and Actions, refer to [Workato Docs](http://resources.workato.com/how-it-works/) and [Workato Support Portal](https://support.workato.com/support/home).

To use this add-on, create Workato recipes that leverage the [Splunk](https://www.workato.com/integrations/splunk) application within the Workato platform.

## Sending alerts from Splunk to Workato

Splunk alerts are used to monitor for and respond to specific events. They use saved searches to look for events in real-time or on a schedule. Alerts trigger when search results meet specific conditions. Alert actions can be used to respond when alerts trigger.

This add-on allows Workato to subscribe for Splunk alerts to trigger the execution of a Workato recipe.

### Custom Splunk alerts

Proceed the following steps:

1. Log in to Splunk to identify an existing Splunk alerts or create a new Splunk alert as described in the [Docs](http://docs.splunk.com/Documentation/Splunk/latest/Alert/AlertWorkflowOverview).
2. Select *Workato* as action for the alert.
3. Set alert permissions to "Shared Globally".
4. Log in to Workato to create a new recipe. Select the *Splunk* application and *New generic alert* as trigger for the recipe.
5. Enter the field names that you expect to be within each Splunk alert. That allows you to pass the data from alert to actions within the Workato recipe.
6. Select the alert that the Workato recipe will subscribe for.
7. Add actions to the Workato recipe to process triggered alerts.

### Splunk IT service alerts

Proceed the following steps:

1. Install and configure [Splunk IT Service Intelligence](https://splunkbase.splunk.com/app/1841/)
3. Log in to Workato to create a new recipe. Select the *Splunk* application and *New service alert* as trigger for the recipe.
6. Add actions to the Workato recipe to process triggered alerts.

### Splunk security alerts

*not yet implemented*

## Sending events from Workato to Splunk

Workato provides a recipe action to send events to Splunk.

Proceed the following steps:

1. Log in to Workato to create a new recipe.
2. Select whatever application as an trigger for the recipe.
3. Select the *Splunk* application and then select the *Send event to Splunk* action
4. Specify the event data in the *Payload* field
5. Optionally, specify the fields *Index*, *Source*, *Sourcetype* and *Host*   

## Running Splunk searches from Workato

Workato provides receipe actions to run searches within Splunk. You can either select from one of the Saves Searches (predefined searches within Splunk) or specify an custom/ad-hoc search to run.

Proceed the following steps:

1. Log in to Workato to create a new recipe.
2. Select whatever application as an trigger for the recipe.
3. Select the *Splunk* application and then select the one of the actions to run searches within Splunk
