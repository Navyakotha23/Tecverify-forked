import "./Home.css";
import { useHistory } from "react-router-dom";
import {useOktaAuth} from "@okta/okta-react";

const Dashboard = () => {
    const history = useHistory();
    const { authState } = useOktaAuth();
    if(authState.isAuthenticated){
        history.push('/home');
    } else {
        history.push('/login');
    }
    return (
        ''
    )
}
export default Dashboard