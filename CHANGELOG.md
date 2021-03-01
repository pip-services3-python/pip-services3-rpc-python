# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Services Logo" width="200"> <br/> Remote Procedure Calls for Python Changelog

## <a name="3.1.4"></a> 3.1.4 (2021-03-01)

### Bug Fixes
* Fixed HttpEndpoint redirect
* Fixed HttpResponseSender.send_deleted_result
* Fixed RestService dependency_resolver init config
* Fixed returned result StatusRestService

## <a name="3.1.3"></a> 3.1.3 (2021-02-26)

### Features
* Added ISwaggerService
* Added CommandableSwaggerDocument for api info generation

### Bug Fixes 
* Fixed static members HttpEndpoint and RestService
* Fixed JSON-dict convertation in clients & services

## <a name="3.1.2"></a> 3.1.2 (2021-02-07)

### Bug Fixes
* Fixed **HttpEndpoint.close**

## <a name="3.1.1"></a> 3.1.1 (2020-12-21)

### Bug Fixes
* Fixed **HttpResponseSender**, **RestOperations** send_deleted_result methods
* Fix threads in **HttpEndpoint**

## <a name="3.1.0"></a> 3.1.0 (2020-08-04)

### Bug Fixes
* Fixed validation in RestService

## <a name="3.0.0"></a> 3.0.0 (2018-10-19)

Initial public release

### Features
* **Auth** - authentication and authorisation components
* **Build** - HTTP service factory
* **Clients** - retrieving connection settings from the microservice’s configuration
* **Connect** - helper module to retrieve connections
* **Services** - basic implementation of services
