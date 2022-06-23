class Constants:
    TOKEN = "token"
    ID_TOKEN = "idtoken"
    ACCESS_TOKEN = "accesstoken"

    OPTIONS = 'OPTIONS'
    POST = 'POST'
    DELETE = 'DELETE'
    
    # Constants in Okta APIs response 
    AUD = 'aud'
    SUB = 'sub'
    CLIENT_ID = 'client_id'
    UID = 'uid'
    ID = 'id'
    EMBEDDED = '_embedded'
    ACTIVATION = 'activation'
    SHARED_SECRET = 'sharedSecret'
    FACTOR_TYPE = 'factorType'
    TOTP_FACTOR = "token:software:totp"
    ACTIVE = 'active'

    # Keys in Request Form
    SECRET_NAME_KEY_IN_REQUEST_FORM = "adminScrtName" # In home.jsx(FE) and in docs.json(BE Swagger) also this should be same
    SECRET_KEY_KEY_IN_REQUEST_FORM = "adminScrtKey" # In home.jsx(FE) and in docs.json(BE Swagger) also this should be same
    OKTA_USER_ID_KEY_IN_REQUEST_FORM = "adminOktaUserId" # In docs.json(BE Swagger) also this should be same
        