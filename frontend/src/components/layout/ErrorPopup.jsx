import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "../pages/Home.css";

const ErrorPopup = ({noError, logoutInErrorPopup, onClose}) => {


    const { authState, authService } = useOktaAuth();
    const logout = async () => authService.logout('/login');

    return (
        <div className="popup-box">
            <div className="box">
                <p style={{fontSize: "initial"}}>{noError}</p>
                <div style={{width: "100%"}}>
                    {
                        logoutInErrorPopup ?
                            <button className="button logout-button" onClick={logout}>
                                logout
                            </button>
                            :
                            <button className="button logout-button" onClick={onClose}>
                                Ok
                            </button>

                    }
                </div>
            </div>
        </div>
    )
}
export default ErrorPopup