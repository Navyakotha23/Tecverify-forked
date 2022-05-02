import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "./Home.css";
import ErrorPopup from '../layout/ErrorPopup'
import DeleteSecretKey from '../layout/DeleteSecretKey'
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css"
import Loader from 'react-loader-spinner'
import {CopyToClipboard} from 'react-copy-to-clipboard';
import Navbar from "../layout/NavBar";
import {useHistory} from "react-router-dom";

const TOKEN = 'token';
const POST = 'POST';
const GET = 'GET';
const Home = () => {
    const history = useHistory();
    const config = JSON.parse(sessionStorage.getItem('config'));
    const { oktaAuth, authState } = useOktaAuth();
    const [expiresIn, setSeconds] = useState();
    const [randomOtp, setRandomOtp] = useState();
    const [onDeletingOtp, setOnDeletingOtp] = useState(false);
    const [userEmail, setUserEmail] = useState();
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
    const [timeInSeconds, setTimeInSeconds] = useState();
    const [logoutInErrorPopup, showLogoutInErrorPopup] = useState(false);
    const [checkEnrollmentStatus, setCheckEnrollmentStatus] = useState(false);
    const logout = async () => {
        await oktaAuth.signOut('/login');
    };

    if (oktaAuth && config) {
        const oktaTokenStorage = JSON.parse(localStorage.getItem('okta-token-storage'));
        const authorizeTokenType = config.AUTHORIZE_TOKEN_TYPE
        let transition, authorizeToken, addButtonStatus, deleteIconStatus, copyIconStatus;
        addButtonStatus = config.SHOW_ADD_SECRET_BUTTON === undefined || config.SHOW_ADD_SECRET_BUTTON === true;
        deleteIconStatus = config.SHOW_DELETE_ICON === undefined || config.SHOW_DELETE_ICON === true;
        copyIconStatus = config.COPY_TO_CLIPBOARD_BUTTON === undefined || config.COPY_TO_CLIPBOARD_BUTTON === true;
        if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType] && oktaTokenStorage['accessToken']) {
            if(oktaTokenStorage[authorizeTokenType][authorizeTokenType] && !checkEnrollmentStatus) {
                setCheckEnrollmentStatus(true);
                fetch(`${config.BACK_END_URL}/api/v1/deleteTOTPfactorIfEnrolledFromOktaVerify`, {
                    // "method": GET,
                    "method": 'DELETE',
                    "headers": {
                        TOKEN: oktaTokenStorage[authorizeTokenType][authorizeTokenType]
                    }
                })
                    .then(response => response.json())
                    .then(response => {
                        autoEnroll();
                    })
                    .catch(err => {
                        console.error(err);
                    });
            }

            if(userEmail === undefined) {
                oktaAuth.getUser().then((info) => {
                    if (info && info.email) {
                        setUserEmail(info.email);
                    }
                    if (!randomOtp) {
                        getOtp()

                        // fetch(`${config.BACK_END_URL}/api/v1/establishConnection`, {
                        //     "method": GET,
                        //     "headers": {
                        //         TOKEN: oktaTokenStorage[authorizeTokenType][authorizeTokenType]
                        //     }
                        // })
                        //     .then(response => response.json())
                        //     .then(response => {
                        //         getOtp()
                        //         console.log(response);
                        //     })
                        //     .catch(err => {
                        //         console.error(err);
                        //     });
                    }
                }).catch(err => {
                    console.log(err);
                });
            }
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
                formData.append('secretName', adminSecret);
                formData.append('adminSecret', sharedSecret);
                fetch(`${config.BACK_END_URL}/api/v1/secret`, {
                    "method": POST,
                    "headers": {
                        TOKEN: authorizeToken
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
            fetch(`${config.BACK_END_URL}/api/v1/secret`, {
                "method": GET,
                "headers": {
                    TOKEN: authorizeToken
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
                setSuccessOrErrorMessage('', '', 'Unable to get Admin secret key.')
                console.log(err);
                setGettingAdminSecret(false)
            });
        }

        const getOtp = () => {
            if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType] && oktaTokenStorage[authorizeTokenType][authorizeTokenType]) {
                fetch(`${config.BACK_END_URL}/api/v1/totp`, {
                    "method": GET,
                    "headers": {
                        TOKEN: oktaTokenStorage[authorizeTokenType][authorizeTokenType]
                    }
                })
                    .then(response => response.json())
                    .then(response => {
                        if (response.length > 0) {
                            let listOfSecretNames = [];
                            setRandomOtp(response);
                            response.forEach(code => {
                                const {secretName} = code;
                                listOfSecretNames.push(secretName);
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

        const autoEnroll = () => {
            if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType] && oktaTokenStorage[authorizeTokenType][authorizeTokenType] && !checkEnrollmentStatus) {
                setCheckEnrollmentStatus(true);
                fetch(`${config.BACK_END_URL}/api/v1/autoEnroll`, {
                    // "method": GET,
                    "method": POST,
                    "headers": {
                        TOKEN: oktaTokenStorage[authorizeTokenType][authorizeTokenType]
                    }
                })
                    .then(response => response.json())
                    .then(response => {
                        getOtp();
                    })
                    .catch(err => {
                        console.error(err);
                    });
            } else {
                setError(`Token Error : No token found with key (${authorizeTokenType}).`);
                showLogoutInErrorPopup(true);
            }
        }
        // const closeConnection = () => {
        //     console.log('destroy connection')
        //     if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType] && oktaTokenStorage[authorizeTokenType][authorizeTokenType]) {
        //         fetch(`${config.BACK_END_URL}/api/v1/destroyConnection`, {
        //             "method": GET,
        //             "headers": {
        //                 TOKEN: oktaTokenStorage[authorizeTokenType][authorizeTokenType]
        //             }
        //         })
        //             .then(response => response.json())
        //             .then(response => {
        //                 logout();
        //                 console.log(response);
        //             })
        //             .catch(err => {
        //                 console.error(err);
        //             });
        //     } else {
        //         setError(`Token Error : No token found with key (${authorizeTokenType}).`);
        //         showLogoutInErrorPopup(true);
        //     }
        // }

        const deleteByPassCode = () => {
            setRandomOtp(null)
            const myHeaders = new Headers();
            myHeaders.append(TOKEN, oktaTokenStorage[authorizeTokenType][authorizeTokenType]);
            const requestOptions = {
                method: 'DELETE',
                headers: myHeaders,
                redirect: 'follow'
            };
            console.log(requestOptions, selectedSecretId)
            fetch(`${config.BACK_END_URL}/api/v1/secret/${selectedSecretId}`, requestOptions)
                .then(response => response.text())
                .then(result => {
                    setOnDeletingOtp(true)
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

        const setSuccessOrErrorMessage = (typeOfKey, key, secretKeyError = null) => {
            if (!secretKeyError) {
                if(key !== '') {
                    setSuccessMessage(`${typeOfKey} copied to clipboard.`);
                    setErrorMessage('');
                } else {
                    setErrorMessage('Cannot copy empty text.')
                    setSuccessMessage('');
                }
            } else {
                setErrorMessage(secretKeyError)
                setSuccessMessage('');
            }
        }
        const alertOnOtpCopyingToClipboard = (otp) => {
            alert('Otp ' + otp + ' copied to clipboard');
        }

        if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType]) {
            const expiresAt = oktaTokenStorage[authorizeTokenType].expiresAt;
            authorizeToken = oktaTokenStorage[authorizeTokenType][authorizeTokenType];
            setTimeout(() => {
                setSeconds(convertHMS((expiresAt) - (new Date().getTime() / 1000)));
            }, 1000);
            if (expiresIn < 100) {
                logout();
            }

            const currentTimeSeconds = getSeconds(new Date().getTime() / 1000);

            if (currentTimeSeconds === 29 || currentTimeSeconds === 59 || currentTimeSeconds === 30 || currentTimeSeconds === 0) {
                if (!timeInSeconds || ((new Date().getTime() / 1000) - timeInSeconds) > 10) {
                    getOtp();
                    setTimeInSeconds(new Date().getTime() / 1000)
                }
            }
            transition = (100 - adjustTimerBar(new Date().getTime() / 1000) === 0 || 100 - adjustTimerBar(new Date().getTime() / 1000) < 4) ? '0s' : 'all 1s cubic-bezier(0.21, 0.19, 0.45, 0.55) 0s';
        }

        const homePage = <div className={"container"}>
            <Navbar userEmail={userEmail} mainHeader={config.MAIN_HEADER}/>
            <div>
                <div className={'instructions'}>
                    <h3 className={'sub-heading'}>{config.INSTRUCTIONS_AND_HEADER_IN_BYPASS_CODE_GENERATOR.HEADER}</h3>
                    <div style={{height: '60%', overflowY: 'auto'}}>
                        <ul style={{listStyleType: 'none', padding: '0'}}>
                            {config.INSTRUCTIONS_AND_HEADER_IN_BYPASS_CODE_GENERATOR.INSTRUCTIONS.map(function (content, index) {
                                return <li key={index}>
                                    <p className={'list-cls'}>
                                        {content}
                                    </p>
                                </li>
                            })}
                        </ul>
                    </div>
                    <div>
                    </div>
                </div>
                <div style={{width: '33.3%'}}>
                    <div className="mobile">
                        <span className="titlecls">{config.BYPASS_CODES_HEADER}</span>
                        {
                            addButtonStatus ?
                                <button
                                    className={"admin-button"}
                                    onClick={() => showAdminSecretForm()}>
                                    +
                                </button> : ''
                        }
                        <div className={'outer-progress-bar'}>
                            <div className="progress-bar" style={{
                                width: 100 - adjustTimerBar(new Date().getTime() / 1000) + "%",
                                transition: transition,
                            }}>
                            </div>
                        </div>
                        <hr className={'divider'} style={{borderColor: '#d6d6d6', marginTop:'4px', marginBottom: '0', marginLeft: '15px'}}/>
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
                                    const {secretName, secretUpdatedAt} = code;
                                    return (
                                        <li className='otp-list-cls' key={index}>
                                            <div style={{display: 'flex'}}>
                                                {
                                                    deleteIconStatus ?
                                                        <DeleteSecretKey
                                                            setSelectedSecretName={setSelectedSecretName}
                                                            setSelectedSecretId={setSelectedSecretId}
                                                            showDeleteConfirmationPopup={showDeleteConfirmationPopup}
                                                            code={code}/> : ''
                                                }
                                                <input className={'bypass-codes-names'} type={'readonly'} value={secretName}/>
                                            </div>
                                            <div style={{display: 'flex'}}>
                                                <span className="random-otp" style={{marginTop: '7px', letterSpacing: '3px'}}>{code.otp}</span>
                                                {
                                                    copyIconStatus ?
                                                        <CopyToClipboard title={'copy to clipboard'} text={code.otp}
                                                                         onCopy={() => {
                                                                             alertOnOtpCopyingToClipboard(code.otp)
                                                                         }}>
                                                            <button className={'copy-icon'} title={'copy to clipboard'}>
                                                            </button>
                                                        </CopyToClipboard> : ''
                                                }
                                                <p className='time-details'>{secretUpdatedAt}</p>
                                            </div>
                                        </li>
                                    )}) :  <div>
                                    {
                                        (randomOtp && randomOtp.length === 0 && onDeletingOtp) ?
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
                        <div className="box" style={{width: '65%',minWidth: '300px', padding: '0'}}>
                            <h3 className="container-header">{config.CONFIRMATION_POPUP_FOR_BYPASS_CODE_FOR_DELETING.HEADER}</h3>
                            <p style={{fontSize: "initial", margin: '30px 0px 20px 50px'}}>
                                {config.CONFIRMATION_POPUP_FOR_BYPASS_CODE_FOR_DELETING.QUESTION}
                                <b>{selectedSecretName}</b> ?</p>
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
                    <ErrorPopup errorMessage={noError} logoutInErrorPopup={logoutInErrorPopup} onClose={setError('')}/>
                ) : ''
            }
            {
                !showOtpDetails ? (
                    <div className="admin-popup-box">
                        <div className="admin-box">
                            <h3 className={'container-header'}>{config.ENROLLMENT_FACTOR_POPUP.HEADER}</h3>
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
                                            <h3 className={'sub-heading'}>{config.ENROLLMENT_FACTOR_POPUP.INSTRUCTIONS.HEADER}</h3>
                                            <ul style={{listStyleType: 'none', padding: '0'}}>
                                                {config.ENROLLMENT_FACTOR_POPUP.INSTRUCTIONS.INSTRUCTIONS_LIST.map(function (code, index) {
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
                                                maxLength={'30'}
                                                placeholder={"Secret Name"}
                                                value={adminSecret.trimStart()}
                                                onChange={e => setAdminSecret(e.target.value)}
                                            />
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
                                            <div className={'shared-secret-div'}>
                                                <input
                                                    className={'shared-secret'}
                                                    readOnly={false}
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
                                            {/*<div className={'shared-secret-div'}>*/}
                                            {/*    <input*/}
                                            {/*        style={SHOW_ENCRYPTED_KEY === 'true' ? {} : {display: "none"}}*/}
                                            {/*        className={'shared-secret'}*/}
                                            {/*        readOnly={true}*/}
                                            {/*        placeholder={"Encrypted Key"}*/}
                                            {/*        value={encryptedSecret}*/}
                                            {/*        onChange={e => setEncryptedSecret(e.target.value)}*/}
                                            {/*    />*/}
                                            {/*    <CopyToClipboard text={encryptedSecret}*/}
                                            {/*                     onCopy={() => {*/}
                                            {/*                         setSuccessOrErrorMessage('Encrypted Key', encryptedSecret)*/}
                                            {/*                     }}>*/}
                                            {/*        <button  style={SHOW_ENCRYPTED_KEY === 'true' ? {} : {display: "none"}} type='button' className={'copy-button'}>Copy*/}
                                            {/*        </button>*/}
                                            {/*    </CopyToClipboard>*/}
                                            {/*</div>*/}
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
            <div className={"footer"}>
                <footer style={{
                    width: '56%',
                    left: '12%',
                    top: '-30%',
                    position: 'absolute',
                    borderTop: '1px solid silver'
                }}>
                                    <span style={{float: 'left', marginRight: '20px', marginTop: '10px'}}>
                                        version {version}
                                    </span>
                    <span style={{float: 'left', marginLeft: '100px', marginTop: '10px'}}>
                                    {config.ISSUER.split('/')[2]}
                                    </span>
                </footer>
            </div>
        </div>

        if(authState.isAuthenticated) {
            return homePage
        } else {
            return <div className="popup-box" style={{background: '#ffffff50'}}>
                <div className="config-error-box">
                    <div style={{background: '#ff4949', height: '50px', padding: '10px'}}>
                        <h2>Alert</h2>
                    </div>
                    <p style={{fontSize: 'initial', textAlign: 'center', marginTop: '40px'}}>Error : Session Expired! </p>
                    <button
                        className={'sign-in-btn'}
                        type='button'
                        onClick={() => { history.push('/login') }}
                    >
                        Login here
                    </button>
                </div>
            </div>;
        }
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
