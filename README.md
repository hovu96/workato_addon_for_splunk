![](static/screenshot.png)

# Introduction

Welcome to the Workato Add-on for Splunk. This add-on enables [Splunk](https://www.splunk.com/) to integrate with the [Workato](https://www.workato.com/) platform.

Features:
- Sending alerts from Splunk to Workato
- Sending events from Workato to Splunk **(not yet implemented)**
- Running Splunk searches from Workato **(not yet implemented)**

# Installation

Until now, this add-on is not published on [Splunkbase](splunkbase.splunk.com). But that will change in future.

Currently, this add-on is available on [GitHub](https://github.com/hovu96/workato_addon_for_splunk) only. Once you clone the repository or download as ZIP, proceed installation *only* on the Splunk Search Head as described in the [Docs](http://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall#Search_heads).

As this add-on provides Splunk REST API endpoints for Workato, the Splunk Search Head's management port (by default, 8089) must be available for incoming HTTP/S requests.

To allow Splunk to send alerts to Workato (to trigger the execution of Workato recipes), the Splunk Search Head must be allowed to send HTTPS requests on port 443 to www.workato.com.

To allow Workato to send events to Splunk (sent by Workato actions as part of the execution of recipes), the Splunk Indexer's [HTTP Event Collector (HEC)](http://dev.splunk.com/view/event-collector/SP-CAAAE6M) feature must be enabled and the HEC port (by default, 8088) must be available for incoming HTTPS requests.

# Usage

To learn more about Splunk and how to create alerts, refer to [Getting Started with Splunk](https://www.splunk.com/en_us/resources/getting-started.html) and the [Splunk Docs](http://docs.splunk.com/Documentation/Splunk/latest).

To learn more about Workato and how to create Workato recipes using Application Connections, Triggers and Actions, refer to [Workato Docs](http://resources.workato.com/how-it-works/) and [Workato Support Portal](https://support.workato.com/support/home).

To use this add-on, create Workato recipes that leverage the *Splunk* application within the Workato platform.

## Sending alerts from Splunk to Workato

Splunk alerts are used to monitor for and respond to specific events. They use saved searches to look for events in real-time or on a schedule. Alerts trigger when search results meet specific conditions. Alert actions can be used to respond when alerts trigger.

This add-on allows Workato to subscribe for Splunk alerts to trigger the execution of a Workato recipe.

### Custom Splunk alerts

Proceed the following steps:

1. Log in to Splunk to identify an existing Splunk alerts or create a new Splunk alert as described in the [Docs](http://docs.splunk.com/Documentation/Splunk/latest/Alert/AlertWorkflowOverview).
2. Select *Workato* as action for the alert.
3. Log in to Workato to create a new recipe. Select the *Splunk* application and *New generic alert* as trigger for the recipe.
4. Enter the field names that you expect to be within each Splunk alert. That allows you to pass the data from alert to actions within the Workato recipe.
5. Select the alert that the Workato recipe will subscribe for.
6. Add actions to the Workato recipe to process triggered alerts.

### Splunk security alerts

*not yet implemented*

### Splunk IT service alerts

*not yet implemented*

## Sending events from Workato to Splunk

*not yet implemented*

## Running Splunk searches from Workato

*not yet implemented*
