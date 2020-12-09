<template>
  <b-navbar  toggleable="md"
    type="dark"
    variant="dark">
    <b-navbar-brand :to="{ name: 'Home'}">Home</b-navbar-brand>
    <b-navbar-nav>
      <b-nav-item-dropdown v-if="isAuthenticated" text="Captchas" right>
        <b-dropdown-item v-if="isAuthenticated" :to="{ name: 'Captchas'}">Previous Captchas</b-dropdown-item> 
        <b-dropdown-item v-if="isAuthenticated" :to="{ name: 'CaptchaUpload'}">Upload New</b-dropdown-item>    
      </b-nav-item-dropdown>
      <b-nav-item-dropdown text="User" left>
        <b-dropdown-item v-if="!isAuthenticated" :to="{ name: 'Login'}">Login</b-dropdown-item>
        <b-dropdown-item v-if="!isAuthenticated" :to="{ name: 'Register'}">Register</b-dropdown-item>
        <b-dropdown-item v-if="isAuthenticated" href="#" v-on:click="logout">Sign Out</b-dropdown-item>
      </b-nav-item-dropdown>
    </b-navbar-nav>
  </b-navbar>
</template>
<script>
export default {
  name: 'Navbar',
  computed: {
    isAuthenticated () {      
      return this.$store.getters.isAuthenticated;
    },    
  },
    methods: {

    logout: function () {
      this.$store.dispatch('logoff').then(() => {this.$router.push('/')});    
    }
  }
  

};
</script>