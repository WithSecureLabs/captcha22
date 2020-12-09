import Vue from 'vue';
import Vuex from 'vuex';

import {isValidJwt, getRole, EventBus, authenticate, register, registerLecturer} from '../api-services/auth.service';

import UserService from '../api-services/user.service';

import CaptchaService from '../api-services/captchas.service';



Vue.use(Vuex);

const USER_RESOURCE_NAME = '/user';

const state = {
    user: '',
    jwt: ''
};

const actions = {

    //Authentication APIs with state
    login (context, data) {
        context.commit('setUsername', { data });
        return authenticate(data.username, data.password)
        .then(response => context.commit('setJwtToken', {jwt : response.data}))
        .catch(error => {
            console.log('Error authenticating: ', error)
            EventBus.$emit('failedAuthentication', 'Authentication Attempt Failed')
        })
    },
    logoff (context) {
        context.commit('clearJWTToken');
        return '';
    },


    //Register
    register (context, data) { 
        console.log("In the actual function in the backend");

        return register(data.username, data.password)
                .then(response => console.log(response.data))
                .catch(error => {
                    console.log('Error registering: ', error)
                    EventBus.$emit('failedRegistration', 'Registration Attempt Failed')
                })
    },

    

    //User APIs with state
    getUser(context, data) {
        console.log("Key: "+ context.state.jwt);
        return UserService.getUser(data, context.state.jwt);
    },
    getUserAll(context) {
        console.log("KeyT: "+ context.state.jwt);
        return UserService.getAll(context.state.jwt);
    },

    deleteUser(context, data) {
        return UserService.deleteUser(data, context.state.jwt);
    },

    updateUser(context, data) {
        return UserService.updateUser(data, context.state.jwt);
    },

    uploadPic(context, data) {
        return UserService.uploadPic(data, context.state.jwt);
    },


    getCaptchaAll(context) {
        return CaptchaService.getAll(context.state.jwt);
    },

    getCaptcha(context, data) {
        return CaptchaService.getCaptcha(data, context.state.jwt);
    },

    getCaptchaTraining(context, data) {
        return CaptchaService.getCaptchaTraining(data, context.state.jwt);
    },

    getCaptchaResults(context, data) {
        return CaptchaService.getCaptchaResults(data, context.state.jwt);
    },

    getCaptchasFiltered(context, data) {
        return CaptchaService.getFiltered(context.state.jwt, data.dStart, data.dEnd, data.category);
    }, 

    activateCaptchaModel(context, data) {
        return CaptchaService.activateCaptchaModel(data, context.state.jwt);
    },

    downloadCaptchaModel(context, data) {
        return CaptchaService.downloadCaptchaModel(data, context.state.jwt);
    },

    uploadCaptcha(context, data) {
        return CaptchaService.uploadCaptcha(data, context.state.jwt);
    },

}

const mutations = {
    setUsername(state, payload) {
       
        state.username = payload.username;
    },
    setJwtToken (state, payload) {        
        localStorage.token = payload.jwt.token;
        state.jwt = payload.jwt.token;
        state.tokenTime = new Date();
    },
    clearJWTToken(state) {
        localStorage.token = '';
        state.jwt = '';
        state.user = '';
        state.tokenTime = '';
    }
}

const getters = {
    //resuable data accessors
    isAuthenticated (state)
    {
        return isValidJwt(state);
    },    
    isEmployee (state)
    {
        if (getRole(state.jwt) == "1")
        {
            return true;
        }
        else
        {
            return false;
        }
    },
    isCustomer (state)
    {
        if (getRole(state.jwt) == "0")
        {
            return true;
        }
        else
        {
            return false;
        }
    }
}

const store = new Vuex.Store({
    state,
    actions,
    mutations,
    getters
})

export default store;