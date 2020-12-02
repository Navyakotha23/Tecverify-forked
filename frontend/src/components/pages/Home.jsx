import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "./Home.css";
import Login from '../auth/Login';
import Footer from '../layout/Footer'
import ErrorPopup from '../layout/ErrorPopup'
import DeleteSecretKey from '../layout/DeleteSecretKey'
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css"
import Loader from 'react-loader-spinner'
import {CopyToClipboard} from 'react-copy-to-clipboard';

const Home = () => {
    const OktaAuth = useOktaAuth();
    const [expiresIn, setSeconds] = useState();
    const [randomOtp, setRandomOtp] = useState();
    const [adminStatus, setAdminStatus] = useState();
    const [showLoadingSpinner, setShowLoadingSpinner] = useState(true);
    const [showLoadingSpinnerInAdminSecretPopup, setShowLoadingSpinnerInAdminSecretPopup] = useState(false);
    const [gettingAdminSecret, setGettingAdminSecret] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [showOtpDetails, setShowOtpDetails] = useState(true);
    const [deleteConfirmationPopup, showDeleteConfirmationPopup] = useState('');
    const [selectedSecretName, setSelectedSecretName] = useState('');
    const [selectedSecretId, setSelectedSecretId] = useState('');
    const [noError, setError] = useState('');
    const [adminSecret, setAdminSecret] = useState('');
    const [sharedSecret, setSharedSecret] = useState('');
    const [timeInSeconds, setTimeInSeconds] = useState('');
    const [logoutInErrorPopup, showLogoutInErrorPopup] = useState(false);
    if (OktaAuth) {
        const authState = OktaAuth.authState;
        const authService = OktaAuth.authService;
        const logout = async () => authService.logout('/login');
        const onClose = async () => setError('');
        const oktaTokenStorage = JSON.parse(localStorage.getItem('okta-token-storage'));
        const config = window.config;
        const authorizeTokenType = config.authorizeTokenType
        const authorizeClaimName = config.authorizeClaimName
        let transition, authorizeToken, adminSecretFormOpener;
        
        if (!adminStatus) {
            authService.getUser().then((info) => {
                if (info && info.email && info[authorizeClaimName]) {
                    setAdminStatus(info[authorizeClaimName])
                }
                if (!randomOtp) {
                    setShowLoadingSpinner(true)
                    getOtp()
                }
            });
        }


        const version = require('../../../package.json').version;

        const handleSubmit = (evt) => {
            setShowLoadingSpinnerInAdminSecretPopup(true)
            evt.preventDefault();
            let formData = new FormData();
            formData.append('secretname', adminSecret);
            formData.append('admin_secret', sharedSecret);
            fetch(`http://${config.backEndUrl}/api/v1/secret`, {
                "method": "POST",
                "headers": {
                    "token": authorizeToken
                },
                "body": formData
            }).then(response => {
                const promise = response.json();
                promise.then(() => {
                    getOtp()
                    setShowLoadingSpinnerInAdminSecretPopup(false)
                });
                if (response.status !== 200) {
                    if (noError === '') {
                        setError(response.statusText);
                    }
                    setShowLoadingSpinnerInAdminSecretPopup(false)
                } else {
                    setSuccessMessage('Secret Name submitted!')
                    setShowLoadingSpinnerInAdminSecretPopup(false)
                }
                setAdminSecret('');
                setSharedSecret('');
            }).catch(err => {
                setError("Unable to submit Name");
                console.log(err);
                setShowLoadingSpinnerInAdminSecretPopup(false)
            });
        }

        const getAdminSecret = () => {
            setGettingAdminSecret(true)
            fetch(`http://${config.backEndUrl}/api/v1/secret`, {
                "method": "GET",
                "headers": {
                    "token": authorizeToken
                }
            }).then(response => {
                const promise = response.json();
                promise.then((val) => {
                    if (val.adminSecret) {
                        setSharedSecret(val.adminSecret);
                        setGettingAdminSecret(false)
                    }
                });
                if (response.status !== 200) {
                    if (noError === '') {
                        setError("Unable to get Admin secret");
                    }
                    setGettingAdminSecret(false)
                }
            }).catch(err => {
                setError("Unable to get Admin secret");
                console.log(err);
                setGettingAdminSecret(false)
            });
        }

        const getOtp = () => {
            if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType] && oktaTokenStorage[authorizeTokenType][authorizeTokenType]) {
                fetch(`http://${config.backEndUrl}/api/v1/totp`, {
                    "method": "GET",
                    "headers": {
                        "token": oktaTokenStorage[authorizeTokenType][authorizeTokenType]
                    }
                })
                    .then(response => response.json())
                    .then(response => {
                        if (response.length > 0) {
                            setRandomOtp(response);
                        }
                        setShowLoadingSpinner(false)
                    })
                    .catch(err => {
                        console.error(err);
                        setShowLoadingSpinner(false)
                    });
            } else {
                setError(`Token Error : No token found with key (${authorizeTokenType}).`);
                showLogoutInErrorPopup(true);
            }
        }

        const deleteByPassCode = () => {
            setShowLoadingSpinner(true)
            const myHeaders = new Headers();
            myHeaders.append("token", oktaTokenStorage[authorizeTokenType][authorizeTokenType]);
            const requestOptions = {
                method: 'DELETE',
                headers: myHeaders,
                redirect: 'follow'
            };
            console.log(requestOptions, selectedSecretId)
            fetch(`http://${config.backEndUrl}/api/v1/secret/${selectedSecretId}`, requestOptions)
                .then(response => response.text())
                .then(result => {
                    setShowLoadingSpinner(true)
                    getOtp()
                    console.log(result, selectedSecretId)
                })
                .catch(error => {
                    setShowLoadingSpinner(false)
                    console.error('error', error)
                });
        }

        const showAdminSecretForm = () => {
            setShowOtpDetails(false);
        }

        const hideAdminSecretForm = () => {
            setAdminSecret('')
            setSuccessMessage('');
            setSharedSecret('');
            setShowOtpDetails(true);
        }

        if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType]) {
            const expiresAt = oktaTokenStorage[authorizeTokenType].expiresAt;
            authorizeToken = oktaTokenStorage[authorizeTokenType][authorizeTokenType];

            setTimeout(() => {
                setSeconds(convertHMS((expiresAt) - (new Date().getTime() / 1000)));
            }, 1000);

            if (expiresIn === 100) {
                authService._oktaAuth.session.close();
                logout();
            }

            adminSecretFormOpener = (adminStatus ?
                <button
                    className={"admin-button"}
                    onClick={() => showAdminSecretForm()}>
                    +
                </button> : '')

            const currentTimeSeconds = getSeconds(new Date().getTime() / 1000);

            if (currentTimeSeconds === 29 || currentTimeSeconds === 59 || currentTimeSeconds === 30 || currentTimeSeconds === 0) {
                if (!timeInSeconds || ((new Date().getTime() / 1000) - timeInSeconds) > 10) {
                    getOtp();
                    setTimeInSeconds(new Date().getTime() / 1000)
                }
            }

            transition = (100 - adjustTimerBar(new Date().getTime() / 1000) === 0 || 100 - adjustTimerBar(new Date().getTime() / 1000) < 4) ? '0s' : 'all 1s cubic-bezier(0.21, 0.19, 0.45, 0.55) 0s';

        }

        return (
            authState.isAuthenticated
                ?
                <div className={"container"}>
                    {
                        showLoadingSpinner ?
                            <div className={"container-body"}>
                                <div className={'loading-spinner'}>
                                    <Loader type="Oval" color="#007dc1" height={50} width={50}/>
                                </div>
                            </div>
                            :
                            <div className={"container-body"}>
                                <div className={'container-center'}>
                                    <div className={'instructions'}>
                                        <h3>Instructions</h3>
                                        <ul style={{listStyleType: 'none', padding: '0'}}>
                                            {config.instructionsInBypassCodeGenerator.map(function (content, index) {
                                                return <li key={index}>
                                                    <p style={{margin: '10px 0 0 0', fontSize: 'larger'}}>{content}</p>
                                                </li>
                                            })}
                                        </ul>
                                    </div>
                                    <div style={{
                                        width: '40%',
                                        position: 'absolute',
                                        left: '55%',
                                        top: '7%',
                                        height: '87%',
                                        padding: '0',
                                        margin: '0'
                                    }}>
                                        <h3 style={{textAlign: 'center'}}>Bypass Codes</h3>
                                        <div className={'bypass-codes'}>
                                            {
                                                (randomOtp && randomOtp.length > 0) ?
                                                    <div className="progress-bar" style={{
                                                        width: 100 - adjustTimerBar(new Date().getTime() / 1000) + "%",
                                                        transition: transition
                                                    }}>
                                                    </div> : ''
                                            }
                                            <ul className={'bypass-codes-unOrder-list'}>
                                                {
                                                    (randomOtp && randomOtp.length > 0) ? randomOtp.map(function (code, index) {
                                                        return <li key={index}>
                                                            <div>
                                                                {
                                                                    adminStatus ?
                                                                        <DeleteSecretKey
                                                                            setSelectedSecretName={setSelectedSecretName}
                                                                            setSelectedSecretId={setSelectedSecretId}
                                                                            showDeleteConfirmationPopup={showDeleteConfirmationPopup}
                                                                            code={code}/> : ''
                                                                }
                                                                <p style={{padding: '10px 1px 1px 10px'}}>{code.secretname}</p>
                                                                <p className={'time-details'}>{code.secretUpdatedAt}</p>
                                                                <h2 className="random-otp">{code.code}</h2>
                                                                <hr className={"divider"} style={{margin: '0'}}/>
                                                            </div>
                                                        </li>
                                                    }) : <p style={{margin: '20px'}}>No Name found with this user.</p>
                                                }
                                            </ul>
                                            {adminSecretFormOpener}
                                        </div>
                                    </div>
                                </div>
                            </div>
                    }
                    {
                        deleteConfirmationPopup ? (
                            <div className="popup-box">
                                <div className="box" style={{width: '55%',minWidth: '300px', padding: '0'}}>
                                    <h3 className="container-header" style={{background: '#f76868'}}>Confirm</h3>
                                    <p style={{fontSize: "initial", margin: '20px'}}>Are you sure you want to delete
                                        ByPass code <b>{selectedSecretName}</b> ?</p>
                                    <div style={{width: "100%"}}>
                                        <button className="button delete-button" onClick={() => {
                                            showDeleteConfirmationPopup('');
                                            deleteByPassCode()
                                        }}>
                                            Confirm
                                        </button>
                                        <button className="button cancel-button"
                                                onClick={() => showDeleteConfirmationPopup('')}>
                                            cancel
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ) : ''
                    }
                    {
                        noError ? (
                            <ErrorPopup noError={noError} logoutInErrorPopup={logoutInErrorPopup} onClose={onClose}/>
                        ) : ''
                    }
                    {
                        !showOtpDetails ? (
                            <div className="admin-popup-box">
                                <div className="admin-box">
                                    <h3 className={'container-header'}>Add Secret Key</h3>
                                    <button className={'close-button'}
                                            onClick={() => {
                                                hideAdminSecretForm();
                                            }}>
                                        X
                                    </button>
                                    {
                                        showLoadingSpinnerInAdminSecretPopup ?
                                            <div style={{marginLeft: '47%', marginTop: '20%'}}>
                                                <Loader type="Oval" color="#007dc1" height={50} width={50}/>
                                            </div>
                                            :
                                            <div className={'admin-secret'}>
                                                <div className={'instructions-admin-secret'}>
                                                    <h3>Instructions</h3>
                                                    <ul style={{listStyleType: 'none', padding: '0'}}>
                                                        {config.instructionsInAdminSecret.map(function (code, index) {
                                                            return <li key={index}>
                                                                <p style={{
                                                                    margin: '10px 0 0 0',
                                                                    fontSize: 'larger'
                                                                }}>{code}</p>
                                                            </li>
                                                        })}
                                                    </ul>
                                                </div>
                                                <div style={{width: "50%"}}>
                                                    <form onSubmit={handleSubmit}>
                                                        <input
                                                            className={'admin-secret-input'}
                                                            type="text"
                                                            placeholder={"Secret Name"}
                                                            value={adminSecret}
                                                            onChange={e => setAdminSecret(e.target.value)}
                                                        />
                                                        <br/>
                                                        <br/>
                                                        <br/>
                                                        <div>
                                                            <button disabled={(gettingAdminSecret)} type="button"
                                                                    className="generate-secret-button"
                                                                    onClick={() => getAdminSecret()}>
                                                                {
                                                                    !gettingAdminSecret ?
                                                                        'Generate Secret Key' :
                                                                        <Loader type="Oval" color="white" height={15}
                                                                                width={15}/>
                                                                }
                                                            </button>
                                                        </div>
                                                        <br/>
                                                        <br/>
                                                        <div className={'shared-secret-div'}>
                                                            <input
                                                                className={'shared-secret'}
                                                                readOnly={true}
                                                                placeholder={"Secret Key"}
                                                                value={sharedSecret}
                                                                onChange={e => setSharedSecret(e.target.value)}
                                                            />
                                                            <CopyToClipboard text={sharedSecret}
                                                                             onCopy={() => {
                                                                                 setSuccessMessage('Secret Key copied to clipboard.');
                                                                             }}>
                                                                <button type='button' className={'copy-button'}>Copy
                                                                </button>
                                                            </CopyToClipboard>
                                                        </div>
                                                        <div>
                                                            <button
                                                                style={{cursor: (!adminSecret || !sharedSecret) ? 'no-drop' : 'pointer'}}
                                                                type="submit" value="Submit" className="save-button"
                                                                disabled={(!adminSecret || !sharedSecret)}>
                                                                Save
                                                            </button>
                                                        </div>
                                                    </form>
                                                </div>
                                                {
                                                    successMessage ?
                                                        <div>
                                                            <span className={"success-message"}>{successMessage}</span>
                                                        </div>
                                                        :
                                                        ''
                                                }
                                            </div>
                                    }
                                </div>
                            </div>
                        ) : ''
                    }
                    <Footer 
                        environment={config.environment}
                        issuer={config.authConfig.issuer}
                        version={version}/>
                </div>
                :
                <Login/>
        )
    } else {
        return '';
    }
}

const convertHMS = (value) => {
    const sec = parseInt(value, 10);
    let hours   = Math.floor(sec / 3600);
    let minutes = Math.floor((sec - (hours * 3600)) / 60);
    let seconds = sec - (hours * 3600) - (minutes * 60);
    const timer = hours+':'+minutes+':'+seconds;
    const a = timer.split(':');
    return (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);
}

const getSeconds = (value) => {
    const sec = parseInt(value, 10);
    let hours   = Math.floor(sec / 3600);
    let minutes = Math.floor((sec - (hours * 3600)) / 60);
    return sec - (hours * 3600) - (minutes * 60);
}

const adjustTimerBar = (value) => {
    const sec = parseInt(value, 10);
    let hours   = Math.floor(sec / 3600);
    let minutes = Math.floor((sec - (hours * 3600)) / 60);
    let seconds = (sec - (hours * 3600) - (minutes * 60));
    if(sec - (hours * 3600) - (minutes * 60) > 30) {
        seconds = (sec - (hours * 3600) - (minutes * 60)) - 30
    }
    return 100 - (100/30 * (seconds));
}

export default Home