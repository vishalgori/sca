### Integrated Static Code Analysis including Open Source Analysis using Gitlab CI/CD

## Pre-requisites
* Run setup script to create new projects and add source control for them in Checkmarx
* Add user credentials to Gitlab CI secret variables for Checkmarx authentication as CxUSER and CxPASS
* Edit gitlab-ci.yml to include below config post build in any Dev stage:
```
    script:
        - ./scan.sh
```
# P.S. Integration tested for build using gradle. Requires a separate task in gradle config to download dependencies (Edit scan.sh depending on your project structure).
