import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "./Home.css";
import Login from '../auth/Login';
import ErrorPopup from '../layout/ErrorPopup'
import DeleteSecretKey from '../layout/DeleteSecretKey'
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css"
import Loader from 'react-loader-spinner'
import {CopyToClipboard} from 'react-copy-to-clipboard';
import Navbar from "../layout/NavBar";

const Home = () => {
    const oktaAuth = useOktaAuth();
    const [expiresIn, setSeconds] = useState();
    const [randomOtp, setRandomOtp] = useState();
    const [adminStatus, setAdminStatus] = useState();
    const [secretNames, setSecretNames] = useState([]);
    const [errorMessage, setErrorMessage] = useState();
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
    const [encryptedSecret, setEncryptedSecret] = useState('');
    const [timeInSeconds, setTimeInSeconds] = useState();
    const [logoutInErrorPopup, showLogoutInErrorPopup] = useState(false);
    if (oktaAuth) {
        const authState = oktaAuth.authState;
        const authService = oktaAuth.authService;
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
                    getOtp()
                }
            });
        }

        const version = require('../../../package.json').version;

        const handleSubmit = () => {
            let noDuplicatesFound = false
            if(secretNames.length > 0) {
                secretNames.forEach(name => {
                    if(name === adminSecret) {
                        noDuplicatesFound = true;
                    }
                })
            }
            if (!noDuplicatesFound) {
                setErrorMessage(false)
                setShowLoadingSpinnerInAdminSecretPopup(true)
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
            } else {
                setShowOtpDetails(false)
                setErrorMessage(`Name (${adminSecret}) is already taken.`)
            }
        }

        const getSecretKey = () => {
            setGettingAdminSecret(true)
            fetch(`http://${config.backEndUrl}/api/v1/secret`, {
                "method": "GET",
                "headers": {
                    "token": authorizeToken
                }
            }).then(response => {
                const promise = response.json();
                promise.then((val) => {
                    console.log(val);
                    const {adminSecret} = val;
                    if (adminSecret) {
                        setSharedSecret(adminSecret);
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
                            let listOfSecretNames = [];
                            setRandomOtp(response);
                            response.forEach(code => {
                                const {secretname} = code;
                                listOfSecretNames.push(secretname);
                            })
                            setSecretNames(listOfSecretNames);
                        } else {
                            setRandomOtp(response);
                        }

                    })
                    .catch(err => {
                        console.error(err);

                    });
            } else {
                setError(`Token Error : No token found with key (${authorizeTokenType}).`);
                showLogoutInErrorPopup(true);
            }
        }

        const deleteByPassCode = () => {
            setRandomOtp(null)

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

                    getOtp()
                    console.log(result, selectedSecretId)
                })
                .catch(error => {

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
            setErrorMessage('');
        }

        const setSuccessOrErrorMessage = (typeOfKey, key) => {
            if(key !== '') {
                setSuccessMessage(`${typeOfKey} copied to clipboard.`);
                setErrorMessage('');
            } else {
                setErrorMessage('Cannot copy empty text.')
                setSuccessMessage('');
            }
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
                    <Navbar mainHeader={config.mainHeader}/>
                    <div>
                        <div className={'instructions'}>
                            <h3 className={'sub-heading'}>Instructions</h3>
                            <ul style={{listStyleType: 'none', padding: '0'}}>
                                {config.instructionsInBypassCodeGenerator.map(function (content, index) {
                                    return <li key={index}>
                                        <p className={'list-cls'}>
                                            {content}
                                        </p>
                                    </li>
                                })}
                            </ul>
                            <footer style={{top: '60%', position: 'relative', borderTop: '1px solid silver'}}>
                                    <span style={{float: 'left', marginRight: '20px', marginTop: '10px'}}>
                                        version {version}
                                    </span>
                                <span style={{float: 'left', marginLeft: '100px', marginTop: '10px'}}>
                                    {config.authConfig.issuer.split('/')[2]}
                                    </span>
                            </footer>
                        </div>
                        <div style={{width: '33.3%'}}>
                            <div className="mobile">
                                <span className="titlecls">Bypass Codes</span>
                                {adminSecretFormOpener}
                                <div className={'outer-progress-bar'}>
                                    <div className="progress-bar" style={{
                                        width: 100 - adjustTimerBar(new Date().getTime() / 1000) + "%",
                                        transition: transition,
                                    }}>
                                    </div>
                                </div>
                                <hr className={'divider'} style={{borderColor: '#d6d6d6', marginTop:'4px', marginBottom: '0', marginLeft: '19px'}}/>
                                <ul style={{
                                    listStyleType: 'none',
                                    marginLeft: '18px',
                                    marginRight: '17px',
                                    overflow: 'auto',
                                    marginTop: '5px',
                                    maxHeight: '400px',
                                    padding: '0'
                                }}>
                                    {
                                        (randomOtp && randomOtp.length > 0) ? randomOtp.map(function (code, index) {
                                            const {secretname, secretUpdatedAt} = code;
                                            return (
                                                <li className='otp-list-cls' key={index}>
                                                     <div style={{display: 'flex'}}>
                                                         {
                                                             adminStatus ?
                                                                 <DeleteSecretKey
                                                                     setSelectedSecretName={setSelectedSecretName}
                                                                     setSelectedSecretId={setSelectedSecretId}
                                                                     showDeleteConfirmationPopup={showDeleteConfirmationPopup}
                                                                     code={code}/> : ''
                                                         }
                                                         <p style={{padding: '10px 1px 1px 20px', fontSize: '18px'}}>{secretname}</p>
                                                     </div>
                                                     <div style={{display: 'flex'}}>
                                                         <h2 className="random-otp" style={{marginTop: '7px', letterSpacing: '3px'}}>{code.code}</h2>
                                                         <p className='time-details'>{secretUpdatedAt}</p>
                                                     </div>
                                                </li>
                                            )}) :  <div>
                                                {
                                                     (randomOtp && randomOtp.length === 0) ?
                                                         <p style={{margin: '20px'}}>No Names found with this user.</p>
                                                         :
                                                         <div style={{marginLeft: '42%', marginTop: '15%'}}>
                                                             <Loader type="Oval" color="#007dc1" height={50} width={50}/>
                                                         </div>
                                                 }
                                            </div>
                                    }
                                </ul>
                            </div>
                        </div>
                    </div>
                    {
                        deleteConfirmationPopup ? (
                            <div className="popup-box">
                                <div className="box" style={{width: '55%',minWidth: '300px', padding: '0'}}>
                                    <h3 className="container-header">Confirm</h3>
                                    <p style={{fontSize: "initial", margin: '30px 0px 20px 50px'}}>Are you sure you want to delete
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
                            <ErrorPopup errorMessage={noError} logoutInErrorPopup={logoutInErrorPopup} onClose={onClose}/>
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
                                                    <h3 className={'sub-heading'}>Instructions</h3>
                                                    <ul style={{listStyleType: 'none', padding: '0'}}>
                                                        {config.instructionsInAdminSecret.map(function (code, index) {
                                                            return  <li key={index}>
                                                                        <p className={'list-cls'}>
                                                                            {code}
                                                                        </p>
                                                                    </li>
                                                        })}
                                                    </ul>
                                                </div>
                                                <div style={{width: "55%"}}>
                                                    <input
                                                        className={'admin-secret-input'}
                                                        type="text"
                                                        maxLength={'15'}
                                                        placeholder={"Secret Name"}
                                                        value={adminSecret.trimStart()}
                                                        onChange={e => setAdminSecret(e.target.value)}
                                                    />
                                                    <br/>
                                                    <br/>
                                                    <br/>
                                                    <div>
                                                        <button disabled={(gettingAdminSecret)} type="button"
                                                                className="generate-secret-button"
                                                                onClick={() => getSecretKey()}>
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
                                                                             setSuccessOrErrorMessage('Secret Key', sharedSecret)
                                                                         }}>
                                                            <button type='button' className={'copy-button'}>Copy
                                                            </button>
                                                        </CopyToClipboard>
                                                    </div>
                                                    <br/>
                                                    <br/>
                                                    <div className={'shared-secret-div'} style={{display: "none"}}>
                                                        <input
                                                            className={'shared-secret'}
                                                            readOnly={true}
                                                            placeholder={"Encrypted Key"}
                                                            value={encryptedSecret}
                                                            onChange={e => setEncryptedSecret(e.target.value)}
                                                        />
                                                        <CopyToClipboard text={encryptedSecret}
                                                                         onCopy={() => {
                                                                             setSuccessOrErrorMessage('Encrypted Key', encryptedSecret)
                                                                         }}>
                                                            <button type='button' className={'copy-button'}>Copy
                                                            </button>
                                                        </CopyToClipboard>
                                                    </div>
                                                    <div>
                                                        <button
                                                            style={{cursor: (!adminSecret || !sharedSecret) ? 'no-drop' : 'pointer'}}
                                                            className="save-button"
                                                            disabled={(!adminSecret || !sharedSecret)}
                                                            onClick={() => handleSubmit()}>
                                                            Save
                                                        </button>
                                                    </div>
                                                </div>
                                                {
                                                    successMessage ?
                                                        <div>
                                                            <span className={"success-message"}>{successMessage}</span>
                                                        </div>
                                                        :
                                                        ''
                                                }
                                                {
                                                    errorMessage ?
                                                        <div>
                                                            <span className={"error-message"}>{errorMessage}</span>
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