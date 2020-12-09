import Vue from 'vue';
import Router from 'vue-router';
import _ from 'lodash'; 
import Home from '@/components/Home';
import NotFound from '@/components/error-pages/NotFound';
import UserList from '@/components/user/UserList';
import UserDetails from '@/components/user/UserDetails';
import UserUpdate from '@/components/user/UserUpdate';
import Login from '@/components/auth/Login';
import store from '@/store';
import Register from '@/components/auth/Register';

import CaptchaList from '@/components/captchas/CaptchaList';
import CaptchaDetails from '@/components/captchas/CaptchaDetails';

import CaptchaUpload from '@/components/captchas/UploadCaptcha';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
    {
      path: '/captchas',
      name: 'Captchas',
      component: CaptchaList
    },
    {
      path: '/captchas/:id',
      name: 'CaptchaDetails',
      component: CaptchaDetails
    },
    {
      path: '/captchaUpload',
      name: 'CaptchaUpload',
      component: CaptchaUpload
    }, 
    
    {
      path: '/login',
      name: 'Login',
      component: Login
    },    
    {
      path: '*',
      name: 'NotFound',
      component: NotFound
    }
  ]
})
