Collection of several Dagster projects to serve as a reference for how to use Dagster in a variety of scenarios + provide code snippets.

Data Engineering with the Open Source Modern Data Stack (From MDS Fest '23)
https://www.youtube.com/watch?v=JHCDgRbWWq0&ab_channel=Dagster

Feel free to add relevant learning resources and projects.

## east-learnings
https://github.com/madviking/dagster-examples/east-learnings
We are collecting some useful information about our own Dagster learnings in here. Please note that our team is a beginner when it comes to Dagster, so there might be bits that go against best practices. We are learning as we go and will update this README with new information as we learn more.

Few words of our setup:
- we rely on Terraform for orchestrating and entire Dagster setup is based on Docker containers
- we are using Google Secrets for storing sensitive information
- we are using a dynamic repo to load all of our Dagster projects
- Dagster is setup to communicate with our Docker based services, startup script configures hosts
- our project structure includes only some general examples, not full codebase
