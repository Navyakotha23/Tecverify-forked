import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "../pages/Home.css";
import Loader from "react-loader-spinner";

const LoginError = () => {

    const { authState, authService } = useOktaAuth();
    const [loader, setLoader] = useState(true);
    const logout = async () => authService.logout('/login');
    setTimeout(() => {
        setLoader(false);
    }, 2000)
    return (
        !authState.isAuthenticated && authState.idToken !== null && authState.idToken === undefined ? (
            <div className="popup-box" style={{background: '#ffffff50'}}>
                {
                    !loader ?
                    <div className="box">
                        <p style={{fontSize: "initial"}}>Error : Unable to get Token info.</p>
                        <div style={{width: "100%"}}>
                            <button className="button" style={{float: 'right', borderRadius: '5px'}} onClick={() => logout()}>
                                ok
                            </button>
                        </div>
                    </div>
                        : <div style={{top: '40%',position: 'absolute',left: '50%'}}><Loader type="Oval" color="#007dc1" height={50} width={50}/></div>
                }
            </div>
        ) : ''
    )
}
export default LoginError
