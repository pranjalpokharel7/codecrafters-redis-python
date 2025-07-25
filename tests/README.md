# Tests

We have two types of tests for our app -
1. **Unit Tests:** Unit tests are mostly concerned with testing individual modules and functionalities, examples include testing rdb parsing, testing individual commands execution, etc.
2. **Integration Tests:** For integration tests, we run our app as the redis server and use the redis-cli to send various commands to our server.

Each type of test has it's own dedicated module.
