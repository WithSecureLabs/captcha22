// utils/auth.service.js

import Vue from 'vue';
import Axios from 'axios';

const RESOURCE_NAME = '/generate_token';

const REGISTER_RESOURCE_NAME = '/register';

const REGISTER_NAME = '/user';
const REGISTER_LEC_RESOURCE_NAME = '/registerLecturer';

export const EventBus = new Vue();

export function isValidJwt(key) {
    console.log("in the auth valid function with: " + key.jwt);
    if (!key.jwt)
    {
        return false;
    }
    //Currently, we hardcode the time that the token is valid for
    const exp = new Date(key.tokenTime);
    exp.setSeconds( exp.getSeconds() + 3000 );
    const now = new Date();
    console.log("This time of token issue was: " + key.tokenTime);
    console.log("This time of token revoke is: " + exp)        
    return now < exp;
}

export function getRole(jwt) {
    //This function has yet to be implemented - If there are more roles, we can add a checker, currently we only have one role.
    return 0;
}

export function authenticate (username, password) {
   
    return Axios.get(RESOURCE_NAME, {        
        headers: {
           Authorization : 'Basic ' + window.btoa(username + ':' + password)         
        }
    });
}

export function register (username, password) {

    console.log("In the actual register function");
    
    var data = {
        username : username,
        password: password
    }

    console.log(data);
   
    return Axios.post(REGISTER_NAME, data);
}


export default {   

    getToken(username, password) {
        return Axios.get(RESOURCE_NAME, {
            params: {
                username : username,
                password: password
            }
        });
    }

}