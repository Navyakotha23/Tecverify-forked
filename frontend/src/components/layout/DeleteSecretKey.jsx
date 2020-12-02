import React, {useState} from 'react';
import {useOktaAuth} from '@okta/okta-react';
import "../pages/Home.css";

const DeleteSecretKey = ({setSelectedSecretId, setSelectedSecretName, showDeleteConfirmationPopup, code, token}) => {

    return (
        // !deleteConfirmationPopup ?
            <button className={'trash-icon'} onClick={() => {
                showDeleteConfirmationPopup(true);
                setSelectedSecretName(code.secretname);
                setSelectedSecretId(code.id);
            }}>
                <svg viewBox="0 0 512 512">
                    <path
                        fill="var(--ci-primary-color, currentColor)"
                        d="M96,472.205A23.715,23.715,0,0,0,119.579,496H392.421A23.715,23.715,0,0,0,416,472.205V168H96ZM334,232h36V432H334Zm-96,0h36V432H238Zm-96,0h36V432H142Z"
                        className="ci-primary"/>
                    <path
                        fill="var(--ci-primary-color, currentColor)"
                        d="M333,91V48c0-16.262-11.684-29-26.6-29H205.6C190.684,19,179,31.738,179,48V91H64v42H448V91ZM221,61h70V91H221Z"
                        className="ci-primary"/>
                </svg>
            </button>
            // :
            // <div className="popup-box">
            //     <div className="box" style={{width: '55%', padding: '0'}}>
            //         <h3 className="container-header" style={{background: '#f76868'}}>Confirm</h3>
            //         <p style={{fontSize: "initial", margin: '20px'}}>Are yoy sure you want to delete ByPass code {code.secretname} ?</p>
            //         <div style={{width: "100%"}}>
            //             <button className="button delete-button" onClick={() => showDeleteConfirmationPopup(true)}>
            //                 Confirm
            //             </button>
            //             <button className="button cancel-button" onClick={() => showDeleteConfirmationPopup(false)}>
            //                 cancel
            //             </button>
            //         </div>
            //     </div>
            // </div>
    )
}
export default DeleteSecretKey