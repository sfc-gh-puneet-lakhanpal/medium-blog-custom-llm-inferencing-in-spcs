# Steps to create an llm api hosted in snowpark container services
## Prerequisities
    - Snowpark Container Services
    - Docker
## Step by Step guide
1. run script `common-setup.sql`. 

2. Install SnowSQL CLI and configure it following these instructions: https://docs.snowflake.com/en/user-guide/snowsql-install-config. Configuration will look like the following in ~/.snowsql/config:

```
[connections.default]
accountname = X
username = X
password = X
warehouse = X
dbname = X
schemaname = X
rolename = X
```

Note that the connection name `sfsenorthamericademo391` is being used in `deploy_api/Makefile`. So if you change the connection name in SnowSQL cli config name, please change in Makefile too.

3. Open a terminal, navigate to the `download_model` folder, put your variables in `config.env` and update hugging face token in download_model.yaml. Lastly, update the image name in `download_model.yaml` and run `make all`. This should start the docker build, tag and push to image repo. This will also upload the spec YAML file to snowflake stage. Now run the `downloadmodel-setup.sql`.


4. Now navigate to the `deploy_api` folder, put your variables in `config.env`, update the image name in `ray_vllm.yaml` and run `make all`. This should start the docker build, tag and push to image repo. This will also upload the spec YAML file to snowflake stage. Now, run `restapi-setup.sql` to create the service and get the api link.