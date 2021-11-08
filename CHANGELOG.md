# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Services Logo" width="200"> <br/> Remote Procedure Calls for Python Changelog

## <a name="3.3.0"></a> 3.3.0 (2021-11-07)

### Bug Fixes
* **services** Added configuration of CORS headers to HttpEndpoint
* **services** Fixed bug with formatting ArraySchema in swagger document

### Features
* **services**  Added RegRxp supporting to interceptors
   Examples:
   - the interceptor route **"/dummies"** corresponds to all of this routes **"/dummies"**, **"/dummies/check"**, **"/dummies/test"**
   - the interceptor route **"/dummies$"** corresponds only for this route **"/dummies"**. The routes **"/dummies/check"**, **"/dummies/test"** aren't processing by interceptor
   Please, don't forgot, route in interceptor always automaticaly concateneted with base route, like this **service_base_route + route_in_interceptor**.
   For example, "/api/v1/" - service base route, "/dummies$" - interceptor route, in result will be next expression - "/api/v1/dummies$"

## <a name="3.2.12"></a> 3.2.12 (2021-10-28)

### Bug Fixes
* Optimize imports
* Update requirements

## <a name="3.2.11"></a> 3.2.11 (2021-09-08)

### Bug Fixes
* Fixed CommandableSwaggerDocument

## <a name="3.2.7-3.2.10"></a> 3.2.7-3.2.10 (2021-09-07)

# Features
* Remove netifaces dependency
* Add verification for supported REST methods

### Bug Fixes
* Fixed json params for requests in RestClient
* Fixed headers and request params passing
* Fixed query and body params passing


## <a name="3.2.5-3.2.6"></a> 3.2.5-3.2.6 (2021-08-30)

### Bug Fixes
* Fixed getting correlation id from request
* Update getting query parameters
* Fixed preparing empty params in services

## <a name="3.2.2 - 3.2.4"></a> 3.2.2 - 3.2.4 (2021-06-17)

### Bug Fixes
* Fixed debug mode for config params
* Fixed get_heart_beat_operation
* Fixed HttpRequestDetector.detect_address
* Fixed HttpResponseSender.send_result


### Features
* HttpEndpoint added register_route_with_auth
* Added **Auth** - authentication and authorisation components

## <a name="3.2.1"></a> 3.2.1 (2021-06-10)

### Bug Fixes
* fixed processing query parameters

## <a name="3.2.0"></a> 3.2.0 (2021-05-10)

### Bug Fixes
* Fixed config and credential resolving
* Fix methods params
* Fix methods and properties names


### Features
* Added InstrumentTiming
* Added _correlation_id_location for RestClient
* Added _get_correlation_id method for services
* Added type hints


## <a name="3.1.5 - 3.1.6"></a> 3.1.5 - 3.1.6 (2021-04-23)

### Features
* Added **test** module for automated testing

### Bug Fixes
* Update references

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
* **Build** - HTTP service factory
* **Clients** - retrieving connection settings from the microservice’s configuration
* **Connect** - helper module to retrieve connections
* **Services** - basic implementation of services
