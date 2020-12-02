import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "./Home.css";
import Login from '../auth/Login';
import Footer from '../layout/Footer'
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css"
import Loader from 'react-loader-spinner'
import {CopyToClipboard} from 'react-copy-to-clipboard';

const Home = () => {
    const { authState, authService } = useOktaAuth();
    const logout = async () => authService.logout('/login');
    const onClose = async () => setError('');
    let [expiresIn, setSeconds] = useState();
    const [randomOtp, setRandomOtp] = useState();
    const [adminStatus, setAdminStatus] = useState();
    const [showLoadingSpinner, setShowLoadingSpinner] = useState(true);
    const [showLoadingSpinnerInAdminSecretPopup, setShowLoadingSpinnerInAdminSecretPopup] = useState(false);
    const [gettingAdminSecret, setGettingAdminSecret] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [showOtpDetails, setShowOtpDetails] = useState(true);
    const [noError, setError] = useState('');
    const [adminSecret, setAdminSecret] = useState('');
    const [sharedSecret, setSharedSecret] = useState('');
    const [encryptedKey, setEncryptedKey] = useState('');
    const [timeInSeconds, setTimeInSeconds] = useState('');
    const [sharedSecretToClipBoard, copySharedSecretToClipBoard] = useState('');
    const [encryptedKeyToClipBoard, copyEncryptedKeyToClipBoard] = useState('');
    const oktaTokenStorage = JSON.parse(localStorage.getItem('okta-token-storage'));
    const config = window.config;
    console.log(config);
    const authorizeTokenType = config.authorizeTokenType
    const authorizeClaimName = config.authorizeClaimName

    console.log(process.env.PUBLIC_URL)
    let transition, authorizeToken, adminSecretFormOpener, borderRadius, overflowY;
    if(!adminStatus) {
        authService.getUser().then((info) => {
            if(info && info.email && info[authorizeClaimName]) {
                setAdminStatus(info[authorizeClaimName])
            }
            if(!randomOtp) {
                setShowLoadingSpinner(true)
                getOtp()
            }});
    }

    const handleSubmit = (evt) => {
        copySharedSecretToClipBoard('');
        copyEncryptedKeyToClipBoard('');
        setShowLoadingSpinnerInAdminSecretPopup(true)
        evt.preventDefault();
        let formData = new FormData();
        formData.append('secretname', adminSecret);
        formData.append('admin_secret', sharedSecret);
        fetch(`http://${config.backEndHostUrl}/api/v1/secret`, {
            "method": "POST",
            "headers": {
                "token": authorizeToken
            },
            "body":  formData
        }).then(response => {
            const promise = response.json();
            promise.then(function(val) {
                getOtp()
                setError(val.error);
                setShowLoadingSpinnerInAdminSecretPopup(false)
            });
            if(response.status !== 200) {
                if(noError === '') {
                    setError(response.statusText);
                }
                setShowLoadingSpinnerInAdminSecretPopup(false)
            } else {
                setSuccessMessage('Name submitted!')
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
        fetch(`http://${config.backEndHostUrl}/api/v1/secret`, {
            "method": "GET",
            "headers": {
                "token": authorizeToken
            }
        }).then(response => {
            const promise = response.json();
            promise.then(function(val) {
                setError(val.error);
                console.log(val);
                if(val.adminSecret) {
                    setSharedSecret(val.adminSecret);
                    setGettingAdminSecret(false)
                }
            });
            if(response.status !== 200) {
                if(noError === '') {
                    setError(response.statusText);
                }
                setGettingAdminSecret(false)
            }
        }).catch(err => {
            setError("Unable to submit Admin secret");
            console.log(err);
            setGettingAdminSecret(false)
        });
    }

    const getOtp = () => {
        if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType] && oktaTokenStorage[authorizeTokenType][authorizeTokenType]) {
            fetch(`http://${config.backEndHostUrl}/api/v1/totp`, {
                "method": "GET",
                "headers": {
                    "token": oktaTokenStorage[authorizeTokenType][authorizeTokenType]
                }
            })
            .then(response => response.json())
            .then(response => {
                if (response.length > 0) {
                    setRandomOtp(response);
                } else {
                    console.log(response);
                    setError(response.statusText);
                    setRandomOtp("Loading...");
                }
                setShowLoadingSpinner(false)
            })
            .catch(err => {
                setError(err);
                console.log(err);
                setShowLoadingSpinner(false)
            });
        }
    }

    const showAdminSecretForm = () => {
        setShowOtpDetails(false);
    }

    const hideAdminSecretForm = () => {
        setSuccessMessage('')
        setShowOtpDetails(true);
    }

    if (oktaTokenStorage && oktaTokenStorage[authorizeTokenType]) {
        const expiresAt = oktaTokenStorage[authorizeTokenType].expiresAt;
        authorizeToken = oktaTokenStorage[authorizeTokenType][authorizeTokenType];

        setTimeout(() => {
            setSeconds(convertHMS((expiresAt) - (new Date().getTime() / 1000)));
        }, 1000);

        if(expiresIn === 100) {
            authService._oktaAuth.session.close();
            logout();
        }

        adminSecretFormOpener = ( adminStatus ?
            <button
                className={"admin-button"}
                onClick={() => showAdminSecretForm()}>
                +
            </button> : '' )

        const currentTimeSeconds = getSeconds(new Date().getTime() / 1000);

        if(currentTimeSeconds === 29 || currentTimeSeconds === 59 || currentTimeSeconds === 30 || currentTimeSeconds === 0) {
            if(!timeInSeconds || ((new Date().getTime() / 1000) - timeInSeconds) > 10 ) {
                getOtp();
                setTimeInSeconds(new Date().getTime() / 1000)
            }
        }

        transition = (100 - adjustTimerBar(new Date().getTime() / 1000) === 0 || 100 - adjustTimerBar(new Date().getTime() / 1000) < 4) ? '0s' : 'all 1s cubic-bezier(0.21, 0.19, 0.45, 0.55) 0s';

        if(randomOtp && randomOtp.length > 0) {
            borderRadius = (randomOtp.length > 5) ? '0px 0px 0px 15px' : '0 0 15px 15px';
        }
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
                                {
                                    randomOtp && randomOtp.length > 0 ? (
                                            <div className={'bypass-codes'}>
                                                <div className="progress-bar" style={{
                                                    width: 100 - adjustTimerBar(new Date().getTime() / 1000) + "%",
                                                    transition: transition
                                                }}>
                                                </div>
                                                <ul style={{
                                                    listStyleType: 'none',
                                                    padding: '0',
                                                    overflowY: 'auto',
                                                    background: 'scroll',
                                                    margin: '0px',
                                                    height: '99%'
                                                }}>
                                                    {randomOtp.map(function (code, index) {
                                                        return <li key={index}>
                                                            <div>
                                                                <p style={{padding: '10px 1px 1px 10px'}}>{code.secretname}</p>
                                                                <h2 className="random-otp">{code.code}</h2>
                                                                {(randomOtp.length - 1 !== index || randomOtp.length <= 5) ?
                                                                    <hr className={"divider"} style={{margin: '0'}}/> : ''}
                                                            </div>
                                                        </li>;
                                                    })}
                                                </ul>
                                                {adminSecretFormOpener}
                                            </div>
                                        )
                                        :
                                        ''
                                }
                            </div>
                        </div>
                    </div>
            }
            {
                noError ? (
                    <div className="popup-box">
                        <div className="box">
                            <p style={{fontSize: "initial"}}>{noError}</p>
                            <div style={{width: "100%"}}>
                                <button className="button logout-button" onClick={onClose}>
                                Ok
                                </button>
                            </div>
                        </div>
                    </div>
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
                                        copyEncryptedKeyToClipBoard('');
                                        copySharedSecretToClipBoard('');
                                        setSharedSecret('');
                                    }}>
                                X
                            </button>
                            {
                                showLoadingSpinnerInAdminSecretPopup ?
                                    <div style={{marginLeft: '48%', marginTop: '20%'}}>
                                        <Loader type="Oval" color="#007dc1" height={50} width={50}/>
                                    </div>
                                    :
                                    <div className={'admin-secret'}>
                                        <div className={'instructions-admin-secret'}>
                                            <h3>Instructions</h3>
                                            <ul style={{listStyleType: 'none', padding: '0'}}>
                                                {config.instructionsInAdminSecret.map(function (code, index) {
                                                    return <li key={index}>
                                                        <p style={{margin: '10px 0 0 0', fontSize: 'larger'}}>{code}</p>
                                                    </li>
                                                })}
                                            </ul>
                                        </div>
                                        <div style={{width: "50%"}}>
                                            <form onSubmit={handleSubmit}>
                                                <input
                                                    className={'admin-secret-input'}
                                                    type="text"
                                                    placeholder={"Name"}
                                                    value={adminSecret}
                                                    onChange={e => setAdminSecret(e.target.value)}
                                                />
                                                <br/>
                                                <br/>
                                                <br/>
                                                <div>
                                                    <button type="button" className="generate-secret-button"
                                                            onClick={() => getAdminSecret()}>
                                                        {
                                                            !gettingAdminSecret ?
                                                                'Generate Secret Key' :
                                                                <Loader type="Oval" color="white" height={15} width={15}/>
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
                                                                         copySharedSecretToClipBoard(sharedSecret);
                                                                         copyEncryptedKeyToClipBoard('');
                                                                     }}>
                                                        <button type='button' className={'copy-button'}>Copy
                                                        </button>
                                                    </CopyToClipboard>
                                                </div>
                                                <div style={{display: "none", marginLeft: '25px', width: '100%'}}>
                                                    <input
                                                        className={'shared-secret'}
                                                        type="text"
                                                        placeholder={"Encrypted-secret."}
                                                        value={encryptedKey}
                                                        onChange={e => setEncryptedKey(e.target.value)}
                                                    />
                                                    <CopyToClipboard text={encryptedKey}
                                                                     onCopy={() => {
                                                                         copyEncryptedKeyToClipBoard(encryptedKey);
                                                                         copySharedSecretToClipBoard('');
                                                                     }}>
                                                        <button type='button' className={'copy-button'}>
                                                            Copy
                                                        </button>
                                                    </CopyToClipboard>
                                                </div>
                                                <div>
                                                    <button
                                                        style={{cursor: (!adminSecret || !sharedSecret) ? 'no-drop' : 'pointer'}}
                                                        type="submit" value="Submit" className="save-button">
                                                        save
                                                    </button>
                                                </div>
                                            </form>
                                        </div>
                                        {
                                            encryptedKeyToClipBoard ?
                                                <div>
                                                    <span className={"success-message"}>Encrypted Key copied to clipboard.</span>
                                                </div>
                                                :
                                                ''
                                        }
                                        {
                                            sharedSecretToClipBoard ?
                                                <div>
                                                    <span className={"success-message"}>Secret Key copied to clipboard.</span>
                                                </div>
                                                :
                                                ''
                                        }
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
            <Footer />
        </div>
        :
        <Login/>
  )
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